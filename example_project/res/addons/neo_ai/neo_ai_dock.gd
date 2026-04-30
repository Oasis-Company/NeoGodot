@tool
extends PanelContainer

signal request_plan(goal: String)
signal import_assets(files: PackedStringArray)

var _session_id: String = ""

func _ready() -> void:
    $VBoxContainer/GoalPanel/SubmitButton.connect("pressed", Callable(self, "_on_submit"))
    $VBoxContainer/ActionsPanel/ImportButton.connect("pressed", Callable(self, "_on_import"))
    $VBoxContainer/ActionsPanel/ClearButton.connect("pressed", Callable(self, "_on_clear"))

func _on_submit() -> void:
    var goal = $VBoxContainer/GoalPanel/GoalInput.text.strip_edges()
    if goal:
        emit_signal("request_plan", goal)
        $VBoxContainer/StatusPanel/PlanOutput.text = "Generating plan..."

func _on_import() -> void:
    emit_signal("import_assets", PackedStringArray())

func _on_clear() -> void:
    $VBoxContainer/GoalPanel/GoalInput.text = ""
    $VBoxContainer/StatusPanel/PlanOutput.text = ""

func set_session_id(session_id: String) -> void:
    _session_id = session_id
    $VBoxContainer/StatusPanel/PlanOutput.text = "Session ID: " + session_id + "\n\nReady to generate plan."

func render_plan(plan: Dictionary) -> void:
    var output = "Plan ID: " + str(plan.plan_id) + "\n"
    output += "Goal: " + plan.goal + "\n\n"
    output += "Tasks:\n"
    
    for i, task in enumerate(plan.tasks):
        output += str(i + 1) + ". [" + task.kind + "] " + task.description + "\n"
        if task.risk_level:
            output += "   Risk: " + task.risk_level + "\n"
        if task.estimated_cost_usd:
            output += "   Est. Cost: $" + str(task.estimated_cost_usd) + "\n"
        if task.dependencies:
            output += "   Depends on: " + str([str(d) for d in task.dependencies]) + "\n"
        output += "\n"
    
    if plan.risk_points:
        output += "Risk Points:\n"
        for point in plan.risk_points:
            output += "- " + point + "\n"
    
    if plan.questions:
        output += "\nQuestions:\n"
        for question in plan.questions:
            output += "- " + question + "\n"
    
    $VBoxContainer/StatusPanel/PlanOutput.text = output

func show_import_result(result: Dictionary) -> void:
    if result.success:
        $VBoxContainer/StatusPanel/PlanOutput.text += "\n\nImport successful!\n"
        $VBoxContainer/StatusPanel/PlanOutput.text += "Imported: " + str(result.imported_paths.size()) + " files"
    else:
        $VBoxContainer/StatusPanel/PlanOutput.text += "\n\nImport failed:\n"
        for error in result.errors:
            $VBoxContainer/StatusPanel/PlanOutput.text += "- " + error + "\n"