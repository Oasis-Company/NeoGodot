# Neo Runtime Gateway

Unified AI runtime gateway for NeoGodot and Trae.

## Features

- REST API endpoints for session management, planning, task execution
- WebSocket event streaming for real-time updates
- Qwen API integration with Ollama fallback
- Provider routing with automatic failover
- Task DAG compilation and execution
- Human-in-the-loop question handling
- Asset import pipeline integration

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry

### Installation

```bash
cd runtime/neo_runtime_gateway
poetry install
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```env
QWEN_API_KEY=your_api_key
QWEN_API_BASE_URL=https://api.tongyi.aliyun.com
OLLAMA_ENABLED=true
SERVER_PORT=7777
```

### Running

```bash
poetry run python main.py
```

The gateway will be available at `http://localhost:7777`

## API Endpoints

### Sessions

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/sessions` | Create new session |
| GET | `/v1/sessions` | List all sessions |
| GET | `/v1/sessions/{id}` | Get session by ID |
| PUT | `/v1/sessions/{id}` | Update session |
| DELETE | `/v1/sessions/{id}` | Delete session |

### Plan

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/plan` | Create plan from goal |
| GET | `/v1/plan/{id}` | Get plan by ID |
| PUT | `/v1/plan/{id}` | Update plan |
| DELETE | `/v1/plan/{id}` | Delete plan |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/tasks` | Create task |
| GET | `/v1/tasks` | List tasks |
| GET | `/v1/tasks/{id}` | Get task by ID |
| POST | `/v1/tasks/{id}/execute` | Execute task |

### Events

| Method | Path | Description |
|--------|------|-------------|
| WS | `/v1/events/ws/{session_id}` | WebSocket event stream |
| GET | `/v1/events/history/{session_id}` | Get event history |

### Import

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/import` | Import assets to Godot |

### Questions

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/questions` | Create question |
| GET | `/v1/questions` | List questions |
| POST | `/v1/questions/{id}/answer` | Answer question |

## API Usage Examples

### Create Session

```bash
curl -X POST http://localhost:7777/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "res://my_project/",
    "mode": "default",
    "budget_usd": 10.0,
    "selected_models": []
  }'
```

### Create Plan

```bash
curl -X POST http://localhost:7777/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "goal": "Create a 2D platformer game",
    "context": "Game development with Godot",
    "constraints": {},
    "existing_artifacts": []
  }'
```

### Create Task

```bash
curl -X POST http://localhost:7777/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "kind": "script.generate",
    "priority": "P1",
    "risk_level": "medium",
    "depends_on": [],
    "metadata": {"purpose": "player movement"}
  }'
```

## Testing

```bash
cd runtime/neo_runtime_gateway
poetry run pytest tests/ -v
```

## Project Structure

```
neo_runtime_gateway/
├── main.py              # FastAPI application entry
├── pyproject.toml       # Dependencies and configuration
├── .env.example         # Environment variables template
├── schemas/             # Pydantic models
│   ├── __init__.py
│   ├── session.py
│   ├── task.py
│   ├── plan.py
│   ├── question.py
│   ├── event.py
│   └── import_request.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── session_service.py
│   ├── task_service.py
│   ├── plan_service.py
│   ├── question_service.py
│   ├── event_service.py
│   ├── import_service.py
│   └── provider_service.py
├── routes/              # API routes
│   ├── __init__.py
│   ├── dependencies.py
│   ├── sessions.py
│   ├── plan.py
│   ├── tasks.py
│   ├── events.py
│   ├── imports.py
│   └── questions.py
├── utils/               # Utility functions
│   └── logger.py
└── tests/               # Test suite
    └── test_gateway.py
```

## License

MIT