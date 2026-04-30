# Phase 01: Baseline & Gateway Prototype

## Objective
Build a unified AI runtime gateway as the single entry point for both NeoGodot and Trae, with Qwen API as the primary model provider. Establish repository-level rules and create a minimal example project for validation.

## Duration
Estimated 2-3 weeks

## Key Deliverables
1. Neo Runtime Gateway with Qwen API integration
2. Trae rules and custom agents configuration
3. Example Godot project for testing
4. API documentation and test cases

---

## 1. Neo Runtime Gateway Implementation

### 1.1 Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Neo Runtime Gateway                      │
├─────────────────────────────────────────────────────────────┤
│  REST API Layer    │  WebSocket Layer  │  MCP Bridge       │
├─────────────────────────────────────────────────────────────┤
│              Provider Router (Model Routing)                │
├─────────────────────────────────────────────────────────────┤
│  Qwen API (Primary) │  Ollama Fallback  │  Future Providers │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Required API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/sessions` | Create new session with project context |
| POST | `/v1/plan` | Compile natural language goal to task DAG |
| POST | `/v1/tasks` | Submit task for execution |
| GET | `/v1/tasks/{id}` | Query task status |
| WS | `/v1/events` | Real-time event streaming |
| POST | `/v1/questions/{id}/answer` | Handle human-in-the-loop questions |
| POST | `/v1/import` | Import generated assets to Godot |

### 1.3 Qwen API Configuration

**Primary Model:** Qwen API (code generation + reasoning)
- Endpoint: `https://api.tongyi.aliyun.com`
- API Key: Stored in environment variable `QWEN_API_KEY`
- Context Window: 256K tokens (default)

**Fallback Model:** Ollama `qwen3-coder:30b`
- Local endpoint: `http://localhost:11434/api`
- Trigger: When cloud API unavailable or privacy required

### 1.4 Task Spec Schema

```json
{
  "task_id": "string",
  "session_id": "string",
  "kind": "enum: [asset.image, code.script, scene.generate, ...]",
  "priority": "enum: [P0, P1, P2]",
  "risk_level": "enum: [low, medium, high, critical]",
  "depends_on": ["task_id"],
  "budget": {
    "max_cost_usd": 1.5,
    "max_latency_ms": 60000
  },
  "output": {
    "path": "res://ai_generated/...",
    "format": "string"
  }
}
```

---

## 2. Trae Configuration

### 2.1 Repository Rules (`.trae/rules/`)

| Rule File | Purpose |
|-----------|---------|
| `01-core-architecture.md` | Plugin-first principle, asset location rules |
| `02-superviser-protocol.md` | Task DAG requirements, approval workflow |
| `03-tech-stack-style.md` | Coding standards, UI guidelines |
| `04-integration.md` | Traceability, undo/redo, testing requirements |

### 2.2 Custom Agents

| Agent | Role | Permissions |
|-------|------|-------------|
| `neo-architect` | Architecture planning, ADR generation | Read-only |
| `neo-editor` | Editor plugin UI/UX development | `editor/` only |
| `neo-runtime` | Gateway, scheduler, provider adapters | Backend only |
| `neo-importer` | Asset normalization & import pipeline | `res://ai_generated/` only |
| `neo-test-release` | Testing, packaging, audit | Tests & docs only |

### 2.3 Agent Policy Matrix

| Action | Requires Approval |
|--------|------------------|
| Read files | No |
| Generate new asset | No (auto-saved to staging) |
| Overwrite existing resource | Yes |
| Modify `.tscn` scene file | Yes |
| Run shell commands | Yes |
| High token consumption (>500K) | Yes |

---

## 3. Example Project Structure

```
example_project/
├── res://
│   ├── ai_generated/
│   │   ├── ui/          # UI textures
│   │   ├── sfx/         # Sound effects
│   │   ├── scripts/     # Generated GDScript
│   │   └── scenes/      # Generated .tscn
│   ├── addons/
│   │   └── neo_ai/      # Editor plugin
│   ├── scenes/          # User scenes
│   └── tests/           # Test fixtures
├── .godot/
└── project.godot
```

---

## 4. Security & Compliance

### 4.1 Trust Boundaries
- **System**: Highest trust level (internal policies)
- **Admin**: Configuration, policy management
- **User**: Normal development operations
- **Tool**: External tool outputs (default: untrusted)
- **Retrieved**: External data (default: untrusted)

### 4.2 Audit Requirements
- All API calls logged with `trace_id`
- Task execution trace stored for replay
- Approval decisions recorded with timestamp

---

## 5. Success Criteria

### Gateway
- [x] Qwen API integration working
- [x] All required endpoints implemented
- [x] Provider routing with fallback
- [x] WebSocket event streaming

### Trae Configuration
- [x] All 4 rule files created
- [x] 5 custom agents configured
- [x] Permission matrix defined

### Example Project
- [x] Directory structure created
- [x] Basic project.godot configured
- [x] Test fixtures prepared

---

## 6. Next Phase (MVP)
After completing Phase 01:
1. Implement Godot Editor Plugin (Dock + Main Screen)
2. Build Plan API integration
3. Implement basic import pipeline
4. Add manual approval workflow