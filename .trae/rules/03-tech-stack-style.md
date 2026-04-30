# 技术栈与开发风格约束

## 代码风格
* 编写任何文档、代码注释或逻辑解释时，严禁使用比喻句。
* 语言必须保持直接、准确且具有工程严谨性。

## UI/UX 规范
* Web 端组件优先采用 **CGS Stack** (Cloudflare, GitHub, Supabase)[cite: 2]。
* UI 设计必须遵循 **Swiss Style**（瑞士风格），使用黑白配色方案，追求极致的简约质感[cite: 2]。

## 并行 Agent 职责
* **Planner**: 仅负责计划编译与风险标注[cite: 1]。
* **Solver**: 负责具体的代码实现[cite: 1]。
* **Critic**: 负责对产出进行安全审查与证据核对[cite: 1]。
