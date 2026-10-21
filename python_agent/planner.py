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

    def finalize(self, state: CityState, proposals: list[Proposal]) -> tuple[list[Proposal], list[dict[str, str]]]:
        """Apply deterministic limits, budget, allowlist, and duplicate checks."""
        accepted: list[Proposal] = []
        rejected: list[dict[str, str]] = []
        seen: set[str] = set()
        spent = 0
        for proposal in proposals:
            if proposal.action not in ALLOWLIST:
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "action not allowlisted"})
                continue
            if proposal.action in seen:
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "duplicate action"})
                continue
            if not proposal.requires_approval:
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "approval is required"})
                continue
            if proposal.cost < 0 or proposal.cost != ALLOWLIST[proposal.action].cost:
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "invalid action cost"})
                continue
            if spent + proposal.cost > min(self.budget, max(0, state.budget)):
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "cycle budget exceeded"})
                continue
            if len(accepted) >= self.max_actions:
                rejected.append({"proposal_id": proposal.proposal_id, "reason": "proposal limit exceeded"})
                continue
            accepted.append(proposal)
            seen.add(proposal.action)
            spent += proposal.cost
        return accepted, rejected
    @staticmethod
    def detect_conflicts(proposals: list[Proposal]) -> list[str]:
        actions = [p.action for p in proposals]
        conflicts = ["duplicate actions"] if len(actions) != len(set(actions)) else []
        if "prioritize_housing" in actions and "inspect_transport" in actions:
            conflicts.append("housing and transport changes require separate cycles")
        return conflicts
