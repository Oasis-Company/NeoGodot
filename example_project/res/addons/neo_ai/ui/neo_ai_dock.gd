@tool
extends PanelContainer

signal generate_plan(goal: String)
signal open_main_screen()
signal clear_all()
signal answer_question(question_id: String, answer: String)
signal locate_artifact(path: String)
signal instantiate_artifact(path: String)
signal rollback_artifact(path: String)

var gateway_client = preload("res://addons/neo_ai/network/gateway_client.gd").new()
var task_state = preload("res://addons/neo_ai/state/task_state.gd").new()

var current_goal: String = ""
var supervisor_mode: String = "guardian"

func _ready():
    _connect_signals()
    _init_ui()

func _connect_signals():
    $VBoxContainer/ActionsSection/GenerateButton.connect("pressed", Callable(self, "_on_generate"))
    $VBoxContainer/ActionsSection/MainScreenButton.connect("pressed", Callable(self, "_on_open_main_screen"))
    $VBoxContainer/ActionsSection/ClearButton.connect("pressed", Callable(self, "_on_clear"))
    $VBoxContainer/Header/ModeSelector.connect("pressed", Callable(self, "_on_mode_changed"))
    
    gateway_client.connect("session_created", Callable(self, "_on_session_created"))
    gateway_client.connect("plan_compiled", Callable(self, "_on_plan_compiled"))
    gateway_client.connect("question_raised", Callable(self, "_on_question_raised"))
    gateway_client.connect("artifact_ready", Callable(self, "_on_artifact_ready"))
    gateway_client.connect("error", Callable(self, "_on_error"))
    
    task_state.connect("budget_updated", Callable(self, "_on_budget_updated"))
    task_state.connect("question_added", Callable(self, "_on_question_added"))
    task_state.connect("artifact_added", Callable(self, "_on_artifact_added"))
    
    gateway_client.create_session(ProjectSettings.globalize_path("res://"))

func _init_ui():
    _update_budget_display(0.0, 10.0)

func _on_generate():
    var goal_dialog = InputDialog.new()
    goal_dialog.title = "Enter Goal"
    goal_dialog.dialog_text = "What would you like to create?"
    goal_dialog.add_button("Generate", true)
    goal_dialog.add_button("Cancel", false)
    goal_dialog.connect("confirmed", Callable(self, "_on_goal_confirmed"))
    add_child(goal_dialog)
    goal_dialog.popup_centered()

func _on_goal_confirmed():
    var dialog = get_node_or_null("InputDialog")
    if dialog:
        current_goal = dialog.get_input_text().strip_edges()
        if current_goal:
            $VBoxContainer/StatusSection/GoalDisplay.text = "Goal: " + current_goal
            gateway_client.compile_plan(current_goal)
        dialog.queue_free()

func _on_open_main_screen():
    emit_signal("open_main_screen")

func _on_clear():
    current_goal = ""
    $VBoxContainer/StatusSection/GoalDisplay.text = "Goal: Not set"
    _clear_questions()
    _clear_artifacts()
    task_state.set_session("", 10.0)
    _update_budget_display(0.0, 10.0)

func _on_mode_changed():
    var modes = ["Shadow", "Guardian", "Collaborative"]
    var idx = modes.find($VBoxContainer/Header/ModeSelector.text)
    idx = (idx + 1) % modes.size()
    supervisor_mode = modes[idx].to_lower()
    $VBoxContainer/Header/ModeSelector.text = modes[idx]

func _on_session_created(session_id: String):
    task_state.set_session(session_id, 10.0)

func _on_plan_compiled(plan: Dictionary):
    task_state.update_plan(plan)
    _update_phase("plan")
    _update_budget_display(task_state.total_cost_usd, task_state.budget_limit_usd)

    if plan.questions and plan.questions.size() > 0:
        for q in plan.questions:
            task_state.add_question({
                "question_id": str(OS.get_ticks_msec()),
                "title": q,
                "type": "information_gap",
                "choices": ["Yes", "No", "Skip"],
                "answered": false
            })

func _on_question_raised(question: Dictionary):
    task_state.add_question(question)

func _on_question_added(question: Dictionary):
    _add_question_ui(question)

func _on_artifact_ready(artifacts: Array):
    for path in artifacts:
        task_state.add_artifact({
            "path": path,
            "type": _get_artifact_type(path),
            "timestamp": DateTime.now().to_string()
        })

func _on_artifact_added(artifact: Dictionary):
    _add_artifact_ui(artifact)

func _on_budget_updated(spent: float, limit: float):
    _update_budget_display(spent, limit)

func _on_error(message: String):
    print("Neo AI Error: ", message)
    var dialog = AcceptDialog.new()
    dialog.title = "Error"
    dialog.dialog_text = message
    add_child(dialog)
    dialog.popup_centered()

func _add_question_ui(question: Dictionary):
    var question_box = VBoxContainer.new()
    question_box.custom_minimum_size = Vector2(0, 80)
    
    var title_label = Label.new()
    title_label.text = question.title
    title_label.autowrap = true
    question_box.add_child(title_label)
    
    var choices_hbox = HBoxContainer.new()
    for choice in question.choices:
        var btn = Button.new()
        btn.text = choice
        btn.connect("pressed", Callable(self, "_on_answer_question", question.question_id, choice))
        choices_hbox.add_child(btn)
    question_box.add_child(choices_hbox)
    
    $VBoxContainer/QuestionsSection/QuestionsScroll/QuestionsVBox.add_child(question_box)
    _update_question_count()

func _on_answer_question(question_id: String, answer: String):
    task_state.answer_question(question_id, answer)
    emit_signal("answer_question", question_id, answer)
    
    _clear_questions()
    for q in task_state.get_pending_questions():
        _add_question_ui(q)

func _clear_questions():
    var vbox = $VBoxContainer/QuestionsSection/QuestionsScroll/QuestionsVBox
    for child in vbox.get_children():
        child.queue_free()
    _update_question_count()

func _update_question_count():
    count = task_state.get_pending_questions().size()
    $VBoxContainer/QuestionsSection/QuestionsLabel.text = "Pending Questions (" + str(count) + ")"

func _add_artifact_ui(artifact: Dictionary):
    var artifact_box = HBoxContainer.new()
    artifact_box.custom_minimum_size = Vector2(0, 30)
    
    var path_label = Label.new()
    path_label.text = artifact.path.get_file()
    path_label.size_flags_horizontal = 3
    artifact_box.add_child(path_label)
    
    var type_label = Label.new()
    type_label.text = artifact.type
    type_label.custom_minimum_size = Vector2(60, 0)
    artifact_box.add_child(type_label)
    
    var locate_btn = Button.new()
    locate_btn.text = "Locate"
    locate_btn.connect("pressed", Callable(self, "_on_locate_artifact", artifact.path))
    artifact_box.add_child(locate_btn)
    
    var instantiate_btn = Button.new()
    instantiate_btn.text = "Instantiate"
    instantiate_btn.connect("pressed", Callable(self, "_on_instantiate_artifact", artifact.path))
    artifact_box.add_child(instantiate_btn)
    
    $VBoxContainer/ArtifactsSection/ArtifactsScroll/ArtifactsVBox.add_child(artifact_box)

func _clear_artifacts():
    var vbox = $VBoxContainer/ArtifactsSection/ArtifactsScroll/ArtifactsVBox
    for child in vbox.get_children():
        child.queue_free()

func _on_locate_artifact(path: String):
    emit_signal("locate_artifact", path)
    get_editor_interface().get_file_system_dock().navigate_to_path(path)

func _on_instantiate_artifact(path: String):
    emit_signal("instantiate_artifact", path)

func _update_budget_display(spent: float, limit: float):
    percentage = (spent / limit) * 100
    $VBoxContainer/BudgetSection/BudgetBar.value = percentage
    $VBoxContainer/BudgetSection/BudgetText.text = "$" + str(spent) + " / $" + str(limit)
    
    if percentage > 90:
        $VBoxContainer/BudgetSection/BudgetBar.theme = preload("res://addons/neo_ai/ui/neo_ai_dock.tscn").get_sub_resource(10)
    elif percentage > 70:
        $VBoxContainer/BudgetSection/BudgetBar.theme = preload("res://addons/neo_ai/ui/neo_ai_dock.tscn").get_sub_resource(9)
    else:
        $VBoxContainer/BudgetSection/BudgetBar.theme = preload("res://addons/neo_ai/ui/neo_ai_dock.tscn").get_sub_resource(8)

func _update_phase(phase: String):
    phases = ["plan", "code", "assets", "import"]
    buttons = [$VBoxContainer/StatusSection/PhaseBar/PhasePlan,
               $VBoxContainer/StatusSection/PhaseBar/PhaseCode,
               $VBoxContainer/StatusSection/PhaseBar/PhaseAssets,
               $VBoxContainer/StatusSection/PhaseBar/PhaseImport]
    
    for i in range(phases.size()):
        buttons[i].pressed = (phases[i] == phase)

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