"""Housing and Population AI configuration."""
from .base import AgentConfig, SpecialistAgent


class HousingPopulationAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "housing_population", "Housing and Population AI",
            "Assess measured population and housing demand, recommending staged growth.",
            "housing", ("population", "housing", "housing_demand", "vacancy"),
            ("Track housing demand", "Coordinate growth with services", "Avoid unsupported expansion"),
            severity=2,
        ))
