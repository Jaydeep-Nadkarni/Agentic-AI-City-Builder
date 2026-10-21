"""Safe action vocabulary and validation; game bridge actions are unavailable."""
from __future__ import annotations
from dataclasses import dataclass
from .models import Action, Proposal

@dataclass(frozen=True)
class ActionSpec:
    name: str
    cost: int
    available: bool = True

ALLOWLIST = {
    "review_budget": ActionSpec("review_budget", 0),
    "prioritize_housing": ActionSpec("prioritize_housing", 100),
    "inspect_transport": ActionSpec("inspect_transport", 50),
    "record_observation": ActionSpec("record_observation", 0),
}

class ActionValidationError(ValueError):
    """Raised for unknown, unavailable, malformed, or unapproved actions."""

def validate_action(action: Action, approved: bool = False) -> ActionSpec:
    spec = ALLOWLIST.get(action.name)
    if spec is None:
        raise ActionValidationError(f"action is not allowlisted: {action.name}")
    if not spec.available:
        raise ActionValidationError(f"action is unavailable: {action.name}")
    if not approved:
        raise ActionValidationError(f"manual approval required: {action.name}")
    if action.cost < 0 or action.cost != spec.cost:
        raise ActionValidationError(f"invalid cost for action: {action.name}")
    if not isinstance(action.parameters, dict):
        raise ActionValidationError("action parameters must be an object")
    return spec

def proposal_to_action(proposal: Proposal, approved: bool = False) -> Action:
    action = Action(proposal.action, dict(proposal.parameters), proposal.cost)
    validate_action(action, approved)
    return action


class ActionDispatcher:
    """Approval-gated dispatcher seam; the default implementation is deliberately inert."""

    def dispatch(self, action: Action | Proposal, approved: bool = False) -> Action:
        if isinstance(action, Proposal):
            action = proposal_to_action(action, approved)
        validate_action(action, approved)
        return action
