# AI Agent Analytics Platform

Product analytics specifically designed for conversational AI and AI agents, showing where users struggle and drop off in AI interactions.

## Tech Stack
- **Frontend**: React 19 with Vite, Tailwind CSS, Shadcn/ui
- **Backend**: FastAPI (Python 3.12+)
- **Database**: SQLite
- **Package Managers**: npm (frontend), pip (backend)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.12+

### Quick Start
The `init.sh` script will set up and start both servers:
```bash
chmod +x init.sh
./init.sh
```

- Frontend runs on http://localhost:3000
- Backend runs on http://localhost:8000
- API Docs at http://localhost:8000/docs

**Note**: Ensure ports 3000 and 8000 are available before running init.sh

## Development

### Frontend
```bash
cd frontend
npm install --include=dev
npm run dev
```

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

## API Documentation
Once the backend is running, visit http://localhost:8000/docs for Swagger UI.
