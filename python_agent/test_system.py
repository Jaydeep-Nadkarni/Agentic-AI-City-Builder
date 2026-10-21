import unittest

from python_agent.actions import ActionValidationError, proposal_to_action
from python_agent.config import ConfigError, Settings
from python_agent.history import History
from python_agent.models import Action, CityState, Observation, Proposal
from python_agent.orchestrator import Orchestrator
from python_agent.planner import Planner
from python_agent.registry import ROLES, RuleAgent, default_registry, register


class SystemTests(unittest.TestCase):
    def test_registry_has_sixteen_roles_and_rejects_duplicates(self):
        registry = default_registry()
        self.assertEqual(len(registry), 16)
        self.assertEqual(set(registry), set(ROLES))
        with self.assertRaises(ValueError):
            register(registry, RuleAgent("budget", "budget", "budget", 1, "duplicate"))

    def test_config_validation_and_env_override(self):
        settings = Settings.load("config/settings.json", {"GROQ_MODEL": "test-model"})
        self.assertEqual(settings.groq_model, "test-model")
        with self.assertRaises(ConfigError):
            Settings.load("config/settings.json", {"GROQ_TIMEOUT_SECONDS": "bad"})

    def test_action_allowlist_requires_approval(self):
        proposal = Proposal("p", "review_budget", {}, "inspect", 0)
        with self.assertRaises(ActionValidationError):
            proposal_to_action(proposal)
        self.assertEqual(proposal_to_action(proposal, True).name, "review_budget")
        with self.assertRaises(ActionValidationError):
            proposal_to_action(Proposal("p", "build_road", {}, "unsupported"), True)

    def test_budget_enforcement_and_conflicts(self):
        state = CityState("c", budget=100, metrics={})
        observations = [Observation("housing", "housing", "need", 2),
                        Observation("transport", "transport", "need", 1)]
        proposals = Planner(budget=100).plan(state, observations)
        self.assertEqual([p.action for p in proposals], ["prioritize_housing"])
        conflict = [Proposal("1", "prioritize_housing", {}, "", 100),
                    Proposal("2", "inspect_transport", {}, "", 50)]
        self.assertTrue(Planner.detect_conflicts(conflict))

    def test_orchestrator_mock_cycle_is_selective_and_records_history(self):
        registry = {"housing": RuleAgent("housing", "housing", "housing", 1, "need")}
        history = History()
        proposals = Orchestrator(registry, Planner(budget=200), history).cycle(
            CityState("city", budget=200, metrics={"housing": 1}))
        self.assertEqual(len(proposals), 1)
        self.assertEqual(history.recent()[0]["proposals"], ["prioritize_housing"])


if __name__ == "__main__":
    unittest.main()
