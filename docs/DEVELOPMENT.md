# Development Guide

This guide provides instructions for developers who want to contribute to NeoGodot.

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/neogodot.git
cd neogodot
```

### 2. Branch Workflow

We use Git Flow:

```bash
git checkout -b feature/my-feature
```

## Project Structure Overview

```
neogodot/
├── addons/neo_godot/  # Godot plugin
│   ├── plugin.gd      # Plugin entry point
│   ├── ui/            # UI components
│   ├── autoload/      # Autoload singletons
│   └── ...
├── runtime/           # Python service
│   ├── main.py        # FastAPI entry point
│   └── ...
└── docs/              # Documentation
```

## Godot Plugin Development

### Extending the Plugin

- Plugin uses GDScript 4.x
- Follow Godot coding style
- Add new UI components in `ui/`

### Adding New Commands

Create new command classes in `commands/` that inherit from `NeuralCommand`.

## Runtime Gateway Development

### Running Development Server

```bash
cd runtime
pip install -r requirements.txt
python main.py
```

### Adding New Endpoints

1. Create new route file in `routes/`
2. Register in `main.py`
3. Add API documentation to `docs/API_REFERENCE.md`

## Testing

### Godot Plugin Testing

Manual testing in Godot editor.

### Runtime Tests

```bash
python -m unittest discover
```

## Commit Guidelines

### Pull Request Process

1. Create branch from `main`
2. Develop and test
3. Create Pull Request
4. Wait for code review
5. Merge

### Commit Messages

Use clear commit messages:

- `feat: add new feature`
- `fix: fix some bug`
- `docs: update documentation`
- `refactor: refactor code`

## Getting Help

Questions? Check [CONTRIBUTING.md](../CONTRIBUTING.md) or create an Issue.
