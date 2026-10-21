"""Disaster Management AI configuration."""
from .base import AgentConfig, SpecialistAgent


class DisasterManagementAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "disaster_management", "Disaster Management AI",
            "Assess observed disaster indicators and clearly label forecasts as unavailable.",
            "disaster", ("disaster_risk", "active_incidents", "emergency_access"),
            ("Assess preparedness", "Prioritize emergency access", "Coordinate recovery evidence"),
            severity=3,
        ))
