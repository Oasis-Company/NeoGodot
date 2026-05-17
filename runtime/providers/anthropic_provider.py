import json
import base64
from typing import AsyncIterator, Dict, Any, Optional, List, Union
import httpx
from .base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API Provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.anthropic.com/v1")
        self.api_version = config.get("api_version", "2023-06-01")
        self.default_model = config.get("model", "claude-3-5-sonnet-20241022")
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
        """生成文本回复（使用 Anthropic Messages API）"""
        headers = self._prepare_headers()
        headers["x-api-key"] = self.api_key
        headers["anthropic-version"] = self.api_version
        headers["anthropic-dangerous-direct-browser-access"] = "true"

        system = kwargs.get("system", "")
        images = kwargs.get("images", [])

        content = []
        if images:
            for img_data in images:
                if isinstance(img_data, dict):
                    content.append({
                        "type": "image",
                        "source": {
                            "type": img_data.get("type", "base64"),
                            "media_type": img_data.get("media_type", "image/jpeg"),
                            "data": img_data.get("data"),
                        }
                    })
            content.append({"type": "text", "text": prompt})
        else:
            content = prompt

        payload = {
            "model": kwargs.get("model", self.default_model),
            "messages": [{"role": "user", "content": content}],
            "temperature": kwargs.get("temperature", 1.0),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }

        if system:
            payload["system"] = system

        top_p = kwargs.get("top_p")
        if top_p is not None:
            payload["top_p"] = top_p

        top_k = kwargs.get("top_k")
        if top_k is not None:
            payload["top_k"] = top_k

        stop_sequences = kwargs.get("stop_sequences")
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences if isinstance(stop_sequences, list) else [stop_sequences]

        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                error = data["error"]
                raise ValueError(f"Claude API Error: {error.get('type', 'unknown')} - {error.get('message', 'Unknown error')}")
            
            return data["content"][0]["text"]
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error: {e.response.status_code}")
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", error_detail)
            except:
                pass
            raise ValueError(f"Anthropic API Error: {error_detail}")
        except Exception as e:
            self._logger.error(f"Request failed: {str(e)}")
            raise

    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式生成文本回复"""
        headers = self._prepare_headers()
        headers["x-api-key"] = self.api_key
        headers["anthropic-version"] = self.api_version
        headers["anthropic-dangerous-direct-browser-access"] = "true"
        headers["Accept"] = "text/event-stream"

        system = kwargs.get("system", "")
        images = kwargs.get("images", [])

        content = []
        if images:
            for img_data in images:
                if isinstance(img_data, dict):
                    content.append({
                        "type": "image",
                        "source": {
                            "type": img_data.get("type", "base64"),
                            "media_type": img_data.get("media_type", "image/jpeg"),
                            "data": img_data.get("data"),
                        }
                    })
            content.append({"type": "text", "text": prompt})
        else:
            content = prompt

        payload = {
            "model": kwargs.get("model", self.default_model),
            "messages": [{"role": "user", "content": content}],
            "temperature": kwargs.get("temperature", 1.0),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
        }

        if system:
            payload["system"] = system

        top_p = kwargs.get("top_p")
        if top_p is not None:
            payload["top_p"] = top_p

        top_k = kwargs.get("top_k")
        if top_k is not None:
            payload["top_k"] = top_k

        stop_sequences = kwargs.get("stop_sequences")
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences if isinstance(stop_sequences, list) else [stop_sequences]

        client = await self._get_client()
        try:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
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
                            event_type = data.get("type")
                            if event_type == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "thinking" and "thinking" in kwargs.get("include", []):
                                    yield f"[thinking]{delta.get('thinking', '')}[/thinking]"
                                elif delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error during streaming: {e.response.status_code}")
            raise
        except Exception as e:
            self._logger.error(f"Streaming request failed: {str(e)}")
            raise

    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成图像（支持图像输入）"""
        image_url = kwargs.get("image_url")
        image_base64 = kwargs.get("image_base64")
        media_type = kwargs.get("media_type", "image/jpeg")
        
        if not image_url and not image_base64:
            raise ValueError("Either image_url or image_base64 must be provided")

        images = []
        if image_url:
            images.append({"type": "url", "source": {"type": "url", "media_type": media_type, "data": image_url}})
        elif image_base64:
            images.append({"type": "base64", "source": {"type": "base64", "media_type": media_type, "data": image_base64}})

        result_text = await self.generate(prompt, images=images, **kwargs)

        return {
            "model": kwargs.get("model", self.default_model),
            "result": result_text,
            "input_type": "image",
            "images": images,
        }

    def get_capabilities(self) -> list:
        capabilities = super().get_capabilities()
        capabilities.extend([
            "vision",
            "extended_thinking",
            "computer_use",
            "tool_use",
        ])
        return capabilities
