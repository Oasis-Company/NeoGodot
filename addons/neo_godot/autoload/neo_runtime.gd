extends Node

class_name NeoRuntime

signal connection_status_changed(connected: bool)
signal generation_completed(result: Dictionary)
signal generation_error(error: String)

var base_url: String = ""
var api_key: String = ""
var connected: bool = false
var last_trace_id: String = ""

var _http_request: HTTPRequest
var _pending_requests: Array = []

func _ready() -> void:
	_http_request = HTTPRequest.new()
	_http_request.timeout = 30.0
	add_child(_http_request)
	_http_request.request_completed.connect(_on_request_completed)
	
	if has_node("/root/NeoConfig"):
		base_url = NeoConfig.get_runtime_url()
		var config = NeoConfig.load_config()
		api_key = config.get("api_key", "")
		NeoConfig.config_changed.connect(_on_config_changed)
		connect_to_runtime(base_url)

func _on_config_changed() -> void:
	if has_node("/root/NeoConfig"):
		var new_url = NeoConfig.get_runtime_url()
		var config = NeoConfig.load_config()
		api_key = config.get("api_key", "")
		
		if new_url != base_url:
			base_url = new_url
			connect_to_runtime(base_url)

func connect_to_runtime(url: String) -> bool:
	if url.is_empty():
		connected = false
		connection_status_changed.emit(false)
		return false
	
	base_url = url
	print("[NeoRuntime] 尝试连接到: ", base_url)
	
	var test_request = HTTPRequest.new()
	test_request.timeout = 10.0
	add_child(test_request)
	
	var headers = PackedStringArray()
	if not api_key.is_empty():
		headers.append("Authorization: Bearer " + api_key)
	
	var result = test_request.request(url + "/health", headers, HTTPClient.METHOD_GET)
	
	if result != OK:
		connected = false
		connection_status_changed.emit(false)
		print("[NeoRuntime] 发送健康检查请求失败 (错误码: " + str(result) + ")")
		test_request.queue_free()
		return false
	
	test_request.request_completed.connect(_on_health_check.bind(test_request))
	
	return true

func disconnect_from_runtime() -> void:
	base_url = ""
	connected = false
	connection_status_changed.emit(false)
	print("[NeoRuntime] 已断开连接")

func send_generate_request(prompt: String, type: String) -> void:
	if base_url.is_empty():
		generation_error.emit("未设置运行时 URL，请在配置中填写正确的地址")
		return
	
	if not connected:
		generation_error.emit("未连接到运行时网关，请检查服务是否启动或 URL 是否正确")
		return
	
	var trace_id = _generate_trace_id()
	last_trace_id = trace_id
	
	var headers = PackedStringArray()
	headers.append("Content-Type: application/json")
	if not api_key.is_empty():
		headers.append("Authorization: Bearer " + api_key)
	headers.append("X-Trace-ID: " + trace_id)
	
	var body_dict = {
		"prompt": prompt,
		"type": type,
		"trace_id": trace_id
	}
	
	var body = JSON.stringify(body_dict)
	
	var result = _http_request.request(
		base_url + "/v1/generate",
		headers,
		HTTPClient.METHOD_POST,
		body
	)
	
	if result != OK:
		var error_msg = ""
		match result:
			ERR_INVALID_PARAMETER:
				error_msg = "发送请求失败：无效参数"
			ERR_CANT_CREATE:
				error_msg = "发送请求失败：无法创建连接"
			ERR_CANT_CONNECT:
				error_msg = "发送请求失败：无法连接到服务器"
			ERR_CONNECTION_ERROR:
				error_msg = "发送请求失败：连接错误"
			_:
				error_msg = "发送请求失败 (错误码: " + str(result) + ")"
		generation_error.emit(error_msg)
		push_error("[NeoRuntime] " + error_msg)
	else:
		print("[NeoRuntime] 请求已发送, trace_id: " + trace_id)

func _generate_trace_id() -> String:
	return "neogodot_" + Time.get_ticks_msec() + "_" + str(randi() % 10000)

func _on_health_check(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray, request_node: HTTPRequest) -> void:
	var old_connected = connected
	connected = (result == OK and response_code == 200)
	
	if connected:
		print("[NeoRuntime] 成功连接到运行时网关")
	else:
		print("[NeoRuntime] 连接失败 - 结果: ", result, " 响应码: ", response_code)
	
	request_node.queue_free()
	
	if old_connected != connected:
		connection_status_changed.emit(connected)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	print("[NeoRuntime] 收到响应 - 结果: ", result, " 响应码: ", response_code)
	
	if result == OK:
		if response_code == 200:
			var json = JSON.new()
			var body_str = body.get_string_from_utf8()
			var parse_result = json.parse(body_str)
			
			if parse_result == OK:
				if json.data.has("error"):
					generation_error.emit("服务器返回错误: " + str(json.data.error))
				else:
					generation_completed.emit(json.data)
			else:
				var error_msg = "解析服务器响应失败: " + json.get_error_message()
				generation_error.emit(error_msg)
				push_error("[NeoRuntime] " + error_msg)
		elif response_code == 400:
			generation_error.emit("请求参数错误，请检查您的输入内容")
		elif response_code == 401:
			generation_error.emit("认证失败，请检查 API 密钥是否正确")
		elif response_code == 403:
			generation_error.emit("权限不足，请检查您的访问权限")
		elif response_code == 404:
			generation_error.emit("接口不存在，请检查运行时 URL 是否正确")
		elif response_code == 429:
			generation_error.emit("请求过于频繁，请稍后再试")
		elif response_code >= 500:
			generation_error.emit("服务器内部错误 (代码 " + str(response_code) + ")，请稍后再试或联系管理员")
		else:
			generation_error.emit("请求失败，服务器返回代码 " + str(response_code))
	else:
		match result:
			HTTPRequest.RESULT_CONNECTION_ERROR:
				generation_error.emit("连接错误，请检查运行时服务是否已启动，以及网络连接是否正常")
			HTTPRequest.RESULT_TIMEOUT:
				generation_error.emit("请求超时，服务器响应时间过长，请稍后再试")
			HTTPRequest.RESULT_CANT_CONNECT:
				generation_error.emit("无法连接到服务器，请检查 URL 是否正确以及服务是否运行")
			HTTPRequest.RESULT_CANT_RESOLVE:
				generation_error.emit("无法解析服务器地址，请检查 URL 是否正确")
			_:
				generation_error.emit("请求失败 (错误码 " + str(result) + ")")
