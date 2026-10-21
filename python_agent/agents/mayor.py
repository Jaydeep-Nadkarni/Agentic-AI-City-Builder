"""Mayor AI configuration."""

from .base import AgentConfig, SpecialistAgent


class MayorAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                role="mayor",
                title="Mayor AI",
                system_prompt=(
                    "Coordinate city priorities, compare specialist evidence, "
                    "and rank feasible recommendations. Never bypass hard "
                    "budget, conflict, or approval rules."
                ),
                topic="budget",
                relevant_metrics=("budget", "happiness"),
                responsibilities=(
                    "Set city-wide priorities",
                    "Compare competing recommendations",
                    "Request human review when evidence is insufficient",
                ),
                threshold=1,
                severity=3,
            )
        )
