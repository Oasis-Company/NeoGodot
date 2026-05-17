# Codebase Structure

## Directory Layout

```
neogodot/
├── addons/neo_godot/              # NeoGodot Editor Plugin
│   ├── plugin.gd                  # Plugin main script
│   ├── plugin.cfg                 # Plugin configuration
│   ├── autoload/                  # Autoload singletons
│   │   └── neo_godot_global.gd    # Global state manager
│   ├── ui/                        # UI components
│   │   ├── main_panel.gd          # Main dock panel
│   │   ├── config_dialog.gd       # Configuration dialog
│   │   └── chat_view.gd           # Chat interface
│   ├── commands/                  # Command system
│   │   ├── command.gd             # Base command class
│   │   ├── generate_script.gd     # Script generation
│   │   ├── generate_scene.gd      # Scene generation
│   │   └── ...
│   ├── services/                  # Service layer
│   │   ├── gateway_client.gd      # Gateway communication
│   │   └── undo_manager.gd        # Undo/Redo wrapper
│   └── config/                    # Configuration
│       └── config.gd              # Config management
│
├── runtime/                       # Runtime Gateway
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Configuration
│   ├── logger.py                  # Logging setup
│   ├── api/                       # API endpoints
│   │   ├── health.py              # Health check
│   │   ├── chat.py                # Chat endpoints
│   │   └── tasks.py               # Task management
│   ├── providers/                 # AI providers
│   │   ├── base.py                # Provider base class
│   │   ├── openai.py              # OpenAI integration
│   │   └── anthropic.py           # Anthropic integration
│   ├── models/                    # Pydantic models
│   │   ├── requests.py            # Request schemas
│   │   └── responses.py           # Response schemas
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Python dependencies
│   ├── start.bat                  # Windows starter
│   └── start.sh                   # Linux/macOS starter
│
├── docs/                          # Documentation
│   ├── ai/                        # AI-specific docs (you are here)
│   ├── INSTALLATION.md            # Installation guide
│   ├── API_REFERENCE.md           # API reference
│   ├── DEVELOPMENT.md             # Development guide
│   └── ...
│
├── assets/                        # Project assets
│   └── neogodotlogo.png           # Project logo
│
├── ai_generated/                  # AI-generated assets (staging)
│   ├── ui/                        # Generated UI assets
│   ├── sfx/                       # Generated sound effects
│   ├── scripts/                   # Generated GDScripts
│   └── scenes/                    # Generated scenes
│
├── core/                          # Godot core (minimal changes)
├── scene/                         # Godot scene system
├── editor/                        # Godot editor
├── modules/                       # Godot modules
├── platform/                      # Platform-specific code
└── ... (standard Godot structure)
```

## Key Files to Reference

### Plugin Entry Points
- `addons/neo_godot/plugin.gd` - Plugin initialization
- `addons/neo_godot/autoload/neo_godot_global.gd` - Global state

### Gateway Entry Points
- `runtime/main.py` - FastAPI app initialization
- `runtime/api/` - All endpoint definitions

### Configuration
- `runtime/.env.example` - Environment variables template
- `addons/neo_godot/config/config.gd` - Plugin config schema

## Godot Core Modifications

NeoGodot maintains minimal changes to Godot core. Any core modifications should be:
- Well-documented
- Kept as small as possible
- Isolated when feasible

See Git history for core changes.
