# NeoGodot AI Integration Architecture Overview

## Executive Summary

NeoGodot is transforming from a standard Godot engine fork into an **AI-powered game development workbench** that is **plannable, executable, traceable, approvable, and rollbackable**. This document describes the architecture, implementation, and capabilities of the integrated AI system.

---

## 1. System Architecture

### 1.1 Core Principles

The architecture follows a **plugin-first, sidecar-runtime, core-last** approach:
- **Plugin-first**: AI capabilities are implemented as EditorPlugins whenever possible
- **Sidecar-runtime**: Model inference and Agent execution happen outside the Godot process
- **Core-last**: Only move critical hot-path logic to modules/GDExtension when proven necessary

### 1.2 Reference Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NeoGodot Editor                             │
│  ┌─────────────────┐  ┌─────────────────────────────────────────┐ │
│  │   AI Dock Panel │  │            Main Screen                   │ │
│  │  - Status Bar   │  │  ┌─────────┐  ┌─────────────────────┐   │ │
│  │  - Budget Bar   │  │  │ Plan    │  │ Task Details        │   │ │
│  │  - Decisions    │  │  │ Tree    │  │ - Success Criteria │   │ │
│  │  - Questions    │  │  │ - DAG   │  │ - Risk Level       │   │ │
│  │  - Artifacts    │  │  │ - State │  │ - Execution Logs   │   │ │
│  └────────┬────────┘  └─────┬───────┴───────────┬─────────────┘   │ │
│           │                 │                   │                 │ │
└───────────┼─────────────────┼───────────────────┼─────────────────┘ │
            │                 │                   │                   │
            ▼                 ▼                   ▼                   │
┌─────────────────────────────────────────────────────────────────────┐
│                    Neo Runtime Gateway                              │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────────────┐   │
│  │ REST API    │  │ WebSocket   │  │         MCP Bridge        │   │
│  │ Layer       │  │ Event Stream│  │ (Tool Authorization)     │   │
│  └─────┬───────┘  └─────┬───────┘  └───────────┬───────────────┘   │
│        │                │                      │                   │
│        ▼                ▼                      ▼                   │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  Provider Router                             │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                   │
│        ┌───────────────────────┼───────────────────────┐           │
│        ▼                       ▼                       ▼           │
│  ┌───────────┐         ┌─────────────┐         ┌─────────────┐     │
│  │ Qwen API  │         │ Ollama      │         │ Future      │     │
│  │ (Primary) │         │ Fallback    │         │ Providers   │     │
│  └───────────┘         └─────────────┘         └─────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **Neo AI Dock** | Persistent status, budget, questions, recent artifacts | EditorPlugin + Dock |
| **Neo AI Main Screen** | Full-screen task orchestration, plan tree visualization | Main Screen Plugin |
| **Supervisor** | Decision controller - when to ask, continue, or approve | Gateway Service |
| **Plan Compiler** | Compiles natural language goals into executable DAGs | Gateway Service |
| **Agent Scheduler** | Task queuing, parallel control, retry policies | Gateway Service |
| **Provider Router** | Model routing, fallback, caching, quota management | Gateway Service |
| **Asset Importer** | Normalization, metadata, reimport triggering | Godot Plugin |
| **Task State Store** | Task status, user answers, audit trail | Shared State |

---

## 2. Neo Runtime Gateway

### 2.1 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/sessions` | Create new session with project context |
| GET | `/v1/sessions` | List all sessions |
| POST | `/v1/plan` | Compile natural language goal to task DAG |
| GET | `/v1/plan/{id}` | Retrieve plan details |
| POST | `/v1/tasks` | Submit task for execution |
| GET | `/v1/tasks/{id}` | Query task status |
| POST | `/v1/tasks/{id}/execute` | Execute task |
| WS | `/v1/events/ws/{session_id}` | Real-time event streaming |
| POST | `/v1/questions/{id}/answer` | Handle human-in-the-loop questions |
| POST | `/v1/import` | Import generated assets to Godot |

### 2.2 Task Specification Schema

```json
{
  "task_id": "string",
  "session_id": "string",
  "kind": "enum: [plan.compile, retrieve.search, tool.call, code.edit, ...]",
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

### 2.3 Event Types

- `task.started` - Task execution began
- `task.completed` - Task finished successfully
- `task.failed` - Task failed
- `question.raised` - Supervisor needs input
- `artifact.ready` - Asset ready for import
- `budget.warning` - Approaching budget limit

---

## 3. Editor Plugin Architecture

### 3.1 Plugin Structure

```
addons/neo_ai/
├── plugin.cfg                    # Plugin configuration
├── neo_ai_plugin.gd              # Main EditorPlugin entry
├── ui/
│   ├── neo_ai_dock.tscn          # Dock panel scene
│   ├── neo_ai_dock.gd            # Dock logic
│   ├── neo_ai_main.tscn          # Main Screen scene
│   └── neo_ai_main.gd            # Main Screen logic
├── network/
│   └── gateway_client.gd         # Gateway API client (HTTP + WebSocket)
├── import/
│   └── neo_importer.gd           # Asset importer
└── state/
    └── task_state.gd             # Task state management
```

### 3.2 Dock Panel Features

**Status Bar Section:**
- Current goal display
- Supervisor mode indicator (Shadow/Guardian/Collaborative)
- Budget bar ($ spent / $ limit)
- Phase progress (Plan → Code → Assets → Import)

**Decisions Section:**
- Primary model selection
- Code subtask model selection
- Vision analysis model (optional)

**Questions Section:**
- Pending questions list
- Multiple choice answers
- Default action indication
- Impact summary

**Artifacts Section:**
- Recently generated assets
- Quick actions: Locate, Instantiate, Rollback

### 3.3 Main Screen Features

**Plan Tree (Left Panel):**
- Visual task DAG display
- Dependency visualization
- Task status indicators (Pending/Approval/Running/Succeeded/Failed)
- Priority badges (P0/P1/P2)

**Task Details (Right Panel):**
- Selected task information
- Success criteria
- Risk level
- Estimated cost
- Execution logs

**Toolbar:**
- Regenerate plan
- Run selected tasks
- Pause/resume
- Export plan as JSON

---

## 4. Supervisor Workflow

### 4.1 Approval Triggers

| Trigger Type | Condition | Default Action |
|--------------|-----------|----------------|
| **Information Gap** | Missing style/format/naming rules | Use defaults, ask later |
| **Architecture Fork** | Multiple implementation paths | Show comparison, require selection |
| **Destructive Change** | Overwrite existing resource | **Require approval** |
| **Cost Jump** | Exceeds budget threshold | Offer downgrade options |
| **Validation Failed** | Import/test failed | Request clarification or rollback |

### 4.2 Supervisor Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Shadow** | Suggest only, no auto-execution | New users, high-risk projects |
| **Guardian** | Low-risk auto, high-risk approve | Standard team workflow |
| **Collaborative** | Confirm at phase boundaries | Architecture design |

### 4.3 Approval Dialog Content

- Action description
- Risk level indicator
- Affected files/resources
- Cost estimate
- Available options
- Default action if no response

---

## 5. Asset Import Pipeline

### 5.1 Supported Asset Types

| Type | Format | Import Handler |
|------|--------|----------------|
| 2D Image | PNG, JPG, WebP | Native texture import |
| Audio | WAV, OGG | Native audio import |
| 3D Model | GLB, GLTF | GLTFDocumentExtension |
| Script | GDScript (.gd) | Direct file write |
| Scene | TSCN | Scene import |
| Configuration | TRES | Direct file write |

### 5.2 Import Workflow

```
Generated Asset → Staging → Normalization → Write → Reimport → Verify
```

**Normalization Steps:**
1. Validate file format
2. Apply naming convention (`{asset_type}_{name}_{hash}.ext`)
3. Add metadata manifest (`.neoasset.json`)
4. Generate fingerprint hash

### 5.3 Manifest Format

```json
{
  "artifact_id": "art_xxx",
  "task_id": "task_xxx",
  "session_id": "sess_xxx",
  "generated_at": "ISO8601",
  "original_prompt": "...",
  "metadata": {
    "purpose": "primary_button",
    "style_ref": "neo_style_v2"
  },
  "fingerprint": "sha256_hash"
}
```

---

## 6. State Management & Undo/Redo

### 6.1 Task State Fields

- `task_id`, `session_id`, `status`
- `created_at`, `started_at`, `completed_at`
- `output_artifacts` array
- `error_message` (if failed)
- `user_answers` dictionary

### 6.2 Change-Set Pattern

Godot's `EditorUndoRedoManager` is used for all modifications:

```gdscript
func apply_change_set(change: Dictionary) -> void:
    var undo_redo = get_editor_interface().get_undo_redo()
    undo_redo.create_action(change.name)
    undo_redo.add_do_method(target, method, args)
    undo_redo.add_undo_method(target, method, revert_args)
    undo_redo.commit_action()
```

### 6.3 Rollback Capability

- **Single artifact rollback** - Undo specific changes
- **Batch rollback** - Last N changes
- **Full session rollback** - Restore to session start

---

## 7. Security & Compliance

### 7.1 Trust Boundaries

| Level | Description | Trust Level |
|-------|-------------|-------------|
| **System** | Internal policies | Highest |
| **Admin** | Configuration, policy management | High |
| **User** | Normal development operations | Medium |
| **Tool** | External tool outputs | Low (default: untrusted) |
| **Retrieved** | External data | Low (default: untrusted) |

### 7.2 Audit Requirements

- All API calls logged with `trace_id`
- Task execution trace stored for replay
- Approval decisions recorded with timestamp
- Artifact generation tracked

### 7.3 Input Validation

- Sanitize all user inputs
- Validate task specifications against schema
- Rate limiting per session

---

## 8. Trae Integration

### 8.1 Custom Agents

| Agent | Role | Permissions |
|-------|------|-------------|
| `neo-architect` | Architecture planning, ADR generation | Read-only |
| `neo-editor` | Editor plugin UI/UX development | `editor/` only |
| `neo-runtime` | Gateway, scheduler, provider adapters | Backend only |
| `neo-importer` | Asset normalization & import pipeline | `res://ai_generated/` only |
| `neo-test-release` | Testing, packaging, audit | Tests & docs only |

### 8.2 Permission Matrix

| Action | Requires Approval |
|--------|------------------|
| Read files | No |
| Generate new asset | No (auto-saved to staging) |
| Overwrite existing resource | Yes |
| Modify `.tscn` scene file | Yes |
| Run shell commands | Yes |
| High token consumption (>500K) | Yes |

---

## 9. Deployment & Operations

### 9.1 Quick Start

```bash
# Start the Gateway
cd runtime/neo_runtime_gateway
poetry install
cp .env.example .env
# Configure Qwen API Key in .env
poetry run python main.py
```

### 9.2 Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `QWEN_API_KEY` | Qwen API key | Required |
| `QWEN_API_BASE_URL` | Qwen API endpoint | `https://api.tongyi.aliyun.com` |
| `OLLAMA_ENABLED` | Enable Ollama fallback | `true` |
| `OLLAMA_BASE_URL` | Ollama endpoint | `http://localhost:11434/api` |
| `SERVER_HOST` | Gateway host | `0.0.0.0` |
| `SERVER_PORT` | Gateway port | `7777` |

### 9.3 Godot Plugin Installation

1. Copy `addons/neo_ai/` to your project's `res://addons/`
2. Enable the plugin in `Project > Project Settings > Plugins`
3. Open the dock via `View > Neo AI`

---

## 10. Future Roadmap

### Phase 03: Beta
- Parallel Agent scheduling
- Advanced asset normalization
- Artifact Registry
- Automated testing and failure recovery

### Phase 04: Hardening
- Trae shared backend
- Budget auditing
- Performance optimization
- Module/GDExtension sinking where needed

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **DAG** | Directed Acyclic Graph - task dependency structure |
| **MCP** | Model Context Protocol - tool authorization standard |
| **Artifact** | Generated asset (image, script, scene, etc.) |
| **Supervisor** | Dialogue-based orchestrator for multi-agent control |
| **Guardian Mode** | Low-risk automatic execution, high-risk approval required |
| **Shadow Mode** | Suggestions only, no automatic execution |
| **Plan Compiler** | Converts natural language goals to executable task DAGs |

---

**Document Version:** 1.0  
**Last Updated:** May 2026  
**Authors:** NeoGodot Team