#!/usr/bin/env python3
"""
Queue Runner
============

Multi-project job queue for yce-harness. Feeds app specs to
autonomous_agent_demo.py sequentially, enabling Metroplex (the L5
autonomy layer) to queue multiple builds.

Usage:
    python queue_runner.py add prompts/app_spec.txt --id metroplex --model haiku
    python queue_runner.py add spec.txt --id my-app --model sonnet --parallel --max-workers 3
    python queue_runner.py start
    python queue_runner.py start --dry-run
    python queue_runner.py status
    python queue_runner.py status --id metroplex
    python queue_runner.py status --json
"""

import argparse
import asyncio
import fcntl
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


# --- Constants ---

HARNESS_DIR: Path = Path(__file__).parent
QUEUE_DIR: Path = HARNESS_DIR / "data"
QUEUE_FILE: Path = QUEUE_DIR / "queue.json"
QUEUE_LOCK: Path = QUEUE_DIR / "queue.lock"
RUNNER_PID_FILE: Path = QUEUE_DIR / "runner.pid"
APP_SPEC_PATH: Path = HARNESS_DIR / "prompts" / "app_spec.txt"

# Graceful shutdown timeout before SIGKILL
SHUTDOWN_TIMEOUT_SECONDS: int = 15


@contextmanager
def queue_lock():
    """Advisory exclusive lock for queue.json access.

    MUST be used by ALL code paths that read or write queue.json:
    cmd_add, cmd_start, cmd_status. Uses fcntl.flock which auto-releases
    on process crash (fd close).
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    fd = open(QUEUE_LOCK, "w")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()


# --- Models ---


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    interrupted = "interrupted"


class QueueJob(BaseModel):
    id: str
    spec_path: str
    model: str = "haiku"
    max_iterations: int = 20
    parallel: bool = False
    max_workers: int = 2
    status: JobStatus = JobStatus.pending
    project_dir: str | None = None
    exit_code: int | None = None
    error: str | None = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None


class QueueState(BaseModel):
    version: int = 1
    jobs: list[QueueJob] = Field(default_factory=list)


# --- Persistence ---


def load_queue() -> QueueState:
    """Load queue state from disk, or return empty state."""
    if not QUEUE_FILE.exists():
        return QueueState()
    data = json.loads(QUEUE_FILE.read_text())
    return QueueState.model_validate(data)


def save_queue(state: QueueState) -> None:
    """Save queue state to disk atomically.

    Writes to a temp file, fsyncs, then renames. The rename is atomic
    on Linux for same-filesystem operations, protecting against
    crash-during-write producing truncated JSON.
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    data = json.dumps(state.model_dump(mode="json"), indent=2) + "\n"
    fd_num, tmp_path = tempfile.mkstemp(dir=QUEUE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd_num, "w") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp_path, QUEUE_FILE)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# --- Helpers ---


def _get_processable_jobs(state: QueueState) -> list[QueueJob]:
    """Return jobs eligible for processing (pending, interrupted, or stale running)."""
    return [
        job
        for job in state.jobs
        if job.status in (JobStatus.pending, JobStatus.interrupted, JobStatus.running)
    ]


def _build_command(job: QueueJob) -> list[str]:
    """Build the subprocess command list for autonomous_agent_demo.py.

    Passes the spec path directly via --spec-path, eliminating the need
    for the global prompts/app_spec.txt swap mechanism. This is required
    for Level 2 concurrent builds where multiple jobs run simultaneously.
    """
    spec_source = Path(job.spec_path)
    if not spec_source.is_absolute():
        spec_source = HARNESS_DIR / spec_source

    cmd = [
        sys.executable,
        str(HARNESS_DIR / "autonomous_agent_demo.py"),
        "--project-dir",
        job.id,
        "--model",
        job.model,
        "--max-iterations",
        str(job.max_iterations),
        "--spec-path",
        str(spec_source.resolve()),
    ]
    if job.parallel:
        cmd.append("--parallel")
        cmd.extend(["--max-workers", str(job.max_workers)])
    return cmd


def _run_job(job: QueueJob, dry_run: bool = False) -> None:
    """
    Execute a single queue job.

    Each job's spec file is passed via --spec-path to autonomous_agent_demo.py.
    No global file swap is needed -- concurrent jobs use their own spec files.
    """
    spec_source = Path(job.spec_path)
    if not spec_source.is_absolute():
        spec_source = HARNESS_DIR / spec_source

    if not spec_source.exists():
        job.status = JobStatus.failed
        job.error = f"Spec file not found: {spec_source}"
        return

    # Resolve project dir
    job.project_dir = str(HARNESS_DIR / "generations" / job.id)

    cmd = _build_command(job)

    if dry_run:
        print(f"  [dry-run] Would execute: {' '.join(cmd)}")
        print(f"  [dry-run] Spec: {spec_source}")
        print(f"  [dry-run] Project dir: {job.project_dir}")
        return

    try:
        job.status = JobStatus.running
        job.started_at = datetime.now(timezone.utc).isoformat()

        print(f"\n{'=' * 70}")
        print(f"  QUEUE: Starting job '{job.id}'")
        print(f"  Model: {job.model} | Parallel: {job.parallel} | Spec: {spec_source.name}")
        print(f"{'=' * 70}\n")

        start_time = time.monotonic()

        result = subprocess.run(
            cmd,
            cwd=str(HARNESS_DIR),
        )

        elapsed = time.monotonic() - start_time
        job.exit_code = result.returncode
        job.duration_seconds = round(elapsed, 1)
        job.completed_at = datetime.now(timezone.utc).isoformat()

        if result.returncode == 0:
            job.status = JobStatus.completed
        elif result.returncode == 130:
            job.status = JobStatus.interrupted
        else:
            job.status = JobStatus.failed
            job.error = f"Process exited with code {result.returncode}"

    except KeyboardInterrupt:
        job.status = JobStatus.interrupted
        job.completed_at = datetime.now(timezone.utc).isoformat()
        raise
    except Exception as e:
        job.status = JobStatus.failed
        job.error = str(e)
        job.completed_at = datetime.now(timezone.utc).isoformat()


# --- Process Registry ---


class ProcessRegistry:
    """Tracks active child processes for graceful shutdown.

    Each child is spawned with os.setsid so it heads its own process group.
    On shutdown, we SIGTERM the entire group, then SIGKILL after timeout.
    """

    def __init__(self) -> None:
        self._children: dict[str, asyncio.subprocess.Process] = {}

    def register(self, job_id: str, proc: asyncio.subprocess.Process) -> None:
        self._children[job_id] = proc

    def unregister(self, job_id: str) -> None:
        self._children.pop(job_id, None)

    @property
    def active_count(self) -> int:
        return len(self._children)

    async def terminate_all(self) -> None:
        """Send SIGTERM to all child process groups, SIGKILL after timeout."""
        if not self._children:
            return

        # Phase 1: SIGTERM to each child's process group
        for job_id, proc in self._children.items():
            if proc.returncode is None:
                try:
                    pgid = os.getpgid(proc.pid)
                    os.killpg(pgid, signal.SIGTERM)
                    print(f"  [shutdown] Sent SIGTERM to job '{job_id}' (PGID {pgid})")
                except (ProcessLookupError, PermissionError):
                    pass

        # Phase 2: Wait up to SHUTDOWN_TIMEOUT_SECONDS, then SIGKILL stragglers
        deadline = time.monotonic() + SHUTDOWN_TIMEOUT_SECONDS
        for job_id, proc in list(self._children.items()):
            remaining = max(0.1, deadline - time.monotonic())
            try:
                await asyncio.wait_for(proc.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                try:
                    pgid = os.getpgid(proc.pid)
                    os.killpg(pgid, signal.SIGKILL)
                    print(f"  [shutdown] Sent SIGKILL to job '{job_id}' (PGID {pgid})")
                except (ProcessLookupError, PermissionError):
                    pass

        self._children.clear()


# --- Runner PID Lock ---


def _acquire_runner_lock() -> int | None:
    """Acquire exclusive runner lock via PID file.

    Returns the lock fd on success, None if another runner is active.
    Uses LOCK_NB (non-blocking) to fail fast.
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(RUNNER_PID_FILE), os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write our PID
        os.ftruncate(fd, 0)
        os.write(fd, str(os.getpid()).encode())
        return fd
    except BlockingIOError:
        os.close(fd)
        return None


def _release_runner_lock(fd: int) -> None:
    """Release runner lock and clean up PID file."""
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        RUNNER_PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


# --- Async Job Execution ---


async def _run_job_async(
    job: QueueJob,
    registry: ProcessRegistry,
    shutdown_event: asyncio.Event,
) -> None:
    """
    Execute a single queue job asynchronously.

    Uses asyncio.create_subprocess_exec for non-blocking execution.
    Each child process gets its own process group (os.setsid) for
    clean shutdown. Streams output with [job-id] prefix.
    """
    spec_source = Path(job.spec_path)
    if not spec_source.is_absolute():
        spec_source = HARNESS_DIR / spec_source

    if not spec_source.exists():
        job.status = JobStatus.failed
        job.error = f"Spec file not found: {spec_source}"
        return

    job.project_dir = str(HARNESS_DIR / "generations" / job.id)
    cmd = _build_command(job)

    # Check for shutdown before starting
    if shutdown_event.is_set():
        return

    try:
        job.status = JobStatus.running
        job.started_at = datetime.now(timezone.utc).isoformat()

        print(f"\n{'=' * 70}")
        print(f"  QUEUE: Starting job '{job.id}' (async)")
        print(f"  Model: {job.model} | Parallel: {job.parallel} | Spec: {spec_source.name}")
        print(f"{'=' * 70}\n")

        start_time = time.monotonic()

        # Spawn with its own process group for clean shutdown
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(HARNESS_DIR),
            preexec_fn=os.setsid,
        )

        registry.register(job.id, proc)

        # Stream output with job prefix
        assert proc.stdout is not None
        while True:
            # Use a timeout on readline so we can check shutdown_event
            try:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=2.0)
            except asyncio.TimeoutError:
                if shutdown_event.is_set():
                    break
                continue
            if not line:
                break
            print(f"  [{job.id}] {line.decode().rstrip()}", flush=True)

        await proc.wait()
        registry.unregister(job.id)

        elapsed = time.monotonic() - start_time
        job.exit_code = proc.returncode
        job.duration_seconds = round(elapsed, 1)
        job.completed_at = datetime.now(timezone.utc).isoformat()

        if proc.returncode == 0:
            job.status = JobStatus.completed
        elif proc.returncode in (130, -signal.SIGTERM):
            job.status = JobStatus.interrupted
        else:
            job.status = JobStatus.failed
            job.error = f"Process exited with code {proc.returncode}"

    except asyncio.CancelledError:
        job.status = JobStatus.interrupted
        job.completed_at = datetime.now(timezone.utc).isoformat()
        registry.unregister(job.id)
    except Exception as e:
        job.status = JobStatus.failed
        job.error = str(e)
        job.completed_at = datetime.now(timezone.utc).isoformat()
        registry.unregister(job.id)
    finally:
        # Persist status immediately after each job completes
        with queue_lock():
            save_queue(load_queue())  # Reload to avoid overwriting concurrent changes
            # Re-apply this job's status to the freshly loaded state
            fresh_state = load_queue()
            for j in fresh_state.jobs:
                if j.id == job.id:
                    j.status = job.status
                    j.started_at = job.started_at
                    j.completed_at = job.completed_at
                    j.duration_seconds = job.duration_seconds
                    j.exit_code = job.exit_code
                    j.error = job.error
                    j.project_dir = job.project_dir
                    break
            save_queue(fresh_state)


async def cmd_start_async(concurrency: int, dry_run: bool = False) -> int:
    """Process the queue with bounded concurrency.

    Uses asyncio.Semaphore to limit concurrent builds. Each job runs
    as an async task with its own subprocess.

    Args:
        concurrency: Maximum concurrent jobs.
        dry_run: If True, print commands without executing.

    Returns:
        Exit code (0 success, 130 interrupted).
    """
    # Acquire runner lock (prevent duplicate instances)
    lock_fd = _acquire_runner_lock()
    if lock_fd is None:
        try:
            existing_pid = RUNNER_PID_FILE.read_text().strip()
        except (FileNotFoundError, OSError):
            existing_pid = "unknown"
        print(f"Error: Another queue runner is already active (PID {existing_pid})")
        return 1

    try:
        # Legacy cleanup
        backup_path = APP_SPEC_PATH.with_suffix(".txt.bak")
        if backup_path.exists():
            print(f"[recovery] Found stale spec backup, restoring {APP_SPEC_PATH.name}")
            shutil.move(str(backup_path), str(APP_SPEC_PATH))

        with queue_lock():
            state = load_queue()
            processable = _get_processable_jobs(state)

        if not processable:
            print("Queue is empty or all jobs are completed/failed.")
            return 0

        if dry_run:
            for job in processable:
                _run_job(job, dry_run=True)
            return 0

        print(f"Processing {len(processable)} job(s) with concurrency={concurrency}...\n")

        registry = ProcessRegistry()
        shutdown_event = asyncio.Event()
        semaphore = asyncio.Semaphore(concurrency)

        # Install signal handlers
        loop = asyncio.get_running_loop()

        def _handle_signal(sig: int) -> None:
            sig_name = signal.Signals(sig).name
            print(f"\n  [runner] Received {sig_name}, initiating graceful shutdown...")
            shutdown_event.set()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, _handle_signal, sig)

        async def _guarded_run(job: QueueJob) -> None:
            """Run a job behind the semaphore gate."""
            async with semaphore:
                if shutdown_event.is_set():
                    return
                await _run_job_async(job, registry, shutdown_event)

        # Launch all jobs as tasks (semaphore controls actual concurrency)
        tasks = [asyncio.create_task(_guarded_run(job)) for job in processable]

        # Wait for all tasks or shutdown
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass

        # If shutdown was requested, terminate remaining children
        if shutdown_event.is_set():
            print("  [runner] Shutting down active builds...")
            await registry.terminate_all()

        # Print summary
        with queue_lock():
            state = load_queue()

        completed = sum(1 for j in state.jobs if j.status == JobStatus.completed)
        failed = sum(1 for j in state.jobs if j.status == JobStatus.failed)
        pending = sum(1 for j in state.jobs if j.status == JobStatus.pending)
        inter = sum(1 for j in state.jobs if j.status == JobStatus.interrupted)

        print(f"\n{'=' * 70}")
        print(f"  QUEUE SUMMARY")
        print(f"  Completed: {completed} | Failed: {failed} | Pending: {pending} | Interrupted: {inter}")
        print(f"{'=' * 70}")

        return 130 if shutdown_event.is_set() else 0

    finally:
        _release_runner_lock(lock_fd)


# --- CLI Commands ---


def cmd_add(args: argparse.Namespace) -> int:
    """Add a job to the queue."""
    spec = Path(args.spec_path)
    if not spec.is_absolute():
        spec = HARNESS_DIR / spec

    if not spec.exists():
        print(f"Error: Spec file not found: {spec}")
        return 1

    with queue_lock():
        state = load_queue()

        # Check for duplicate ID
        existing_ids = {job.id for job in state.jobs}
        if args.id in existing_ids:
            print(f"Error: Job with id '{args.id}' already exists")
            print("Use a different --id or remove the existing job from data/queue.json")
            return 1

        job = QueueJob(
            id=args.id,
            spec_path=args.spec_path,
            model=args.model,
            max_iterations=args.max_iterations,
            parallel=args.parallel,
            max_workers=args.max_workers,
        )

        state.jobs.append(job)
        save_queue(state)

    print(f"Added job '{job.id}' to queue")
    print(f"  Spec: {args.spec_path}")
    print(f"  Model: {job.model} | Iterations: {job.max_iterations} | Parallel: {job.parallel}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    """Process the queue sequentially."""
    # Legacy cleanup: if a .bak from the old spec swap mechanism exists, restore it.
    backup_path = APP_SPEC_PATH.with_suffix(".txt.bak")
    if backup_path.exists():
        print(f"[recovery] Found stale spec backup from old swap mechanism, restoring {APP_SPEC_PATH.name}")
        shutil.move(str(backup_path), str(APP_SPEC_PATH))

    with queue_lock():
        state = load_queue()
        processable = _get_processable_jobs(state)

    if not processable:
        print("Queue is empty or all jobs are completed/failed.")
        return 0

    print(f"Processing {len(processable)} job(s)...\n")

    interrupted = False
    for job in processable:
        try:
            _run_job(job, dry_run=args.dry_run)
        except KeyboardInterrupt:
            print(f"\n\nInterrupted during job '{job.id}'")
            interrupted = True
            break
        finally:
            if not args.dry_run:
                with queue_lock():
                    save_queue(state)

    # Print summary
    if not args.dry_run:
        completed = sum(1 for j in state.jobs if j.status == JobStatus.completed)
        failed = sum(1 for j in state.jobs if j.status == JobStatus.failed)
        pending = sum(1 for j in state.jobs if j.status == JobStatus.pending)
        inter = sum(1 for j in state.jobs if j.status == JobStatus.interrupted)

        print(f"\n{'=' * 70}")
        print(f"  QUEUE SUMMARY")
        print(f"  Completed: {completed} | Failed: {failed} | Pending: {pending} | Interrupted: {inter}")
        print(f"{'=' * 70}")

    return 130 if interrupted else 0


def cmd_status(args: argparse.Namespace) -> int:
    """Display queue status."""
    with queue_lock():
        state = load_queue()

    if not state.jobs:
        if args.json:
            print(json.dumps({"jobs": [], "summary": {}}, indent=2))
        else:
            print("Queue is empty.")
        return 0

    # Filter by ID if provided
    jobs = state.jobs
    if args.id:
        jobs = [j for j in jobs if j.id == args.id]
        if not jobs:
            print(f"No job found with id '{args.id}'")
            return 1

    if args.json:
        output = {
            "jobs": [j.model_dump(mode="json") for j in jobs],
            "summary": {
                "total": len(state.jobs),
                "pending": sum(1 for j in state.jobs if j.status == JobStatus.pending),
                "running": sum(1 for j in state.jobs if j.status == JobStatus.running),
                "completed": sum(1 for j in state.jobs if j.status == JobStatus.completed),
                "failed": sum(1 for j in state.jobs if j.status == JobStatus.failed),
                "interrupted": sum(1 for j in state.jobs if j.status == JobStatus.interrupted),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Queue: {len(state.jobs)} job(s)\n")
        for job in jobs:
            status_icon = {
                JobStatus.pending: " ",
                JobStatus.running: "~",
                JobStatus.completed: "+",
                JobStatus.failed: "x",
                JobStatus.interrupted: "!",
            }.get(job.status, "?")
            duration = f" ({job.duration_seconds}s)" if job.duration_seconds else ""
            error = f" — {job.error}" if job.error else ""
            print(f"  [{status_icon}] {job.id}: {job.status.value}{duration}{error}")
            print(f"      spec={job.spec_path} model={job.model} parallel={job.parallel}")

    return 0


# --- Argument Parsing ---


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="yce-harness multi-project job queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python queue_runner.py add prompts/app_spec.txt --id metroplex --model haiku
  python queue_runner.py add spec.txt --id my-app --model sonnet --parallel --max-workers 3
  python queue_runner.py start
  python queue_runner.py start --dry-run
  python queue_runner.py status
  python queue_runner.py status --id metroplex --json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- add ---
    add_parser = subparsers.add_parser("add", help="Add a job to the queue")
    add_parser.add_argument(
        "spec_path",
        type=str,
        help="Path to the app spec file",
    )
    add_parser.add_argument(
        "--id",
        type=str,
        required=True,
        help="Unique job identifier (used as project directory name)",
    )
    add_parser.add_argument(
        "--model",
        type=str,
        choices=["haiku", "sonnet", "opus"],
        default="haiku",
        help="Orchestrator model (default: haiku)",
    )
    add_parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum agent iterations (default: 20)",
    )
    add_parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Enable parallel execution mode",
    )
    add_parser.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Max concurrent workers in parallel mode (default: 2)",
    )

    # --- start ---
    start_parser = subparsers.add_parser("start", help="Process the queue")
    start_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would run without executing",
    )
    start_parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Maximum concurrent builds (default: 1 = sequential). "
        "Values > 1 use async execution with bounded concurrency.",
    )

    # --- status ---
    status_parser = subparsers.add_parser("status", help="Show queue status")
    status_parser.add_argument(
        "--id",
        type=str,
        default=None,
        help="Filter by job ID",
    )
    status_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output machine-parseable JSON",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        return cmd_add(args)
    elif args.command == "start":
        concurrency = getattr(args, "concurrency", 1)
        if concurrency > 1:
            return asyncio.run(
                cmd_start_async(concurrency=concurrency, dry_run=args.dry_run)
            )
        else:
            return cmd_start(args)
    elif args.command == "status":
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
