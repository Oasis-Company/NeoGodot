@tool
extends EditorPlugin

const NEO_GATEWAY_URL = "http://127.0.0.1:7777/v1"

var dock: Control
var http: HTTPRequest
var session_id: String = ""

func _enter_tree() -> void:
    dock = preload("res://addons/neo_ai/neo_ai_dock.tscn").instantiate()
    http = HTTPRequest.new()
    add_child(http)
    add_dock(dock)
    
    dock.connect("request_plan", Callable(self, "_on_request_plan"))
    dock.connect("import_assets", Callable(self, "_on_import_assets"))
    
    _create_session()

func _exit_tree() -> void:
    remove_dock(dock)
    dock.queue_free()
    http.queue_free()

func _create_session() -> void:
    var body = JSON.stringify({
        "project_path": ProjectSettings.globalize_path("res://"),
        "mode": "default",
        "budget_usd": 10.0,
        "selected_models": []
    })
    
    http.request_completed.connect(_on_session_created, CONNECT_ONE_SHOT)
    http.request(
        NEO_GATEWAY_URL + "/sessions",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_session_created(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        session_id = str(data.session_id)
        dock.call("set_session_id", session_id)
    else:
        push_warning("Failed to create session: " + str(code))

func _on_request_plan(goal: String) -> void:
    if not session_id:
        push_warning("No active session")
        return
    
    var body = JSON.stringify({
        "session_id": session_id,
        "goal": goal,
        "context": "",
        "constraints": {},
        "existing_artifacts": []
    })
    
    http.request_completed.connect(_on_plan_completed, CONNECT_ONE_SHOT)
    http.request(
        NEO_GATEWAY_URL + "/plan",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_plan_completed(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        dock.call("render_plan", data)
    else:
        push_warning("Plan request failed: " + str(code))

func _on_import_assets(files: PackedStringArray) -> void:
    if not session_id:
        push_warning("No active session")
        return
    
    var body = JSON.stringify({
        "session_id": session_id,
        "files": files,
        "resource_type": "other",
        "target_directory": "res://ai_generated/",
        "metadata": {}
    })
    
    http.request_completed.connect(_on_import_completed, CONNECT_ONE_SHOT)
    http.request(
        NEO_GATEWAY_URL + "/import",
        ["Content-Type: application/json"],
        HTTPClient.METHOD_POST,
        body
    )

func _on_import_completed(result: int, code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
    if code == 200:
        var data = JSON.parse_string(body.get_string_from_utf8())
        if data.success:
            _reimport_assets(data.imported_paths)
        dock.call("show_import_result", data)
    else:
        push_warning("Import failed: " + str(code))

func _reimport_assets(files: Array) -> void:
    var ei = get_editor_interface()
    var fs = ei.get_resource_filesystem()
    
    for path in files:
        fs.update_file(path)
    
    fs.reimport_files(files)
    
    if files.size() > 0:
        ei.get_file_system_dock().navigate_to_path(files[0])