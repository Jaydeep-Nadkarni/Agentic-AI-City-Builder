import json
import unittest
from pathlib import Path

from python_agent.actions import ActionDispatcher
from python_agent.history import History
from python_agent.llm_client import GroqClientError
from python_agent.llm_reasoner import LLMReasoner
from python_agent.observation_bridge import ObservationValidationError
from python_agent.planner import Planner
from python_agent.registry import build_registry
from python_agent.shadow import ShadowModePipeline
from python_agent.orchestrator import Orchestrator


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "simulated_city_state.json"
)


class FailingClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, _prompt: str) -> str:
        self.calls += 1
        raise GroqClientError("simulated Groq outage")


class EndToEndShadowTests(unittest.TestCase):
    def load_fixture(self) -> dict:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def create_pipeline(self, history: History, client: FailingClient):
        registry = build_registry("specialist")
        orchestrator = Orchestrator(
            registry,
            Planner(max_actions=3, budget=1000),
            history=history,
            reasoner=LLMReasoner(client),
            llm_enabled=True,
        )
        return ShadowModePipeline(orchestrator, history=history)

    def test_fixture_to_audit_record_with_groq_failure(self):
        history = History()
        client = FailingClient()
        pipeline = self.create_pipeline(history, client)

        proposals = pipeline.cycle(self.load_fixture())
        audit = pipeline.last_diagnostics

        self.assertEqual(len(pipeline.orchestrator.registry), 16)
        self.assertTrue(audit["simulated"])
        self.assertEqual(audit["source"]["kind"], "fixture")
        self.assertEqual(audit["snapshot_id"], "simulated-city-001")
        self.assertGreater(audit["observations"], 0)
        self.assertTrue(audit["diagnostics"]["activated"])
        self.assertEqual(client.calls, 1)
        self.assertIn("simulated Groq outage", audit["diagnostics"]["llm_error"])
        self.assertEqual(audit["execution"], "not executed")
        self.assertFalse(audit["execution_enabled"])
        self.assertTrue(all(proposal.requires_approval for proposal in proposals))
        self.assertEqual(history.recent(1)[0]["type"], "shadow_cycle")

    def test_rejected_snapshot_is_audited_and_does_not_dispatch(self):
        history = History()
        client = FailingClient()
        pipeline = self.create_pipeline(history, client)
        invalid = self.load_fixture()
        invalid["observations"]["budget"] = "not-a-number"

        dispatch_calls = []
        original_dispatch = ActionDispatcher.dispatch

        def record_dispatch(*args, **kwargs):
            dispatch_calls.append((args, kwargs))
            raise AssertionError("shadow pipeline must not dispatch")

        ActionDispatcher.dispatch = record_dispatch
        try:
            with self.assertRaises(ObservationValidationError):
                pipeline.cycle(invalid)
        finally:
            ActionDispatcher.dispatch = original_dispatch

        audit = history.recent(1)[0]
        self.assertEqual(audit["type"], "shadow_cycle")
        self.assertEqual(audit["status"], "rejected")
        self.assertFalse(audit["simulated"])
        self.assertFalse(audit["execution_enabled"])
        self.assertEqual(dispatch_calls, [])
        self.assertEqual(client.calls, 0)


if __name__ == "__main__":
    unittest.main()
