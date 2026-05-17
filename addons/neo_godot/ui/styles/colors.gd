extends RefCounted
class_name NeoColors
## NeoGodot Design System - Color Palette
## 遵循 WCAG AA 标准设计

# Primary Colors - AI Blue
const PRIMARY_50: Color = Color("#EFF6FF")
const PRIMARY_100: Color = Color("#DBEAFE")
const PRIMARY_400: Color = Color("#60A5FA")
const PRIMARY_500: Color = Color("#3B82F6")
const PRIMARY_600: Color = Color("#2563EB")
const PRIMARY_900: Color = Color("#1E3A8A")

# Accent Gradient Colors
const ACCENT_START: Color = Color("#3B82F6")
const ACCENT_END: Color = Color("#8B5CF6")

# Semantic Colors
const SUCCESS: Color = Color("#10B981")
const SUCCESS_DARK: Color = Color("#059669")
const WARNING: Color = Color("#F59E0B")
const WARNING_DARK: Color = Color("#D97706")
const ERROR: Color = Color("#EF4444")
const ERROR_DARK: Color = Color("#DC2626")

# Background Colors
const BG_BASE: Color = Color("#09090B")
const BG_SURFACE: Color = Color("#18181B")
const BG_ELEVATED: Color = Color("#27272A")
const BG_HIGHLIGHT: Color = Color("#3F3F46")

# Text Colors
const TEXT_PRIMARY: Color = Color("#FAFAFA")
const TEXT_SECONDARY: Color = Color("#A1A1AA")
const TEXT_MUTED: Color = Color("#71717A")

# Helper function to create gradient
static func get_primary_gradient() -> Gradient:
	var gradient := Gradient.new()
	gradient.set_color(0, ACCENT_START)
	gradient.set_color(1, ACCENT_END)
	return gradient

# Helper function to create glow effect color
static func get_glow_color() -> Color:
	return Color(ACCENT_START.r, ACCENT_START.g, ACCENT_START.b, 0.3)
