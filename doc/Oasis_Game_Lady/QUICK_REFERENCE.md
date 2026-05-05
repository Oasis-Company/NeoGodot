# NeoGodot AI Quick Reference

## Quick Start

```bash
# 1. Start Gateway
cd "Oasis Prepare/runtime/neo_runtime_gateway"
python main.py

# 2. Open Godot
# - Import example_project/project.godot
# - Enable Neo AI plugin in Project Settings > Plugins
# - View > Neo AI to open panel
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check service status |
| POST | `/v1/sessions` | Create session |
| GET | `/v1/sessions` | List sessions |
| POST | `/v1/plan` | Compile plan |
| POST | `/v1/tasks` | Create task |
| POST | `/v1/tasks/{id}/execute` | Execute task |
| WS | `/v1/events/ws/{session_id}` | Event stream |
| POST | `/v1/questions/{id}/answer` | Answer question |
| POST | `/v1/import` | Import assets |

---

## Common Commands

```bash
# Check Gateway status
curl http://localhost:7777/health

# Create session
python -c "
import requests
resp = requests.post('http://localhost:7777/v1/sessions', json={
    'project_path': 'res://test/',
    'mode': 'default',
    'budget_usd': 10.0
})
print(resp.json())
"
```

---

## Plugin Structure

```
addons/neo_ai/
├── plugin.cfg              # Plugin config
├── neo_ai_plugin.gd       # Main entry
├── ui/
│   ├── neo_ai_dock.tscn   # Dock scene
│   ├── neo_ai_dock.gd     # Dock logic
│   ├── neo_ai_main.tscn   # Main screen
│   └── neo_ai_main.gd     # Main screen logic
├── network/
│   └── gateway_client.gd  # API client
├── state/
│   └── task_state.gd      # State management
└── import/
    └── neo_importer.gd    # Asset importer
```

---

## Configuration

### Environment (.env)
```env
QWEN_API_KEY=your_key
SERVER_PORT=7777
OLLAMA_ENABLED=true
```

### Gateway URL (gateway_client.gd)
```gdscript
const GATEWAY_URL = "http://127.0.0.1:7777/v1"
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Gateway not starting | Check port 7777, restart |
| Plugin not connecting | Start Gateway first |
| API errors | Verify API key |
| UI not showing | Enable plugin in settings |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| View > Neo AI | Open AI dock |
| Ctrl+Shift+G | Generate plan |
| Ctrl+Z | Undo |

---

## Support

- Documentation: `doc/Oasis_Game_Lady/`
- Gateway: `http://localhost:7777`
- Swagger: `http://localhost:7777/docs`