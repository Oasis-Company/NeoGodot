<p align="center">
  <img src="assets/neogodotlogo.png" width="400" alt="NeoGodot logo">
</p>

# NeoGodot

> AI-enhanced game engine based on Godot Engine, making game development smarter.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Godot Version](https://img.shields.io/badge/Godot-4.x-blue)](https://godotengine.org/)
[![Python Version](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

---

## ✨ Features

### 🎮 Godot Native Features
- Complete Godot Engine capabilities preserved
- Unified 2D and 3D development interface
- Cross-platform export support
- GDScript, C#, C++ multi-language support

### 🤖 AI Enhanced Features
- **AI Assistant Integration** - Built-in AI assistant panel
- **Smart Code Generation** - Generate GDScript via natural language
- **Scene and Resource Generation** - Auto-create game assets
- **Undo/Redo Support** - All AI actions are undoable
- **Configuration Management** - Flexible custom configuration

### 🔌 Runtime Gateway
- FastAPI backend service
- RESTful API and WebSocket support
- Multi-AI provider integration
- Health check and monitoring

---

## 🚀 Quick Start

### Prerequisites

- Godot 4.x editor
- Python 3.9+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/neogodot.git
cd neogodot

# 2. Install and start Runtime Gateway
cd runtime
pip install -r requirements.txt
cp .env.example .env
# Edit .env to configure API Key
python main.py
```

### Using the Plugin

1. Copy `addons/neo_godot/` to your Godot project
2. Enable the plugin in Godot Editor
3. Click the NeoGodot config button to connect Gateway
4. Start using the AI assistant!

Detailed guide: [Quick Start](QuickStart.md).

---

## 📖 Documentation

- [📚 Documentation Center](docs/README.md)
- [🚀 Quick Start](QuickStart.md)
- [📦 Installation Guide](docs/INSTALLATION.md)
- [🏗️ Architecture Overview](ARCHITECTURE.md)
- [📋 API Reference](docs/API_REFERENCE.md)
- [🤖 AI Documentation](docs/ai/README.md) - Documentation specifically for AI systems
- [💡 FAQ](FAQ.md)
- [🔧 Troubleshooting](TROUBLESHOOTING.md)

---

## 📂 Project Structure

```
neogodot/
├── addons/neo_godot/  # Godot plugin
│   ├── plugin.gd      # Plugin main script
│   ├── autoload/      # Autoloads
│   ├── ui/            # UI components
│   ├── commands/        # Command system
│   └── ...
├── runtime/           # Python service
│   ├── main.py        # Entry point
│   └── ...
├── assets/            # Assets
├── docs/              # Documentation
├── docs/ai/          # AI-specific documentation
└── ai_generated/      # AI-generated assets
```

---

## 🤝 Contributing

We welcome all forms of contribution! Please see:

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Code of conduct

### Quick contribution flow:

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'feat: add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open source under the [MIT License](LICENSE.txt).

---

## 🙏 Acknowledgments

- Thanks to the [Godot Engine](https://godotengine.org/) community
- Thanks to all contributors

---

<p align="center">
  <b>Made with 💖 for game developers</b><br>
  NeoGodot - Making game development smarter 🚀
</p>
