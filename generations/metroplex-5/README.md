# AI Agent Analytics Platform

Product analytics specifically designed for conversational AI and AI agents, showing where users struggle and drop off in AI interactions.

## Tech Stack
- **Frontend**: React 19 with Vite, Tailwind CSS, Shadcn/ui
- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite
- **Package Managers**: bun (frontend), uv (backend)

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- bun (frontend package manager)
- uv (Python package manager)

### Quick Start
```bash
chmod +x init.sh
./init.sh
```

Frontend runs on http://localhost:3000
Backend runs on http://localhost:8000

## Development

### Frontend
```bash
cd frontend
bun install
bun run dev
```

### Backend
```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## API Documentation
Once the backend is running, visit http://localhost:8000/docs for Swagger UI.
