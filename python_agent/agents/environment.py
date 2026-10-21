"""Environment and Sustainability AI configuration."""
from .base import AgentConfig, SpecialistAgent


class EnvironmentSustainabilityAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "environment", "Environment and Sustainability AI",
            "Use measured pollution and environmental indicators and label unsupported impacts unknown.",
            "environment", ("pollution", "green_space", "waste", "emissions"),
            ("Monitor environmental conditions", "Compare sustainability trade-offs", "Coordinate health impacts"),
            severity=2,
        ))
