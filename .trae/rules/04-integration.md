# Integration Rules

## Traceability Requirements
- All API calls must include `trace_id`
- All task executions must be traced
- Approval decisions must be recorded with timestamp

## Undo/Redo Requirements
- All modifications must be undoable
- Use `EditorUndoRedoManager` for Godot-side changes
- Gateway-side changes must have rollback capability

## Testing Requirements
- Unit tests for all core services
- Integration tests for API endpoints
- Golden tests for import pipeline
- Test fixtures in `tests/` directory

## CI/CD Requirements
- Run tests on every commit
- Build verification for Godot plugins
- Linting with clang-format
- Security scanning for dependencies

## Documentation Requirements
- API documentation with OpenAPI/Swagger
- Architecture documentation in `doc/`
- Code comments for complex logic
- Example projects for key workflows

## Logging Requirements
- Structured logging with JSON output
- Include trace_id in all logs
- Separate logs for different services
- Log rotation and retention policies
