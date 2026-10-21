"""One deterministic observation/planning cycle."""
from __future__ import annotations
from .history import History
from .models import CityState, Proposal
from .planner import Planner
from .registry import Agent

class Orchestrator:
    def __init__(self, registry: dict[str, Agent], planner: Planner,
                 history: History | None = None) -> None:
        self.registry, self.planner, self.history = registry, planner, history or History()
    def cycle(self, state: CityState) -> list[Proposal]:
        observations = [result for agent in self.registry.values()
                        if (result := agent.observe(state)) is not None]
        proposals = self.planner.plan(state, observations)
        if self.planner.detect_conflicts(proposals):
            return []
        self.history.append({"city_id": state.city_id, "observations": len(observations),
                             "proposals": [p.action for p in proposals]})
        return proposals
