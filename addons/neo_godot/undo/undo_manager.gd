extends Node
class_name NeoUndoManager

signal action_committed
signal action_rolled_back

var _undo_redo: EditorUndoRedoManager
var _plugin: EditorPlugin
var _action_name: String = ""
var _is_batching: bool = false

func _init() -> void:
	_plugin = EditorPlugin.new()
	_undo_redo = _plugin.get_undo_redo()

func begin_action(name: String) -> void:
	if _is_batching:
		return
	_action_name = name
	_is_batching = true
	_undo_redo.create_action(name)

func add_do_method(object: Object, method: String, args: Array = []) -> void:
	if not _is_batching:
		return
	_undo_redo.add_do_method(object, method)
	for arg in args:
		_undo_redo.add_do_reference(object)

func add_undo_method(object: Object, method: String, args: Array = []) -> void:
	if not _is_batching:
		return
	_undo_redo.add_undo_method(object, method)
	for arg in args:
		_undo_redo.add_undo_reference(object)

func commit_action() -> void:
	if not _is_batching:
		return
	_undo_redo.commit_action()
	_is_batching = false
	action_committed.emit()

func rollback() -> void:
	if not _is_batching:
		return
	_undo_redo.rollback()
	_is_batching = false
	action_rolled_back.emit()

func get_action_count() -> int:
	return _undo_redo.get_history_count()

func clear_history() -> void:
	_undo_redo.clear_history()
