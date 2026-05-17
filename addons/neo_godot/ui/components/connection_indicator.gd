extends Control

enum Status { CONNECTED, DISCONNECTED, CONNECTING, ERROR }

var _current_status: int = Status.DISCONNECTED

func _ready() -> void:
	custom_minimum_size = Vector2(16, 16)

func set_status(status: int) -> void:
	_current_status = status
	queue_redraw()

func _draw() -> void:
	var center: Vector2 = Vector2(size.x / 2, size.y / 2)
	var radius: float = min(size.x, size.y) / 2 - 2
	
	match _current_status:
		Status.CONNECTED:
			draw_circle(center, radius, Color.GREEN)
		Status.DISCONNECTED:
			draw_circle(center, radius, Color.GRAY)
		Status.CONNECTING:
			draw_circle(center, radius, Color.YELLOW)
		Status.ERROR:
			draw_circle(center, radius, Color.RED)
		_:
			draw_circle(center, radius, Color.GRAY)
