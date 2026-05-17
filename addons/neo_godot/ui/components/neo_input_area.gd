extends Control
class_name NeoInputArea
## NeoInputArea Component - Input area with type selector and send button

signal send_request(prompt: String, generation_type: int)
signal stop_request()

@export var generation_types: Array[String] = ["💬 文本", "📝 脚本", "🎨 图像"]

var _type_selector: OptionButton
var _input_field: LineEdit
var _send_button: Button
var _stop_button: Button
var _is_generating: bool = false

func _ready() -> void:
	_setup_ui()

func _setup_ui() -> void:
	var hbox := HBoxContainer.new()
	hbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	hbox.add_theme_constant_override("separation", NeoTypography.SPACE_3)
	add_child(hbox)
	
	# Type selector
	_type_selector = OptionButton.new()
	_type_selector.custom_minimum_size.x = 120
	for gen_type in generation_types:
		_type_selector.add_item(gen_type)
	hbox.add_child(_type_selector)
	
	# Input field
	_input_field = LineEdit.new()
	_input_field.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_input_field.placeholder_text = "输入你的需求..."
	_input_field.clear_button_enabled = true
	_input_field.caret_blink = true
	hbox.add_child(_input_field)
	
	# Send button
	_send_button = Button.new()
	_send_button.text = "发送"
	_send_button.custom_minimum_size.x = 80
	hbox.add_child(_send_button)
	
	# Stop button
	_stop_button = Button.new()
	_stop_button.text = "停止"
	_stop_button.custom_minimum_size.x = 80
	_stop_button.disabled = true
	hbox.add_child(_stop_button)
	
	# Connect signals
	_send_button.pressed.connect(_on_send_pressed)
	_stop_button.pressed.connect(_on_stop_pressed)
	_input_field.text_submitted.connect(_on_text_submitted)

func _on_send_pressed() -> void:
	var prompt: String = _input_field.text.strip_edges()
	if prompt.is_empty():
		return
	
	send_request.emit(prompt, _type_selector.selected)
	_input_field.clear()

func _on_text_submitted(text: String) -> void:
	_on_send_pressed()

func _on_stop_pressed() -> void:
	stop_request.emit()

func set_generating_state(generating: bool) -> void:
	_is_generating = generating
	_send_button.disabled = generating
	_stop_button.disabled = not generating
	_input_field.editable = not generating

func get_prompt() -> String:
	return _input_field.text

func set_prompt(text: String) -> void:
	_input_field.text = text

func set_type(index: int) -> void:
	if index >= 0 and index < generation_types.size():
		_type_selector.selected = index

func get_type() -> int:
	return _type_selector.selected
