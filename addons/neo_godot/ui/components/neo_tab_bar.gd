extends Control
class_name NeoTabBar
## NeoTabBar Component - Tab navigation with animations

signal tab_changed(index: int)

@export var tabs: Array[String] = ["对话", "快速生成", "历史"]
@export var icons: Array[String] = ["💬", "⚡", "📜"]

var _current_tab: int = 0
var _tab_buttons: Array[Button] = []
var _tab_container: HBoxContainer
var _indicator: ColorRect
var _content_container: VBoxContainer

func _ready() -> void:
	_setup_ui()

func _setup_ui() -> void:
	# Main container
	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(vbox)
	
	# Tab buttons container
	_tab_container = HBoxContainer.new()
	_tab_container.custom_minimum_size.y = 48
	vbox.add_child(_tab_container)
	
	# Create tab buttons
	for i in range(tabs.size()):
		var btn := Button.new()
		btn.text = "  " + icons[i] + " " + tabs[i] + "  "
		btn.custom_minimum_size.y = 40
		btn.theme.set_stylebox("normal", "Button", NeoStyles.get_tab_normal_style())
		btn.theme.set_stylebox("hover", "Button", NeoStyles.get_tab_hover_style())
		btn.theme.set_stylebox("pressed", "Button", NeoStyles.get_tab_active_style())
		btn.theme.set_color("font_color", "Button", NeoColors.TEXT_MUTED)
		btn.theme.set_color("font_hover_color", "Button", NeoColors.TEXT_SECONDARY)
		btn.theme.set_color("font_pressed_color", "Button", NeoColors.TEXT_PRIMARY)
		btn.pressed.connect(_on_tab_button_pressed.bind(i))
		_tab_container.add_child(btn)
		_tab_buttons.append(btn)
	
	# Tab indicator
	_indicator = ColorRect.new()
	_indicator.custom_minimum_size.y = 2
	_indicator.color = NeoColors.PRIMARY_500
	_tab_container.add_child(_indicator)
	
	# Content placeholder
	_content_container = VBoxContainer.new()
	_content_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(_content_container)
	
	# Set initial tab
	_update_tab(0)

func _on_tab_button_pressed(index: int) -> void:
	if index == _current_tab:
		return
	_update_tab(index)
	tab_changed.emit(index)

func _update_tab(index: int) -> void:
	_current_tab = index
	
	# Update button styles
	for i in range(_tab_buttons.size()):
		var btn := _tab_buttons[i]
		if i == index:
			btn.add_theme_stylebox_override("normal", NeoStyles.get_tab_active_style())
		else:
			btn.add_theme_stylebox_override("normal", NeoStyles.get_tab_normal_style())
	
	# Animate indicator
	_update_indicator_position()

func _update_indicator_position() -> void:
	if _current_tab >= _tab_buttons.size():
		return
	
	var btn := _tab_buttons[_current_tab]
	var target_x := btn.position.x
	var target_width := btn.size.x
	
	# Animate indicator
	var tween := create_tween()
	tween.tween_property(_indicator, "position:x", target_x, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(_indicator, "custom_minimum_size:x", target_width, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func get_current_tab() -> int:
	return _current_tab

func set_current_tab(index: int) -> void:
	if index >= 0 and index < tabs.size():
		_update_tab(index)
