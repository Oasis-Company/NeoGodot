class_name NeoGenerateTextureCommand
extends NeoCommand

var prompt: String = ""
var output_path: String = ""
var _generated_texture: ImageTexture

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
			"type": "texture_generation",
			"prompt": prompt,
			"trace_id": trace_id,
			"policy_id": policy_id
		}
		neo_runtime.send_request(request_payload)
	
	if not output_path.begins_with("res://ai_generated/ui/"):
		output_path = "res://ai_generated/ui/" + output_path.get_file()
	
	var dir = DirAccess.open("res://ai_generated/ui/")
	if not dir:
		DirAccess.make_dir_recursive_absolute("res://ai_generated/ui/")
	
	var image = Image.create(256, 256, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.5, 0.5, 0.5, 1.0))
	
	_generated_texture = ImageTexture.create_from_image(image)
	
	if _generated_texture:
		status = COMPLETED
		_set_result(true, {"path": output_path, "texture": _generated_texture})
	else:
		status = FAILED
		_set_result(false, {"error": "Failed to create texture"})

func undo() -> void:
	if FileAccess.file_exists(output_path):
		var dir = DirAccess.open(output_path.get_base_dir())
		if dir:
			dir.remove(output_path)
