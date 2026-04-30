# Core Architecture Rules

## Plugin-First Principle
- All AI-related UI and workflow should be implemented as EditorPlugins first
- Only move to modules/GDExtension when profiling proves plugins can't meet performance requirements
- Prefer `EditorPlugin`, `add_dock()`, `main_screen` over core engine modifications

## Asset Location Rules
- AI-generated assets must go to `res://ai_generated/` directory
- Subdirectories:
  - `ui/` - UI textures and sprites
  - `sfx/` - Sound effects
  - `scripts/` - Generated GDScript files
  - `scenes/` - Generated .tscn scenes
- All assets must go through Godot's native import pipeline

## Traceability Requirements
- Every AI action must have a trace_id
- All decisions must be logged with: policy_id, decision_reason, critic_scores
- Artifacts must be indexed with session_id and task_id

## Undo/Redo Compliance
- All modifications must use `EditorUndoRedoManager`
- Batch operations must be wrapped in a single change-set
- AI-generated changes must be undoable just like manual changes
