@tool
extends PanelContainer

signal close_main_screen()
signal run_task(task_id: String)
signal approve_task(task_id: String)
signal reject_task(task_id: String)

var gateway_client = preload("res://addons/neo_ai/network/gateway_client.gd").new()
var task_state = preload("res://addons/neo_ai/state/task_state.gd").new()

var selected_task_id: String = ""

func _ready():
    _connect_signals()
    _update_plan_tree()

func _connect_signals():
    $HSplitContainer/LeftPanel/PlanHeader/Toolbar/RegenerateBtn.connect("pressed", Callable(self, "_on_regenerate"))
    $HSplitContainer/LeftPanel/PlanHeader/Toolbar/RunBtn.connect("pressed", Callable(self, "_on_run_selected"))
    $HSplitContainer/LeftPanel/PlanHeader/Toolbar/PauseBtn.connect("pressed", Callable(self, "_on_pause"))
    $HSplitContainer/LeftPanel/PlanHeader/Toolbar/ExportBtn.connect("pressed", Callable(self, "_on_export"))
    $HSplitContainer/LeftPanel/PlanTree.connect("item_selected", Callable(self, "_on_task_selected"))
    $HSplitContainer/RightPanel/Actions/ApproveBtn.connect("pressed", Callable(self, "_on_approve"))
    $HSplitContainer/RightPanel/Actions/RejectBtn.connect("pressed", Callable(self, "_on_reject"))
    $HSplitContainer/RightPanel/Actions/CloseBtn.connect("pressed", Callable(self, "_on_close"))

    task_state.connect("plan_updated", Callable(self, "_on_plan_updated"))
    task_state.connect("task_updated", Callable(self, "_on_task_updated"))

func _update_plan_tree():
    var tree = $HSplitContainer/LeftPanel/PlanTree
    tree.clear()
    
    var root = tree.create_item()
    root.set_text(0, "Task DAG")
    
    tasks = task_state.tasks
    if not tasks:
        root.set_text(0, "No plan available")
        return
    
    task_items = {}
    
    for task_id in tasks:
        task = tasks[task_id]
        item = tree.create_item(root)
        item.set_text(0, task.description)
        item.set_text(1, task.status)
        item.set_text(2, task.priority)
        item.set_text(3, task.risk_level)
        item.set_metadata(0, task_id)
        task_items[task_id] = item
        
        if task.status == "succeeded":
            item.set_icon(0, _get_status_icon("succeeded"))
        elif task.status == "failed":
            item.set_icon(0, _get_status_icon("failed"))
        elif task.status == "running":
            item.set_icon(0, _get_status_icon("running"))
        elif task.status == "waiting_approval":
            item.set_icon(0, _get_status_icon("waiting_approval"))
    
    for task_id in tasks:
        task = tasks[task_id]
        for dep_id in task.depends_on:
            if dep_id in task_items and task_id in task_items:
                task_items[task_id].add_child(task_items[dep_id])

func _get_status_icon(status: String) -> Texture2D:
    var icon_cache = {
        "succeeded": get_editor_interface().get_base_control().get_icon("Check", "EditorIcons"),
        "failed": get_editor_interface().get_base_control().get_icon("X", "EditorIcons"),
        "running": get_editor_interface().get_base_control().get_icon("Loader", "EditorIcons"),
        "waiting_approval": get_editor_interface().get_base_control().get_icon("AlertTriangle", "EditorIcons")
    }
    return icon_cache.get(status, null)

func _on_task_selected():
    var tree = $HSplitContainer/LeftPanel/PlanTree
    var selected = tree.get_selected()
    if selected and selected != tree.get_root():
        selected_task_id = selected.get_metadata(0)
        _update_task_details(selected_task_id)
    else:
        selected_task_id = ""
        _clear_task_details()

func _update_task_details(task_id: String):
    task = task_state.get_task(task_id)
    if not task:
        return
    
    $HSplitContainer/RightPanel/TaskInfo/TaskIDLabel.text = "Task ID: " + task.task_id
    $HSplitContainer/RightPanel/TaskInfo/TaskKindLabel.text = "Kind: " + task.kind
    $HSplitContainer/RightPanel/TaskInfo/TaskStatusLabel.text = "Status: " + task.status
    $HSplitContainer/RightPanel/TaskInfo/TaskPriorityLabel.text = "Priority: " + task.priority
    $HSplitContainer/RightPanel/TaskInfo/TaskRiskLabel.text = "Risk: " + task.risk_level
    $HSplitContainer/RightPanel/TaskInfo/TaskCostLabel.text = "Est. Cost: $" + str(task.estimated_cost_usd)
    
    criteria_text = "\n".join(task.success_criteria) if task.success_criteria else "None"
    $HSplitContainer/RightPanel/SuccessCriteria/CriteriaList.text = criteria_text
    
    logs_text = "\n".join(task.logs) if task.logs else "No logs yet"
    $HSplitContainer/RightPanel/ExecutionLogs/LogsText.text = logs_text
    
    needs_approval = task_state.needs_approval(task)
    $HSplitContainer/RightPanel/Actions/ApproveBtn.visible = needs_approval and task.status == "waiting_approval"
    $HSplitContainer/RightPanel/Actions/RejectBtn.visible = needs_approval and task.status == "waiting_approval"

func _clear_task_details():
    $HSplitContainer/RightPanel/TaskInfo/TaskIDLabel.text = "Task ID: "
    $HSplitContainer/RightPanel/TaskInfo/TaskKindLabel.text = "Kind: "
    $HSplitContainer/RightPanel/TaskInfo/TaskStatusLabel.text = "Status: "
    $HSplitContainer/RightPanel/TaskInfo/TaskPriorityLabel.text = "Priority: "
    $HSplitContainer/RightPanel/TaskInfo/TaskRiskLabel.text = "Risk: "
    $HSplitContainer/RightPanel/TaskInfo/TaskCostLabel.text = "Est. Cost: $"
    $HSplitContainer/RightPanel/SuccessCriteria/CriteriaList.text = ""
    $HSplitContainer/RightPanel/ExecutionLogs/LogsText.text = ""
    $HSplitContainer/RightPanel/Actions/ApproveBtn.visible = false
    $HSplitContainer/RightPanel/Actions/RejectBtn.visible = false

func _on_regenerate():
    if task_state.current_plan.goal:
        gateway_client.compile_plan(task_state.current_plan.goal)

func _on_run_selected():
    if selected_task_id:
        task = task_state.get_task(selected_task_id)
        if task and task.status == "draft":
            if task_state.needs_approval(task):
                task_state.update_task_status(selected_task_id, "waiting_approval")
                _show_approval_dialog(selected_task_id)
            else:
                _execute_task(selected_task_id)

func _execute_task(task_id: String):
    task_state.update_task_status(task_id, "running")
    gateway_client.execute_task(task_id)

func _on_pause():
    pass

func _on_export():
    var plan = task_state.current_plan
    var json_str = JSON.stringify(plan)
    var file = FileAccess.new()
    if file.open("res://plan_export.json", FileAccess.WRITE) == OK:
        file.store_string(json_str)
        file.close()
        var dialog = AcceptDialog.new()
        dialog.title = "Export Successful"
        dialog.dialog_text = "Plan exported to plan_export.json"
        add_child(dialog)
        dialog.popup_centered()

func _on_approve():
    if selected_task_id:
        task_state.update_task_status(selected_task_id, "ready")
        _execute_task(selected_task_id)

func _on_reject():
    if selected_task_id:
        task_state.update_task_status(selected_task_id, "failed")
        _update_plan_tree()

func _on_close():
    emit_signal("close_main_screen")

func _on_plan_updated(plan: Dictionary):
    _update_plan_tree()

func _on_task_updated(task_id: String, status: String):
    _update_plan_tree()
    if selected_task_id == task_id:
        _update_task_details(task_id)

func _show_approval_dialog(task_id: String):
    var task = task_state.get_task(task_id)
    if not task:
        return
    
    var dialog = ConfirmationDialog.new()
    dialog.title = "Approval Required"
    dialog.dialog_text = "This task requires approval before execution:\n\n" + \
                        "Task: " + task.description + "\n" + \
                        "Risk Level: " + task.risk_level + "\n" + \
                        "Estimated Cost: $" + str(task.estimated_cost_usd) + "\n\n" + \
                        "Do you want to approve this task?"
    
    dialog.add_button("Approve", true)
    dialog.add_button("Reject", false)
    dialog.connect("confirmed", Callable(self, "_on_approval_confirmed", task_id))
    dialog.connect("cancelled", Callable(self, "_on_approval_rejected", task_id))
    
    add_child(dialog)
    dialog.popup_centered()

func _on_approval_confirmed(task_id: String):
    _on_approve()

func _on_approval_rejected(task_id: String):
    _on_reject()