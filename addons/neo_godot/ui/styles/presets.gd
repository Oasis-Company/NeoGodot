extends RefCounted
class_name NeoStyles
## NeoGodot Design System - Style Presets

const colors := NeoColors
const typography := NeoTypography

# Panel Style (for cards and containers)
static func get_panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_SURFACE
	style.border_color = colors.BG_HIGHLIGHT
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_LG
	style.corner_radius_top_right = NeoTypography.RADIUS_LG
	style.corner_radius_bottom_left = NeoTypography.RADIUS_LG
	style.corner_radius_bottom_right = NeoTypography.RADIUS_LG
	style.content_margin_left = NeoTypography.SPACE_6
	style.content_margin_top = NeoTypography.SPACE_6
	style.content_margin_right = NeoTypography.SPACE_6
	style.content_margin_bottom = NeoTypography.SPACE_6
	return style

# Elevated Panel Style (for raised elements)
static func get_elevated_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_ELEVATED
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_4
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_4
	return style

# User Message Style
static func get_user_message_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_ELEVATED
	style.corner_radius_top_left = NeoTypography.RADIUS_SM
	style.corner_radius_top_right = NeoTypography.RADIUS_LG
	style.corner_radius_bottom_left = NeoTypography.RADIUS_LG
	style.corner_radius_bottom_right = NeoTypography.RADIUS_LG
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_3
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_3
	return style

# AI Message Style
static func get_ai_message_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_SURFACE
	style.border_color = colors.BG_HIGHLIGHT
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_LG
	style.corner_radius_top_right = NeoTypography.RADIUS_LG
	style.corner_radius_bottom_left = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_right = NeoTypography.RADIUS_LG
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_3
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_3
	return style

# System Message Style
static func get_system_message_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(colors.WARNING.r, colors.WARNING.g, colors.WARNING.b, 0.1)
	style.border_color = colors.WARNING
	style.border_width_left = 3
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_3
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_3
	return style

# Primary Button Style
static func get_primary_button_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.PRIMARY_500
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_6
	style.content_margin_top = NeoTypography.SPACE_2
	style.content_margin_right = NeoTypography.SPACE_6
	style.content_margin_bottom = NeoTypography.SPACE_2
	return style

# Secondary Button Style
static func get_secondary_button_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_ELEVATED
	style.border_color = colors.BG_HIGHLIGHT
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_6
	style.content_margin_top = NeoTypography.SPACE_2
	style.content_margin_right = NeoTypography.SPACE_6
	style.content_margin_bottom = NeoTypography.SPACE_2
	return style

# Input Field Style
static func get_input_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_SURFACE
	style.border_color = colors.BG_HIGHLIGHT
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_3
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_3
	return style

# Input Field Focus Style
static func get_input_focus_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_SURFACE
	style.border_color = colors.PRIMARY_500
	style.border_width_left = 2
	style.border_width_top = 2
	style.border_width_right = 2
	style.border_width_bottom = 2
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_3
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_3
	return style

# Code Block Style
static func get_code_block_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_BASE
	style.border_color = colors.BG_HIGHLIGHT
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = NeoTypography.RADIUS_MD
	style.corner_radius_top_right = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_left = NeoTypography.RADIUS_MD
	style.corner_radius_bottom_right = NeoTypography.RADIUS_MD
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_4
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_4
	return style

# Tab Button Normal Style
static func get_tab_normal_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color.TRANSPARENT
	style.corner_radius_top_left = NeoTypography.RADIUS_SM
	style.corner_radius_top_right = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_left = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_right = NeoTypography.RADIUS_SM
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_2
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_2
	return style

# Tab Button Hover Style
static func get_tab_hover_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = colors.BG_SURFACE
	style.corner_radius_top_left = NeoTypography.RADIUS_SM
	style.corner_radius_top_right = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_left = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_right = NeoTypography.RADIUS_SM
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_2
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_2
	return style

# Tab Button Active Style
static func get_tab_active_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(colors.PRIMARY_500.r, colors.PRIMARY_500.g, colors.PRIMARY_500.b, 0.1)
	style.corner_radius_top_left = NeoTypography.RADIUS_SM
	style.corner_radius_top_right = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_left = NeoTypography.RADIUS_SM
	style.corner_radius_bottom_right = NeoTypography.RADIUS_SM
	style.content_margin_left = NeoTypography.SPACE_4
	style.content_margin_top = NeoTypography.SPACE_2
	style.content_margin_right = NeoTypography.SPACE_4
	style.content_margin_bottom = NeoTypography.SPACE_2
	return style
