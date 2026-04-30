# Supervisor Protocol Rules

## Task DAG Requirements
- All tasks must be compiled to structured DAG before execution
- Each task must specify: kind, priority, risk_level, depends_on
- Tasks with risk_level >= "high" require explicit approval

## Approval Workflow
- Overwriting existing resources: MUST APPROVE
- Modifying .tscn scene files: MUST APPROVE
- Running shell commands: MUST APPROVE
- High token consumption (>500K): MUST APPROVE
- Creating new assets: auto-saved to staging, no approval needed

## Risk Classification
- **Low**: Read-only operations, search, information retrieval
- **Medium**: Creating new assets, generating code drafts
- **High**: Modifying existing files, running tests
- **Critical**: Deploying builds, publishing, external API calls

## Human-in-the-Loop
- System must ask clarifying questions when information is missing
- Default actions must be explicitly stated when asking questions
- Users must be able to see what will be affected before approving
