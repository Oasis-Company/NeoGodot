# NeoGodot AI Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying and running the NeoGodot AI system on a new machine.

---

## 1. System Requirements

### 1.1 Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 5 GB free | 20 GB free |
| GPU | Optional | NVIDIA GPU with 12GB+ VRAM (for local models) |

### 1.2 Software Requirements
| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Gateway backend |
| Godot Engine | 4.2+ | Game engine |
| Git | Latest | Version control |

### 1.3 Network Requirements
- Internet connection for cloud API access
- Port 7777 open for Gateway service

---

## 2. Quick Start Checklist

```
✅ Install Python 3.11+
✅ Clone repository
✅ Install dependencies
✅ Configure environment
✅ Start Gateway service
✅ Open Godot project
✅ Enable Neo AI plugin
✅ Test connection
```

---

## 3. Installation Steps

### 3.1 Clone Repository

```bash
git clone https://github.com/Oasis-Company/NeoGodot.git
cd NeoGodot
```

### 3.2 Install Python Dependencies

```bash
cd "Oasis Prepare/runtime/neo_runtime_gateway"
pip install fastapi uvicorn httpx pydantic python-dotenv websockets
```

### 3.3 Configure Environment

```bash
cd "Oasis Prepare/runtime/neo_runtime_gateway"
copy .env.example .env
```

Edit `.env` file:
```env
# Qwen API Configuration
QWEN_API_KEY=your_qwen_api_key_here
QWEN_API_BASE_URL=https://api.tongyi.aliyun.com

# Ollama Configuration (for fallback)
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434/api

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=7777
DEBUG=false

# Security
SECRET_KEY=your_secret_key_here
```

### 3.4 Start Gateway Service

```bash
cd "Oasis Prepare/runtime/neo_runtime_gateway"
python main.py
```

Expected output:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7777
```

### 3.5 Verify Gateway

```bash
# Test health endpoint
curl http://localhost:7777/health
# Expected: {"status":"healthy","service":"neo_runtime_gateway"}
```

### 3.6 Open Godot Project

1. Launch Godot Engine
2. Click "Import"
3. Select `example_project/project.godot`
4. Wait for project to load

### 3.7 Enable Plugin

1. Go to `Project > Project Settings`
2. Click `Plugins` tab
3. Find "Neo AI" in the list
4. Click the checkbox to enable

### 3.8 Open AI Panel

1. Go to `View > Neo AI`
2. The AI dock should appear on the right
3. If connection is successful, you'll see "Ready" status

---

## 4. Configuration Reference

### 4.1 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| QWEN_API_KEY | Qwen API authentication key | - | Yes |
| QWEN_API_BASE_URL | Qwen API endpoint | `https://api.tongyi.aliyun.com` | No |
| OLLAMA_ENABLED | Enable local Ollama fallback | `true` | No |
| OLLAMA_BASE_URL | Ollama local endpoint | `http://localhost:11434/api` | No |
| SERVER_HOST | Gateway listening address | `0.0.0.0` | No |
| SERVER_PORT | Gateway listening port | `7777` | No |
| DEBUG | Enable debug mode | `false` | No |
| SECRET_KEY | Security secret for sessions | - | Yes |

### 4.2 Plugin Configuration

The plugin is configured via `addons/neo_ai/plugin.cfg`:

```ini
[plugin]
name="Neo AI"
description="AI-powered asset generation for NeoGodot"
author="NeoGodot Team"
version="0.1.0"
script="neo_ai_plugin.gd"
```

### 4.3 Gateway URL

The plugin connects to Gateway at `http://127.0.0.1:7777`. To change this, modify `gateway_client.gd`:

```gdscript
const GATEWAY_URL = "http://your-server-ip:7777/v1"
```

---

## 5. Troubleshooting Guide

### 5.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Gateway not starting | Port 7777 in use | Change port in `.env` or kill conflicting process |
| Plugin not connecting | Gateway not running | Start Gateway first |
| API errors | Invalid API key | Check QWEN_API_KEY in `.env` |
| Import errors | Missing dependencies | Run `pip install -r requirements.txt` |
| UI not showing | Plugin not enabled | Enable in Project Settings > Plugins |

### 5.2 Log Locations

- **Gateway logs**: Console output (stdout)
- **Godot logs**: `Editor > Editor Settings > Network > Logging`
- **Plugin logs**: Godot console (bottom panel)

### 5.3 Debug Commands

```bash
# Check Gateway status
curl http://localhost:7777/health

# Check running processes on port 7777
netstat -ano | findstr :7777

# Kill process on port 7777 (Windows)
taskkill /F /PID <PID>
```

---

## 6. Development Workflow

### 6.1 Starting Development

```bash
# Terminal 1: Start Gateway
cd "Oasis Prepare/runtime/neo_runtime_gateway"
python main.py

# Terminal 2: Open Godot
godot --editor example_project/project.godot
```

### 6.2 Making Changes

1. **Gateway**: Edit files in `runtime/neo_runtime_gateway/`
2. **Plugin**: Edit files in `example_project/res/addons/neo_ai/`
3. **Restart Gateway** after backend changes
4. **Reload plugin** (disable/enable) after frontend changes

### 6.3 Testing Changes

```bash
# Run API tests
python test_api.py

# Test specific endpoint
curl -X POST http://localhost:7777/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"project_path":"res://test/","mode":"default","budget_usd":10.0}'
```

---

## 7. Backup & Migration

### 7.1 Backup Important Files

```bash
# Backup configuration
cp .env .env.backup

# Backup session data (if using persistent storage)
cp -r data/ data_backup/

# Backup plugin settings
cp addons/neo_ai/plugin.cfg addons/neo_ai/plugin.cfg.backup
```

### 7.2 Migrate to New Machine

1. Clone repository on new machine
2. Copy `.env` file
3. Install dependencies
4. Start Gateway
5. Open project in Godot

---

## 8. Security Best Practices

1. **Never commit API keys** - Use `.env` file (already in `.gitignore`)
2. **Restrict network access** - Bind Gateway to localhost in production
3. **Use HTTPS** - Enable SSL in production environments
4. **Limit permissions** - Run Gateway with minimal privileges
5. **Monitor logs** - Regularly check for suspicious activity

---

## 9. Support & Contact

### 9.1 Documentation

- Architecture: `doc/Oasis_Game_Lady/ARCHITECTURE_OVERVIEW.md`
- API Reference: `doc/Oasis_Game_Lady/API_REFERENCE.md`
- User Guide: `doc/Oasis_Game_Lady/USER_GUIDE.md`

### 9.2 Support Channels

- GitHub Issues: Report bugs and feature requests
- Discord/Slack: Team communication
- Email: support@neogodot.dev

---

## 10. Quick Reference Sheet

### Commands

| Command | Purpose |
|---------|---------|
| `python main.py` | Start Gateway |
| `curl http://localhost:7777/health` | Check Gateway status |
| `git pull` | Update repository |
| `pip install <package>` | Install Python package |

### URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:7777` | Gateway API |
| `http://localhost:7777/docs` | Swagger documentation |

### File Paths

| Path | Purpose |
|------|---------|
| `runtime/neo_runtime_gateway/` | Gateway backend |
| `example_project/res/addons/neo_ai/` | Godot plugin |
| `doc/Oasis_Game_Lady/` | Documentation |

---

**Document Version:** 1.0  
**Last Updated:** May 2026  
**Author:** NeoGodot Team