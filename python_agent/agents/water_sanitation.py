"""Water and Sanitation AI configuration."""
from .base import AgentConfig, SpecialistAgent


class WaterSanitationAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "water_sanitation", "Water and Sanitation AI",
            "Use only observed water, sewage, waste, and sanitation indicators.",
            "water", ("water_capacity", "water_demand", "sewage_capacity", "waste_capacity"),
            ("Identify coverage gaps", "Monitor capacity", "Flag missing sanitation data"),
            severity=2,
        ))
