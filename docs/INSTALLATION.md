# Installation Guide

## Prerequisites

Before installing NeoGodot, make sure your system meets the following requirements:

- **Godot 4.x** - Editor
- **Python 3.9+** - For Runtime Gateway
- **pip** - Python package manager

## 1. Get the Project

There are several ways to get NeoGodot:

### Option 1: Clone the Repository

```bash
git clone https://github.com/yourusername/neogodot.git
cd neogodot
```

### Option 2: Download ZIP

1. Visit the project homepage
2. Click "Code" > "Download ZIP"
3. Extract to your desired location

## 2. Install Runtime Gateway

Navigate to the runtime directory and install dependencies:

```bash
cd runtime
pip install -r requirements.txt
```

### Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Test the Server

```bash
python main.py
```

Visit http://localhost:8000/v1/health to verify the service is running.

## 3. Using the Plugin

### In an Existing Project:

1. Copy the `addons/neo_godot/` directory to your Godot project root
2. Open your project in Godot Editor
3. Go to Project > Project Settings > Plugins
4. Enable "NeoGodot AI Assistant"

### Creating a New Project:

1. Create a new project in Godot
2. Copy the `addons/` directory into it
3. Enable the plugin

## 4. Verify Installation

1. Ensure Runtime Gateway is running
2. Enable the plugin in Godot
3. Click the NeoGodot config button
4. Verify connection status is healthy

## Next Steps

After installation, check out the [Quick Start](../QuickStart.md) to begin!

Having issues? Check [Troubleshooting](../TROUBLESHOOTING.md).
