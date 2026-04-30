from uuid import UUID
from typing import Dict, Optional, List
from schemas.plan import Plan, PlanCreate, PlanTask
from schemas.task import TaskSpec, TaskKind, TaskPriority, TaskRiskLevel

class PlanService:
    def __init__(self):
        self.plans: Dict[UUID, Plan] = {}

    async def create_plan(self, create_data: PlanCreate) -> Plan:
        plan = Plan(
            session_id=create_data.session_id,
            goal=create_data.goal,
            context=create_data.context
        )
        await self._compile_plan(plan)
        self.plans[plan.plan_id] = plan
        return plan

    async def _compile_plan(self, plan: Plan):
        tasks = []
        
        default_tasks = [
            {
                "kind": TaskKind.RETRIEVE_SEARCH.value,
                "description": "搜索相关资源和上下文",
                "risk_level": TaskRiskLevel.LOW.value,
                "cost": 0.05
            },
            {
                "kind": TaskKind.CRITIC_GROUNDING.value,
                "description": "验证证据充分性",
                "risk_level": TaskRiskLevel.LOW.value,
                "cost": 0.03,
                "depends_on": [0]
            },
            {
                "kind": TaskKind.SCRIPT_GENERATE.value,
                "description": "生成GDScript代码",
                "risk_level": TaskRiskLevel.MEDIUM.value,
                "cost": 0.15,
                "depends_on": [1]
            },
            {
                "kind": TaskKind.CODE_TEST.value,
                "description": "运行测试验证",
                "risk_level": TaskRiskLevel.LOW.value,
                "cost": 0.02,
                "depends_on": [2]
            }
        ]

        task_ids = []
        for i, task_def in enumerate(default_tasks):
            task = PlanTask(
                task_id=UUID(int=i + 1),
                kind=task_def["kind"],
                description=task_def["description"],
                risk_level=task_def["risk_level"],
                estimated_cost_usd=task_def["cost"]
            )
            if "depends_on" in task_def:
                task.dependencies = [task_ids[j] for j in task_def["depends_on"]]
            task_ids.append(task.task_id)
            tasks.append(task)
        
        plan.tasks = tasks
        plan.risk_points = ["需要用户确认最终实现方案"]
        plan.questions = ["是否需要特定的代码风格或命名规范？"]

    async def get_plan(self, plan_id: UUID) -> Optional[Plan]:
        return self.plans.get(plan_id)

    async def update_plan(self, plan_id: UUID, **kwargs) -> Optional[Plan]:
        plan = self.plans.get(plan_id)
        if plan:
            for key, value in kwargs.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            plan.updated_at = plan.__fields__["updated_at"].default_factory()
        return plan

    async def delete_plan(self, plan_id: UUID) -> bool:
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False