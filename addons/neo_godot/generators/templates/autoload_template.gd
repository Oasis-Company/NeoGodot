extends Node
class_name AutoloadTemplate

var _is_initialized := false

func _ready() -> void:
	_initialize_autoload()
	print("[AutoloadTemplate] Singleton initialized")

func _initialize_autoload() -> void:
	if _is_initialized:
		return
	
	_is_initialized = true
	_setup_autoload()

func _setup_autoload() -> void:
	pass

func _process(delta: float) -> void:
	_tick_update(delta)

func _tick_update(_delta: float) -> void:
	pass

func get_instance() -> AutoloadTemplate:
	return self

static func get_singleton() -> AutoloadTemplate:
	var root := Engine.get_main_loop()
	if root and root.has_node("/root/AutoloadTemplate"):
		return root.get_node("/root/AutoloadTemplate") as AutoloadTemplate
	return null
