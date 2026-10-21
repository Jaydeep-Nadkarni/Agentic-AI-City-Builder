"""Traffic and Transportation AI configuration."""
from .base import AgentConfig, SpecialistAgent


class TrafficTransportAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "traffic_transport", "Traffic and Transportation AI",
            "Analyze measured traffic indicators and report uncertainty when congestion data is absent.",
            "transport", ("congestion", "traffic_flow", "road_connectivity"),
            ("Identify congestion", "Recommend connectivity improvements", "Measure outcomes when data exists"),
            severity=2,
        ))
