# Architecture Overview

## System Architecture

NeoGodot is built as a modified version of Godot Engine with AI-enhanced capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                        NeoGodot Editor                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              EditorPlugin: NeoGodot                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │   UI Panel   │  │  Commands    │  │  Undo/Redo   │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Gateway (FastAPI)                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  API Endpoints   │  │  AI Providers    │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Godot Editor Plugin
- **Location**: `addons/neo_godot/`
- **Technology**: GDScript 4.x
- **Features**:
  - AI assistant dock panel
  - Command execution system
  - Undo/Redo integration
  - Configuration management

### 2. Runtime Gateway
- **Location**: `runtime/`
- **Technology**: Python 3.9+, FastAPI
- **Features**:
  - RESTful API endpoints
  - WebSocket real-time communication
  - Multi-provider AI integration
  - Health monitoring

### 3. Core Godot Engine
- **Location**: Root directories (`core/`, `scene/`, `editor/`, etc.)
- **Modifications**: Minimal changes to Godot core
- **Principle**: Keep core changes minimal, prefer plugins

## Design Principles

### Plugin-First
All new features should be implemented as EditorPlugins first. Only move to core/modules when:
- Profiling shows plugin can't meet performance requirements
- Deep engine integration is absolutely necessary

### Traceability
Every AI action must have:
- `trace_id`: Unique identifier for the action
- `policy_id`: Policy that governed the decision
- `decision_reason`: Why the decision was made
- `critic_scores`: Evaluation metrics
- `session_id` + `task_id`: Indexing for artifacts

### Undo/Redo Compliance
- All modifications use `EditorUndoRedoManager`
- Batch operations wrapped in single change-set
- AI changes indistinguishable from manual changes

## Data Flow

1. User interacts with NeoGodot UI panel
2. Plugin sends request to Runtime Gateway
3. Gateway processes request (calls AI provider if needed)
4. Response returns to plugin
5. Plugin executes actions via EditorInterface
6. All changes recorded in UndoRedo system
