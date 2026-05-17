extends Control
class_name AIAssistantDock

signal request_sent(prompt: String, generation_type: int)
signal generation_result(result: Dictionary)

const NeoStyles = preload("res://addons/neo_godot/ui/styles/presets.gd")
const NeoColors = preload("res://addons/neo_godot/ui/styles/colors.gd")
const NeoTypography = preload("res://addons/neo_godot/ui/styles/typography.gd")

var _is_generating: bool = false
var _history: Array = []
var _current_tab: int = 0
const MAX_HISTORY_SIZE: int = 100
const HISTORY_FILE: String = "user://ai_assistant_history.json"

@onready var _header: HBoxContainer
@onready var _logo: Label
@onready var _title: Label
@onready var _connection_indicator: Control
@onready var _tab_bar: HBoxContainer
@onready var _tab_buttons: Array = []
@onready var _tab_indicator: ColorRect
@onready var _content_stack: VBoxContainer
@onready var _chat_content: ScrollContainer
@onready var _chat_container: VBoxContainer
@onready var _quick_content: GridContainer
@onready var _history_content: ScrollContainer
@onready var _history_container: VBoxContainer
@onready var _input_area: HBoxContainer
@onready var _type_selector: OptionButton
@onready var _prompt_input: LineEdit
@onready var _send_btn: Button
@onready var _stop_btn: Button
@onready var _progress_bar: ColorRect
@onready var _progress_fill: ColorRect

func _ready() -> void:
	_setup_ui()
	_connect_signals()
	_load_history()

func _setup_ui() -> void:
	var main_vbox := VBoxContainer.new()
	main_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(main_vbox)
	
	_setup_header(main_vbox)
	_setup_tab_bar(main_vbox)
	_setup_content_area(main_vbox)
	_setup_input_area(main_vbox)
	_setup_progress_bar(main_vbox)
	
	_update_connection_status(false)

func _setup_header(parent: VBoxContainer) -> void:
	var header := HBoxContainer.new()
	header.custom_minimum_size.y = 56
	header.add_theme_stylebox_override("panel", NeoStyles.get_panel_style())
	parent.add_child(header)
	
	var logo := Label.new()
	logo.text = "🤖"
	logo.add_theme_font_size_override("font_size", 28)
	logo.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header.add_child(logo)
	
	var title := Label.new()
	title.text = " NeoGodot AI"
	title.add_theme_font_size_override("font_size", NeoTypography.SIZE_TITLE)
	title.add_theme_color_override("font_color", NeoColors.TEXT_PRIMARY)
	title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header.add_child(title)
	
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)
	
	var indicator := preload("res://addons/neo_godot/ui/components/connection_indicator.tscn").instantiate()
	header.add_child(indicator)
	
	_header = header
	_logo = logo
	_title = title
	_connection_indicator = indicator

func _setup_tab_bar(parent: VBoxContainer) -> void:
	var tab_bar := HBoxContainer.new()
	tab_bar.custom_minimum_size.y = 48
	parent.add_child(tab_bar)
	
	var tabs := ["💬 对话", "⚡ 快速生成", "📜 历史"]
	for i in range(tabs.size()):
		var btn := Button.new()
		btn.text = "  " + tabs[i] + "  "
		btn.custom_minimum_size.y = 40
		btn.add_theme_stylebox_override("normal", NeoStyles.get_tab_normal_style())
		btn.add_theme_stylebox_override("hover", NeoStyles.get_tab_hover_style())
		btn.add_theme_stylebox_override("pressed", NeoStyles.get_tab_active_style())
		btn.add_theme_color_override("font_color", NeoColors.TEXT_MUTED)
		btn.add_theme_color_override("font_hover_color", NeoColors.TEXT_SECONDARY)
		btn.add_theme_color_override("font_pressed_color", NeoColors.TEXT_PRIMARY)
		btn.pressed.connect(_on_tab_selected.bind(i))
		tab_bar.add_child(btn)
		_tab_buttons.append(btn)
	
	var indicator := ColorRect.new()
	indicator.custom_minimum_size.y = 2
	indicator.color = NeoColors.PRIMARY_500
	tab_bar.add_child(indicator)
	_tab_indicator = indicator
	
	_tab_bar = tab_bar
	_update_tab_indicator(0)

func _setup_content_area(parent: VBoxContainer) -> void:
	var content := VBoxContainer.new()
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	parent.add_child(content)
	_content_stack = content
	
	var chat_scroll := ScrollContainer.new()
	chat_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	content.add_child(chat_scroll)
	
	var chat_container := VBoxContainer.new()
	chat_container.add_theme_constant_override("separation", NeoTypography.SPACE_3)
	chat_scroll.add_child(chat_container)
	_chat_content = chat_scroll
	_chat_container = chat_container
	
	var quick_grid := GridContainer.new()
	quick_grid.columns = 2
	quick_grid.visible = false
	content.add_child(quick_grid)
	_setup_quick_actions(quick_grid)
	_quick_content = quick_grid
	
	var history_scroll := ScrollContainer.new()
	history_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	history_scroll.visible = false
	content.add_child(history_scroll)
	
	var history_container := VBoxContainer.new()
	history_container.add_theme_constant_override("separation", NeoTypography.SPACE_2)
	history_scroll.add_child(history_container)
	_history_content = history_scroll
	_history_container = history_container
	
	_show_tab_content(0)

func _setup_quick_actions(grid: GridContainer) -> void:
	var actions := [
		["🎮", "角色脚本", "玩家、NPC、敌人控制器"],
		["🗺️", "游戏场景", "关卡、地图、房间结构"],
		["🖼️", "UI 界面", "菜单、HUD、对话框"],
		["✨", "着色器", "视觉效果、特效、滤镜"]
	]
	
	for action in actions:
		var panel := PanelContainer.new()
		panel.add_theme_stylebox_override("panel", NeoStyles.get_elevated_style())
		panel.gui_input.connect(_on_quick_action_input.bind(action[1]))
		grid.add_child(panel)
		
		var vbox := VBoxContainer.new()
		vbox.add_theme_constant_override("separation", NeoTypography.SPACE_2)
		panel.add_child(vbox)
		
		var icon := Label.new()
		icon.text = action[0]
		icon.add_theme_font_size_override("font_size", 32)
		icon.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vbox.add_child(icon)
		
		var title_lbl := Label.new()
		title_lbl.text = action[1]
		title_lbl.add_theme_font_size_override("font_size", NeoTypography.SIZE_BODY)
		title_lbl.add_theme_color_override("font_color", NeoColors.TEXT_PRIMARY)
		title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vbox.add_child(title_lbl)
		
		var desc := Label.new()
		desc.text = action[2]
		desc.add_theme_font_size_override("font_size", NeoTypography.SIZE_CAPTION)
		desc.add_theme_color_override("font_color", NeoColors.TEXT_MUTED)
		desc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vbox.add_child(desc)

func _setup_input_area(parent: VBoxContainer) -> void:
	var input_area := HBoxContainer.new()
	input_area.add_theme_constant_override("separation", NeoTypography.SPACE_3)
	parent.add_child(input_area)
	
	var type_sel := OptionButton.new()
	type_sel.custom_minimum_size.x = 100
	type_sel.add_item("💬 文本")
	type_sel.add_item("📝 脚本")
	type_sel.add_item("🎨 图像")
	type_sel.add_theme_stylebox_override("normal", NeoStyles.get_input_style())
	type_input_area.add_child(type_sel)
	_type_selector = type_sel
	
	var prompt := LineEdit.new()
	prompt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	prompt.placeholder_text = "输入你的需求..."
	prompt.clear_button_enabled = true
	prompt.caret_blink = true
	prompt.add_theme_stylebox_override("normal", NeoStyles.get_input_style())
	prompt.add_theme_stylebox_override("focus", NeoStyles.get_input_focus_style())
	prompt.text_submitted.connect(_on_prompt_submitted)
	input_area.add_child(prompt)
	_prompt_input = prompt
	
	var send_btn := Button.new()
	send_btn.text = "发送"
	send_btn.custom_minimum_size.x = 80
	send_btn.add_theme_stylebox_override("normal", NeoStyles.get_primary_button_style())
	send_btn.add_theme_color_override("font_color", NeoColors.TEXT_PRIMARY)
	send_btn.pressed.connect(_on_send_pressed)
	input_area.add_child(send_btn)
	_send_btn = send_btn
	
	var stop_btn := Button.new()
	stop_btn.text = "停止"
	stop_btn.custom_minimum_size.x = 80
	stop_btn.disabled = true
	stop_btn.add_theme_stylebox_override("normal", NeoStyles.get_secondary_button_style())
	stop_btn.add_theme_color_override("font_color", NeoColors.TEXT_SECONDARY)
	stop_btn.pressed.connect(_on_stop_pressed)
	input_area.add_child(stop_btn)
	_stop_btn = stop_btn
	
	_input_area = input_area

func _setup_progress_bar(parent: VBoxContainer) -> void:
	var bar := ColorRect.new()
	bar.custom_minimum_size.y = 4
	bar.color = NeoColors.BG_ELEVATED
	parent.add_child(bar)
	
	var fill := ColorRect.new()
	fill.color = NeoColors.PRIMARY_500
	fill.size.x = 0
	bar.add_child(fill)
	
	_progress_bar = bar
	_progress_fill = fill

func _connect_signals() -> void:
	pass

func _on_tab_selected(index: int) -> void:
	if index == _current_tab:
		return
	_update_tab_indicator(index)
	_show_tab_content(index)
	_current_tab = index

func _update_tab_indicator(index: int) -> void:
	if index >= _tab_buttons.size():
		return
	
	for i in range(_tab_buttons.size()):
		var btn := _tab_buttons[i]
		if i == index:
			btn.add_theme_stylebox_override("normal", NeoStyles.get_tab_active_style())
		else:
			btn.add_theme_stylebox_override("normal", NeoStyles.get_tab_normal_style())
	
	var btn := _tab_buttons[index]
	var tween := create_tween()
	tween.tween_property(_tab_indicator, "position:x", btn.position.x, 0.15).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

func _show_tab_content(index: int) -> void:
	_chat_content.visible = (index == 0)
	_quick_content.visible = (index == 1)
	_history_content.visible = (index == 2)
	
	var tween := create_tween()
	tween.tween_property(_content_stack, "modulate:a", 0.0, 0.1)
	await tween.finished
	tween = create_tween()
	tween.tween_property(_content_stack, "modulate:a", 1.0, 0.15)

func _on_send_pressed() -> void:
	var prompt: String = _prompt_input.text.strip_edges()
	if prompt.is_empty():
		return
	
	var gen_type: int = _type_selector.selected
	_add_message("user", prompt)
	request_sent.emit(prompt, gen_type)
	
	_prompt_input.clear()
	_set_generating_state(true)
	_save_history()

func _on_prompt_submitted(text: String) -> void:
	_on_send_pressed()

func _on_stop_pressed() -> void:
	_set_generating_state(false)
	_reset_progress()

func _on_quick_action_input(event: InputEvent, action: String) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var prompts := {
			"角色脚本": "生成一个 Godot 4.x 角色脚本，包含移动、跳跃和攻击逻辑",
			"游戏场景": "生成一个 Godot 4.x 场景文件结构，包含主摄像机和光照设置",
			"UI 界面": "生成一个 Godot 4.x UI 面板，包含标题栏和关闭按钮",
			"着色器": "生成一个 Godot 4.x Fragment Shader，实现简单的渐变效果"
		}
		if prompts.has(action):
			_prompt_input.text = prompts[action]
			_type_selector.selected = 1
			_on_tab_selected(0)

func _add_message(role: String, content: String) -> void:
	var timestamp := _get_timestamp()
	var msg := {"role": role, "content": content, "timestamp": timestamp}
	_history.append(msg)
	
	if _history.size() > MAX_HISTORY_SIZE:
		_history.pop_front()
	
	var msg_item := preload("res://addons/neo_godot/ui/components/message_item.gd").new()
	
	match role:
		"user":
			msg_item.setup(0, content, timestamp)
		"assistant":
			msg_item.setup(1, content, timestamp)
		_:
			msg_item.setup(2, content, timestamp)
	
	_chat_container.add_child(msg_item)
	msg_item.animate_in()
	
	_call_deferred("_scroll_to_bottom")

func _scroll_to_bottom() -> void:
	await get_tree().process_frame
	_chat_content.scroll_vertical = _chat_container.get_minimum_size().y

func _update_connection_status(connected: bool) -> void:
	if _connection_indicator.has_method("set_status"):
		if connected:
			_connection_indicator.set_status(2)
		else:
			_connection_indicator.set_status(0)

func _on_generation_progress(progress: float) -> void:
	var tween := create_tween()
	tween.tween_property(_progress_fill, "size:x", _progress_bar.size.x * progress, 0.3)

func _on_generation_complete(result: Dictionary) -> void:
	_set_generating_state(false)
	
	var tween := create_tween()
	tween.tween_property(_progress_fill, "size:x", _progress_bar.size.x, 0.3)
	
	if result.has("error"):
		_add_message("system", "错误: " + str(result["error"]))
	else:
		var content: String = result.get("content", "")
		_add_message("assistant", content)
	
	generation_result.emit(result)
	_save_history()

func _load_history() -> void:
	if not FileAccess.file_exists(HISTORY_FILE):
		return
	
	var file := FileAccess.open(HISTORY_FILE, FileAccess.READ)
	if file == null:
		push_warning("Failed to open history file: " + str(FileAccess.get_open_error()))
		return
	
	var json_string := file.get_as_text()
	file.close()
	
	var json := JSON.new()
	if json.parse(json_string) == OK:
		var data := json.get_data()
		if data is Array:
			_history = data

func _save_history() -> void:
	var file := FileAccess.open(HISTORY_FILE, FileAccess.WRITE)
	if file == null:
		push_warning("Failed to save history file: " + str(FileAccess.get_open_error()))
		return
	
	var json_string := JSON.stringify(_history)
	file.store_string(json_string)
	file.close()

func _set_generating_state(generating: bool) -> void:
	_is_generating = generating
	_send_btn.disabled = generating
	_stop_btn.disabled = not generating
	_prompt_input.editable = not generating

func _reset_progress() -> void:
	var tween := create_tween()
	tween.tween_property(_progress_fill, "size:x", 0.0, 0.3)

func _get_timestamp() -> String:
	var dt := Time.get_datetime_dict_from_system()
	return "%02d:%02d" % [dt.hour, dt.minute]
