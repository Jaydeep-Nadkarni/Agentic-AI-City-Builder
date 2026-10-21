import json
import unittest

from python_agent.actions import ActionDispatcher, ActionValidationError
from python_agent.history import History
from python_agent.llm_reasoner import LLMReasoner
from python_agent.models import CityState, Proposal
from python_agent.orchestrator import Orchestrator
from python_agent.planner import Planner
from python_agent.registry import build_registry


class Client:
    def __init__(self, response="not-json"):
        self.response, self.calls = response, 0

    def complete(self, prompt):
        self.calls += 1
        return self.response


class IntegrationTests(unittest.TestCase):
    def test_registration_modes_and_selective_activation(self):
        self.assertEqual(len(build_registry("legacy")), 16)
        self.assertEqual(len(build_registry("specialist")), 16)
        combined = build_registry("combined")
        self.assertEqual(len(combined), 32)
        history = History()
        result = Orchestrator(
            {"mayor": combined["mayor"]}, Planner(), history
        ).cycle(CityState("c", budget=100, metrics={"unrelated": 1}))
        self.assertEqual(result, [])
        self.assertEqual(history.recent()[0]["activated"], [])
        self.assertFalse(history.recent()[0]["llm_called"])

    def test_llm_failure_falls_back_and_records_diagnostics(self):
        client = Client()
        history = History()
        result = Orchestrator(
            {"mayor": build_registry("specialist")["mayor"]},
            Planner(budget=100),
            history,
            LLMReasoner(client),
            True,
        ).cycle(CityState("c", budget=100, metrics={"budget": 1}))
        self.assertEqual([p.action for p in result], ["review_budget"])
        self.assertEqual(client.calls, 1)
        self.assertIn("LLM did not return valid JSON", history.recent()[0]["llm_error"])

    def test_conflict_is_whole_cycle_and_dispatch_is_approval_gated(self):
        proposals = [
            Proposal("h", "prioritize_housing", {}, "h", 100),
            Proposal("t", "inspect_transport", {}, "t", 50),
        ]
        planner = Planner(budget=200)
        accepted, rejected = planner.finalize(CityState("c", budget=200), proposals)
        self.assertEqual(len(accepted), 2)
        self.assertTrue(planner.detect_conflicts(accepted))
        with self.assertRaises(ActionValidationError):
            ActionDispatcher().dispatch(accepted[0])
        self.assertEqual(ActionDispatcher().dispatch(accepted[0], True).name,
                         "prioritize_housing")

    def test_valid_llm_proposal_is_accepted_and_requires_approval(self):
        response = json.dumps({"proposals": [{
            "action": "review_budget", "reason": "observed deficit",
            "cost": 0, "agent_role": "mayor", "parameters": {},
        }]})
        client = Client(response)
        result = Orchestrator(
            {"mayor": build_registry("specialist")["mayor"]},
            Planner(budget=100), reasoner=LLMReasoner(client), llm_enabled=True,
        ).cycle(CityState("c", budget=100, metrics={"budget": 1}))
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].requires_approval)


if __name__ == "__main__":
    unittest.main()
