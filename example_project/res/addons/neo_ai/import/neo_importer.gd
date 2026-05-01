@tool
extends RefCounted

signal import_completed(success: bool, imported_paths: Array, errors: Array)
signal file_normalized(path: String)

var import_base_path: String = "res://ai_generated/"

func import_assets(files: Array, resource_type: String = "other") -> void:
    var imported_paths: Array = []
    var errors: Array = []
    
    for file_path in files:
        if not FileAccess.file_exists(file_path):
            errors.append("File not found: " + file_path)
            continue
        
        var result = _normalize_and_import(file_path, resource_type)
        if result.success:
            imported_paths.append(result.path)
            emit_signal("file_normalized", result.path)
        else:
            errors.append(result.error)
    
    _trigger_godot_reimport(imported_paths)
    emit_signal("import_completed", errors.empty(), imported_paths, errors)

func _normalize_and_import(file_path: String, resource_type: String) -> Dictionary:
    var file_name = _generate_normalized_name(file_path, resource_type)
    var target_path = import_base_path + file_name
    
    if not _ensure_directory(import_base_path):
        return {"success": false, "error": "Failed to create directory"}
    
    var file = FileAccess.new()
    var error = file.open(file_path, FileAccess.READ)
    if error != OK:
        return {"success": false, "error": "Failed to read source file"}
    
    var content = file.get_buffer(file.get_length())
    file.close()
    
    var target_file = FileAccess.new()
    error = target_file.open(target_path, FileAccess.WRITE)
    if error != OK:
        return {"success": false, "error": "Failed to write target file"}
    
    target_file.store_buffer(content)
    target_file.close()
    
    _generate_manifest(target_path, resource_type)
    
    return {"success": true, "path": target_path}

func _generate_normalized_name(file_path: String, resource_type: String) -> String:
    var extension = file_path.get_extension().to_lower()
    var hash = _compute_fingerprint(file_path)
    var base_name = resource_type + "_" + hash + "." + extension
    return base_name

func _compute_fingerprint(file_path: String) -> String:
    var file = FileAccess.new()
    if file.open(file_path, FileAccess.READ) != OK:
        return str(OS.get_ticks_msec())
    
    var content = file.get_buffer(file.get_length())
    file.close()
    
    var md5 = Crypto.new().md5_string(content.get_string_from_utf8())
    return md5.substr(0, 8)

func _ensure_directory(path: String) -> bool:
    var dir = DirAccess.new()
    if dir.dir_exists(path):
        return true
    
    return dir.make_dir_recursive(path) == OK

func _generate_manifest(target_path: String, resource_type: String) -> void:
    var manifest = {
        "artifact_id": "art_" + str(OS.get_ticks_msec()),
        "task_id": "",
        "session_id": "",
        "generated_at": str(DateTime.now()),
        "original_prompt": "",
        "metadata": {
            "purpose": "",
            "style_ref": "neo_style_v1"
        },
        "fingerprint": _compute_fingerprint(target_path)
    }
    
    var manifest_path = target_path.get_basename() + ".neoasset.json"
    var file = FileAccess.new()
    if file.open(manifest_path, FileAccess.WRITE) == OK:
        file.store_string(JSON.stringify(manifest))
        file.close()

func _trigger_godot_reimport(paths: Array) -> void:
    if paths.empty():
        return
    
    var editor = get_editor_interface()
    var fs = editor.get_resource_filesystem()
    
    for path in paths:
        fs.update_file(path)
    
    fs.reimport_files(paths)
    
    editor.get_file_system_dock().navigate_to_path(paths[0])

func get_supported_types() -> Dictionary:
    return {
        "image": ["png", "jpg", "jpeg", "webp"],
        "audio": ["wav", "ogg"],
        "3d": ["glb", "gltf"],
        "script": ["gd"],
        "scene": ["tscn"],
        "config": ["tres"]
    }

func get_import_handler(resource_type: String) -> String:
    match resource_type:
        "image": return "native_texture"
        "audio": return "native_audio"
        "3d": return "gltf_document"
        "script": return "direct_write"
        "scene": return "scene_import"
        "config": return "direct_write"
        _: return "generic"

func validate_asset(file_path: String) -> Dictionary:
    var extension = file_path.get_extension().to_lower()
    var supported = get_supported_types()
    
    for type_name, exts in supported:
        if extension in exts:
            return {"valid": true, "type": type_name, "handler": get_import_handler(type_name)}
    
    return {"valid": false, "type": "unknown", "handler": "generic"}