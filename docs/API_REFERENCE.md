# Runtime Gateway API Reference

## Base Information

**API Base URL**: `http://localhost:8000/v1`

**Authentication**: Not required (local development)

## Common Response

All responses include `trace_id` for tracing.

---

## Endpoints

### Health Check

```http
GET /v1/health
```

#### Example Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### Text Generation

```http
POST /v1/generate
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `prompt` | string | Yes | User prompt |
| `model` | string | No | Model to use |
| `max_tokens` | int | No | Maximum tokens |
| `temperature` | float | No | Temperature, 0-1 |

#### Example Response

```json
{
  "content": "Generated content...",
  "trace_id": "abc-123",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200
  }
}
```

---

### Image Generation

```http
POST /v1/generate/image
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `prompt` | string | Yes | Image description |
| `size` | string | No | Image size |
| `quality` | string | No | Quality setting |

---

## WebSocket

### Connection

```
ws://localhost:8000/ws/stream
```

### Message Types

| Type | Description |
| --- | --- |
| `ping` | Heartbeat check |
| `pong` | Heartbeat response |
| `generate` | Generation request |
| `generation_complete` | Generation complete |
| `error` | Error message |

### Error Handling

All error responses follow the same format:

```json
{
  "error": "Description",
  "code": "ERROR_CODE",
  "trace_id": "trace-id"
}
```
