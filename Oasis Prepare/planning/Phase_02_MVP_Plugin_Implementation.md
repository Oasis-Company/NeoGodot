# Phase 02: MVP Plugin Implementation

## Objective
Implement the complete NeoGodot AI Editor Plugin with Dock panel, Main Screen, plan compilation workflow, asset import pipeline, and manual approval system. Connect to the Neo Runtime Gateway established in Phase 01.

## Duration
Estimated 4-5 weeks

## Key Deliverables
1. NeoGodot AI Dock Panel (persistent status, budget, questions)
2. NeoGodot AI Main Screen (full-screen task orchestration)
3. Plan API integration with Gateway
4. Asset import pipeline with normalization
5. Manual approval workflow with Supervisor
6. EditorUndoRedoManager integration

---

## 1. Godot Editor Plugin Architecture

### 1.1 Plugin Structure
```
addons/neo_ai/
├── plugin.cfg              # Plugin configuration
├── neo_ai_plugin.gd       # Main EditorPlugin entry
├── ui/
│   ├── neo_ai_dock.tscn   # Dock panel scene
│   ├── neo_ai_dock.gd     # Dock logic
│   ├── neo_ai_main.tscn   # Main Screen scene
│   └── neo_ai_main.gd     # Main Screen logic
├── network/
│   └── gateway_client.gd  # Gateway API client
├── import/
│   └── neo_importer.gd    # Asset importer
└── state/
    └── task_state.gd      # Task state management
```

### 1.2 Dock Panel Requirements

**Top Section - Status Bar:**
- Current goal display
- Mode indicator (Guardian/Collaborative/Shadow)
- Budget bar ($ spent / $ limit)
- Phase progress (Plan → Code → Assets → Import)

**Middle Section - Current Decisions:**
- Primary model selection (Qwen)
- Code subtask model
- Vision analysis model (optional)

**Action Section - Questions:**
- Pending questions list
- Multiple choice answers
- Default action indication
- Impact summary

**Bottom Section - Recent Artifacts:**
- List of recently generated assets
- Quick actions: Locate, Instantiate, Rollback

### 1.3 Main Screen Requirements

**Left Panel - Plan Tree:**
- Visual task DAG display
- Dependency visualization
- Task status indicators (Pending/Approval/Running/Succeeded/Failed)
- Priority badges (P0/P1/P2)

**Right Panel - Task Details:**
- Selected task info
- Success criteria
- Risk level
- Estimated cost
- Execution logs

**Toolbar:**
- Regenerate plan
- Run selected tasks
- Pause/resume
- Export plan as JSON

---

## 2. Plan API Integration

### 2.1 Gateway Client Implementation

**Required Methods:**
```gdscript
class GatewayClient:
    func create_session(project_path: String, budget_usd: float) -> String:
    func compile_plan(goal: String, context: Dictionary) -> Dictionary:
    func submit_task(task_spec: Dictionary) -> String:
    func get_task_status(task_id: String) -> Dictionary:
    func stream_events(session_id: String) -> void:
    func answer_question(question_id: String, answer: String) -> void:
```

### 2.2 Plan Compiler Workflow

```
User Goal → Gateway → Qwen API → Task DAG → Validation → Display
```

**Task DAG Requirements:**
- Each task has unique `task_id`
- `depends_on` array for dependencies
- `risk_level` (low/medium/high/critical)
- `success_criteria` array
- `estimated_cost_usd`
- `output_path` specification

### 2.3 Event Streaming

**Event Types:**
- `task.started` - Task execution began
- `task.completed` - Task finished successfully
- `task.failed` - Task failed
- `question.raised` - Supervisor needs input
- `artifact.ready` - Asset ready for import
- `budget.warning` - Approaching budget limit

---

## 3. Asset Import Pipeline

### 3.1 Supported Asset Types

| Type | Format | Import Handler |
|------|--------|----------------|
| 2D Image | PNG, JPG | Native texture import |
| Audio | WAV, OGG | Native audio import |
| 3D Model | GLB, GLTF | GLTFDocumentExtension |
| Script | GDScript (.gd) | Direct file write |
| Scene | TSCN | Scene import |
| Configuration | TRES | Direct file write |

### 3.2 Import Workflow

```
Generated Asset → Staging → Normalization → Write → Reimport → Verify
```

**Normalization Steps:**
1. Validate file format
2. Apply naming convention (`{asset_type}_{name}_{hash}.ext`)
3. Add metadata manifest (`.neoasset.json`)
4. Generate fingerprint hash

**Godot Integration:**
```gdscript
func reimport_generated_assets(files: PackedStringArray) -> void:
    var fs = get_editor_interface().get_resource_filesystem()
    for path in files:
        fs.update_file(path)
    fs.reimport_files(files)
    get_editor_interface().get_file_system_dock().navigate_to_path(files[0])
```

### 3.3 Manifest Format

```json
{
  "artifact_id": "art_xxx",
  "task_id": "task_xxx",
  "session_id": "sess_xxx",
  "generated_at": "ISO8601",
  "original_prompt": "...",
  "metadata": {
    "purpose": "primary_button",
    "style_ref": "neo_style_v2"
  },
  "fingerprint": "sha256_hash"
}
```

---

## 4. Manual Approval Workflow

### 4.1 Approval Triggers

| Trigger Type | Condition | Default Action |
|--------------|-----------|----------------|
| Information Gap | Missing style/format/naming rules | Use defaults, ask later |
| Architecture Fork | Multiple implementation paths | Show comparison, require selection |
| Destructive Change | Overwrite existing resource | Require approval |
| Cost Jump | Exceeds budget threshold | Offer downgrade options |
| Validation Failed | Import/test failed | Request clarification or rollback |

### 4.2 Approval UI Flow

```
Risk Detected → Show Approval Dialog → User Action → Proceed/Rollback
```

**Approval Dialog Content:**
- Action description
- Risk level indicator
- Affected files/resources
- Cost estimate
- Available options
- Default action if no response

### 4.3 Supervisor Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| Shadow | Suggest only, no auto-execution | New users, high-risk projects |
| Guardian | Low-risk auto, high-risk approve | Standard team workflow |
| Collaborative | Confirm at phase boundaries | Architecture design |

---

## 5. State Management & Undo/Redo

### 5.1 Task State Store

**Required Fields:**
- `task_id`, `session_id`, `status`
- `created_at`, `started_at`, `completed_at`
- `output_artifacts` array
- `error_message` (if failed)
- `user_answers` dictionary

### 5.2 Undo/Redo Integration

**Change-Set Pattern:**
```gdscript
func apply_change_set(change: Dictionary) -> void:
    var undo_redo = get_editor_interface().get_undo_redo()
    undo_redo.create_action(change.name)
    # Apply changes
    undo_redo.add_do_method(target, method, args)
    # Revert changes
    undo_redo.add_undo_method(target, method, revert_args)
    undo_redo.commit_action()
```

### 5.3 Rollback Capability

**Rollback Types:**
- Single artifact rollback
- Batch rollback (last N changes)
- Full session rollback

---

## 6. Success Criteria

### Plugin UI
- [x] Dock panel functional with all sections
- [x] Main Screen with plan tree visualization
- [x] Responsive design matching Godot theme

### API Integration
- [x] All Gateway endpoints connected
- [x] Real-time event streaming working
- [x] Error handling and reconnection

### Import Pipeline
- [x] All supported asset types import correctly
- [x] File system navigation works
- [x] Metadata manifests generated

### Approval Workflow
- [x] All trigger types detected
- [x] Approval dialog displayed correctly
- [x] Three supervisor modes functional

### State Management
- [x] Task state persistence
- [x] Undo/redo integration
- [x] Rollback functionality

---

## 7. Security & Compliance

### 7.1 Input Validation
- Sanitize all user inputs
- Validate task specifications against schema
- Rate limiting per session

### 7.2 Audit Logs
- Log all API calls
- Record approval decisions
- Track artifact generation

---

## 8. Next Phase (Beta)
After completing Phase 02:
1. Parallel Agent scheduling
2. Advanced asset normalization
3. Artifact Registry
4. Automated testing and failure recovery