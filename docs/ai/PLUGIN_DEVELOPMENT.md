# Plugin Development Guide

## Getting Started

### Creating a New Command

1. Create new file in `addons/neo_godot/commands/`
2. Extend `NeoGodotCommand` base class
3. Implement required methods

```gdscript
# addons/neo_godot/commands/my_command.gd
class_name NeoGodotMyCommand
extends NeoGodotCommand

func _init():
    command_name = "my_command"
    command_description = "Description of what this does"

func execute(arguments: Dictionary) -> CommandResult:
    var result = CommandResult.new()
    result.success = true
    result.message = "Command executed successfully"
    return result
```

### Registering the Command

Add to `plugin.gd` or command registry:

```gdscript
var my_command = NeoGodotMyCommand.new()
command_registry.register_command(my_command)
```

## UI Components

### Adding a Dock Panel

```gdscript
# In plugin.gd
func _enter_tree():
    var panel = preload("ui/my_panel.tscn").instantiate()
    add_control_to_dock(DOCK_SLOT_LEFT_UL, panel)
```

### Using EditorInterface

```gdscript
var editor_interface = EditorInterface.get_singleton()
var edited_scene = editor_interface.get_edited_scene_root()
```

## Undo/Redo Integration

```gdscript
var undo_redo = EditorUndoRedoManager.get_singleton()
undo_redo.create_action("My Action")
undo_redo.add_do_method(self, "my_method")
undo_redo.add_undo_method(self, "my_undo_method")
undo_redo.commit_action()
```

## Best Practices

1. **Always use UndoRedo** for any modifications
2. **Provide traceability** with trace_id in logs
3. **Use staging directory** for AI-generated assets: `res://ai_generated/`
4. **Follow GDScript style guide** - 4-space indentation, snake_case
5. **Keep plugins modular** - separate concerns
6. **Document all commands** with clear descriptions
