extends Node2D
class_name CharacterTemplate

signal health_changed(current_health: float, max_health: float)
signal died()
signal level_up(new_level: int)

enum CharacterState {
	IDLE,
	MOVING,
	ATTACKING,
	DEFENDING,
	DEAD
}

@export_group("Character Properties")
@export var character_name: String = "New Character"
@export var max_health: float = 100.0
@export var move_speed: float = 200.0
@export var attack_damage: float = 10.0

@export_group("Movement")
@export var acceleration: float = 1000.0
@export var friction: float = 800.0

var current_health: float
var current_state: CharacterState = CharacterState.IDLE
var velocity: Vector2 = Vector2.ZERO
var facing_direction: Vector2 = Vector2.RIGHT
var level: int = 1
var experience: float = 0.0

func _ready() -> void:
	current_health = max_health
	_set_state(CharacterState.IDLE)

func _process(delta: float) -> void:
	match current_state:
		CharacterState.IDLE:
			_process_idle(delta)
		CharacterState.MOVING:
			_process_moving(delta)
		CharacterState.ATTACKING:
			_process_attacking(delta)
		CharacterState.DEFENDING:
			_process_defending(delta)

func _physics_process(delta: float) -> void:
	if velocity.length() > 0.1:
		velocity = velocity.normalized() * min(velocity.length(), move_speed)
		position += velocity * delta

func _process_idle(_delta: float) -> void:
	if velocity.length() > 0.1:
		_set_state(CharacterState.MOVING)

func _process_moving(_delta: float) -> void:
	if velocity.length() < 0.1:
		_set_state(CharacterState.IDLE)

func _process_attacking(_delta: float) -> void:
	pass

func _process_defending(_delta: float) -> void:
	pass

func take_damage(amount: float) -> void:
	if current_state == CharacterState.DEAD:
		return
	
	current_health = max(0.0, current_health - amount)
	health_changed.emit(current_health, max_health)
	
	if current_health <= 0.0:
		die()

func heal(amount: float) -> void:
	if current_state == CharacterState.DEAD:
		return
	
	current_health = min(max_health, current_health + amount)
	health_changed.emit(current_health, max_health)

func die() -> void:
	_set_state(CharacterState.DEAD)
	died.emit()

func gain_experience(amount: float) -> void:
	experience += amount
	
	var exp_needed := _calculate_exp_needed()
	while experience >= exp_needed:
		experience -= exp_needed
		level_up_character()

func level_up_character() -> void:
	level += 1
	max_health += 10.0
	move_speed += 5.0
	attack_damage += 2.0
	level_up.emit(level)

func _calculate_exp_needed() -> float:
	return 100.0 * pow(1.5, level - 1)

func _set_state(new_state: CharacterState) -> void:
	current_state = new_state

func move(direction: Vector2) -> void:
	if current_state == CharacterState.DEAD:
		return
	
	facing_direction = direction.normalized()
	velocity = facing_direction * move_speed

func stop_movement() -> void:
	velocity = Vector2.ZERO

func attack(target: Node2D) -> void:
	if current_state == CharacterState.DEAD:
		return
	
	_set_state(CharacterState.ATTACKING)
	if target and target.has_method("take_damage"):
		target.take_damage(attack_damage)
	
	await get_tree().create_timer(0.5).timeout
	if current_state == CharacterState.ATTACKING:
		_set_state(CharacterState.IDLE)

func defend() -> void:
	if current_state == CharacterState.DEAD:
		return
	
	_set_state(CharacterState.DEFENDING)

func _get_configuration_warnings() -> PackedStringArray:
	var warnings := PackedStringArray()
	if character_name.is_empty():
		warnings.append("Character name is empty")
	if max_health <= 0:
		warnings.append("Max health must be greater than 0")
	return warnings
