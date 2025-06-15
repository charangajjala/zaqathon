"""LLM factory for creating language model instances."""

import os
from typing import Any, Optional

from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

from core.exceptions import LLMError
from core.interfaces import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def create_llm(self, **kwargs) -> BaseLanguageModel:
        """Create OpenAI LLM instance."""
        config = self.get_default_config()
        config.update(kwargs)

        api_key = config.pop("api_key", None) or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMError("OpenAI API key is required")

        return ChatOpenAI(api_key=api_key, **config)

    def get_default_config(self) -> dict[str, Any]:
        """Get default OpenAI configuration."""
        return {
            "model": os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview"),
            "temperature": float(os.getenv("TEMPERATURE", "0.0")),
        }


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider."""

    def create_llm(self, **kwargs) -> BaseLanguageModel:
        """Create Anthropic LLM instance."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise LLMError(
                "langchain-anthropic package is required for Anthropic provider"
            ) from e

        config = self.get_default_config()
        config.update(kwargs)

        api_key = config.pop("api_key", None) or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError("Anthropic API key is required")

        return ChatAnthropic(api_key=api_key, **config)

    def get_default_config(self) -> dict[str, Any]:
        """Get default Anthropic configuration."""
        return {
            "model": "claude-3-sonnet-20240229",
            "temperature": float(os.getenv("TEMPERATURE", "0.0")),
        }


class LLMFactory:
    """Factory for creating LLM instances."""

    _providers: dict[str, LLMProvider] = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
    }

    @classmethod
    def create_llm(cls, provider: Optional[str] = None, **kwargs) -> BaseLanguageModel:
        """Create LLM instance from specified provider."""
        provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai")

        if provider not in cls._providers:
            raise LLMError(
                f"Unknown provider: {provider}. Available: {list(cls._providers.keys())}"
            )

        return cls._providers[provider].create_llm(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider: LLMProvider):
        """Register a new LLM provider."""
        cls._providers[name] = provider

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers."""
        return list(cls._providers.keys())
