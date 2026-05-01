@tool
extends RefCounted

const GATEWAY_URL = "http://127.0.0.1:7777/v1"

signal session_created(session_id: String)
signal plan_compiled(plan: Dictionary)
signal task_submitted(task_id: String)
signal task_status_updated(task: Dictionary)
signal event_received(event: Dictionary)
signal question_raised(question: Dictionary)
signal artifact_ready(artifacts: Array)
signal error(message: String)

var http: HTTPRequest
var websocket: WebSocketClient
var session_id: String = ""
var connected: bool = false

func _init():
    http = HTTPRequest.new()
    websocket = WebSocketClient.new()
    websocket.connect("connection_closed", Callable(self, "_on_ws_closed"))
    websocket.connect("connection_error", Callable(self, "_on_ws_error"))
    websocket.connect("data_received", Callable(self, "_on_ws_data"))

func create_session(project_path: String, budget_usd: float = 10.0) -> void:
    var body = JSON.stringify({
        "project_path": project_path,
        "mode": "default",
        "budget_usd": budget_usd,
        "selected_models": []
    })
    
    http.request_completed.connect(_on_session_created, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/sessions",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_session_created(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        session_id = str(data.session_id)
        emit_signal("session_created", session_id)
        _connect_websocket()
    else:
        emit_signal("error", "Failed to create session: " + str(code))

func compile_plan(goal: String, context: Dictionary = {}) -> void:
    if not session_id:
        emit_signal("error", "No active session")
        return
    
    var body = JSON.stringify({
        "session_id": session_id,
        "goal": goal,
        "context": context,
        "constraints": {},
        "existing_artifacts": []
    })
    
    http.request_completed.connect(_on_plan_compiled, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/plan",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_plan_compiled(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        emit_signal("plan_compiled", data)
    else:
        emit_signal("error", "Plan compilation failed: " + str(code))

func submit_task(task_spec: Dictionary) -> void:
    if not session_id:
        emit_signal("error", "No active session")
        return
    
    task_spec["session_id"] = session_id
    var body = JSON.stringify(task_spec)
    
    http.request_completed.connect(_on_task_submitted, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/tasks",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_task_submitted(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        emit_signal("task_submitted", str(data.task_id))
    else:
        emit_signal("error", "Task submission failed: " + str(code))

func execute_task(task_id: String) -> void:
    if not session_id:
        emit_signal("error", "No active session")
        return
    
    http.request_completed.connect(_on_task_executed, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/tasks/" + task_id + "/execute",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST
    )

func _on_task_executed(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        emit_signal("task_status_updated", data)
    else:
        emit_signal("error", "Task execution failed: " + str(code))

func get_task_status(task_id: String) -> void:
    http.request_completed.connect(_on_task_status, CONNECT_ONE_SHOT)
    http.request(GATEWAY_URL + "/tasks/" + task_id)

func _on_task_status(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        emit_signal("task_status_updated", data)
    else:
        emit_signal("error", "Failed to get task status: " + str(code))

func answer_question(question_id: String, answer: String, user_comment: String = "") -> void:
    if not session_id:
        emit_signal("error", "No active session")
        return
    
    var body = JSON.stringify({
        "question_id": question_id,
        "answer": answer,
        "user_comment": user_comment
    })
    
    http.request_completed.connect(_on_question_answered, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/questions/" + question_id + "/answer",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_question_answered(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code != 200:
        emit_signal("error", "Failed to answer question: " + str(code))

func import_assets(files: Array, resource_type: String = "other") -> void:
    if not session_id:
        emit_signal("error", "No active session")
        return
    
    var body = JSON.stringify({
        "session_id": session_id,
        "files": files,
        "resource_type": resource_type,
        "target_directory": "res://ai_generated/",
        "metadata": {}
    })
    
    http.request_completed.connect(_on_import_completed, CONNECT_ONE_SHOT)
    http.request(
        GATEWAY_URL + "/import",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_import_completed(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        if data.success:
            emit_signal("artifact_ready", data.imported_paths)
        else:
            emit_signal("error", "Import failed: " + str(data.errors))
    else:
        emit_signal("error", "Import request failed: " + str(code))

func _connect_websocket() -> void:
    websocket.connect_to_url("ws://127.0.0.1:7777/v1/events/ws/" + session_id)

func _on_ws_closed(was_clean: bool, code: int, reason: String) -> void:
    connected = false
    if code != 1000:
        emit_signal("error", "WebSocket closed unexpectedly: " + reason)

func _on_ws_error(err: WebSocketClient.ConnectionError) -> void:
    emit_signal("error", "WebSocket error: " + str(err))

func _on_ws_data() -> void:
    while websocket.get_ready_state() == WebSocketClient.STATE_OPEN:
        var data = websocket.get_packet()
        if data.size() > 0:
            var event = JSON.parse_string(data.get_string_from_utf8())
            emit_signal("event_received", event)
            
            match event.event_type:
                "question.raised":
                    emit_signal("question_raised", event.payload)
                "artifact.ready":
                    emit_signal("artifact_ready", event.payload.imported_paths)
                "task.completed":
                    emit_signal("task_status_updated", {"task_id": event.payload.task_id, "status": "succeeded"})
                "task.failed":
                    emit_signal("task_status_updated", {"task_id": event.payload.task_id, "status": "failed", "error": event.payload.error})