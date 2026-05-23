"""Ollama local model provider adapter for NeoGodot."""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, Optional
import aiohttp
import logging

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """Ollama local model provider adapter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1")
        self.timeout = config.get("timeout", 120)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama API (non-streaming)
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
            
        Returns:
            Generated text content
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        system = kwargs.get("system", "")
        context = kwargs.get("context", "")
        
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"Ollama API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    return result.get("response", "")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection error: {e}")
            raise RuntimeError(f"Failed to connect to Ollama: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Ollama request timeout")
            raise RuntimeError("Ollama request timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Ollama JSON decode error: {e}")
            raise RuntimeError(f"Failed to parse Ollama response: {e}")
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation using Ollama API
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.)
            
        Yields:
            Text chunks as they are generated
        """
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        system = kwargs.get("system", "")
        context = kwargs.get("context", "")
        
        full_prompt = prompt
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"Ollama API error: {response.status} - {error_text}")
                    
                    async for line in response.content:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                                
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection error: {e}")
            raise RuntimeError(f"Failed to connect to Ollama: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Ollama request timeout")
            raise RuntimeError("Ollama request timed out")
    
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image (Ollama doesn't support image generation natively)
        
        Args:
            prompt: Image description
            **kwargs: Additional parameters
            
        Returns:
            Dict with error information
        """
        return {
            "error": "Image generation not supported by Ollama provider",
            "message": "Use OpenAI or another provider for image generation"
        }
    
    async def list_models(self) -> list:
        """List available models from Ollama
        
        Returns:
            List of available models
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("models", [])
                    return []
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama library
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            Success status
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=self.timeout * 10
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def get_capabilities(self) -> list:
        """Get provider capabilities
        
        Returns:
            List of supported capabilities
        """
        return [
            "text_generation",
            "streaming",
            "chat",
            "code_generation",
        ]
