"""Economy and Industry AI configuration."""
from .base import AgentConfig, SpecialistAgent


class EconomyIndustryAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "economy_industry", "Economy and Industry AI",
            "Analyze observed employment and economic indicators without speculative forecasts.",
            "economy", ("employment", "commercial_demand", "industrial_demand", "income"),
            ("Identify development opportunities", "Coordinate utilities and transport", "Report uncertainty"),
            severity=2,
        ))
