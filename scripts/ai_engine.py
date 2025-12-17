"""
AI Engine - Model-Agnostic Provider Layer.

IMPORTANT: This is the ONLY file where AI provider logic is allowed.
All AI integrations must go through this module.

Default provider: Groq
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class AIProvider(Enum):
    """Supported AI providers."""

    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class AIResponse:
    """Standardized AI response."""

    content: str
    model: str
    provider: AIProvider
    tokens_used: int
    metadata: dict[str, Any]


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Generate a completion for the given prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class GroqProvider(BaseAIProvider):
    """Groq AI provider implementation (DEFAULT)."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    def complete(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Generate completion using Groq."""
        if not self.is_available():
            raise RuntimeError("Groq provider not configured")

        # Implementation would go here
        # from groq import Groq
        # client = Groq(api_key=self.api_key)
        # response = client.chat.completions.create(...)

        raise NotImplementedError("Implement Groq API call")

    def is_available(self) -> bool:
        """Check if Groq is configured."""
        return bool(self.api_key)


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")

    def complete(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Generate completion using OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI provider not configured")

        raise NotImplementedError("Implement OpenAI API call")

    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.api_key)


class AnthropicProvider(BaseAIProvider):
    """Anthropic provider implementation."""

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def complete(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Generate completion using Anthropic."""
        if not self.is_available():
            raise RuntimeError("Anthropic provider not configured")

        raise NotImplementedError("Implement Anthropic API call")

    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(self.api_key)


class AIEngine:
    """
    Model-agnostic AI engine.

    Automatically selects the best available provider.
    Default: Groq
    """

    PROVIDER_PRIORITY = [
        AIProvider.GROQ,
        AIProvider.ANTHROPIC,
        AIProvider.OPENAI,
    ]

    def __init__(self, provider: Optional[AIProvider] = None) -> None:
        self._providers: dict[AIProvider, BaseAIProvider] = {
            AIProvider.GROQ: GroqProvider(),
            AIProvider.OPENAI: OpenAIProvider(),
            AIProvider.ANTHROPIC: AnthropicProvider(),
        }
        self._active_provider = provider or self._select_provider()

    def _select_provider(self) -> AIProvider:
        """Select the first available provider based on priority."""
        # Check environment override
        override = os.getenv("AI_PROVIDER")
        if override:
            try:
                provider = AIProvider(override.lower())
                if self._providers[provider].is_available():
                    return provider
            except ValueError:
                pass

        # Fall back to priority list
        for provider in self.PROVIDER_PRIORITY:
            if self._providers[provider].is_available():
                return provider

        raise RuntimeError("No AI provider available. Set GROQ_API_KEY or equivalent.")

    def complete(self, prompt: str, **kwargs: Any) -> AIResponse:
        """Generate a completion using the active provider."""
        provider = self._providers[self._active_provider]
        return provider.complete(prompt, **kwargs)

    @property
    def provider(self) -> AIProvider:
        """Get the active provider."""
        return self._active_provider

    def switch_provider(self, provider: AIProvider) -> None:
        """Switch to a different provider."""
        if not self._providers[provider].is_available():
            raise RuntimeError(f"Provider {provider.value} is not available")
        self._active_provider = provider


# Module-level convenience function
def get_engine(provider: Optional[AIProvider] = None) -> AIEngine:
    """Get an AI engine instance."""
    return AIEngine(provider=provider)
