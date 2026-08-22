"""LLM provider implementations"""

import logging
import httpx
import json
import tiktoken
from typing import Optional, AsyncIterator, Dict, Any
from app.config import get_settings
from app.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIProvider(LLMProvider):
    """OpenAI (GPT-4o) provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate using OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                tokens_in = data["usage"]["prompt_tokens"]
                tokens_out = data["usage"]["completion_tokens"]

                return LLMResponse(
                    content=content,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=self.model,
                    provider="openai",
                )
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream from OpenAI"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str and data_str != "[DONE]":
                                try:
                                    data = json.loads(data_str)
                                    chunk = data["choices"][0].get("delta", {}).get("content", "")
                                    if chunk:
                                        yield chunk
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens accurately using tiktoken"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback to approximate count
            return len(text.split())

    async def health_check(self) -> bool:
        """Check OpenAI API availability"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models/{self.model}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2024-06-01"
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate using Anthropic API"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json",
            }

            body = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if system_prompt:
                body["system"] = system_prompt

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=body,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["content"][0]["text"]
                tokens_in = data["usage"]["input_tokens"]
                tokens_out = data["usage"]["output_tokens"]

                return LLMResponse(
                    content=content,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=self.model,
                    provider="anthropic",
                )
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream from Anthropic"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json",
            }

            body = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": True,
            }
            if system_prompt:
                body["system"] = system_prompt

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=body,
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str:
                                try:
                                    data = json.loads(data_str)
                                    if data.get("type") == "content_block_delta":
                                        delta = data.get("delta", {})
                                        if delta.get("type") == "text_delta":
                                            text = delta.get("text", "")
                                            if text:
                                                yield text
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic API"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages/count_tokens",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": text}],
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("input_tokens", len(text.split()))
        except Exception as e:
            logger.warning(f"Token counting failed, using fallback: {e}")

        # Fallback to approximate count
        return len(text.split())

    async def health_check(self) -> bool:
        """Check Anthropic API availability"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json={
                        "model": self.model,
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "test"}],
                    },
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False


class GoogleProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = settings.GOOGLE_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate using Google API"""
        try:
            headers = {"x-goog-api-key": self.api_key}

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                tokens_in = data["usage"]["prompt_tokens"]
                tokens_out = data["usage"]["completion_tokens"]

                return LLMResponse(
                    content=content,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=self.model,
                    provider="google",
                )
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream from Google"""
        try:
            headers = {"x-goog-api-key": self.api_key}

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str and data_str != "[DONE]":
                                try:
                                    data = json.loads(data_str)
                                    chunk = data["choices"][0].get("delta", {}).get("content", "")
                                    if chunk:
                                        yield chunk
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            logger.error(f"Google streaming failed: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Count tokens using Google API"""
        try:
            headers = {"x-goog-api-key": self.api_key}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": text}],
                        "max_tokens": 1,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("usage", {}).get("prompt_tokens", len(text.split()))
        except Exception as e:
            logger.warning(f"Token counting failed, using fallback: {e}")

        return len(text.split())

    async def health_check(self) -> bool:
        """Check Google API availability"""
        try:
            headers = {"x-goog-api-key": self.api_key}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 10,
                    },
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Google health check failed: {e}")
            return False


class LocalOpenAIProvider(LLMProvider):
    """Local OpenAI-compatible provider (vLLM, Ollama)"""

    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or settings.LOCAL_LLM_ENDPOINT
        self.model = settings.LOCAL_LLM_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate using local OpenAI-compatible endpoint"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                tokens_in = data.get("usage", {}).get("prompt_tokens", len(prompt.split()))
                tokens_out = data.get("usage", {}).get("completion_tokens", len(content.split()))

                return LLMResponse(
                    content=content,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    model=self.model,
                    provider="local",
                )
        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream from local LLM"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.endpoint}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str and data_str != "[DONE]":
                                try:
                                    data = json.loads(data_str)
                                    chunk = data["choices"][0].get("delta", {}).get("content", "")
                                    if chunk:
                                        yield chunk
                                except json.JSONDecodeError:
                                    continue
        except Exception as e:
            logger.error(f"Local LLM streaming failed: {e}")
            raise

    async def count_tokens(self, text: str) -> int:
        """Estimate tokens using word count"""
        # Local LLM might not have token counting API
        return len(text.split())

    async def health_check(self) -> bool:
        """Check local LLM availability"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/health",
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Local LLM health check failed: {e}")
            return False


class MockProvider(LLMProvider):
    """Mock provider for testing"""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Generate mock response"""
        return LLMResponse(
            content=f"Mock response to: {prompt[:50]}...",
            tokens_in=len(prompt.split()),
            tokens_out=10,
            model="mock",
            provider="mock",
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream mock response"""
        for chunk in ["Mock ", "response ", "streaming"]:
            yield chunk

    async def count_tokens(self, text: str) -> int:
        """Mock token counting"""
        return len(text.split())

    async def health_check(self) -> bool:
        """Mock health check"""
        return True
