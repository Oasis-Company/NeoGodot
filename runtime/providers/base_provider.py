from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
import logging


class BaseProvider(ABC):
    """抽象基类，定义 AI Provider 的通用接口"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self.model_name = config.get("model", "default")
        self.timeout = config.get("timeout", 60)
        self.max_retries = config.get("max_retries", 3)
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本回复（非流式）

        Args:
            prompt: 输入提示词
            **kwargs: 额外参数（如 temperature, max_tokens 等）

        Returns:
            生成的文本内容
        """
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """流式生成文本回复

        Args:
            prompt: 输入提示词
            **kwargs: 额外参数

        Yields:
            文本片段（流式返回）
        """
        pass

    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成图像

        Args:
            prompt: 图像描述
            **kwargs: 额外参数（如 size, quality 等）

        Returns:
            包含图像 URL 或 base64 的字典
        """
        pass

    def get_model_name(self) -> str:
        """获取当前模型名称"""
        return self.model_name

    def get_capabilities(self) -> list:
        """获取当前 provider 支持的能力列表"""
        return [
            "text_generation",
            "streaming",
            "image_generation",
        ]

    def _prepare_headers(self) -> Dict[str, str]:
        """准备 HTTP 请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _handle_error(self, response_data: Dict[str, Any]) -> None:
        """处理 API 错误响应"""
        if "error" in response_data:
            error = response_data["error"]
            error_message = error.get("message", "Unknown error")
            error_type = error.get("type", "unknown")
            raise ValueError(f"API Error [{error_type}]: {error_message}")
