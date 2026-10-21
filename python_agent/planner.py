"""Deterministic selective planner with budget and conflict checks."""
from __future__ import annotations
from .actions import ALLOWLIST
from .models import CityState, Observation, Proposal

ACTION_BY_TOPIC = {"budget": "review_budget", "housing": "prioritize_housing",
                   "transport": "inspect_transport"}

class Planner:
    def __init__(self, max_actions: int = 3, budget: int = 1000,
                 approval_required: bool = True) -> None:
        self.max_actions, self.budget, self.approval_required = max_actions, budget, approval_required
    def plan(self, state: CityState, observations: list[Observation]) -> list[Proposal]:
        proposals, seen, spent = [], set(), 0
        for index, observation in enumerate(sorted(observations, key=lambda x: (-x.severity, x.agent_role))):
            action_name = ACTION_BY_TOPIC.get(observation.topic)
            if not action_name or action_name in seen:
                continue
            cost = ALLOWLIST[action_name].cost
            if spent + cost > min(self.budget, max(0, state.budget)):
                continue
            proposals.append(Proposal(f"{state.city_id}-{index}", action_name, {},
                                      observation.summary, cost, observation.agent_role,
                                      self.approval_required))
            seen.add(action_name)
            spent += cost
            if len(proposals) >= self.max_actions:
                break
        return proposals
    @staticmethod
    def detect_conflicts(proposals: list[Proposal]) -> list[str]:
        actions = [p.action for p in proposals]
        conflicts = ["duplicate actions"] if len(actions) != len(set(actions)) else []
        if "prioritize_housing" in actions and "inspect_transport" in actions:
            conflicts.append("housing and transport changes require separate cycles")
        return conflicts
