"""Shared contract for selectively activated specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from ..llm_reasoner import LLMReasoner
    from ..models import CityState, Observation, Proposal
except ImportError:
    from python_agent.llm_reasoner import LLMReasoner
    from python_agent.models import CityState, Observation, Proposal


@dataclass(frozen=True)
class AgentConfig:
    role: str
    title: str
    system_prompt: str
    topic: str
    relevant_metrics: tuple[str, ...]
    responsibilities: tuple[str, ...]
    threshold: float = 1.0
    severity: int = 1


class SpecialistAgent:
    """Deterministic observation producer with optional shared-LLM reasoning."""

    def __init__(self, config: AgentConfig) -> None:
        if not config.role.strip():
            raise ValueError("agent role is required")
        self.config = config
        self.role = config.role

    def observe(self, state: CityState) -> Observation | None:
        values = {
            metric: float(state.metrics.get(metric, 0))
            for metric in self.config.relevant_metrics
        }
        active_values = {
            metric: value
            for metric, value in values.items()
            if value >= self.config.threshold
        }
        if not active_values:
            return None
        return Observation(
            agent_role=self.role,
            topic=self.config.topic,
            summary=f"{self.config.title} requires attention",
            severity=self.config.severity,
            data={
                "metrics": active_values,
                "missing_metrics": [
                    metric
                    for metric, value in values.items()
                    if value == 0
                ],
            },
        )

    def prompt_context(self) -> dict[str, Any]:
        return {
            "role": self.config.role,
            "title": self.config.title,
            "responsibilities": list(self.config.responsibilities),
            "relevant_metrics": list(self.config.relevant_metrics),
            "system_prompt": self.config.system_prompt,
        }

    def reason(
        self,
        reasoner: LLMReasoner,
        state: CityState,
        observations: list[Observation],
    ) -> list[Proposal]:
        return reasoner.propose(
            state,
            observations,
            role_context=self.prompt_context(),
        )
