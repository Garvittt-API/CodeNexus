# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for Redis, Ollama)
- Git

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/codenexus/codenexus.git
cd codenexus
```

### 2. Set up environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

### 5. Start services

**Option A: Docker Compose (recommended)**

```bash
docker-compose up -d redis ollama
```

**Option B: Manual Redis**

```bash
# Install and start Redis
redis-server
```

### 6. Start development servers

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Project Structure

```
codenexus/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, security, exceptions
│   │   ├── domain/       # Entities and value objects
│   │   ├── services/     # Business logic
│   │   ├── repositories/ # Data access
│   │   ├── infrastructure/ # External integrations
│   │   └── utils/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   ├── hooks/            # Custom hooks
│   ├── lib/              # Utilities and API client
│   ├── styles/           # CSS
│   ├── Dockerfile
│   └── package.json
├── docs/
├── docker-compose.yml
├── .github/workflows/
└── README.md
```

## Testing

### Run all tests

```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html
```

### Run unit tests only

```bash
cd backend
python -m pytest tests/ -v -m "not integration"
```

### Run integration tests

```bash
cd backend
python -m pytest tests/ -v -m integration
```

### Open coverage report

```bash
open htmlcov/index.html
```

## Linting & Formatting

```bash
cd backend
ruff check app/ tests/
ruff format app/ tests/
black app/ tests/
mypy app/ --ignore-missing-imports
```

## Docker

### Build images

```bash
docker-compose build
```

### Start all services

```bash
docker-compose up -d
```

### View logs

```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

### Stop all services

```bash
docker-compose down
```

## Git Hooks

Pre-commit hooks are configured via `.pre-commit-config.yaml`:

```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`:
- Trailing whitespace removal
- YAML/JSON validation
- Ruff linting & formatting
- Black formatting
- MyPy type checking

## IDE Setup

### VS Code

Install extensions:
- Python
- Pylance
- Tailwind CSS IntelliSense
- ESLint

Recommended settings in `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```
