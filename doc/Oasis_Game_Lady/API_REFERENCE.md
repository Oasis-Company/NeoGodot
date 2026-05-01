# Neo Runtime Gateway API Reference

## Overview

The Neo Runtime Gateway provides a unified API for AI-powered game development workflows. This document describes all available endpoints and their usage.

---

## Base URL

All endpoints are prefixed with `/v1/`:
```
http://localhost:7777/v1/
```

---

## 1. Sessions

### 1.1 Create Session

**POST** `/sessions`

Creates a new session with project context.

**Request Body:**
```json
{
  "project_path": "res://my_project/",
  "mode": "default",
  "budget_usd": 10.0,
  "selected_models": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_path` | string | Yes | Godot project path |
| `mode` | string | No | Session mode (default: "default") |
| `budget_usd` | float | No | Maximum budget in USD (default: 10.0) |
| `selected_models` | array | No | List of selected model names |

**Response:**
```json
{
  "session_id": "uuid-string",
  "project_path": "res://my_project/",
  "mode": "default",
  "budget_usd": 10.0,
  "remaining_budget_usd": 10.0,
  "selected_models": [],
  "status": "active",
  "created_at": "2026-05-01T12:00:00Z",
  "updated_at": "2026-05-01T12:00:00Z"
}
```

### 1.2 Get Session

**GET** `/sessions/{session_id}`

Retrieves session details.

**Response:** Same as create session response.

### 1.3 List Sessions

**GET** `/sessions`

Lists all active sessions.

**Response:**
```json
[
  { /* Session object */ }
]
```

### 1.4 Update Session

**PUT** `/sessions/{session_id}`

Updates session configuration.

**Request Body:** Same as create session.

### 1.5 Delete Session

**DELETE** `/sessions/{session_id}`

Deletes a session.

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

---

## 2. Plan

### 2.1 Create Plan

**POST** `/plan`

Compiles natural language goal to task DAG.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "goal": "Create a 2D platformer level",
  "context": "Game development with Godot",
  "constraints": {},
  "existing_artifacts": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session ID |
| `goal` | string | Yes | Natural language goal |
| `context` | string | No | Additional context |
| `constraints` | object | No | Constraints dictionary |
| `existing_artifacts` | array | No | List of existing artifact paths |

**Response:**
```json
{
  "plan_id": "uuid-string",
  "session_id": "uuid-string",
  "goal": "Create a 2D platformer level",
  "context": "Game development with Godot",
  "tasks": [
    {
      "task_id": "uuid-string",
      "kind": "retrieve.search",
      "description": "Search relevant documentation",
      "dependencies": [],
      "risk_level": "low",
      "estimated_cost_usd": 0.05
    }
  ],
  "risk_points": ["Need user confirmation"],
  "questions": ["Any specific style requirements?"],
  "created_at": "2026-05-01T12:00:00Z",
  "updated_at": "2026-05-01T12:00:00Z"
}
```

### 2.2 Get Plan

**GET** `/plan/{plan_id}`

Retrieves plan details.

### 2.3 Update Plan

**PUT** `/plan/{plan_id}`

Updates plan goal.

**Request Body:**
```json
{
  "goal": "Updated goal"
}
```

### 2.4 Delete Plan

**DELETE** `/plan/{plan_id}`

Deletes a plan.

---

## 3. Tasks

### 3.1 Create Task

**POST** `/tasks`

Submits a task for execution.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "kind": "script.generate",
  "priority": "P1",
  "risk_level": "medium",
  "depends_on": ["task-id-1"],
  "timeout_ms": 60000,
  "retry_policy": {
    "max_attempts": 3,
    "backoff": "exponential",
    "idempotent": true
  },
  "tool_scope": [],
  "budget": {
    "max_cost_usd": 1.0
  },
  "success_criteria": ["Script compiles without errors"],
  "evidence_refs": [],
  "metadata": {
    "purpose": "player movement"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Session ID |
| `kind` | string | Yes | Task type (see Task Kinds) |
| `priority` | string | No | P0/P1/P2 (default: P1) |
| `risk_level` | string | No | low/medium/high/critical (default: medium) |
| `depends_on` | array | No | List of dependent task IDs |
| `timeout_ms` | int | No | Timeout in milliseconds (default: 60000) |
| `retry_policy` | object | No | Retry configuration |

**Response:**
```json
{
  "task_id": "uuid-string",
  "session_id": "uuid-string",
  "kind": "script.generate",
  "status": "draft",
  ...
}
```

### 3.2 Execute Task

**POST** `/tasks/{task_id}/execute`

Executes a task.

**Response:** Same as get task response.

### 3.3 Get Task

**GET** `/tasks/{task_id}`

Retrieves task status.

**Response:**
```json
{
  "task_id": "uuid-string",
  "session_id": "uuid-string",
  "kind": "script.generate",
  "status": "running",
  "priority": "P1",
  "risk_level": "medium",
  "depends_on": [],
  "output_artifacts": [],
  "cost_usd": 0.0,
  "error_message": null,
  "logs": ["Task started"],
  "created_at": "2026-05-01T12:00:00Z",
  "updated_at": "2026-05-01T12:00:00Z"
}
```

### 3.4 List Tasks

**GET** `/tasks?session_id={session_id}`

Lists tasks for a session.

---

## 4. Events

### 4.1 WebSocket Event Stream

**WebSocket** `/events/ws/{session_id}`

Connects to real-time event stream.

**Events received:**
```json
{
  "event_id": "event-uuid",
  "session_id": "session-uuid",
  "task_id": "task-uuid",
  "event_type": "task.completed",
  "payload": {
    "task_id": "task-uuid",
    "artifacts": ["res://ai_generated/script.gd"]
  },
  "timestamp": "2026-05-01T12:00:00Z"
}
```

### 4.2 Event History

**GET** `/events/history/{session_id}?limit=100`

Retrieves event history.

---

## 5. Questions

### 5.1 Create Question

**POST** `/questions`

Creates a question requiring human input.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "task_id": "uuid-string",
  "type": "information_gap",
  "title": "Missing style reference",
  "description": "No UI style specified",
  "default_action": "use_default",
  "choices": ["Use default", "Upload reference", "Skip"],
  "affected_resources": ["button.png", "panel.png"],
  "estimated_cost_impact": 0.5
}
```

### 5.2 Answer Question

**POST** `/questions/{question_id}/answer`

Answers a question.

**Request Body:**
```json
{
  "answer": "Use default",
  "user_comment": "Proceed with default style"
}
```

### 5.3 List Questions

**GET** `/questions?session_id={session_id}&answered=false`

Lists pending questions.

---

## 6. Import

### 6.1 Import Assets

**POST** `/import`

Imports generated assets to Godot project.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "files": ["/tmp/generated/button.png"],
  "resource_type": "image",
  "target_directory": "res://ai_generated/",
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "imported_paths": ["res://ai_generated/button_abc123.png"],
  "failed_paths": [],
  "errors": [],
  "message": "Imported 1 file(s)"
}
```

---

## Task Kinds

| Kind | Description | Risk Level |
|------|-------------|------------|
| `plan.compile` | Compile plan from goal | Low |
| `retrieve.search` | Search documentation | Low |
| `tool.call` | Call external tool | Medium |
| `code.edit` | Edit code file | High |
| `code.test` | Run tests | Medium |
| `answer.compose` | Compose answer | Low |
| `approval.request` | Request approval | Low |
| `critic.safety` | Safety review | Low |
| `critic.grounding` | Grounding review | Low |
| `asset.image` | Generate image | Medium |
| `asset.audio` | Generate audio | Medium |
| `asset.3d` | Generate 3D model | Medium |
| `scene.generate` | Generate scene | High |
| `script.generate` | Generate script | Medium |

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "trace_id": "trace-uuid"
}
```

**Common Error Codes:**
- `SESSION_NOT_FOUND` - Session does not exist
- `TASK_NOT_FOUND` - Task does not exist
- `PLAN_NOT_FOUND` - Plan does not exist
- `INVALID_INPUT` - Invalid request body
- `BUDGET_EXCEEDED` - Budget limit exceeded
- `INTERNAL_ERROR` - Server error

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |