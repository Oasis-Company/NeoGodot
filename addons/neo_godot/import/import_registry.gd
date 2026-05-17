extends Node

class_name ImportRegistry

var _plugins: Dictionary = {}
var _extension_map: Dictionary = {}

static func get_instance() -> ImportRegistry:
	var path: String = "res://addons/neo_godot/import/import_registry.gd"
	var registry: ImportRegistry

	if Engine.has_singleton("ImportRegistry"):
		registry = Engine.get_singleton("ImportRegistry")
	else:
		registry = load(path).new()
		Engine.register_singleton("ImportRegistry", registry)

	return registry

func _init() -> void:
	pass

func register_plugin(plugin: EditorImportPlugin) -> bool:
	if plugin == null:
		push_warning("Cannot register null plugin")
		return false

	var plugin_name: String = plugin.get_plugin_name()
	if _plugins.has(plugin_name):
		push_warning("Plugin already registered: " + plugin_name)
		return false

	_plugins[plugin_name] = plugin

	var recognized_extensions: PackedStringArray = plugin.get_recognized_extensions()
	for ext in recognized_extensions:
		var normalized_ext: String = ext.to_lower()
		if _extension_map.has(normalized_ext):
			push_warning("Extension already registered by another plugin: " + normalized_ext)
		else:
			_extension_map[normalized_ext] = plugin_name

	return true

func unregister_plugin(plugin_name: String) -> bool:
	if not _plugins.has(plugin_name):
		push_warning("Plugin not found: " + plugin_name)
		return false

	var plugin: EditorImportPlugin = _plugins[plugin_name]
	var recognized_extensions: PackedStringArray = plugin.get_recognized_extensions()

	for ext in recognized_extensions:
		var normalized_ext: String = ext.to_lower()
		if _extension_map.get(normalized_ext) == plugin_name:
			_extension_map.erase(normalized_ext)

	_plugins.erase(plugin_name)
	return true

func get_plugin_for_extension(ext: String) -> EditorImportPlugin:
	var normalized_ext: String = ext.to_lower()

	if not _extension_map.has(normalized_ext):
		return null

	var plugin_name: String = _extension_map[normalized_ext]
	return _plugins.get(plugin_name)

func get_all_plugins() -> Array[EditorImportPlugin]:
	return _plugins.values()

func get_plugin(plugin_name: String) -> EditorImportPlugin:
	return _plugins.get(plugin_name)

func has_plugin(plugin_name: String) -> bool:
	return _plugins.has(plugin_name)

func clear() -> void:
	_plugins.clear()
	_extension_map.clear()
