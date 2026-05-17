extends HBoxContainer

var _role: String = ""
var _content: String = ""
var _timestamp: String = ""

@onready var icon_label: Label = $IconLabel
@onready var content_label: Label = $ContentLabel
@onready var timestamp_label: Label = $TimestampLabel

func _ready() -> void:
	custom_minimum_size.y = 40

func setup(role: String, content: String, timestamp: String) -> void:
	_role = role
	_content = content
	_timestamp = timestamp
	
	content_label.text = content
	timestamp_label.text = _format_timestamp(timestamp)
	
	match role:
		"user":
			set_user_style()
		"assistant":
			set_ai_style()
		_:
			set_error_style()

func _format_timestamp(timestamp: String) -> String:
	var parts: PackedStringArray = timestamp.split("T")
	if parts.size() >= 2:
		return parts[1].left(5)
	return timestamp

func set_user_style() -> void:
	icon_label.text = "👤"
	content_label.add_theme_color_override("font_color", Color(0.9, 0.95, 1.0))
	add_theme_stylebox_override("panel", _create_style(Color(0.2, 0.3, 0.5, 0.3)))

func set_ai_style() -> void:
	icon_label.text = "🤖"
	content_label.add_theme_color_override("font_color", Color(0.85, 0.9, 1.0))
	add_theme_stylebox_override("panel", _create_style(Color(0.15, 0.25, 0.4, 0.3)))

func set_error_style() -> void:
	icon_label.text = "⚠️"
	content_label.add_theme_color_override("font_color", Color(1.0, 0.4, 0.4))
	add_theme_stylebox_override("panel", _create_style(Color(0.5, 0.2, 0.2, 0.3)))

func _create_style(color: Color) -> StyleBoxFlat:
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = color
	style.set_corner_radius_all(4)
	style.set_content_margin_all(8)
	return style
