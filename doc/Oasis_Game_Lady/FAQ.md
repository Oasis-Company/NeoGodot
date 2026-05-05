# NeoGodot AI FAQ

## General

### Q: What is NeoGodot AI?
A: NeoGodot AI is an AI-powered game development toolkit integrated into the Godot engine. It provides AI-assisted asset generation, code generation, and task planning capabilities.

### Q: How does it work?
A: The system consists of:
1. **Neo Runtime Gateway** - Backend service that handles AI API calls
2. **Godot Plugin** - Editor integration with UI panels
3. **Supervisor** - Decision controller for approval workflows

### Q: What AI models are supported?
A: 
- Primary: Qwen API (code generation + reasoning)
- Fallback: Ollama `qwen3-coder:30b` (local)
- Vision: Optional `qwen3-vl:30b`

---

## Installation

### Q: How do I install the system?
A: See `DEPLOYMENT_GUIDE.md` for step-by-step instructions.

### Q: What are the system requirements?
A: 
- Python 3.11+
- Godot 4.2+
- Internet connection (for cloud APIs)
- Port 7777 available

### Q: Do I need an API key?
A: Yes, you need a Qwen API key from Alibaba Cloud. Get one at: https://dashscope.console.aliyun.com/

---

## Usage

### Q: How do I generate a plan?
A: 
1. Open the AI dock (View > Neo AI)
2. Click "Generate Plan"
3. Enter your goal (e.g., "Create a 2D platformer")
4. Click "Generate"

### Q: What are the different supervisor modes?
A:
- **Shadow**: Suggest only, no auto-execution
- **Guardian**: Low-risk auto, high-risk require approval
- **Collaborative**: Confirm at phase boundaries

### Q: How do I approve a task?
A: 
1. Tasks requiring approval show "Waiting Approval" status
2. Click the task in the Main Screen
3. Click "Approve" or "Reject"

---

## Technical

### Q: Where are generated assets stored?
A: `res://ai_generated/` with subdirectories for `ui/`, `sfx/`, `scripts/`, `scenes/`

### Q: Can I use local models?
A: Yes, enable Ollama in `.env` and run `ollama run qwen3-coder:30b`

### Q: How do I customize the Gateway URL?
A: Edit `gateway_client.gd` and change `GATEWAY_URL` constant

### Q: Is there an undo feature?
A: Yes, all plugin operations use Godot's `EditorUndoRedoManager`

---

## Troubleshooting

### Q: Gateway won't start
A: Check:
- Port 7777 is not in use
- Python dependencies are installed
- `.env` file exists with valid configuration

### Q: Plugin won't connect to Gateway
A: Check:
- Gateway is running (`python main.py`)
- Gateway URL is correct in `gateway_client.gd`
- No firewall blocking port 7777

### Q: Assets not importing
A: Check:
- File format is supported (PNG, WAV, GLB, GD, TSCN)
- Output path is valid
- Godot's file system is refreshed

### Q: Budget exceeded error
A: 
- Reduce task complexity
- Increase budget in session settings
- Review and cancel expensive tasks

---

## Development

### Q: How do I modify the plugin?
A: Edit files in `example_project/res/addons/neo_ai/`

### Q: How do I add new API endpoints?
A: Add routes in `runtime/neo_runtime_gateway/routes/`

### Q: Where is the documentation?
A: All documentation is in `doc/Oasis_Game_Lady/`

---

## Security

### Q: Are API keys stored securely?
A: Yes, API keys are stored in `.env` file which is excluded from Git

### Q: Can I restrict access to the Gateway?
A: Yes, change `SERVER_HOST` in `.env` to `127.0.0.1` for local access only

### Q: Are my assets private?
A: Yes, all assets are stored locally in your project directory

---

## Support

### Q: Where can I get help?
A: 
- Check documentation in `doc/Oasis_Game_Lady/`
- Review the example project
- Contact the NeoGodot team

### Q: How do I report bugs?
A: Create issues in the GitHub repository

---

**Last Updated:** May 2026