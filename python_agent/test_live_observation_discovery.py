import json
import unittest
from pathlib import Path

from python_agent.observation_bridge import ObservationBridge, ObservationValidationError


ROOT = Path(__file__).resolve().parents[1]


class LiveObservationDiscoveryTests(unittest.TestCase):
    def test_capability_inventory_marks_transport_unverified(self):
        inventory = json.loads(
            (ROOT / "bridge" / "capabilities.json").read_text(encoding="utf-8")
        )
        self.assertFalse(inventory["transport_verified"])
        statuses = {item["name"]: item["status"] for item in inventory["capabilities"]}
        self.assertEqual(statuses["city_read_metrics"], "documented")
        self.assertEqual(statuses["read_only_observation_display"], "experimental")
        self.assertEqual(statuses["http_transport"], "unsupported")

    def test_live_claim_is_rejected_until_transport_is_verified(self):
        payload = json.loads(
            (ROOT / "tests" / "fixtures" / "theotown_probe_unverified.json").read_text(
                encoding="utf-8"
            )
        )
        with self.assertRaises(ObservationValidationError):
            ObservationBridge().ingest(payload)

    def test_isolated_probe_files_exist_without_touching_baseline(self):
        probe = ROOT / "plugin" / "observation probe"
        self.assertTrue((probe / "observation.json").is_file())
        source = (probe / "observer.lua").read_text(encoding="utf-8")
        self.assertIn("City.getPeople", source)
        self.assertIn("City.getMoney", source)
        self.assertIn("Runtime.toJson", source)
        self.assertNotIn("ActionDispatcher", source)
        baseline = ROOT / "plugin" / "scripting test" / "myscript.lua"
        self.assertIn("Hello World!", baseline.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
