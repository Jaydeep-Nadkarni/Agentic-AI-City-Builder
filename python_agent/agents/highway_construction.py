"""Highway and Construction AI configuration."""
from .base import AgentConfig, SpecialistAgent


class HighwayConstructionAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "highway_construction", "Highway and Construction AI",
            "Analyze connectivity and construction gaps; never assume a valid build target.",
            "transport", ("road_connectivity", "construction_demand", "budget"),
            ("Identify road gaps", "Check construction feasibility", "Coordinate infrastructure priorities"),
            severity=2,
        ))
