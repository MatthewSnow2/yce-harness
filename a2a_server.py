"""
YCE A2A Thin Wrapper Server

Exposes YCE Harness queue_runner.py as an A2A-compliant agent.
Metroplex dispatches builds via A2A protocol instead of raw subprocess calls.
"""
import asyncio
import json
import logging
import os
import signal
import subprocess
import tempfile
import uuid
from pathlib import Path

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Artifact,
    Message,
    Part,
    Role,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TextPart,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("yce-a2a")

YCE_DIR = Path(__file__).parent
QUEUE_RUNNER = YCE_DIR / "queue_runner.py"
YCE_PYTHON = YCE_DIR / "venv" / "bin" / "python"
RUNNER_PID_FILE = YCE_DIR / "data" / "runner.pid"

BUILD_TIMEOUT = 5400  # 90 minutes
POLL_INTERVAL = 5  # seconds


class YCEBuildExecutor(AgentExecutor):
    """Executes YCE builds by shelling out to queue_runner.py."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id
        context_id = context.context_id

        # Extract build params from the incoming message
        try:
            params = self._extract_params(context.message)
        except (ValueError, KeyError) as e:
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id,
                    context_id=context_id,
                    final=True,
                    status=TaskStatus(state=TaskState.failed, message=Message(
                        role=Role.agent, parts=[TextPart(text=f"Invalid params: {e}")],
                        message_id=str(uuid.uuid4()),
                    )),
                )
            )
            return

        # Signal working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                final=False,
                status=TaskStatus(state=TaskState.working),
            )
        )

        job_id = params["job_id"]
        spec_content = params["spec_content"]
        model = params.get("model", "opus")
        parallel = params.get("parallel", False)
        max_workers = params.get("max_workers", 2)

        # Write spec to temp file
        spec_dir = YCE_DIR / "data" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_path = spec_dir / f"{job_id}.txt"
        spec_path.write_text(spec_content)

        # Queue the build via queue_runner.py add
        command = [
            str(YCE_PYTHON), str(QUEUE_RUNNER), "add",
            str(spec_path), "--id", job_id, "--model", model,
        ]
        if parallel:
            command.extend(["--parallel", "--max-workers", str(max_workers)])

        try:
            result = await asyncio.to_thread(
                subprocess.run, command, capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                error = result.stderr.strip() or result.stdout.strip() or "queue_runner add failed"
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id, context_id=context_id, final=True,
                        status=TaskStatus(state=TaskState.failed, message=Message(
                            role=Role.agent, parts=[TextPart(text=error)],
                            message_id=str(uuid.uuid4()),
                        )),
                    )
                )
                return
        except subprocess.TimeoutExpired:
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=task_id, context_id=context_id, final=True,
                    status=TaskStatus(state=TaskState.failed, message=Message(
                        role=Role.agent, parts=[TextPart(text="queue_runner add timed out")],
                        message_id=str(uuid.uuid4()),
                    )),
                )
            )
            return

        # Poll queue_runner.py status until terminal
        elapsed = 0
        while elapsed < BUILD_TIMEOUT:
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

            status_cmd = [
                str(YCE_PYTHON), str(QUEUE_RUNNER),
                "status", "--id", job_id, "--json",
            ]
            try:
                poll_result = await asyncio.to_thread(
                    subprocess.run, status_cmd, capture_output=True, text=True, timeout=30,
                )
                if poll_result.returncode != 0:
                    continue
                status_data = json.loads(poll_result.stdout)
            except (subprocess.TimeoutExpired, json.JSONDecodeError):
                continue

            # queue_runner --json outputs {"jobs": [...], "summary": {...}}
            jobs_list = status_data.get("jobs", [])
            if not jobs_list:
                continue
            job_data = jobs_list[0]
            job_status = job_data.get("status", "unknown")

            if job_status == "completed":
                artifacts_text = json.dumps({
                    "job_id": job_id,
                    "project_dir": job_data.get("project_dir", ""),
                    "status": "completed",
                })
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        task_id=task_id, context_id=context_id,
                        artifact=Artifact(
                            artifact_id=str(uuid.uuid4()),
                            name="build_result",
                            parts=[TextPart(text=artifacts_text)],
                        ),
                    )
                )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id, context_id=context_id, final=True,
                        status=TaskStatus(state=TaskState.completed),
                    )
                )
                return

            if job_status == "failed":
                error_msg = job_data.get("error", "Build failed")
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id, context_id=context_id, final=True,
                        status=TaskStatus(state=TaskState.failed, message=Message(
                            role=Role.agent, parts=[TextPart(text=error_msg)],
                            message_id=str(uuid.uuid4()),
                        )),
                    )
                )
                return

        # Timeout
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id, context_id=context_id, final=True,
                status=TaskStatus(state=TaskState.failed, message=Message(
                    role=Role.agent, parts=[TextPart(text=f"Build timed out after {BUILD_TIMEOUT}s")],
                    message_id=str(uuid.uuid4()),
                )),
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Kill the runner process
        if RUNNER_PID_FILE.exists():
            try:
                pid = int(RUNNER_PID_FILE.read_text().strip())
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except (ValueError, ProcessLookupError, PermissionError):
                pass

        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                final=True,
                status=TaskStatus(state=TaskState.canceled),
            )
        )

    def _extract_params(self, message: Message) -> dict:
        """Extract build parameters from the first TextPart as JSON."""
        for part in message.parts:
            if isinstance(part, TextPart):
                return json.loads(part.text)
        raise ValueError("No TextPart found in message")


def build_agent_card() -> AgentCard:
    return AgentCard(
        name="yce-build-agent",
        description="YCE Harness autonomous build agent. Accepts spec content and dispatches builds.",
        url="http://127.0.0.1:18900",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[
            AgentSkill(
                id="build",
                name="Build",
                description="Build a project from an app spec",
                tags=["build", "yce", "autonomous"],
            ),
        ],
    )


def main():
    agent_card = build_agent_card()
    executor = YCEBuildExecutor()
    task_store = InMemoryTaskStore()
    queue_manager = InMemoryQueueManager()
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        queue_manager=queue_manager,
    )
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=handler)
    uvicorn.run(app.build(), host="127.0.0.1", port=18900)


if __name__ == "__main__":
    main()
