# VoiceNotify MCP Plugin

A plug-in for the Model Context Protocol (MCP) server that monitors the lifecycle of an AI coding agent. When the agent signals completion, stalls, or needs a decision, the plug-in automatically notifies the developer by either placing a local phone call or delivering a Telegram-style voice note saved to a local directory.

## Features

- **Agent Lifecycle Monitoring**: Listens for agent state changes (completion, stall, decision required)
- **Voice Notifications**: Generates voice notes using text-to-speech
- **Multi-Channel Delivery**: Support for local phone calls and voice note files
- **Configurable**: Customizable language, voice, and playback settings
- **Standard Library Only**: No external dependencies required (stdlib only)
- **MCP Integration**: Built as an MCP server plugin for seamless integration

## Tech Stack

- **Language**: Python 3.11+
- **Dependencies**: Standard library only (no third-party packages)
- **Testing**: pytest
- **Platform**: Linux, macOS, Windows

## Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VOICENOTIFY_MODE` | string | `file` | Notification delivery mode: `call` (phone), `file` (voice note), or `both` |
| `VOICENOTIFY_TARGET` | string | `./notifications` | Target for file mode: phone number for call mode, directory path for file mode |
| `VOICENOTIFY_LANG` | string | `en` | Language code for text-to-speech (e.g., `en`, `es`, `fr`) |
| `VOICENOTIFY_VOICE` | string | `default` | Voice type for TTS (e.g., `default`, `alto`, `bass`) |
| `VOICENOTIFY_PLAYBACK` | bool | `true` | Whether to automatically play generated voice notes |

## Quick Start

### Setup

1. Clone the repository and navigate to the project directory
2. Run the initialization script:
   ```bash
   chmod +x init.sh
   ./init.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Set environment variables (optional):
   ```bash
   export VOICENOTIFY_MODE=file
   export VOICENOTIFY_TARGET=./voice_notifications
   export VOICENOTIFY_LANG=en
   ```

### Running the Plugin

```bash
# Start the MCP server with the plugin
python -m voicenotify.main

# Run tests
pytest tests/
```

### Usage Example

The plugin listens for agent events via MCP RPC and automatically sends notifications:

```python
from voicenotify.models import AgentEvent, NotificationConfig

# Agent completion triggers voice notification
event = AgentEvent(
    agent_id="agent-001",
    status="completed",
    message="Task completed successfully"
)

# Plugin automatically generates and sends notification
# based on VOICENOTIFY_* environment variables
```

## Project Structure

```
voicenotify/
├── __init__.py              # Package initialization
├── main.py                  # MCP RPC listener & event routing
├── event_hook.py            # AgentEvent parsing and validation
├── notifier.py              # Call logic & TTS voice-note generation
├── config.py                # Environment variable loading
├── models.py                # Data models (AgentEvent, NotificationConfig)
└── utils.py                 # Helper utilities (subprocess, audio encoding)

tests/
├── __init__.py
├── test_main.py
├── test_event_hook.py
└── test_notifier.py

requirements.txt             # Empty (stdlib only)
README.md                    # This file
init.sh                      # Setup script
.gitignore                   # Git ignore patterns
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

The project follows PEP 8 guidelines and uses only the Python standard library.

## License

MIT
