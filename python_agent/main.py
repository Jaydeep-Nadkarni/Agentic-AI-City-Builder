"""CLI entry point for a local, deterministic planning cycle."""
from __future__ import annotations
import json
from pathlib import Path
from .config import Settings
from .models import CityState
from .orchestrator import Orchestrator
from .planner import Planner
from .registry import default_registry

def run(settings_path: str | Path = "config/settings.json") -> list[dict]:
    settings = Settings.load(settings_path)
    state = CityState("local", budget=settings.cycle_budget,
                      metrics={"budget": 1} if settings.cycle_budget else {})
    proposals = Orchestrator(default_registry(), Planner(
        settings.max_actions_per_cycle, settings.cycle_budget, settings.approval_required)).cycle(state)
    return [proposal.__dict__ for proposal in proposals]

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
