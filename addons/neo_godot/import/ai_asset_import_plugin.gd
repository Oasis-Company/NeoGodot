extends EditorImportPlugin

class_name AIAssetImportPlugin

const IMPORT_UTILS_PATH = "res://addons/neo_godot/import/import_utils.gd"

var _import_utils: Node

func _init() -> void:
	_import_utils = preload(IMPORT_UTILS_PATH).new()

func get_visible_name() -> String:
	return "AI Asset"

func get_import_order() -> int:
	return 1

func get_recognized_extensions() -> PackedStringArray:
	return ["png", "jpg", "jpeg", "svg", "gd", "gdshader", "tscn"]

func get_save_extension() -> String:
	var extension_type: String = _get_resource_extension_type()
	match extension_type:
		"texture":
			return "ctex"
		"script":
			return "gd"
		"scene":
			return "tscn"
		_:
			return "res"

func get_resource_type() -> String:
	var extension_type: String = _get_resource_extension_type()
	match extension_type:
		"texture":
			return "CompressedTexture2D"
		"script":
			return "Script"
		"scene":
			return "PackedScene"
		_:
			return "Resource"

func import(source_file: String, save_path: String, options: Dictionary, platform_variants: Array, gen_files: Array) -> int:
	if not _import_utils.validate_source_file(source_file):
		return ERR_FILE_NOT_FOUND

	var trace_id: String = _generate_trace_id()
	var extension_type: String = _get_extension_type(source_file)

	var normalized_options: Dictionary
	match extension_type:
		"texture":
			normalized_options = _import_utils.normalize_texture_options(options)
		"script":
			normalized_options = _import_utils.normalize_script_options(options)
		"scene":
			normalized_options = _import_utils.normalize_scene_options(options)
		_:
			push_warning("Unknown extension type for: " + source_file)
			return ERR_UNAVAILABLE

	var metadata: Dictionary = _import_utils.generate_import_metadata(source_file, trace_id)

	match extension_type:
		"texture":
			return _import_texture(source_file, save_path, normalized_options, metadata)
		"script":
			return _import_script(source_file, save_path, normalized_options, metadata)
		"scene":
			return _import_scene(source_file, save_path, normalized_options, metadata)
		_:
			return ERR_UNAVAILABLE

func get_option_visibility(path: String, option_name: String, options: Dictionary) -> bool:
	var extension_type: String = _get_extension_type(path)
	match extension_type:
		"texture":
			return _get_texture_option_visibility(option_name, options)
		"script":
			return _get_script_option_visibility(option_name, options)
		"scene":
			return _get_scene_option_visibility(option_name, options)
	return true

func get_import_options(path: String, option_index: int) -> Array[Dictionary]:
	var extension_type: String = _get_extension_type(path)
	match extension_type:
		"texture":
			return _get_texture_import_options()
		"script":
			return _get_script_import_options()
		"scene":
			return _get_scene_import_options()
	return []

func _get_resource_extension_type() -> String:
	var recognized_exts: PackedStringArray = get_recognized_extensions()
	if recognized_exts.is_empty():
		return ""
	return "texture" if recognized_exts[0] in ["png", "jpg", "jpeg", "svg"] else "script"

func _get_extension_type(path: String) -> String:
	var ext: String = path.get_extension().to_lower()
	if ext in ["png", "jpg", "jpeg", "svg"]:
		return "texture"
	elif ext in ["gd", "gdshader"]:
		return "script"
	elif ext == "tscn":
		return "scene"
	return "unknown"

func _generate_trace_id() -> String:
	return "import_%d_%d" % [Time.get_unix_time_from_system(), randi() % 10000]

func _import_texture(source_file: String, save_path: String, options: Dictionary, metadata: Dictionary) -> int:
	var image: Image = Image.new()
	var ext: String = source_file.get_extension().to_lower()

	if ext == "svg":
		push_warning("SVG import requires external conversion tool")
		return ERR_UNAVAILABLE

	var err: int = image.load(source_file)
	if err != err:
		push_error("Failed to load image: " + source_file)
		return err

	var texture: ImageTexture = ImageTexture.create_from_image(image)

	var save_extension: String = get_save_extension()
	var save_file: String = save_path + "." + save_extension

	resource_saver_save(texture, save_file)
	return OK

func _import_script(source_file: String, save_path: String, options: Dictionary, metadata: Dictionary) -> int:
	var script_content: String = FileAccess.get_file_as_string(source_file)
	if script_content.is_empty():
		push_error("Failed to read script: " + source_file)
		return ERR_FILE_CANT_READ

	var ext: String = source_file.get_extension().to_lower()
	var script: Resource

	if ext == "gdshader":
		script = GDScript.new()
		script.set_source_code(script_content)
	else:
		script = GDScript.new()
		script.set_source_code(script_content)

	if options.get("class_name", ""):
		script.set_class_name(options["class_name"])

	var save_extension: String = get_save_extension()
	var save_file: String = save_path + "." + save_extension

	resource_saver_save(script, save_file)
	return OK

func _import_scene(source_file: String, save_path: String, options: Dictionary, metadata: Dictionary) -> int:
	var scene_file: FileAccess = FileAccess.open(source_file, FileAccess.READ)
	if scene_file == null:
		push_error("Failed to open scene file: " + source_file)
		return ERR_FILE_CANT_OPEN

	var scene_content: String = scene_file.get_as_text()
	scene_file.close()

	var packed_scene: PackedScene = PackedScene.new()
	var state: SceneState = packed_scene.get_state()

	state.set_display_scale(options.get("display_scale", 1.0))

	var save_extension: String = get_save_extension()
	var save_file: String = save_path + "." + save_extension

	var err: int = packed_scene.pack(source_file)
	if err != OK:
		push_error("Failed to pack scene: " + source_file)
		return err

	err = ResourceSaver.save(packed_scene, save_file)
	return err

func _get_texture_import_options() -> Array[Dictionary]:
	return [
		{
			"name": "compress_mode",
			"type": TYPE_INT,
			"default_value": 0,
			"hint": PROPERTY_HINT_ENUM,
			"hint_string": "Lossy:2,Lossless:1,VRAM Compressed:0,VRAM Uncompressed:3,BAS:4"
		},
		{
			"name": "flags",
			"type": TYPE_INT,
			"default_value": 4,
			"hint": PROPERTY_HINT_FLAGS,
			"hint_string": "Mipmaps:1,Repeat:2,Filter:4,Til_from_Tex:8,Mirror:16,Fix_Alpha:32,Detach_Base:64,Detach_Process:128,Detach_Read Next:256"
		},
		{
			"name": "filter",
			"type": TYPE_BOOL,
			"default_value": true
		}
	]

func _get_script_import_options() -> Array[Dictionary]:
	return [
		{
			"name": "class_name",
			"type": TYPE_STRING,
			"default_value": ""
		},
		{
			"name": "tool",
			"type": TYPE_BOOL,
			"default_value": false
		},
		{
			"name": "icon_path",
			"type": TYPE_STRING,
			"default_value": ""
		}
	]

func _get_scene_import_options() -> Array[Dictionary]:
	return [
		{
			"name": "nodes_count",
			"type": TYPE_INT,
			"default_value": 0
		},
		{
			"name": "optimization",
			"type": TYPE_BOOL,
			"default_value": true
		}
	]

func _get_texture_option_visibility(option_name: String, options: Dictionary) -> bool:
	return true

func _get_script_option_visibility(option_name: String, options: Dictionary) -> bool:
	return true

func _get_scene_option_visibility(option_name: String, options: Dictionary) -> bool:
	return true
