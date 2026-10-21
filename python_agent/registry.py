"""Role registry using one shared agent interface and no per-role clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import CityState, Observation


class Agent(Protocol):
    role: str

    def observe(self, state: CityState) -> Observation | None: ...


def specialist_agents() -> tuple[Agent, ...]:
    """Construct the bundled specialists without changing their implementations."""
    from .agents import (
        CityIntelligenceAgent, DisasterManagementAgent, EconomyIndustryAgent,
        EducationCommunityAgent, EnergyUtilitiesAgent, EnvironmentSustainabilityAgent,
        FinanceTreasuryAgent, FireEmergencyAgent, HighwayConstructionAgent,
        HousingPopulationAgent, MayorAgent, PublicHealthAgent, PublicSafetyAgent,
        TrafficTransportAgent, UrbanPlanningAgent, WaterSanitationAgent,
    )
    return (
        MayorAgent(), UrbanPlanningAgent(), HousingPopulationAgent(),
        EconomyIndustryAgent(), HighwayConstructionAgent(), TrafficTransportAgent(),
        EnergyUtilitiesAgent(), WaterSanitationAgent(), DisasterManagementAgent(),
        FireEmergencyAgent(), PublicSafetyAgent(), PublicHealthAgent(),
        EducationCommunityAgent(), EnvironmentSustainabilityAgent(),
        FinanceTreasuryAgent(), CityIntelligenceAgent(),
    )


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


def build_registry(mode: str = "legacy", enabled_specialist_roles: tuple[str, ...] | None = None) -> dict[str, Agent]:
    """Build legacy, specialist, or combined registries with explicit collision safety."""
    if mode not in {"legacy", "specialist", "combined"}:
        raise ValueError("agent mode must be legacy, specialist, or combined")
    registry: dict[str, Agent] = {}
    if mode in {"legacy", "combined"}:
        registry.update(default_registry())
    if mode in {"specialist", "combined"}:
        allowed = set(enabled_specialist_roles) if enabled_specialist_roles else None
        for agent in specialist_agents():
            if allowed is not None and agent.role not in allowed:
                continue
            key = agent.role
            if key in registry:
                # Preserve both implementations while keeping registry keys unique.
                key = f"specialist:{agent.role}"
            registry[key] = agent
    return registry
