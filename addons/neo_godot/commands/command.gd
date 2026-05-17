class_name NeoCommand
extends RefCounted

const PENDING: int = 0
const RUNNING: int = 1
const COMPLETED: int = 2
const FAILED: int = 3

var trace_id: String = ""
var policy_id: String = ""
var status: int = PENDING
var _result: Dictionary = {}

func execute() -> void:
	status = RUNNING

func undo() -> void:
	pass

func get_result() -> Dictionary:
	return _result

func _set_result(success: bool, data: Dictionary = {}) -> void:
	_result = {
		"success": success,
		"trace_id": trace_id,
		"policy_id": policy_id,
		"status": status
	}
	for key in data:
		_result[key] = data[key]
