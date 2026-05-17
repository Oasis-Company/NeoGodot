extends Node

class_name NeoConfig

signal config_changed

var _config: Dictionary = {}
var _config_file_path: String = "res://.godot/neogodot_config.json"

func _ready() -> void:
	load_config()

func load_config() -> Dictionary:
	if FileAccess.file_exists(_config_file_path):
		var file = FileAccess.open(_config_file_path, FileAccess.READ)
		if file:
			var content = file.get_as_text()
			file.close()
			var json = JSON.new()
			if json.parse(content) == OK:
				_config = json.data
				return _config
	_config = _get_default_config()
	save_config(_config)
	return _config

func save_config(config: Dictionary) -> void:
	_config = config
	_ensure_config_dir()
	var file = FileAccess.open(_config_file_path, FileAccess.WRITE)
	if file:
		var json_string = JSON.stringify(_config, "\t")
		file.store_string(json_string)
		file.close()
		config_changed.emit()

func _ensure_config_dir() -> void:
	var dir = DirAccess.open("res://.godot")
	if not dir:
		dir = DirAccess.open("res://")
		dir.make_dir(".godot")

func get_runtime_url() -> String:
	return _config.get("runtime_url", "http://localhost:8080")

func set_runtime_url(url: String) -> void:
	_config["runtime_url"] = url
	save_config(_config)

func get_provider_config(provider_name: String) -> Dictionary:
	var providers = _config.get("providers", {})
	return providers.get(provider_name, {})

func _get_default_config() -> Dictionary:
	return {
		"runtime_url": "http://localhost:8080",
		"api_key": "",
		"default_provider": "openai",
		"providers": {
			"openai": {
				"enabled": false,
				"model": "gpt-4"
			},
			"anthropic": {
				"enabled": false,
				"model": "claude-3-opus-20240229"
			}
		},
		"auto_save": true,
		"trace_enabled": true
	}
