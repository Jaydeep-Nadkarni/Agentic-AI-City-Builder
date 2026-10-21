"""Fire and Emergency Services AI configuration."""
from .base import AgentConfig, SpecialistAgent


class FireEmergencyAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "fire_emergency", "Fire and Emergency Services AI",
            "Evaluate measured emergency coverage and avoid inventing response statistics.",
            "emergency", ("fire_coverage", "emergency_access", "fire_incidents"),
            ("Evaluate service coverage", "Identify response gaps", "Protect critical access"),
            severity=3,
        ))
