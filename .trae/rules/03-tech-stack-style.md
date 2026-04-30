# Tech Stack & Style Rules

## Coding Standards
- Use GDScript 4.x syntax
- Follow Godot's official style guide
- Use 4-space indentation
- File names: snake_case
- Class names: PascalCase
- Function names: snake_case

## UI Guidelines
- Follow Godot editor theme conventions
- Use built-in Control nodes where possible
- Prefer `add_dock()` for persistent panels
- Use `EditorInterface` for editor integration

## Python Backend Standards
- Use Python 3.11+
- Use FastAPI for REST endpoints
- Use Pydantic for data validation
- Use async/await for all I/O operations

## API Design Principles
- REST endpoints under `/v1/` prefix
- WebSocket for real-time events
- JSON Schema for request/response validation
- Error responses with `{"error": "...", "code": "..."}`

## Versioning
- API versioning via URL path
- Schema versioning in request/response
- Breaking changes require new version

## Security Practices
- Validate all inputs
- Use HTTPS in production
- Store secrets in environment variables
- Rate limiting on all endpoints
