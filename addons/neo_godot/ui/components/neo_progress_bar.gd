extends Control
class_name NeoProgressBar
## NeoProgressBar Component - Animated progress indicator

@export var show_percentage: bool = false

var _progress: float = 0.0
var _is_indeterminate: bool = false
var _animation_tween: Tween = null

@onready var _background: ColorRect = $Background
@onready var _fill: ColorRect = $Fill
@onready var _label: Label = $Label

func _ready() -> void:
	_setup_ui()

func _setup_ui() -> void:
	custom_minimum_size.y = 4
	
	# Background
	_background = ColorRect.new()
	_background.color = NeoColors.BG_ELEVATED
	_background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_background)
	
	# Fill
	_fill = ColorRect.new()
	_fill.color = NeoColors.PRIMARY_500
	_background.add_child(_fill)
	
	# Label (hidden by default)
	_label = Label.new()
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.visible = show_percentage
	add_child(_label)
	
	# Round corners using clip children
	_background.clip_children = Control.CLIP_CHILDREN_ENABLED

func set_progress(value: float) -> void:
	_progress = clamp(value, 0.0, 1.0)
	_is_indeterminate = false
	_stop_animation()
	
	var tween := create_tween()
	tween.tween_property(_fill, "size:x", _background.size.x * _progress, 0.3).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	
	if show_percentage:
		_label.text = "%d%%" % int(_progress * 100)

func start_indeterminate() -> void:
	_is_indeterminate = true
	_fill.size.x = _background.size.x * 0.3
	
	_animation_tween = create_tween()
	_animation_tween.set_loops()
	_animation_tween.tween_property(_fill, "position:x", _background.size.x * 0.7, 1.0).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
	_animation_tween.tween_property(_fill, "position:x", 0.0, 1.0).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)

func stop() -> void:
	_stop_animation()
	_progress = 0.0
	_fill.size.x = 0
	_fill.position.x = 0

func _stop_animation() -> void:
	if _animation_tween:
		_animation_tween.kill()
		_animation_tween = null
