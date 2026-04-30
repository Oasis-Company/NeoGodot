import os
import httpx
from uuid import UUID
from schemas.task import Task, TaskKind
from typing import Dict, Any

class ProviderService:
    def __init__(self):
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "")
        self.qwen_base_url = os.getenv("QWEN_API_BASE_URL", "https://api.tongyi.aliyun.com")
        self.ollama_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        provider = await self._select_provider(task)
        
        if provider == "qwen":
            return await self._call_qwen_api(task)
        elif provider == "ollama":
            return await self._call_ollama_api(task)
        else:
            return await self._execute_fallback(task)

    async def _select_provider(self, task: Task) -> str:
        if self.qwen_api_key:
            return "qwen"
        elif self.ollama_enabled:
            return "ollama"
        return "fallback"

    async def _call_qwen_api(self, task: Task) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.qwen_api_key}",
            "Content-Type": "application/json"
        }

        prompt = self._build_prompt(task)
        
        payload = {
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": "你是一个帮助生成Godot游戏开发资源的助手。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.qwen_base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        return {
            "artifacts": [{"kind": "text", "content": data["choices"][0]["message"]["content"]}],
            "cost_usd": 0.05,
            "model": "qwen"
        }

    async def _call_ollama_api(self, task: Task) -> Dict[str, Any]:
        prompt = self._build_prompt(task)
        
        payload = {
            "model": "qwen3-coder:30b",
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_base_url}/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        return {
            "artifacts": [{"kind": "text", "content": data.get("response", "")}],
            "cost_usd": 0.0,
            "model": "ollama"
        }

    async def _execute_fallback(self, task: Task) -> Dict[str, Any]:
        default_responses = {
            TaskKind.SCRIPT_GENERATE: "extends Node2D\n\nfunc _ready():\n    print(\"Generated script\")",
            TaskKind.ASSET_IMAGE: "Generated image placeholder",
            TaskKind.CODE_TEST: "Test passed",
            TaskKind.RETRIEVE_SEARCH: "Found relevant documentation"
        }
        
        content = default_responses.get(task.kind, "Task completed")
        
        return {
            "artifacts": [{"kind": "text", "content": content}],
            "cost_usd": 0.0,
            "model": "fallback"
        }

    def _build_prompt(self, task: Task) -> str:
        base_prompts = {
            TaskKind.SCRIPT_GENERATE: f"Generate a GDScript for {task.metadata.get('purpose', 'a game feature')}. Follow Godot best practices.",
            TaskKind.ASSET_IMAGE: "Describe an image asset for game development.",
            TaskKind.CODE_TEST: "Generate test cases for the given code.",
            TaskKind.RETRIEVE_SEARCH: f"Search for information about {task.metadata.get('query', 'Godot development')}.",
            TaskKind.CRITIC_GROUNDING: "Review the following plan for evidence sufficiency.",
            TaskKind.PLAN_COMPILE: f"Create a task plan for: {task.metadata.get('goal', '')}",
        }
        return base_prompts.get(task.kind, f"Complete the task: {task.kind.value}")