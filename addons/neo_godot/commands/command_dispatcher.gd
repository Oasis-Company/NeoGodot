extends Node
class_name NeoCommandDispatcher

signal command_started(command: NeoCommand)
signal command_completed(command: NeoCommand, result: Dictionary)
signal command_failed(command: NeoCommand, error: String)
signal queue_empty

var undo_manager: NeoUndoManager
var _pending_commands: Array[NeoCommand] = []
var _is_processing: bool = false

func enqueue_command(command: NeoCommand) -> void:
	_pending_commands.append(command)
	if not _is_processing:
		_process_queue()

func _process_queue() -> void:
	if _pending_commands.is_empty():
		_is_processing = false
		queue_empty.emit()
		return
	
	_is_processing = true
	var command: NeoCommand = _pending_commands.pop_front()
	command_started.emit(command)
	
	command.execute()
	
	if command.status == NeoCommand.COMPLETED:
		command_completed.emit(command, command.get_result())
	elif command.status == NeoCommand.FAILED:
		command_failed.emit(command, "Command execution failed")
	
	call_deferred("_process_queue")

func cancel_command(trace_id: String) -> bool:
	for i in range(_pending_commands.size()):
		if _pending_commands[i].trace_id == trace_id:
			_pending_commands.remove_at(i)
			return true
	return false

func get_command_status(trace_id: String) -> int:
	for command in _pending_commands:
		if command.trace_id == trace_id:
			return command.status
	return NeoCommand.PENDING

func clear_queue() -> void:
	_pending_commands.clear()
	_is_processing = false
