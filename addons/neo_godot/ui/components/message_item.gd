extends Control
class_name MessageItem
## Message Item Component - Displays chat messages with styling

enum Role { USER, ASSISTANT, SYSTEM }

@export var message_role: Role = Role.ASSISTANT
@export var message_text: String = ""
@export var message_time: String = ""
@export var show_code_block: bool = false
@export var code_content: String = ""

var _role_icon: Label
var _author_label: Label
var _time_label: Label
var _content_label: RichTextLabel
var _code_panel: PanelContainer
var _code_label: RichTextLabel

func _ready() -> void:
	_setup_ui()
	_update_content()

func _setup_ui() -> void:
	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", NeoTypography.SPACE_2)
	add_child(vbox)
	
	# Header row
	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", NeoTypography.SPACE_2)
	vbox.add_child(header)
	
	# Role icon
	_role_icon = Label.new()
	_role_icon.text = "🤖"
	_role_icon.autowrap_mode = TextServer.AUTOWRAP_OFF
	header.add_child(_role_icon)
	
	# Author label
	_author_label = Label.new()
	_author_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(_author_label)
	
	# Time label
	_time_label = Label.new()
	_time_label.add_theme_color_override("font_color", NeoColors.TEXT_MUTED)
	header.add_child(_time_label)
	
	# Content panel
	var content_panel := PanelContainer.new()
	content_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(content_panel)
	
	# Content label
	_content_label = RichTextLabel.new()
	_content_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_content_label.bbcode_enabled = true
	_content_label.fit_content = true
	content_panel.add_child(_content_label)
	
	# Code panel (hidden by default)
	_code_panel = PanelContainer.new()
	_code_panel.visible = false
	vbox.add_child(_code_panel)
	
	var code_scroll := ScrollContainer.new()
	_code_panel.add_child(code_scroll)
	
	_code_label = RichTextLabel.new()
	_code_label.bbcode_enabled = true
	code_scroll.add_child(_code_label)

func setup(role: Role, text: String, timestamp: String = "") -> void:
	message_role = role
	message_text = text
	message_time = timestamp if timestamp else _get_current_time()
	_update_content()

func _update_content() -> void:
	match message_role:
		Role.USER:
			_role_icon.text = "👤"
			_author_label.text = "你"
			_author_label.add_theme_color_override("font_color", NeoColors.TEXT_PRIMARY)
			get_child(0).get_child(0).add_theme_stylebox_override("panel", NeoStyles.get_user_message_style())
		Role.ASSISTANT:
			_role_icon.text = "🤖"
			_author_label.text = "AI 助手"
			_author_label.add_theme_color_override("font_color", NeoColors.PRIMARY_400)
			get_child(0).get_child(0).add_theme_stylebox_override("panel", NeoStyles.get_ai_message_style())
		Role.SYSTEM:
			_role_icon.text = "⚠️"
			_author_label.text = "系统"
			_author_label.add_theme_color_override("font_color", NeoColors.WARNING)
			get_child(0).get_child(0).add_theme_stylebox_override("panel", NeoStyles.get_system_message_style())
	
	_time_label.text = message_time
	_content_label.text = "[color=#A1A1AA]" + message_text + "[/color]"

func show_code(code: String) -> void:
	_code_panel.visible = true
	show_code_block = true
	code_content = code
	
	var code_panel_inner = _code_panel.get_child(0).get_child(0)
	code_panel_inner.add_theme_stylebox_override("panel", NeoStyles.get_code_block_style())
	_code_label.text = "[code]" + code + "[/code]"
	_code_label.add_theme_color_override("default_color", NeoColors.TEXT_PRIMARY)

func _get_current_time() -> String:
	var dt := Time.get_datetime_dict_from_system()
	return "%02d:%02d" % [dt.hour, dt.minute]

# Animation entry
func animate_in() -> void:
	modulate.a = 0
	position.y += 10
	
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "modulate:a", 1.0, 0.25)
	tween.tween_property(self, "position:y", position.y - 10, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
