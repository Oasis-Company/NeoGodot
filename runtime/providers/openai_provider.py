import json
from typing import AsyncIterator, Dict, Any, Optional, List
import httpx
from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI 兼容 API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.organization = config.get("organization", None)
        # 创建可复用的 httpx 客户端，启用连接池
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建 httpx 客户端（带连接池）"""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(timeout=self.timeout)
            limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                http2=True,
                verify=True,
            )
        return self._client
    
    async def close(self):
        """关闭客户端连接池"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本回复（非流式）"""
        headers = self._prepare_headers()
        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        payload = {
            "model": kwargs.get("model", self.model_name),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "stream": False,
        }

        stop = kwargs.get("stop")
        if stop:
            payload["stop"] = stop if isinstance(stop, list) else [stop]

        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            await self._handle_error(data)
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            self._logger.error(f"Request failed: {str(e)}")
            raise

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式生成文本回复"""
        headers = self._prepare_headers()
        headers["Accept"] = "text/event-stream"
        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        payload = {
            "model": kwargs.get("model", self.model_name),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": True,
        }

        stop = kwargs.get("stop")
        if stop:
            payload["stop"] = stop if isinstance(stop, list) else [stop]

        client = await self._get_client()
        try:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error during streaming: {e.response.status_code}")
            raise
        except Exception as e:
            self._logger.error(f"Streaming request failed: {str(e)}")
            raise

    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成图像（DALL-E 兼容）"""
        headers = self._prepare_headers()
        payload = {
            "prompt": prompt,
            "n": kwargs.get("n", 1),
            "size": kwargs.get("size", "1024x1024"),
            "quality": kwargs.get("quality", "standard"),
            "response_format": kwargs.get("response_format", "url"),
        }
        model = kwargs.get("model", "dall-e-3")
        
        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            await self._handle_error(data)
            
            result = {
                "model": model,
                "images": [],
            }
            for img in data.get("data", []):
                result["images"].append({
                    "url": img.get("url"),
                    "b64_json": img.get("b64_json"),
                    "revised_prompt": img.get("revised_prompt"),
                })
            return result
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            self._logger.error(f"Image generation failed: {str(e)}")
            raise

    def get_capabilities(self) -> list:
        capabilities = super().get_capabilities()
        capabilities.extend([
            "function_calling",
            "json_mode",
            "vision",
        ])
        return capabilities
