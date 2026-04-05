"""Tests for the YCE A2A thin wrapper server."""
import json
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from a2a_server import YCEBuildExecutor, build_agent_card


@pytest.fixture
def executor():
    return YCEBuildExecutor()


@pytest.fixture
def mock_context():
    ctx = MagicMock()
    ctx.task_id = "test-task-123"
    ctx.context_id = "test-context-456"
    return ctx


@pytest.fixture
def mock_event_queue():
    eq = AsyncMock()
    eq.enqueue_event = AsyncMock()
    return eq


def make_message(params: dict):
    """Create a mock Message with TextPart containing JSON params."""
    part = MagicMock()
    part.text = json.dumps(params)
    # Make isinstance check work for TextPart
    from a2a.types import TextPart
    part.__class__ = TextPart
    msg = MagicMock()
    msg.parts = [part]
    return msg


class TestAgentCard:
    def test_card_has_required_fields(self):
        card = build_agent_card()
        assert card.name == "yce-build-agent"
        assert card.url == "http://127.0.0.1:18900"
        assert card.version == "1.0.0"
        assert len(card.skills) == 1
        assert card.skills[0].id == "build"

    def test_card_capabilities(self):
        card = build_agent_card()
        assert card.capabilities.streaming is False


class TestParamExtraction:
    def test_extract_valid_params(self, executor):
        params = {
            "spec_content": "build a calculator",
            "job_id": "test-job-1",
            "model": "haiku",
        }
        msg = make_message(params)
        result = executor._extract_params(msg)
        assert result["job_id"] == "test-job-1"
        assert result["model"] == "haiku"
        assert result["spec_content"] == "build a calculator"

    def test_extract_invalid_json(self, executor):
        part = MagicMock()
        part.text = "not json"
        from a2a.types import TextPart
        part.__class__ = TextPart
        msg = MagicMock()
        msg.parts = [part]
        with pytest.raises(json.JSONDecodeError):
            executor._extract_params(msg)

    def test_extract_no_text_part(self, executor):
        msg = MagicMock()
        msg.parts = []
        with pytest.raises(ValueError, match="No TextPart found"):
            executor._extract_params(msg)


class TestExecuteFailure:
    @pytest.mark.asyncio
    async def test_invalid_params_emits_failed(self, executor, mock_context, mock_event_queue):
        """Bad params should emit a failed status."""
        msg = MagicMock()
        msg.parts = []  # No TextPart
        mock_context.message = msg

        await executor.execute(mock_context, mock_event_queue)

        # Should have emitted exactly one event (failed)
        assert mock_event_queue.enqueue_event.call_count == 1
        event = mock_event_queue.enqueue_event.call_args[0][0]
        assert event.final is True
        assert event.status.state.value == "failed"

    @pytest.mark.asyncio
    async def test_queue_runner_failure_emits_failed(self, executor, mock_context, mock_event_queue):
        """queue_runner add returning non-zero should emit failed."""
        params = {
            "spec_content": "test spec",
            "job_id": "fail-job",
            "model": "haiku",
        }
        mock_context.message = make_message(params)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "some error"
        mock_result.stdout = ""

        with patch("a2a_server.asyncio.to_thread", return_value=mock_result):
            with patch("a2a_server.Path.write_text"):
                with patch("a2a_server.Path.mkdir"):
                    await executor.execute(mock_context, mock_event_queue)

        # Should have: working + failed = 2 events
        assert mock_event_queue.enqueue_event.call_count == 2
        last_event = mock_event_queue.enqueue_event.call_args_list[-1][0][0]
        assert last_event.final is True
        assert last_event.status.state.value == "failed"


class TestPollLoop:
    @pytest.mark.asyncio
    async def test_poll_to_completion(self, executor, mock_context, mock_event_queue):
        """Full happy path: add succeeds, poll returns completed with project_dir."""
        params = {
            "spec_content": "test spec",
            "job_id": "happy-job",
            "model": "haiku",
        }
        mock_context.message = make_message(params)

        # First call: queue_runner add (success)
        add_result = MagicMock()
        add_result.returncode = 0
        add_result.stdout = "Queued"

        # Second call: queue_runner status --json (completed)
        status_result = MagicMock()
        status_result.returncode = 0
        status_result.stdout = json.dumps({
            "jobs": [{
                "id": "happy-job",
                "status": "completed",
                "project_dir": "/tmp/generations/happy-job",
            }],
            "summary": {"total": 1, "completed": 1},
        })

        call_count = 0

        async def mock_to_thread(fn, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return add_result  # queue_runner add
            if call_count == 2:
                return None  # _ensure_runner_started
            return status_result  # queue_runner status

        with patch("a2a_server.asyncio.to_thread", side_effect=mock_to_thread):
            with patch("a2a_server.asyncio.sleep", new_callable=AsyncMock):
                with patch("a2a_server.Path.write_text"):
                    with patch("a2a_server.Path.mkdir"):
                        await executor.execute(mock_context, mock_event_queue)

        # Events: working + artifact + completed = 3
        assert mock_event_queue.enqueue_event.call_count == 3
        # Check final event is completed
        final_event = mock_event_queue.enqueue_event.call_args_list[-1][0][0]
        assert final_event.final is True
        assert final_event.status.state.value == "completed"
        # Check artifact contains project_dir
        artifact_event = mock_event_queue.enqueue_event.call_args_list[1][0][0]
        part = artifact_event.artifact.parts[0]
        # Part may be a union -- access .root.text if wrapped, else .text
        text = getattr(part, "text", None) or part.root.text
        art_data = json.loads(text)
        assert art_data["project_dir"] == "/tmp/generations/happy-job"

    @pytest.mark.asyncio
    async def test_poll_to_failure(self, executor, mock_context, mock_event_queue):
        """Poll loop detects failed status from queue_runner."""
        params = {
            "spec_content": "test spec",
            "job_id": "fail-poll-job",
            "model": "haiku",
        }
        mock_context.message = make_message(params)

        add_result = MagicMock()
        add_result.returncode = 0

        status_result = MagicMock()
        status_result.returncode = 0
        status_result.stdout = json.dumps({
            "jobs": [{
                "id": "fail-poll-job",
                "status": "failed",
                "error": "Build crashed",
            }],
            "summary": {"total": 1, "failed": 1},
        })

        call_count = 0

        async def mock_to_thread(fn, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return add_result  # queue_runner add
            if call_count == 2:
                return None  # _ensure_runner_started
            return status_result  # queue_runner status

        with patch("a2a_server.asyncio.to_thread", side_effect=mock_to_thread):
            with patch("a2a_server.asyncio.sleep", new_callable=AsyncMock):
                with patch("a2a_server.Path.write_text"):
                    with patch("a2a_server.Path.mkdir"):
                        await executor.execute(mock_context, mock_event_queue)

        # Events: working + failed = 2
        assert mock_event_queue.enqueue_event.call_count == 2
        final_event = mock_event_queue.enqueue_event.call_args_list[-1][0][0]
        assert final_event.final is True
        assert final_event.status.state.value == "failed"


class TestEnsureRunnerStarted:
    def test_no_pid_file_starts_runner(self, executor):
        """No PID file should start queue_runner."""
        with patch("a2a_server.RUNNER_PID_FILE") as mock_pid_file:
            mock_pid_file.exists.return_value = False
            with patch("a2a_server.subprocess.Popen") as mock_popen:
                mock_popen.return_value.pid = 12345
                with patch("builtins.open", mock_open()):
                    executor._ensure_runner_started()
                mock_popen.assert_called_once()

    def test_live_pid_skips_start(self, executor):
        """Existing PID file with a live process should skip starting."""
        with patch("a2a_server.RUNNER_PID_FILE") as mock_pid_file:
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "9999"
            with patch("a2a_server.os.kill") as mock_kill:
                mock_kill.return_value = None  # Process is alive
                with patch("a2a_server.subprocess.Popen") as mock_popen:
                    executor._ensure_runner_started()
                    mock_popen.assert_not_called()

    def test_stale_pid_starts_runner(self, executor):
        """Stale PID file (dead process) should start a new runner."""
        with patch("a2a_server.RUNNER_PID_FILE") as mock_pid_file:
            mock_pid_file.exists.return_value = True
            mock_pid_file.read_text.return_value = "9999"
            with patch("a2a_server.os.kill", side_effect=ProcessLookupError):
                with patch("a2a_server.subprocess.Popen") as mock_popen:
                    mock_popen.return_value.pid = 12345
                    with patch("builtins.open", mock_open()):
                        executor._ensure_runner_started()
                    mock_popen.assert_called_once()

    def test_start_failure_does_not_crash(self, executor):
        """Popen failure should log but not raise."""
        with patch("a2a_server.RUNNER_PID_FILE") as mock_pid_file:
            mock_pid_file.exists.return_value = False
            with patch("builtins.open", mock_open()):
                with patch("a2a_server.subprocess.Popen", side_effect=OSError("no such file")):
                    # Should not raise
                    executor._ensure_runner_started()


class TestCancel:
    @pytest.mark.asyncio
    async def test_cancel_emits_canceled(self, executor, mock_context, mock_event_queue):
        with patch("a2a_server.RUNNER_PID_FILE") as mock_pid:
            mock_pid.exists.return_value = False
            await executor.cancel(mock_context, mock_event_queue)

        assert mock_event_queue.enqueue_event.call_count == 1
        event = mock_event_queue.enqueue_event.call_args[0][0]
        assert event.status.state.value == "canceled"
