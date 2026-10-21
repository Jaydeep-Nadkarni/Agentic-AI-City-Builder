"""Energy and Utilities AI configuration."""
from .base import AgentConfig, SpecialistAgent


class EnergyUtilitiesAgent(SpecialistAgent):
    def __init__(self) -> None:
        super().__init__(AgentConfig(
            "energy_utilities", "Energy and Utilities AI",
            "Evaluate measured utility capacity and shortages without fabricating supply data.",
            "utilities", ("electricity_capacity", "electricity_demand", "utility_capacity"),
            ("Monitor supply", "Identify capacity constraints", "Check infrastructure dependencies"),
            severity=2,
        ))
