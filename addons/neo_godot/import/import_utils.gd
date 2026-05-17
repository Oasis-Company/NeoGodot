class_name ImportUtils

const DEFAULT_TEXTURE_OPTIONS: Dictionary = {
	"compress_mode": 0,
	"flags": 4,
	"filter": true,
	"mipmaps": true
}

const DEFAULT_SCRIPT_OPTIONS: Dictionary = {
	"class_name": "",
	"tool": false,
	"icon_path": ""
}

const DEFAULT_SCENE_OPTIONS: Dictionary = {
	"nodes_count": 0,
	"optimization": true,
	"display_scale": 1.0
}

func normalize_texture_options(options: Dictionary) -> Dictionary:
	var normalized: Dictionary = DEFAULT_TEXTURE_OPTIONS.duplicate()

	if options.has("compress_mode"):
		normalized["compress_mode"] = int(options["compress_mode"])

	if options.has("flags"):
		normalized["flags"] = int(options["flags"])

	if options.has("filter"):
		normalized["filter"] = bool(options["filter"])

	if options.has("mipmaps"):
		normalized["mipmaps"] = bool(options["mipmaps"])

	return normalized

func normalize_script_options(options: Dictionary) -> Dictionary:
	var normalized: Dictionary = DEFAULT_SCRIPT_OPTIONS.duplicate()

	if options.has("class_name"):
		normalized["class_name"] = str(options["class_name"])

	if options.has("tool"):
		normalized["tool"] = bool(options["tool"])

	if options.has("icon_path"):
		normalized["icon_path"] = str(options["icon_path"])

	return normalized

func normalize_scene_options(options: Dictionary) -> Dictionary:
	var normalized: Dictionary = DEFAULT_SCENE_OPTIONS.duplicate()

	if options.has("nodes_count"):
		normalized["nodes_count"] = int(options["nodes_count"])

	if options.has("optimization"):
		normalized["optimization"] = bool(options["optimization"])

	if options.has("display_scale"):
		normalized["display_scale"] = float(options["display_scale"])

	return normalized

func generate_import_metadata(source_path: String, trace_id: String) -> Dictionary:
	var metadata: Dictionary = {
		"trace_id": trace_id,
		"source_path": source_path,
		"import_time": Time.get_datetime_string_from_system(),
		"plugin_version": "1.0.0"
	}

	if FileAccess.file_exists(source_path):
		var file: FileAccess = FileAccess.open(source_path, FileAccess.READ)
		if file != null:
			metadata["file_size"] = file.get_length()
			metadata["file_modified"] = FileAccess.get_modified_time(source_path)
			file.close()

	return metadata

func validate_source_file(path: String) -> bool:
	if path.is_empty():
		push_warning("Source path is empty")
		return false

	if not path.begins_with("res://"):
		push_warning("Source path must be a resource path: " + path)
		return false

	if not FileAccess.file_exists(path):
		push_warning("Source file does not exist: " + path)
		return false

	var ext: String = path.get_extension().to_lower()
	var valid_extensions: Array = ["png", "jpg", "jpeg", "svg", "gd", "gdshader", "tscn"]

	if not ext in valid_extensions:
		push_warning("Unsupported file extension: " + ext)
		return false

	return true
