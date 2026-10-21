import json
import unittest

from python_agent.llm_reasoner import LLMReasoner, LLMReasonerError
from python_agent.models import CityState, Observation


class FakeClient:
    def __init__(self, response: str):
        self.response = response
        self.prompt = ""

    def complete(self, prompt: str) -> str:
        self.prompt = prompt
        return self.response


def city() -> CityState:
    return CityState("test-city", budget=500, metrics={"housing": 1})


class LLMReasonerTests(unittest.TestCase):
    def test_valid_response_becomes_approval_required_proposal(self):
        client = FakeClient(
            json.dumps(
                {
                    "proposals": [
                        {
                            "action": "prioritize_housing",
                            "parameters": {"phase": 1},
                            "reason": "Housing demand requires staged review.",
                            "cost": 100,
                            "agent_role": "mayor",
                        }
                    ]
                }
            )
        )

        proposals = LLMReasoner(client).propose(
            city(),
            [Observation("housing", "housing", "Demand is elevated", 2)],
        )

        self.assertEqual(proposals[0].action, "prioritize_housing")
        self.assertTrue(proposals[0].requires_approval)
        self.assertIn('"city_id": "test-city"', client.prompt)

    def test_invalid_json_is_rejected(self):
        with self.assertRaisesRegex(LLMReasonerError, "valid JSON"):
            LLMReasoner(FakeClient("not-json")).propose(city(), [])

    def test_unsupported_action_is_rejected(self):
        response = json.dumps({"proposals": [{"action": "build_road"}]})
        with self.assertRaisesRegex(LLMReasonerError, "Unsupported action"):
            LLMReasoner(FakeClient(response)).propose(city(), [])

    def test_cost_over_budget_is_rejected(self):
        response = json.dumps(
            {
                "proposals": [
                    {
                        "action": "prioritize_housing",
                        "reason": "Too expensive",
                        "cost": 501,
                    }
                ]
            }
        )
        with self.assertRaisesRegex(LLMReasonerError, "exceeds"):
            LLMReasoner(FakeClient(response)).propose(city(), [])


if __name__ == "__main__":
    unittest.main()
