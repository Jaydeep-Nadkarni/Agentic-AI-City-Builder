"""Role registry using one shared agent interface and no per-role clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import CityState, Observation


class Agent(Protocol):
    role: str

    def observe(self, state: CityState) -> Observation | None: ...


@dataclass(frozen=True)
class RuleAgent:
    role: str
    topic: str
    metric: str
    threshold: float
    summary: str
    severity: int = 1

    def observe(self, state: CityState) -> Observation | None:
        value = float(state.metrics.get(self.metric, 0))
        if value >= self.threshold:
            return Observation(self.role, self.topic, self.summary, self.severity,
                               {"metric": self.metric, "value": value})
        return None


ROLES = (
    "budget", "zoning", "housing", "transport", "utilities", "energy",
    "water", "waste", "health", "education", "safety", "environment",
    "economy", "happiness", "population", "resilience",
)


def default_registry() -> dict[str, Agent]:
    return {
        role: RuleAgent(role, role, role, 1, f"{role} requires attention")
        for role in ROLES
    }


def register(registry: dict[str, Agent], agent: Agent) -> None:
    if not getattr(agent, "role", "").strip():
        raise ValueError("agent role is required")
    if agent.role in registry:
        raise ValueError(f"agent role already registered: {agent.role}")
    registry[agent.role] = agent

