extends Control
class_name ConnectionIndicator
## Connection Status Indicator Component
## 显示与 Runtime Gateway 的连接状态

enum Status {
	DISCONNECTED = 0,  # 红色 - 未连接
	CONNECTING = 1,     # 黄色 - 连接中
	CONNECTED = 2,      # 绿色 - 已连接
	NOT_CONFIGURED = 3   # 灰色 - 未配置
}

signal status_changed(new_status: int)

var _current_status: int = Status.DISCONNECTED
var _pulse_tween: Tween = null

@onready var _dot: ColorRect = $Dot
@onready var _label: Label = $Label

func _ready() -> void:
	_update_appearance()

func set_status(status: int) -> void:
	"""
	设置连接状态
	
	Args:
		status: Status 枚举值
	"""
	if _current_status == status:
		return
	
	_current_status = status
	_update_appearance()
	status_changed.emit(status)

func get_status() -> int:
	return _current_status

func _update_appearance() -> void:
	if not is_inside_tree():
		return
	
	_stop_animations()
	
	match _current_status:
		Status.CONNECTED:
			_dot.color = NeoColors.SUCCESS
			_label.text = "在线"
			_label.modulate = NeoColors.SUCCESS
			_start_pulse()
		Status.CONNECTING:
			_dot.color = NeoColors.WARNING
			_label.text = "连接中"
			_label.modulate = NeoColors.WARNING
			_start_rotate()
		Status.DISCONNECTED:
			_dot.color = NeoColors.ERROR
			_label.text = "离线"
			_label.modulate = NeoColors.ERROR
		Status.NOT_CONFIGURED:
			_dot.color = NeoColors.TEXT_MUTED
			_label.text = "未配置"
			_label.modulate = NeoColors.TEXT_MUTED

func _start_pulse() -> void:
	"""
	开始脉冲动画（在线状态）
	"""
	_pulse_tween = create_tween()
	_pulse_tween.set_loops()
	_pulse_tween.tween_property(_dot, "modulate:a", 0.4, 1.0)
	_pulse_tween.tween_property(_dot, "modulate:a", 1.0, 1.0)

func _start_rotate() -> void:
	"""
	开始旋转动画（连接中状态）
	"""
	_pulse_tween = create_tween()
	_pulse_tween.set_loops()
	_pulse_tween.tween_property(_dot, "rotation", TAU, 1.0).set_trans(Tween.TRANS_LINEAR)

func _stop_animations() -> void:
	"""
	停止所有动画
	"""
	if _pulse_tween:
		_pulse_tween.kill()
		_pulse_tween = null
	_dot.modulate.a = 1.0
	_dot.rotation = 0.0
