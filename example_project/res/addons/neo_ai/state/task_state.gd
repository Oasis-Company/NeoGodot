@tool
extends RefCounted

enum TaskStatus {
    DRAFT = "draft",
    WAITING_APPROVAL = "waiting_approval",
    READY = "ready",
    RUNNING = "running",
    WAITING_USER = "waiting_user",
    SUCCEEDED = "succeeded",
    FAILED = "failed",
    RETRYING = "retrying",
    ESCALATED = "escalated",
    IMPORTED = "imported",
    VERIFIED = "verified"
}

enum TaskPriority {
    P0 = "P0",
    P1 = "P1",
    P2 = "P2"
}

enum TaskRiskLevel {
    LOW = "low",
    MEDIUM = "medium",
    HIGH = "high",
    CRITICAL = "critical"
}

var tasks: Dictionary = {}
var session_id: String = ""
var current_plan: Dictionary = {}
var pending_questions: Array = []
var recent_artifacts: Array = []
var total_cost_usd: float = 0.0
var budget_limit_usd: float = 10.0

signal task_updated(task_id: String, status: String)
signal plan_updated(plan: Dictionary)
signal question_added(question: Dictionary)
signal artifact_added(artifact: Dictionary)
signal budget_updated(spent: float, limit: float)

func set_session(session_id: String, budget: float = 10.0) -> void:
    self.session_id = session_id
    self.budget_limit_usd = budget
    self.total_cost_usd = 0.0
    tasks.clear()
    pending_questions.clear()
    recent_artifacts.clear()

func update_plan(plan: Dictionary) -> void:
    current_plan = plan
    
    for task_data in plan.tasks:
        var task_id = str(task_data.task_id)
        tasks[task_id] = {
            "task_id": task_id,
            "kind": task_data.kind,
            "description": task_data.description,
            "status": TaskStatus.DRAFT,
            "priority": task_data.priority or TaskPriority.P1,
            "risk_level": task_data.risk_level or TaskRiskLevel.MEDIUM,
            "depends_on": [str(d) for d in task_data.dependencies] if task_data.dependencies else [],
            "estimated_cost_usd": task_data.estimated_cost_usd or 0.0,
            "success_criteria": task_data.success_criteria or [],
            "output_artifacts": [],
            "error_message": "",
            "logs": []
        }
    
    emit_signal("plan_updated", plan)

func update_task_status(task_id: String, status: String) -> void:
    if task_id in tasks:
        tasks[task_id]["status"] = status
        emit_signal("task_updated", task_id, status)

func add_task_log(task_id: String, log_message: String) -> void:
    if task_id in tasks:
        tasks[task_id]["logs"].append(log_message)

func add_artifact(artifact: Dictionary) -> void:
    recent_artifacts.append(artifact)
    if recent_artifacts.size() > 20:
        recent_artifacts.pop_front()
    emit_signal("artifact_added", artifact)

func add_question(question: Dictionary) -> void:
    pending_questions.append(question)
    emit_signal("question_added", question)

func answer_question(question_id: String, answer: String) -> void:
    for i in range(pending_questions.size()):
        if str(pending_questions[i].question_id) == question_id:
            pending_questions[i]["answered"] = true
            pending_questions[i]["answer"] = answer
            break

func get_pending_questions() -> Array:
    return [q for q in pending_questions if not q.get("answered", false)]

func update_cost(cost_usd: float) -> void:
    total_cost_usd += cost_usd
    emit_signal("budget_updated", total_cost_usd, budget_limit_usd)

func get_task(task_id: String) -> Dictionary:
    return tasks.get(task_id, {})

func get_tasks_by_status(status: String) -> Array:
    return [t for t in tasks.values() if t["status"] == status]

func get_ready_tasks() -> Array:
    ready = []
    for task in tasks.values():
        if task["status"] != TaskStatus.DRAFT:
            continue
        all_deps_ready = true
        for dep_id in task["depends_on"]:
            dep = tasks.get(dep_id)
            if not dep or dep["status"] != TaskStatus.SUCCEEDED:
                all_deps_ready = false
                break
        if all_deps_ready:
            ready.append(task)
    return ready

func get_budget_percentage() -> float:
    if budget_limit_usd <= 0:
        return 0.0
    return (total_cost_usd / budget_limit_usd) * 100.0

func needs_approval(task: Dictionary) -> bool:
    risk = task.get("risk_level", TaskRiskLevel.LOW)
    return risk in [TaskRiskLevel.HIGH, TaskRiskLevel.CRITICAL]

func get_plan_summary() -> Dictionary:
    summary = {
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks.values() if t["status"] == TaskStatus.SUCCEEDED]),
        "pending_tasks": len([t for t in tasks.values() if t["status"] == TaskStatus.DRAFT]),
        "waiting_approval": len([t for t in tasks.values() if t["status"] == TaskStatus.WAITING_APPROVAL]),
        "estimated_total_cost": sum([t["estimated_cost_usd"] for t in tasks.values()]),
        "pending_questions": len(self.get_pending_questions())
    }
    return summary