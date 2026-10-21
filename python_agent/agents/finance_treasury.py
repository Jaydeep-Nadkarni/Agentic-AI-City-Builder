"""Finance and Treasury AI configuration."""

from .base import AgentConfig, SpecialistAgent


class FinanceTreasuryAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(
            AgentConfig(
                role="finance_treasury",
                title="Finance and Treasury AI",
                system_prompt=(
                    "Evaluate affordability, reserves, and financial risk "
                    "using only measured city data. Flag missing cost data."
                ),
                topic="budget",
                relevant_metrics=("budget", "income", "expenses"),
                responsibilities=(
                    "Track available funds",
                    "Evaluate proposal affordability",
                    "Recommend spending limits and reserves",
                ),
                threshold=1,
                severity=3,
            )
        )
