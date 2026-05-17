extends Control

class_name NeoConfigPanel

@onready var runtime_url_input: LineEdit = $MainContainer/RuntimeUrlContainer/RuntimeUrlInput
@onready var api_key_input: LineEdit = $MainContainer/ApiKeyContainer/ApiKeyInput
@onready var default_provider_option: OptionButton = $MainContainer/DefaultProviderContainer/DefaultProviderOption
@onready var test_connection_btn: Button = $MainContainer/ButtonRow/TestConnectionBtn
@onready var save_btn: Button = $MainContainer/ButtonRow/SaveBtn
@onready var reset_btn: Button = $MainContainer/ButtonRow/ResetBtn

var _config: Dictionary = {}

func _ready() -> void:
	_initialize_provider_options()
	_load_config_to_ui()
	_connect_signals()

func _initialize_provider_options() -> void:
	default_provider_option.clear()
	default_provider_option.add_item("OpenAI", 0)
	default_provider_option.add_item("Anthropic", 1)

func _connect_signals() -> void:
	test_connection_btn.pressed.connect(_on_test_connection_pressed)
	save_btn.pressed.connect(_on_save_pressed)
	reset_btn.pressed.connect(_on_reset_pressed)

func _load_config_to_ui() -> void:
	if has_node("/root/NeoConfig"):
		var config_node = get_node("/root/NeoConfig")
		_config = config_node.load_config()
		runtime_url_input.text = _config.get("runtime_url", "http://localhost:8080")
		
		var api_key = _config.get("api_key", "")
		api_key_input.text = api_key
		api_key_input.secret = true
		
		var default_provider = _config.get("default_provider", "openai")
		match default_provider:
			"openai":
				default_provider_option.selected = 0
			"anthropic":
				default_provider_option.selected = 1

func _save_ui_to_config() -> void:
	_config["runtime_url"] = runtime_url_input.text.strip_edges()
	_config["api_key"] = api_key_input.text.strip_edges()
	
	var provider_index = default_provider_option.selected
	match provider_index:
		0:
			_config["default_provider"] = "openai"
		1:
			_config["default_provider"] = "anthropic"

func _on_test_connection_pressed() -> void:
	test_connection_btn.disabled = true
	test_connection_btn.text = "测试中..."
	
	var runtime_url = runtime_url_input.text.strip_edges()
	if runtime_url.is_empty():
		_show_message("请输入 Runtime Gateway URL", true)
		test_connection_btn.disabled = false
		test_connection_btn.text = "测试连接"
		return
	
	await _test_connection(runtime_url)
	
	test_connection_btn.disabled = false
	test_connection_btn.text = "测试连接"

func _test_connection(url: String) -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	
	var error = http_request.request(url)
	if error != OK:
		_show_message("连接失败: 无法发起请求", true)
		return
	
	var result = await http_request.request_completed
	http_request.queue_free()
	
	var result_code = result[0]
	var response_headers = result[1]
	var response_body = result[2]
	var response_code = result[3]
	
	if result_code == OK and response_code == 200:
		_show_message("连接成功！", false)
	else:
		_show_message("连接失败: 响应代码 %d" % response_code, true)

func _on_save_pressed() -> void:
	_save_ui_to_config()
	
	if has_node("/root/NeoConfig"):
		var config_node = get_node("/root/NeoConfig")
		config_node.save_config(_config)
		_show_message("配置已保存", false)

func _on_reset_pressed() -> void:
	_load_config_to_ui()
	_show_message("配置已重置", false)

func _show_message(text: String, is_error: bool) -> void:
	var dialog = AcceptDialog.new()
	dialog.title = "NeoGodot 配置"
	dialog.unresizable = true
	dialog.dialog_text = text
	
	if is_error:
		dialog.dialog_text = "错误: " + text
	
	add_child(dialog)
	dialog.popup_centered()
