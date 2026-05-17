extends RefCounted
class_name NeoAnimations
## NeoGodot Design System - Animation Utilities

# Transition Durations (milliseconds)
const DURATION_FAST: int = 150
const DURATION_NORMAL: int = 250
const DURATION_SLOW: int = 400

# Easing Functions (Godot uses TransitionType)
const TRANSITION_FAST: Tween.TransitionType = Tween.TRANSITION_QUAD
const TRANSITION_STANDARD: Tween.TransitionType = Tween.TRANSITION_QUAD
const TRANSITION_SMOOTH: Tween.TransitionType = Tween.TRANSITION_SINE
const TRANSITION_BOUNCE: Tween.TransitionType = Tween.TRANSITION_BOUNCE
const TRANSITION_ELASTIC: Tween.TransitionType = Tween.TRANSITION_ELASTIC

# Easing Directions
const EASE_OUT: Tween.EaseType = Tween.EASE_OUT
const EASE_IN: Tween.EaseType = Tween.EASE_IN
const EASE_IN_OUT: Tween.EaseType = Tween.EASE_IN_OUT

class AnimationConfig:
	var duration: float
	var transition: Tween.TransitionType
	var easing: Tween.EaseType
	
	func _init(
		p_duration: float = 0.25,
		p_transition: Tween.TransitionType = TRANSITION_STANDARD,
		p_easing: Tween.EaseType = EASE_OUT
	):
		duration = p_duration
		transition = p_transition
		easing = p_easing

static func get_fast() -> AnimationConfig:
	return AnimationConfig.new(0.15, TRANSITION_FAST, EASE_OUT)

static func get_normal() -> AnimationConfig:
	return AnimationConfig.new(0.25, TRANSITION_STANDARD, EASE_OUT)

static func get_slow() -> AnimationConfig:
	return AnimationConfig.new(0.4, TRANSITION_SMOOTH, EASE_OUT)

static func get_bounce() -> AnimationConfig:
	return AnimationConfig.new(0.4, TRANSITION_BOUNCE, EASE_OUT)

static func get_elastic() -> AnimationConfig:
	return AnimationConfig.new(0.5, TRANSITION_ELASTIC, EASE_OUT)

# Slide in from bottom animation
static func create_slide_in(node: Node, duration: float = 0.25) -> Tween:
	var tween := node.create_tween()
	tween.set_parallel(true)
	
	var start_pos := node.position
	node.position.y += 20
	node.modulate.a = 0
	
	tween.tween_property(node, "position:y", start_pos.y, duration)
	tween.tween_property(node, "modulate:a", 1.0, duration)
	
	return tween

# Fade in animation
static func create_fade_in(node: Node, duration: float = 0.25) -> Tween:
	var tween := node.create_tween()
	node.modulate.a = 0
	tween.tween_property(node, "modulate:a", 1.0, duration)
	return tween

# Scale bounce animation
static func create_scale_bounce(node: Node, duration: float = 0.3) -> Tween:
	var tween := node.create_tween()
	
	node.scale = Vector2(0.8, 0.8)
	node.modulate.a = 0
	
	tween.set_parallel(true)
	tween.tween_property(node, "scale", Vector2(1.05, 1.05), duration * 0.6).set_trans(TRANSITION_BOUNCE)
	tween.tween_property(node, "modulate:a", 1.0, duration * 0.4)
	
	tween.chain().tween_property(node, "scale", Vector2(1.0, 1.0), duration * 0.4).set_trans(TRANSITION_SINE)
	
	return tween

# Pulse animation for status indicators
static func create_pulse(node: Node) -> Tween:
	var tween := node.create_tween()
	tween.set_loops()
	tween.tween_property(node, "modulate:a", 0.4, 1.0)
	tween.tween_property(node, "modulate:a", 1.0, 1.0)
	return tween
