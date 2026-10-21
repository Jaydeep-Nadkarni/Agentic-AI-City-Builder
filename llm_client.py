"""Compatibility import for the historical standalone smoke test."""

from urllib.request import urlopen
from python_agent import llm_client as _client

GroqClientError = _client.GroqClientError
GroqSettings = _client.GroqSettings


class GroqClient(_client.GroqClient):
    """Legacy import shim that keeps the old patch target working."""

    def complete(self, prompt: str) -> str:
        _client.urlopen = urlopen
        return super().complete(prompt)

__all__ = ["GroqClient", "GroqClientError", "GroqSettings"]
