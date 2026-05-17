# AI Documentation Hub

Welcome to the AI Documentation Hub - a comprehensive guide designed specifically for AI systems working with NeoGodot.

## Overview

This directory contains structured documentation optimized for AI agents to understand NeoGodot's architecture, capabilities, and workflows.

## Quick Navigation

- [Architecture Overview](ARCHITECTURE.md) - Core system architecture and design principles
- [Codebase Structure](CODEBASE_STRUCTURE.md) - Directory structure and key files
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Plugin Development](PLUGIN_DEVELOPMENT.md) - How to develop NeoGodot plugins
- [Task Workflows](TASK_WORKFLOWS.md) - Common task patterns and recipes
- [Context Templates](CONTEXT_TEMPLATES.md) - Ready-to-use prompt templates

## Key Concepts

### Plugin-First Principle
All AI-related UI and workflows should be implemented as EditorPlugins first. Only move to modules/GDExtension when profiling proves plugins can't meet performance requirements.

### Asset Location
AI-generated assets must go to `res://ai_generated/` directory with subdirectories:
- `ui/` - UI textures and sprites
- `sfx/` - Sound effects
- `scripts/` - Generated GDScript files
- `scenes/` - Generated .tscn scenes

### Traceability
Every AI action must have a `trace_id`. All decisions must be logged with: policy_id, decision_reason, critic_scores. Artifacts must be indexed with session_id and task_id.

### Undo/Redo Compliance
All modifications must use `EditorUndoRedoManager`. Batch operations must be wrapped in a single change-set.

## Getting Started

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
2. Review [CODEBASE_STRUCTURE.md](CODEBASE_STRUCTURE.md) to learn the codebase layout
3. Check [TASK_WORKFLOWS.md](TASK_WORKFLOWS.md) for common patterns
4. Use [CONTEXT_TEMPLATES.md](CONTEXT_TEMPLATES.md) for quick task setup
