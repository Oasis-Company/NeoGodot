extends RefCounted
class_name NeoTypography
## NeoGodot Design System - Typography

# Font Sizes
const SIZE_TITLE: int = 20
const SIZE_HEADING: int = 16
const SIZE_BODY: int = 14
const SIZE_CAPTION: int = 12
const SIZE_CODE: int = 13

# Line Heights
const LINE_HEIGHT_TIGHT: float = 1.25
const LINE_HEIGHT_NORMAL: float = 1.5
const LINE_HEIGHT_RELAXED: float = 1.75

# Font Weights (Godot uses bold property instead)
const WEIGHT_NORMAL: int = 400
const WEIGHT_MEDIUM: int = 500
const WEIGHT_SEMIBOLD: int = 600
const WEIGHT_BOLD: int = 700

# Spacing Scale (4px base)
const SPACE_1: int = 4
const SPACE_2: int = 8
const SPACE_3: int = 12
const SPACE_4: int = 16
const SPACE_6: int = 24
const SPACE_8: int = 32

# Border Radius
const RADIUS_SM: int = 4
const RADIUS_MD: int = 8
const RADIUS_LG: int = 12
const RADIUS_FULL: int = 9999

# Font Settings for Theme
class FontSetting:
	var size: int
	var weight: int
	
	func _init(p_size: int, p_weight: int = WEIGHT_NORMAL):
		size = p_size
		weight = p_weight

static func get_title_font() -> FontSetting:
	return FontSetting.new(SIZE_TITLE, WEIGHT_BOLD)

static func get_heading_font() -> FontSetting:
	return FontSetting.new(SIZE_HEADING, WEIGHT_SEMIBOLD)

static func get_body_font() -> FontSetting:
	return FontSetting.new(SIZE_BODY, WEIGHT_NORMAL)

static func get_caption_font() -> FontSetting:
	return FontSetting.new(SIZE_CAPTION, WEIGHT_NORMAL)

static func get_code_font() -> FontSetting:
	return FontSetting.new(SIZE_CODE, WEIGHT_NORMAL)
