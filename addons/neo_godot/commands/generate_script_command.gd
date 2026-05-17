class_name NeoGenerateScriptCommand
extends NeoCommand

var prompt: String = ""
var template_type: String = ""
var output_path: String = ""
var _generated_code: String = ""

func _init(p_trace_id: String = "", p_policy_id: String = "", p_prompt: String = "", p_template_type: String = "", p_output_path: String = "") -> void:
	trace_id = p_trace_id
	policy_id = p_policy_id
	prompt = p_prompt
	template_type = p_template_type
	output_path = p_output_path

func execute() -> void:
	super.execute()
	
	var runtime = Engine.get_main_loop() as Node
	if runtime and runtime.has_node("/root/NeoRuntime"):
		var neo_runtime = runtime.get_node("/root/NeoRuntime")
		var request_payload = {
			"type": "script_generation",
			"prompt": prompt,
			"template_type": template_type,
			"trace_id": trace_id,
			"policy_id": policy_id
		}
		neo_runtime.send_request(request_payload)
	
	_generated_code = "[extends Node]\n[class_name GeneratedScript]\n\nfunc _init() -> void:\n	pass\n"
	
	var file = FileAccess.open(output_path, FileAccess.WRITE)
	if file:
		file.store_string(_generated_code)
		file.close()
		status = COMPLETED
		_set_result(true, {"path": output_path, "code": _generated_code})
	else:
		status = FAILED
		_set_result(false, {"error": "Failed to create script file"})

func undo() -> void:
	var dir = DirAccess.open(output_path.get_base_dir())
	if dir and FileAccess.file_exists(output_path):
		dir.remove(output_path)
