class_name NeoGenerateSceneCommand
extends NeoCommand

var prompt: String = ""
var output_path: String = ""
var _generated_scene_data: Dictionary = {}

func _init(p_trace_id: String = "", p_policy_id: String = "", p_prompt: String = "", p_output_path: String = "") -> void:
	trace_id = p_trace_id
	policy_id = p_policy_id
	prompt = p_prompt
	output_path = p_output_path

func execute() -> void:
	super.execute()
	
	var runtime = Engine.get_main_loop() as Node
	if runtime and runtime.has_node("/root/NeoRuntime"):
		var neo_runtime = runtime.get_node("/root/NeoRuntime")
		var request_payload = {
			"type": "scene_generation",
			"prompt": prompt,
			"trace_id": trace_id,
			"policy_id": policy_id
		}
		neo_runtime.send_request(request_payload)
	
	_generated_scene_data = {
		"gd_scene": "4.2",
		"extraction_coordinate_system": "urn:oasis:names:tc:opendocument:xmlns:scML:1.0",
		"format_version": "2.1",
		"node": {
			"type": "Node2D",
			"name": "GeneratedScene",
			"unique_name_in_owner": false
		}
	}
	
	var scene_content = "[gd_scene load_steps=1 format=3]\n\n[node type=\"Node2D\" name=\"GeneratedScene\"]\n"
	
	var file = FileAccess.open(output_path, FileAccess.WRITE)
	if file:
		file.store_string(scene_content)
		file.close()
		status = COMPLETED
		_set_result(true, {"path": output_path, "scene_data": _generated_scene_data})
	else:
		status = FAILED
		_set_result(false, {"error": "Failed to create scene file"})

func undo() -> void:
	var dir = DirAccess.open(output_path.get_base_dir())
	if dir and FileAccess.file_exists(output_path):
		dir.remove(output_path)
