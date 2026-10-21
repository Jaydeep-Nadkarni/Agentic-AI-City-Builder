"""Small Groq Chat Completions client used by the smoke test."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GroqClientError(RuntimeError):
    """Raised when a Groq request cannot be completed or parsed."""


@dataclass(frozen=True)
class GroqSettings:
    endpoint: str = "https://api.groq.com/openai/v1/chat/completions"
    model: str = "llama-3.1-8b-instant"
    timeout_seconds: float = 30.0

    @classmethod
    def from_environment(cls) -> "GroqSettings":
        timeout = os.getenv("GROQ_TIMEOUT_SECONDS", "30")
        try:
            timeout_seconds = float(timeout)
        except ValueError as exc:
            raise GroqClientError("GROQ_TIMEOUT_SECONDS must be a number") from exc
        if timeout_seconds <= 0:
            raise GroqClientError("GROQ_TIMEOUT_SECONDS must be greater than zero")

        return cls(
            endpoint=os.getenv(
                "GROQ_ENDPOINT",
                "https://api.groq.com/openai/v1/chat/completions",
            ),
            model=os.getenv("GROQ_MODEL", cls.model),
            timeout_seconds=timeout_seconds,
        )


class GroqClient:
    def __init__(self, api_key: str, settings: GroqSettings | None = None) -> None:
        if not api_key.strip():
            raise GroqClientError("GROQ_API_KEY is missing or empty")
        self._api_key = api_key
        self._settings = settings or GroqSettings.from_environment()

    def complete(self, prompt: str) -> str:
        if not prompt.strip():
            raise GroqClientError("The prompt must not be empty")

        payload = {
            "model": self._settings.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 100,
        }
        request = Request(
            self._settings.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "theotown-ai/1.0",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._settings.timeout_seconds) as response:
                response_data: Any = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            if len(error_body) > 1500:
                error_body = error_body[:1500]
            raise GroqClientError(
                f"Groq request failed with HTTP {exc.code}: {error_body}"
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise GroqClientError("Could not reach the Groq API") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GroqClientError("Groq returned an invalid JSON response") from exc

        try:
            content = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqClientError("Groq response did not contain message content") from exc
        if not isinstance(content, str) or not content.strip():
            raise GroqClientError("Groq returned empty message content")
        return content.strip()
