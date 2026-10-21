import json
import unittest

from python_agent.agents import (
    CityIntelligenceAgent,
    DisasterManagementAgent,
    EconomyIndustryAgent,
    EducationCommunityAgent,
    EnergyUtilitiesAgent,
    EnvironmentSustainabilityAgent,
    FireEmergencyAgent,
    FinanceTreasuryAgent,
    HighwayConstructionAgent,
    HousingPopulationAgent,
    MayorAgent,
    PublicHealthAgent,
    PublicSafetyAgent,
    TrafficTransportAgent,
    UrbanPlanningAgent,
    WaterSanitationAgent,
)
from python_agent.llm_reasoner import LLMReasoner
from python_agent.models import CityState


class FakeClient:
    def complete(self, prompt: str) -> str:
        self.prompt = prompt
        return json.dumps({"proposals": []})


class AgentTests(unittest.TestCase):
    def test_all_sixteen_specialists_have_unique_roles(self):
        agents = [
            MayorAgent(), UrbanPlanningAgent(), HousingPopulationAgent(),
            EconomyIndustryAgent(), HighwayConstructionAgent(),
            TrafficTransportAgent(), EnergyUtilitiesAgent(),
            WaterSanitationAgent(), DisasterManagementAgent(),
            FireEmergencyAgent(), PublicSafetyAgent(), PublicHealthAgent(),
            EducationCommunityAgent(), EnvironmentSustainabilityAgent(),
            FinanceTreasuryAgent(), CityIntelligenceAgent(),
        ]
        self.assertEqual(len(agents), 16)
        self.assertEqual(len({agent.role for agent in agents}), 16)

    def test_three_agents_have_distinct_contracts(self):
        agents = [MayorAgent(), FinanceTreasuryAgent(), UrbanPlanningAgent()]
        self.assertEqual(
            {agent.role for agent in agents},
            {"mayor", "finance_treasury", "urban_planning"},
        )
        self.assertEqual(len({agent.config.system_prompt for agent in agents}), 3)

    def test_agents_report_only_relevant_metrics(self):
        observation = FinanceTreasuryAgent().observe(
            CityState("city", budget=100, metrics={"budget": 1, "housing": 99})
        )
        self.assertIsNotNone(observation)
        self.assertEqual(observation.data["metrics"], {"budget": 1})
        self.assertNotIn("housing", observation.data["metrics"])

    def test_missing_metrics_are_reported_without_inventing_values(self):
        observation = WaterSanitationAgent().observe(
            CityState("city", metrics={"water_capacity": 1})
        )
        self.assertIsNotNone(observation)
        self.assertIn("water_demand", observation.data["missing_metrics"])
        self.assertNotIn("water_demand", observation.data["metrics"])

    def test_specialists_do_not_activate_without_relevant_evidence(self):
        state = CityState("city", metrics={"unrelated_metric": 999})
        for agent in (
            HighwayConstructionAgent(),
            PublicHealthAgent(),
            EnvironmentSustainabilityAgent(),
            CityIntelligenceAgent(),
        ):
            self.assertIsNone(agent.observe(state), agent.role)

    def test_reasoning_uses_shared_reasoner_and_role_context(self):
        client = FakeClient()
        agent = UrbanPlanningAgent()
        proposals = agent.reason(
            LLMReasoner(client),
            CityState("city", budget=100),
            [],
        )
        self.assertEqual(proposals, [])
        self.assertIn("Urban Planning AI", client.prompt)
        self.assertIn("buildable", client.prompt)


if __name__ == "__main__":
    unittest.main()
