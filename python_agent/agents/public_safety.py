"""Public Safety AI configuration."""
from .base import AgentConfig, SpecialistAgent


class PublicSafetyAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "public_safety", "Public Safety AI",
            "Use available safety coverage indicators and identify unknown crime data explicitly.",
            "safety", ("safety_coverage", "police_coverage", "crime_rate"),
            ("Evaluate coverage", "Recommend supported services", "Escalate missing safety data"),
            severity=2,
        ))
