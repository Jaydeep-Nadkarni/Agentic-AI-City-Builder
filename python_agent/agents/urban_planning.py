"""Urban Planning AI configuration."""

from .base import AgentConfig, SpecialistAgent


class UrbanPlanningAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                role="urban_planning",
                title="Urban Planning AI",
                system_prompt=(
                    "Evaluate land-use and development needs alongside "
                    "infrastructure dependencies. Do not assume a tile is "
                    "buildable without evidence."
                ),
                topic="housing",
                relevant_metrics=("housing", "population", "infrastructure"),
                responsibilities=(
                    "Identify zoning imbalances",
                    "Coordinate growth with infrastructure",
                    "Recommend staged development",
                ),
                threshold=1,
                severity=2,
            )
        )
