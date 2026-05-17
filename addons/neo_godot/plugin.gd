extends EditorPlugin

class_name NeoGodotPlugin

signal ai_generation_completed(result: Dictionary)
signal ai_error_occurred(error: String)

enum NotificationType {
	INFO,
	WARNING,
	ERROR,
	SUCCESS
}

var _ai_dock_scene: PackedScene
var _ai_dock_instance: Control
var _config_panel_scene: PackedScene
var _config_panel_instance: Control
var _config_menu_button: Button
var _main_menu: PopupMenu
var _main_menu_button: Button
var _command_dispatcher: NeoCommandDispatcher
var _undo_manager: NeoUndoManager

func _enter_tree() -> void:
	_initialize_plugin()

func _initialize_plugin() -> void:
	_ensure_directories()
	_initialize_services()
	_initialize_ai_dock()
	_initialize_config_panel()
	_initialize_autoload()
	_add_toolbar_buttons()
	_add_main_menu()
	_connect_signals()

func _ensure_directories() -> void:
	var dirs = [
		"res://ai_generated",
		"res://ai_generated/ui",
		"res://ai_generated/sfx",
		"res://ai_generated/scripts",
		"res://ai_generated/scenes"
	]
	
	for dir_path in dirs:
		if not DirAccess.dir_exists_absolute(dir_path):
			var dir = DirAccess.open("res://")
			if dir:
				var rel_path = dir_path.replace("res://", "")
				dir.make_dir_recursive(rel_path)
				print("[NeoGodot] 已创建目录: ", dir_path)
			else:
				show_notification("无法创建必要目录: " + dir_path + "\n请检查项目文件夹权限。", NotificationType.ERROR)

func _initialize_services() -> void:
	_undo_manager = NeoUndoManager.new()
	_undo_manager._plugin = self
	_undo_manager._undo_redo = get_undo_redo()
	_command_dispatcher = NeoCommandDispatcher.new()
	_command_dispatcher.undo_manager = _undo_manager
	add_child(_command_dispatcher)
	add_child(_undo_manager)
	print("[NeoGodot] 服务层已初始化")

func _initialize_ai_dock() -> void:
	var dock_path = "res://addons/neo_godot/ui/ai_assistant_dock.tscn"
	_ai_dock_scene = load(dock_path)
	
	if not _ai_dock_scene:
		show_notification("无法加载 AI 助手 Dock 场景文件: " + dock_path + "\n请检查插件文件是否完整。", NotificationType.ERROR)
		return
	
	_ai_dock_instance = _ai_dock_scene.instantiate()
	if not _ai_dock_instance:
		show_notification("无法实例化 AI 助手 Dock。\n请检查场景文件是否损坏。", NotificationType.ERROR)
		return
	
	_ai_dock_instance.name = "NeoGodotDock"
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, _ai_dock_instance)
	print("[NeoGodot] AI 助手 Dock 已加载")

func _initialize_config_panel() -> void:
	var config_panel_path = "res://addons/neo_godot/ui/config_panel.tscn"
	_config_panel_scene = load(config_panel_path)
	
	if not _config_panel_scene:
		show_notification("无法加载配置面板场景文件: " + config_panel_path + "\n请检查插件文件是否完整。", NotificationType.ERROR)
		return
	
	print("[NeoGodot] 配置面板场景已加载")

func _add_toolbar_buttons() -> void:
	_config_menu_button = Button.new()
	_config_menu_button.text = "⚙️"
	_config_menu_button.tooltip_text = "NeoGodot 配置"
	_config_menu_button.pressed.connect(_on_config_menu_pressed)
	add_control_to_container(CONTAINER_TOOLBAR, _config_menu_button)
	
	_main_menu_button = Button.new()
	_main_menu_button.text = "🤖 NeoGodot"
	_main_menu_button.pressed.connect(_on_main_menu_button_pressed)
	add_control_to_container(CONTAINER_TOOLBAR, _main_menu_button)
	
	print("[NeoGodot] 工具栏按钮已添加")

func _add_main_menu() -> void:
	_main_menu = PopupMenu.new()
	_main_menu.add_item("生成脚本", 1)
	_main_menu.add_item("生成场景", 2)
	_main_menu.add_item("生成纹理", 3)
	_main_menu.add_separator()
	_main_menu.add_item("显示/隐藏助手", 4)
	_main_menu.add_separator()
	_main_menu.add_item("配置", 5)
	_main_menu.add_item("关于", 6)
	_main_menu.id_pressed.connect(_on_main_menu_item_pressed)
	add_child(_main_menu)
	
	print("[NeoGodot] 主菜单已添加")

func _on_main_menu_button_pressed() -> void:
	_main_menu.popup_centered()

func _on_main_menu_item_pressed(id: int) -> void:
	match id:
		1:
			_show_quick_dialog("生成脚本", "请描述需要生成的脚本：", "script")
		2:
			_show_quick_dialog("生成场景", "请描述需要生成的场景：", "scene")
		3:
			_show_quick_dialog("生成纹理", "请描述需要生成的纹理：", "texture")
		4:
			_toggle_dock_visibility()
		5:
			_on_config_menu_pressed()
		6:
			_show_about_dialog()

func _toggle_dock_visibility() -> void:
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance.visible = !_ai_dock_instance.visible

func _show_quick_dialog(title: String, hint: String, type: String) -> void:
	var dialog = ConfirmationDialog.new()
	dialog.title = title
	dialog.ok_button_text = "生成"
	dialog.cancel_button_text = "取消"
	
	var vbox = VBoxContainer.new()
	dialog.add_child(vbox)
	
	var label = Label.new()
	label.text = hint
	vbox.add_child(label)
	
	var line_edit = LineEdit.new()
	line_edit.custom_minimum_size = Vector2(400, 0)
	vbox.add_child(line_edit)
	
	dialog.confirmed.connect(func():
		var prompt = line_edit.text.strip_edges()
		if prompt.is_empty():
			return
		
		if has_node("/root/NeoRuntime"):
			NeoRuntime.send_generate_request(prompt, type)
	)
	
	add_child(dialog)
	dialog.popup_centered()

func _show_about_dialog() -> void:
	var dialog = AcceptDialog.new()
	dialog.title = "关于 NeoGodot"
	dialog.unresizable = true
	
	var vbox = VBoxContainer.new()
	dialog.add_child(vbox)
	
	var title_label = Label.new()
	title_label.text = "🤖 NeoGodot v0.1.0"
	title_label.add_theme_stylebox_override("normal", create_stylebox(Color(0.2, 0.2, 0.2)))
	vbox.add_child(title_label)
	
	var desc_label = Label.new()
	desc_label.text = "AI 驱动的 Godot 编辑器助手"
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	desc_label.custom_minimum_size = Vector2(300, 0)
	vbox.add_child(desc_label)
	
	add_child(dialog)
	dialog.popup_centered()

func create_stylebox(color: Color) -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = color
	return style

func show_notification(message: String, type: NotificationType = NotificationType.INFO) -> void:
	var notification = AcceptDialog.new()
	
	match type:
		NotificationType.ERROR:
			notification.title = "⚠️ NeoGodot 错误"
			notification.unresizable = true
		NotificationType.WARNING:
			notification.title = "⚠️ NeoGodot 警告"
			notification.unresizable = true
		NotificationType.SUCCESS:
			notification.title = "✅ NeoGodot 成功"
			notification.unresizable = true
		_:
			notification.title = "ℹ️ NeoGodot 提示"
			notification.unresizable = true
	
	var vbox = VBoxContainer.new()
	vbox.custom_minimum_size = Vector2(400, 0)
	notification.add_child(vbox)
	
	var label = Label.new()
	label.text = message
	label.autowrap_mode = TextServer.AUTOWRAP_WORD
	vbox.add_child(label)
	
	add_child(notification)
	notification.popup_centered()
	
	if type == NotificationType.ERROR:
		push_error("[NeoGodot] " + message)
	elif type == NotificationType.WARNING:
		push_warning("[NeoGodot] " + message)
	else:
		print("[NeoGodot] " + message)

func _initialize_autoload() -> void:
	if has_node("/root/NeoConfig"):
		NeoConfig.config_changed.connect(_on_config_changed)
		print("[NeoGodot] NeoConfig 已连接")
	
	if has_node("/root/NeoRuntime"):
		NeoRuntime.connection_status_changed.connect(_on_runtime_connection_changed)
		NeoRuntime.generation_completed.connect(_on_generation_completed)
		NeoRuntime.generation_error.connect(_on_generation_error)
		print("[NeoGodot] NeoRuntime 已连接")

func _connect_signals() -> void:
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance.request_sent.connect(_on_dock_request_sent)
	
	if _command_dispatcher:
		_command_dispatcher.command_completed.connect(_on_command_completed)
		_command_dispatcher.command_failed.connect(_on_command_failed)
	
	print("[NeoGodot] 信号已连接")

func _on_dock_request_sent(prompt: String, generation_type: int) -> void:
	var type_map = ["script", "scene", "texture", "shader"]
	var type_str = type_map[clamp(generation_type, 0, type_map.size() - 1)]
	
	if has_node("/root/NeoRuntime"):
		NeoRuntime.send_generate_request(prompt, type_str)
	else:
		show_notification("NeoRuntime 未初始化，请检查插件配置和自动加载设置。", NotificationType.ERROR)

func _on_config_menu_pressed() -> void:
	if not _config_panel_instance:
		if not _config_panel_scene:
			show_notification("配置面板场景未加载，无法打开配置。", NotificationType.ERROR)
			return
		
		_config_panel_instance = _config_panel_scene.instantiate()
		if not _config_panel_instance:
			show_notification("无法实例化配置面板。\n请检查场景文件是否损坏。", NotificationType.ERROR)
			return
		
		_config_panel_instance.name = "NeoGodotConfigPanel"
		_config_panel_instance.custom_minimum_size = Vector2(500, 400)
	
	var dialog = AcceptDialog.new()
	dialog.title = "NeoGodot 配置"
	dialog.unresizable = true
	dialog.add_child(_config_panel_instance)
	add_child(dialog)
	dialog.popup_centered()

func _exit_tree() -> void:
	_cleanup_plugin()

func _cleanup_plugin() -> void:
	if is_instance_valid(_ai_dock_instance):
		remove_control_from_dock(_ai_dock_instance)
		_ai_dock_instance.queue_free()
		_ai_dock_instance = null
		print("[NeoGodot] AI 助手 Dock 已移除")
	
	if is_instance_valid(_config_menu_button):
		remove_control_from_container(CONTAINER_TOOLBAR, _config_menu_button)
		_config_menu_button.queue_free()
		_config_menu_button = null
	
	if is_instance_valid(_main_menu_button):
		remove_control_from_container(CONTAINER_TOOLBAR, _main_menu_button)
		_main_menu_button.queue_free()
		_main_menu_button = null
	
	if is_instance_valid(_main_menu):
		_main_menu.queue_free()
		_main_menu = null
	
	if is_instance_valid(_config_panel_instance):
		_config_panel_instance.queue_free()
		_config_panel_instance = null
	
	if has_node("/root/NeoConfig"):
		var config = get_node("/root/NeoConfig")
		if config.config_changed.is_connected(_on_config_changed):
			config.config_changed.disconnect(_on_config_changed)
			print("[NeoGodot] NeoConfig 已断开")
	
	if has_node("/root/NeoRuntime"):
		var runtime = get_node("/root/NeoRuntime")
		if runtime.connection_status_changed.is_connected(_on_runtime_connection_changed):
			runtime.connection_status_changed.disconnect(_on_runtime_connection_changed)
		if runtime.generation_completed.is_connected(_on_generation_completed):
			runtime.generation_completed.disconnect(_on_generation_completed)
		if runtime.generation_error.is_connected(_on_generation_error):
			runtime.generation_error.disconnect(_on_generation_error)
		print("[NeoGodot] NeoRuntime 已断开")
	
	print("[NeoGodot] 工具栏按钮已移除")

func make_visible(visible: bool) -> void:
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance.visible = visible

func _on_config_changed() -> void:
	print("[NeoGodot] 配置已更新")
	_reconnect_runtime()

func _reconnect_runtime() -> void:
	if has_node("/root/NeoRuntime") and has_node("/root/NeoConfig"):
		var url = NeoConfig.get_runtime_url()
		NeoRuntime.connect_to_runtime(url)

func _on_runtime_connection_changed() -> void:
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance._update_connection_status(NeoRuntime.connected)

func _on_generation_completed(result: Dictionary) -> void:
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance._on_generation_complete(result)
	ai_generation_completed.emit(result)

func _on_generation_error(error: String) -> void:
	show_notification("AI 生成失败: " + error, NotificationType.ERROR)
	if is_instance_valid(_ai_dock_instance):
		_ai_dock_instance._add_message("system", "错误: " + error)
		_ai_dock_instance._set_generating_state(false)
	ai_error_occurred.emit(error)

func _on_command_completed(command: NeoCommand, result: Dictionary) -> void:
	print("[NeoGodot] 命令完成: ", command.get_class())

func _on_command_failed(command: NeoCommand, error: String) -> void:
	show_notification("操作失败: " + error, NotificationType.ERROR)
