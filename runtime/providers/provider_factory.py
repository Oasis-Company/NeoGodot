from typing import Dict, Type, Any, List
import logging
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider


class ProviderFactory:
    """Provider 工厂类，用于注册和创建 AI Provider 实例"""

    _providers: Dict[str, Type[BaseProvider]] = {}
    _logger = logging.getLogger(__name__)

    @classmethod
    def register(cls, name: str, provider_class: Type[BaseProvider]) -> None:
        """注册一个新的 Provider

        Args:
            name: Provider 名称（唯一标识）
            provider_class: Provider 类的引用

        Example:
            ProviderFactory.register("my_provider", MyCustomProvider)
        """
        if not issubclass(provider_class, BaseProvider):
            raise TypeError(f"Provider class must inherit from BaseProvider")

        if name in cls._providers:
            cls._logger.warning(f"Provider '{name}' is being overwritten")

        cls._providers[name] = provider_class
        cls._logger.info(f"Registered provider: {name} -> {provider_class.__name__}")

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseProvider:
        """创建 Provider 实例

        Args:
            name: 已注册的 Provider 名称
            config: Provider 配置字典，包含 api_key, base_url, model 等

        Returns:
            Provider 实例

        Raises:
            ValueError: 如果 Provider 未注册

        Example:
            config = {
                "api_key": "sk-...",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4",
                "timeout": 60,
            }
            provider = ProviderFactory.create("openai", config)
        """
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys()) or "none"
            raise ValueError(
                f"Provider '{name}' not found. Available providers: {available}"
            )

        provider_class = cls._providers[name]
        cls._logger.info(f"Creating provider instance: {name}")
        return provider_class(config)

    @classmethod
    def list_providers(cls) -> List[str]:
        """获取所有已注册的 Provider 名称

        Returns:
            Provider 名称列表

        Example:
            providers = ProviderFactory.list_providers()
            # ["openai", "anthropic", "my_custom_provider"]
        """
        return list(cls._providers.keys())

    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseProvider]:
        """获取 Provider 类

        Args:
            name: Provider 名称

        Returns:
            Provider 类

        Raises:
            ValueError: 如果 Provider 未注册
        """
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys()) or "none"
            raise ValueError(
                f"Provider '{name}' not found. Available providers: {available}"
            )
        return cls._providers[name]

    @classmethod
    def unregister(cls, name: str) -> bool:
        """注销一个 Provider

        Args:
            name: Provider 名称

        Returns:
            是否成功注销
        """
        if name in cls._providers:
            del cls._providers[name]
            cls._logger.info(f"Unregistered provider: {name}")
            return True
        return False

    @classmethod
    def clear(cls) -> None:
        """清除所有已注册的 Provider"""
        cls._providers.clear()
        cls._logger.info("Cleared all registered providers")


ProviderFactory.register("openai", OpenAIProvider)
ProviderFactory.register("anthropic", AnthropicProvider)
ProviderFactory.register("openai_compatible", OpenAIProvider)
