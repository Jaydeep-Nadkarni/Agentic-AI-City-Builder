"""Education and Community AI configuration."""
from .base import AgentConfig, SpecialistAgent


class EducationCommunityAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "education_community", "Education and Community AI",
            "Evaluate measured school and community-service capacity against population needs.",
            "education", ("school_coverage", "school_capacity", "population", "community_services"),
            ("Evaluate education coverage", "Identify capacity gaps", "Coordinate population growth"),
            severity=1,
        ))
