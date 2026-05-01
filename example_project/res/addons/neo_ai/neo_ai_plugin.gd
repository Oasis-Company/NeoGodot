@tool
extends EditorPlugin

const PLUGIN_NAME = "Neo AI"
const GATEWAY_URL = "http://127.0.0.1:7777/v1"

var dock: Control
var main_screen: Control
var gateway_client: Object
var task_state: Object
var neo_importer: Object
var undo_redo: EditorUndoRedoManager

var session_id: String = ""
var supervisor_mode: String = "guardian"

func _enter_tree():
    _init_services()
    _init_ui()
    _connect_signals()

func _exit_tree():
    _cleanup_ui()
    _cleanup_services()

func _init_services():
    gateway_client = preload("res://addons/neo_ai/network/gateway_client.gd").new()
    task_state = preload("res://addons/neo_ai/state/task_state.gd").new()
    neo_importer = preload("res://addons/neo_ai/import/neo_importer.gd").new()
    undo_redo = get_editor_interface().get_undo_redo()

func _init_ui():
    dock = preload("res://addons/neo_ai/ui/neo_ai_dock.tscn").instantiate()
    add_dock(dock)
    
    main_screen = preload("res://addons/neo_ai/ui/neo_ai_main.tscn").instantiate()
    main_screen.visible = false

func _connect_signals():
    dock.connect("generate_plan", Callable(self, "_on_generate_plan"))
    dock.connect("open_main_screen", Callable(self, "_on_open_main_screen"))
    dock.connect("clear_all", Callable(self, "_on_clear_all"))
    dock.connect("answer_question", Callable(self, "_on_answer_question"))
    dock.connect("locate_artifact", Callable(self, "_on_locate_artifact"))
    dock.connect("instantiate_artifact", Callable(self, "_on_instantiate_artifact"))
    
    main_screen.connect("close_main_screen", Callable(self, "_on_close_main_screen"))
    main_screen.connect("run_task", Callable(self, "_on_run_task"))
    main_screen.connect("approve_task", Callable(self, "_on_approve_task"))
    main_screen.connect("reject_task", Callable(self, "_on_reject_task"))
    
    gateway_client.connect("session_created", Callable(self, "_on_session_created"))
    gateway_client.connect("plan_compiled", Callable(self, "_on_plan_compiled"))
    gateway_client.connect("task_status_updated", Callable(self, "_on_task_status_updated"))
    gateway_client.connect("question_raised", Callable(self, "_on_question_raised"))
    gateway_client.connect("artifact_ready", Callable(self, "_on_artifact_ready"))
    gateway_client.connect("error", Callable(self, "_on_error"))
    
    neo_importer.connect("import_completed", Callable(self, "_on_import_completed"))
    neo_importer.connect("file_normalized", Callable(self, "_on_file_normalized"))

    gateway_client.create_session(ProjectSettings.globalize_path("res://"))

func _cleanup_ui():
    remove_dock(dock)
    dock.queue_free()
    if main_screen.visible:
        get_editor_interface().get_viewport().remove_child(main_screen)
    main_screen.queue_free()

func _cleanup_services():
    gateway_client = null
    task_state = null
    neo_importer = null

func _on_generate_plan(goal: String):
    gateway_client.compile_plan(goal)

func _on_open_main_screen():
    main_screen.visible = true
    get_editor_interface().get_viewport().add_child(main_screen)
    main_screen.rect_position = Vector2(0, 0)
    main_screen.rect_size = get_editor_interface().get_viewport().rect_size

func _on_close_main_screen():
    main_screen.visible = false
    get_editor_interface().get_viewport().remove_child(main_screen)

func _on_clear_all():
    session_id = ""
    task_state.set_session("", 10.0)
    _on_close_main_screen()

func _on_answer_question(question_id: String, answer: String):
    gateway_client.answer_question(question_id, answer)

func _on_locate_artifact(path: String):
    get_editor_interface().get_file_system_dock().navigate_to_path(path)

func _on_instantiate_artifact(path: String):
    _instantiate_resource(path)

func _on_run_task(task_id: String):
    gateway_client.execute_task(task_id)

func _on_approve_task(task_id: String):
    task_state.update_task_status(task_id, "ready")
    _on_run_task(task_id)

func _on_reject_task(task_id: String):
    task_state.update_task_status(task_id, "failed")

func _on_session_created(session_id: String):
    self.session_id = session_id
    task_state.set_session(session_id, 10.0)

func _on_plan_compiled(plan: Dictionary):
    task_state.update_plan(plan)
    _show_success_notification("Plan compiled successfully")

func _on_task_status_updated(task: Dictionary):
    task_id = str(task.task_id)
    status = task.status
    task_state.update_task_status(task_id, status)
    
    if status == "succeeded":
        if task.output_artifacts:
            for artifact in task.output_artifacts:
                if artifact.path:
                    task_state.add_artifact({
                        "path": artifact.path,
                        "type": _get_artifact_type(artifact.path),
                        "timestamp": DateTime.now().to_string()
                    })
            _on_artifact_ready([a.path for a in task.output_artifacts if a.path])

func _on_question_raised(question: Dictionary):
    task_state.add_question(question)

func _on_artifact_ready(artifacts: Array):
    neo_importer.import_assets(artifacts)

func _on_import_completed(success: bool, imported_paths: Array, errors: Array):
    if success:
        _reimport_godot_assets(imported_paths)
        _show_success_notification("Imported " + str(imported_paths.size()) + " assets")
    else:
        _show_error_notification("Import failed: " + str(errors))

func _on_file_normalized(path: String):
    print("Normalized: ", path)

func _on_error(message: String):
    _show_error_notification(message)

func _reimport_godot_assets(files: Array):
    var ei = get_editor_interface()
    var fs = ei.get_resource_filesystem()
    
    for path in files:
        fs.update_file(path)
    
    fs.reimport_files(files)
    
    if files.size() > 0:
        ei.get_file_system_dock().navigate_to_path(files[0])

func _instantiate_resource(path: String):
    var resource = load(path)
    if resource:
        var editor = get_editor_interface()
        var current_scene = editor.get_edited_scene()
        if current_scene:
            var instance = resource.instantiate()
            current_scene.add_child(instance)
            
            undo_redo.create_action("Instantiate AI Asset")
            undo_redo.add_do_method(current_scene, "add_child", instance)
            undo_redo.add_undo_method(instance, "queue_free")
            undo_redo.commit_action()
            
            _show_success_notification("Instantiated: " + path.get_file())
        else:
            _show_error_notification("No scene open")
    else:
        _show_error_notification("Failed to load: " + path)

func _get_artifact_type(path: String) -> String:
    ext = path.get_extension().to_lower()
    if ext in ["png", "jpg", "jpeg"]:
        return "Image"
    elif ext in ["wav", "ogg"]:
        return "Audio"
    elif ext in ["glb", "gltf"]:
        return "3D"
    elif ext in ["gd"]:
        return "Script"
    elif ext in ["tscn"]:
        return "Scene"
    else:
        return "Other"

func _show_success_notification(message: String):
    get_editor_interface().get_base_control().show_notification(message, 2)

func _show_error_notification(message: String):
    get_editor_interface().get_base_control().show_notification(message, 3)

func apply_change_set(change: Dictionary):
    undo_redo.create_action(change.name)
    
    for do_op in change.do_ops:
        undo_redo.add_do_method(do_op.target, do_op.method, do_op.args)
    
    for undo_op in change.undo_ops:
        undo_redo.add_undo_method(undo_op.target, undo_op.method, undo_op.args)
    
    undo_redo.commit_action()

func rollback_last_changes(count: int = 1):
    for _ in range(count):
        undo_redo.undo()

func rollback_session():
    while undo_redo.has_undo():
        undo_redo.undo()