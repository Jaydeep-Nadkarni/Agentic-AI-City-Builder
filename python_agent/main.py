"""CLI entry point for a local, deterministic planning cycle."""
from __future__ import annotations
import json
import os
from pathlib import Path
from .config import Settings
from .llm_client import GroqClient, GroqSettings
from .llm_reasoner import LLMReasoner
from .models import CityState
from .orchestrator import Orchestrator
from .planner import Planner
from .registry import build_registry


def configured_reasoner(settings: Settings) -> LLMReasoner | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not settings.llm_enabled or not api_key:
        return None
    client_settings = GroqSettings(
        endpoint=settings.groq_endpoint,
        model=settings.groq_model,
        timeout_seconds=settings.groq_timeout_seconds,
    )
    return LLMReasoner(GroqClient(api_key, client_settings))


def run(settings_path: str | Path = "config/settings.json") -> list[dict]:
    settings = Settings.load(settings_path)
    state = CityState("local", budget=settings.cycle_budget,
                      metrics={"budget": 1} if settings.cycle_budget else {})
    proposals = Orchestrator(
        build_registry(settings.agent_mode, settings.enabled_specialist_roles),
        Planner(settings.max_actions_per_cycle, settings.cycle_budget, settings.approval_required),
        reasoner=configured_reasoner(settings),
        llm_enabled=settings.llm_enabled,
    ).cycle(state)
    return [proposal.__dict__ for proposal in proposals]

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
