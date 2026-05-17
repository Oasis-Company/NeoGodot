extends Control
class_name AIAssistantDock

signal request_sent(prompt: String, generation_type: int)
signal generation_result(result: Dictionary)

@onready var header_container: HBoxContainer = $MainContainer/Header
@onready var title_label: Label = $MainContainer/Header/TitleLabel
@onready var connection_indicator: Control = $MainContainer/Header/ConnectionIndicator
@onready var tab_container: TabContainer = $MainContainer/ContentArea/TabContainer
@onready var history_container: VBoxContainer = $MainContainer/ContentArea/TabContainer/ChatTab/ScrollContainer/HistoryContainer
@onready var history_tree: Tree = $MainContainer/ContentArea/TabContainer/HistoryTab/HistoryTree
@onready var prompt_input: LineEdit = $MainContainer/InputArea/PromptInput
@onready var type_option: OptionButton = $MainContainer/InputArea/ButtonRow/TypeOption
@onready var send_btn: Button = $MainContainer/InputArea/ButtonRow/SendBtn
@onready var stop_btn: Button = $MainContainer/InputArea/ButtonRow/StopBtn
@onready var progress_bar: ProgressBar = $MainContainer

var _is_generating: bool = false
var _history: Array = []
const MAX_HISTORY_SIZE: int = 100
const HISTORY_FILE: String = "user://ai_assistant_history.json"

func _ready() -> void:
	_initialize_ui()
	_connect_signals()
	_load_history()

func _initialize_ui() -> void:
	_update_connection_status(false)
	progress_bar.value = 0.0
	tab_container.set_tab_title(0, "对话")
	tab_container.set_tab_title(1, "快速生成")
	tab_container.set_tab_title(2, "历史")

func _connect_signals() -> void:
	send_btn.pressed.connect(_on_send_pressed)
	stop_btn.pressed.connect(_on_stop_pressed)
	prompt_input.text_submitted.connect(_on_prompt_submitted)
	
	var grid_container: GridContainer = $MainContainer/ContentArea/TabContainer/QuickGenTab/GridContainer
	grid_container.get_child(0).pressed.connect(_on_quick_action.bind("character"))
	grid_container.get_child(1).pressed.connect(_on_quick_action.bind("scene"))
	grid_container.get_child(2).pressed.connect(_on_quick_action.bind("ui"))
	grid_container.get_child(3).pressed.connect(_on_quick_action.bind("shader"))

func _on_send_pressed() -> void:
	var prompt: String = prompt_input.text.strip_edges()
	if prompt.is_empty():
		return
	
	var generation_type: int = type_option.selected
	_add_message("user", prompt)
	request_sent.emit(prompt, generation_type)
	
	prompt_input.clear()
	_set_generating_state(true)
	_save_history()

func _on_prompt_submitted(text: String) -> void:
	_on_send_pressed()

func _on_stop_pressed() -> void:
	_set_generating_state(false)
	progress_bar.value = 0.0

func _add_message(role: String, content: String) -> void:
	var timestamp: String = Time.get_datetime_string_from_system()
	var message_entry: Dictionary = {
		"role": role,
		"content": content,
		"timestamp": timestamp
	}
	_history.append(message_entry)
	
	if _history.size() > MAX_HISTORY_SIZE:
		_history.pop_front()
	
	var message_item_scene: PackedScene = preload("res://addons/neo_godot/ui/components/message_item.tscn")
	var message_item: Control = message_item_scene.instantiate()
	history_container.add_child(message_item)
	
	if role == "user":
		message_item.setup("user", content, timestamp)
	elif role == "assistant":
		message_item.setup("assistant", content, timestamp)
	else:
		message_item.setup("system", content, timestamp)

func _update_connection_status(connected: bool) -> void:
	if connection_indicator.has_method("set_status"):
		if connected:
			connection_indicator.set_status(0)
		else:
			connection_indicator.set_status(1)

func _on_generation_progress(progress: float) -> void:
	progress_bar.value = progress

func _on_generation_complete(result: Dictionary) -> void:
	_set_generating_state(false)
	progress_bar.value = 1.0
	
	if result.has("error"):
		_add_message("system", "错误: " + str(result["error"]))
	else:
		var content: String = result.get("content", "")
		_add_message("assistant", content)
	
	generation_result.emit(result)
	_save_history()

func _on_quick_action(action: String) -> void:
	var prompt: String
	match action:
		"character":
			prompt = "生成一个 Godot 4.x 角色脚本，包含移动、跳跃和攻击逻辑"
		"scene":
			prompt = "生成一个 Godot 4.x 场景文件结构，包含主摄像机和光照设置"
		"ui":
			prompt = "生成一个 Godot 4.x UI 面板，包含标题栏和关闭按钮"
		"shader":
			prompt = "生成一个 Godot 4.x Fragment Shader，实现简单的渐变效果"
		_:
			return
	
	prompt_input.text = prompt
	type_option.selected = 1
	_on_send_pressed()

func _load_history() -> void:
	if not FileAccess.file_exists(HISTORY_FILE):
		return
	
	var file: FileAccess = FileAccess.open(HISTORY_FILE, FileAccess.READ)
	if file == null:
		push_warning("Failed to open history file: " + str(FileAccess.get_open_error()))
		return
	
	var json_string: String = file.get_as_text()
	file.close()
	
	var json: JSON = JSON.new()
	if json.parse(json_string) == OK:
		var parsed_data: Variant = json.get_data()
		if parsed_data is Array:
			_history = parsed_data
			_refresh_history_display()

func _save_history() -> void:
	var file: FileAccess = FileAccess.open(HISTORY_FILE, FileAccess.WRITE)
	if file == null:
		push_warning("Failed to save history file: " + str(FileAccess.get_open_error()))
		return
	
	var json_string: String = JSON.stringify(_history)
	file.store_string(json_string)
	file.close()

func _refresh_history_display() -> void:
	history_container.queue_redraw()
	for child in history_container.get_children():
		child.queue_free()
	
	for entry in _history:
		var message_item_scene: PackedScene = preload("res://addons/neo_godot/ui/components/message_item.tscn")
		var message_item: Control = message_item_scene.instantiate()
		history_container.add_child(message_item)
		message_item.setup(entry["role"], entry["content"], entry["timestamp"])

func _set_generating_state(generating: bool) -> void:
	_is_generating = generating
	send_btn.disabled = generating
	stop_btn.disabled = not generating
