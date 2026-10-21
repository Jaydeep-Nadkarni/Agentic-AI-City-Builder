"""City Intelligence and Audit AI configuration."""
from .base import AgentConfig, SpecialistAgent


class CityIntelligenceAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "city_intelligence", "City Intelligence and Audit AI",
            "Audit observations and proposals for missing, stale, duplicate, or conflicting evidence.",
            "audit", ("data_freshness", "proposal_conflicts", "observation_quality"),
            ("Detect inconsistent state", "Check policy compliance", "Recommend human review"),
            severity=3,
        ))
