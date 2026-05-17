extends Node
class_name NodeTemplate

@export_group("Node Properties")
@export var enabled: bool = true
@export var update_rate: float = 1.0

var _update_timer: float = 0.0

func _ready() -> void:
	_initialize()

func _process(delta: float) -> void:
	if not enabled:
		return
	
	_update_timer += delta
	if _update_timer >= update_rate:
		_update_timer = 0.0
		_on_update()

func _physics_process(_delta: float) -> void:
	if not enabled:
		return
	
	_physics_update()

func _initialize() -> void:
	_update_timer = 0.0

func _on_update() -> void:
	pass

func _physics_update() -> void:
	pass

func enable() -> void:
	enabled = true

func disable() -> void:
	enabled = false

func reset() -> void:
	_initialize()
