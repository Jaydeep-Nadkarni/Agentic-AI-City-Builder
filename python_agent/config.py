"""Validated settings loading without a third-party dependency."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """Raised when configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    groq_endpoint: str
    groq_model: str
    groq_timeout_seconds: float
    history_path: str
    dashboard_host: str
    dashboard_port: int
    approval_required: bool
    max_actions_per_cycle: int
    cycle_budget: int
    agent_mode: str = "legacy"
    enabled_specialist_roles: tuple[str, ...] = ()
    llm_enabled: bool = False

    @classmethod
    def load(cls, path: str | Path | None = None, environ: dict[str, str] | None = None) -> "Settings":
        env = os.environ if environ is None else environ
        raw: dict = {}
        if path is not None:
            try:
                raw = json.loads(Path(path).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ConfigError(f"cannot read settings: {exc}") from exc
        groq = raw.get("groq", {})
        dashboard = raw.get("dashboard", {})
        planner = raw.get("planner", {})
        agents = raw.get("agents", {})
        llm = raw.get("llm", {})

        def value(name: str, default: object) -> object:
            return env.get(name, default)

        def integer(name: str, default: object, minimum: int = 0) -> int:
            try:
                result = int(value(name, default))
            except (TypeError, ValueError) as exc:
                raise ConfigError(f"{name} must be an integer") from exc
            if result < minimum:
                raise ConfigError(f"{name} must be at least {minimum}")
            return result

        try:
            timeout = float(value("GROQ_TIMEOUT_SECONDS", groq.get("timeout_seconds", 30)))
        except (TypeError, ValueError) as exc:
            raise ConfigError("GROQ_TIMEOUT_SECONDS must be a number") from exc
        if timeout <= 0:
            raise ConfigError("GROQ_TIMEOUT_SECONDS must be greater than zero")
        endpoint = str(value("GROQ_ENDPOINT", groq.get("endpoint", ""))).strip()
        model = str(value("GROQ_MODEL", groq.get("model", ""))).strip()
        if not endpoint.startswith(("http://", "https://")) or not model:
            raise ConfigError("Groq endpoint and model are required")
        host = str(value("DASHBOARD_HOST", dashboard.get("host", "127.0.0.1"))).strip()
        approval = str(value("APPROVAL_REQUIRED", planner.get("approval_required", True))).lower()
        if approval not in {"true", "false", "1", "0", "yes", "no"}:
            raise ConfigError("APPROVAL_REQUIRED must be boolean")
        mode = str(value("AGENT_MODE", agents.get("mode", "legacy"))).lower()
        if mode not in {"legacy", "specialist", "combined"}:
            raise ConfigError("AGENT_MODE must be legacy, specialist, or combined")
        roles_raw = value("ENABLED_SPECIALIST_ROLES", agents.get("enabled_specialist_roles", []))
        roles = tuple(r.strip() for r in str(roles_raw).split(",") if r.strip()) if isinstance(roles_raw, str) else tuple(roles_raw)
        llm_raw = str(value("LLM_ENABLED", llm.get("enabled", False))).lower()
        if llm_raw not in {"true", "false", "1", "0", "yes", "no"}:
            raise ConfigError("LLM_ENABLED must be boolean")
        return cls(endpoint, model, timeout, str(value("HISTORY_PATH", "logs/history.jsonl")),
                   host, integer("DASHBOARD_PORT", dashboard.get("port", 8765), 1),
                   approval in {"true", "1", "yes"},
                   integer("MAX_ACTIONS_PER_CYCLE", planner.get("max_actions_per_cycle", 3), 1),
                   integer("CYCLE_BUDGET", planner.get("cycle_budget", 1000), 0),
                   mode, roles, llm_raw in {"true", "1", "yes"})
