"""Public Health AI configuration."""
from .base import AgentConfig, SpecialistAgent


class PublicHealthAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "public_health", "Public Health AI",
            "Distinguish measured health and pollution indicators from inferred risks.",
            "health", ("health_coverage", "health_capacity", "pollution", "population"),
            ("Monitor healthcare capacity", "Identify coverage gaps", "Coordinate health risks"),
            severity=2,
        ))
