import json
import unittest
from pathlib import Path

from python_agent.actions import ActionDispatcher
from python_agent.history import History
from python_agent.observation_bridge import (
    ObservationBridge,
    ObservationValidationError,
)
from python_agent.planner import Planner
from python_agent.registry import build_registry
from python_agent.shadow import ShadowModePipeline
from python_agent.orchestrator import Orchestrator


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
    / "simulated_city_state.json"
)


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class ObservationShadowTests(unittest.TestCase):
    def test_fixture_is_ingested_with_simulation_provenance(self):
        snapshot = ObservationBridge().ingest(load_fixture())

        self.assertEqual(snapshot.snapshot_id, "simulated-city-001")
        self.assertTrue(snapshot.simulated)
        self.assertEqual(snapshot.source["kind"], "fixture")
        self.assertEqual(snapshot.state.population, 12500)
        self.assertEqual(snapshot.state.metrics["housing"], 1.0)

    def test_unknown_fields_and_live_sources_are_rejected(self):
        payload = load_fixture()
        payload["unexpected"] = True
        with self.assertRaises(ObservationValidationError):
            ObservationBridge().ingest(payload)

        payload = load_fixture()
        payload["source"]["simulated"] = False
        with self.assertRaises(ObservationValidationError):
            ObservationBridge().ingest(payload)

    def test_malformed_metrics_are_rejected(self):
        payload = load_fixture()
        payload["observations"]["metrics"]["housing"] = "unknown"
        with self.assertRaises(ObservationValidationError):
            ObservationBridge().ingest(payload)

    def test_shadow_cycle_records_recommendations_and_no_execution(self):
        history = History()
        orchestrator = Orchestrator(
            build_registry("legacy"),
            Planner(budget=1000),
            history,
        )
        pipeline = ShadowModePipeline(orchestrator, history=history)
        proposals = pipeline.cycle(load_fixture())

        self.assertTrue(pipeline.shadow_mode)
        self.assertFalse(pipeline.execution_enabled)
        self.assertTrue(proposals)
        audit = pipeline.last_diagnostics
        self.assertEqual(audit["snapshot_id"], "simulated-city-001")
        self.assertTrue(audit["simulated"])
        self.assertEqual(audit["execution"], "not executed")
        self.assertEqual(history.recent(1)[0]["type"], "shadow_cycle")
        self.assertTrue(history.recent(1)[0]["proposal_details"])

    def test_shadow_pipeline_never_calls_dispatcher(self):
        original = ActionDispatcher.dispatch

        def fail_if_called(*_args, **_kwargs):
            raise AssertionError("shadow mode must not dispatch actions")

        ActionDispatcher.dispatch = fail_if_called
        try:
            pipeline = ShadowModePipeline(
                Orchestrator(build_registry("legacy"), Planner(budget=1000))
            )
            pipeline.cycle(load_fixture())
        finally:
            ActionDispatcher.dispatch = original


if __name__ == "__main__":
    unittest.main()
