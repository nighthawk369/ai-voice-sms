"""LLM provider router"""

import logging
from typing import Optional
from app.config import get_settings
from app.llm.base import LLMProvider
from app.llm.providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    LocalOpenAIProvider,
    MockProvider,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMRouter:
    """Routes to correct LLM provider based on configuration"""

    def __init__(self):
        self.providers = {
            "openai": self._create_openai,
            "anthropic": self._create_anthropic,
            "google": self._create_google,
            "local": self._create_local,
            "mock": self._create_mock,
        }
        self.primary_provider = settings.LLM_PROVIDER
        self.fallback_providers = ["mock"]

    def _create_openai(self) -> LLMProvider:
        """Create OpenAI provider"""
        try:
            return OpenAIProvider()
        except ValueError as e:
            logger.warning(f"Could not create OpenAI provider: {e}")
            return None

    def _create_anthropic(self) -> LLMProvider:
        """Create Anthropic provider"""
        try:
            return AnthropicProvider()
        except ValueError as e:
            logger.warning(f"Could not create Anthropic provider: {e}")
            return None

    def _create_google(self) -> LLMProvider:
        """Create Google provider"""
        try:
            return GoogleProvider()
        except ValueError as e:
            logger.warning(f"Could not create Google provider: {e}")
            return None

    def _create_local(self) -> LLMProvider:
        """Create local provider"""
        try:
            return LocalOpenAIProvider()
        except ValueError as e:
            logger.warning(f"Could not create local provider: {e}")
            return None

    def _create_mock(self) -> LLMProvider:
        """Create mock provider"""
        return MockProvider()

    async def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """Get LLM provider by name, with fallback"""
        name = provider_name or self.primary_provider

        if name not in self.providers:
            logger.warning(f"Unknown provider: {name}, using fallback")
            name = self.primary_provider

        try:
            provider = self.providers[name]()
            if provider and await provider.health_check():
                logger.info(f"Using {name} provider")
                return provider
        except Exception as e:
            logger.warning(f"Error creating {name} provider: {e}")

        # Try fallback providers
        for fallback_name in self.fallback_providers:
            try:
                provider = self.providers[fallback_name]()
                if provider and await provider.health_check():
                    logger.warning(f"Falling back to {fallback_name} provider")
                    return provider
            except Exception as e:
                logger.warning(f"Error creating fallback {fallback_name} provider: {e}")

        # Last resort: always return mock
        logger.error("All providers failed, using mock provider")
        return MockProvider()

    async def generate(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        **kwargs
    ):
        """Generate using selected provider"""
        provider = await self.get_provider(provider_name)
        return await provider.generate(prompt, **kwargs)


# Global router instance
_router = None


def get_llm_router() -> LLMRouter:
    """Get or create global LLM router"""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
