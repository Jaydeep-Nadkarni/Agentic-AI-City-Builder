"""Local dashboard for the AI city-planning system."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from bridge.protocol import as_dict as bridge_details
from python_agent.config import Settings
from python_agent.history import History
from python_agent.llm_client import GroqClient, GroqSettings
from python_agent.llm_reasoner import LLMReasoner
from python_agent.models import CityState
from python_agent.orchestrator import Orchestrator
from python_agent.planner import Planner
from python_agent.registry import build_registry
from python_agent.observation_bridge import ObservationBridge
from python_agent.shadow import ShadowModePipeline


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent


def _json_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _json_value(item) for key, item in asdict(value).items()}
    if isinstance(value, (set, frozenset, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value


class DashboardState:
    """Owns the state displayed by the dashboard process."""

    def __init__(self, settings_path: Path | str = PROJECT_ROOT / "config" / "settings.json"):
        self.settings = Settings.load(settings_path)
        self.registry = build_registry(
            self.settings.agent_mode,
            self.settings.enabled_specialist_roles,
        )
        self.history = History(str(PROJECT_ROOT / self.settings.history_path))
        self.planner = Planner(
            self.settings.max_actions_per_cycle,
            self.settings.cycle_budget,
            self.settings.approval_required,
        )
        reasoner = None
        api_key = os.getenv("GROQ_API_KEY")
        if self.settings.llm_enabled and api_key:
            reasoner = LLMReasoner(
                GroqClient(
                    api_key,
                    GroqSettings(
                        endpoint=self.settings.groq_endpoint,
                        model=self.settings.groq_model,
                        timeout_seconds=self.settings.groq_timeout_seconds,
                    ),
                )
            )
        self.orchestrator = Orchestrator(
            self.registry,
            self.planner,
            self.history,
            reasoner=reasoner,
            llm_enabled=self.settings.llm_enabled,
        )
        self.observation_bridge = ObservationBridge()
        fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "simulated_city_state.json"
        with fixture_path.open(encoding="utf-8") as handle:
            self.snapshot_payload = json.load(handle)
        snapshot = self.observation_bridge.ingest(self.snapshot_payload)
        self.city = snapshot.state
        self.snapshot_metadata = snapshot.metadata
        self.shadow_pipeline = ShadowModePipeline(
            self.orchestrator, self.observation_bridge, self.history
        )
        self.proposals: list[Any] = []
        self.last_cycle: str | None = None

    def run_cycle(self) -> list[dict[str, Any]]:
        self.proposals = self.shadow_pipeline.cycle(self.snapshot_payload)
        self.last_cycle = self.history.recent(1)[0].get("created_at") if self.history.recent(1) else None
        return [_json_value(proposal) for proposal in self.proposals]

    def overview(self) -> dict[str, Any]:
        return {
            "status": "online",
            "city": _json_value(self.city),
            "agents": [
                {
                    "role": role,
                    "name": role.replace("_", " ").title(),
                    "active": True,
                    "type": type(agent).__name__,
                }
                for role, agent in self.registry.items()
            ],
            "proposals": [_json_value(proposal) for proposal in self.proposals],
            "history": self.history.recent(25),
            "bridge": bridge_details(),
            "observation": self.snapshot_metadata,
            "shadow_mode": self.shadow_pipeline.shadow_mode,
            "execution_enabled": self.shadow_pipeline.execution_enabled,
            "latest_diagnostics": self.shadow_pipeline.last_diagnostics,
            "last_cycle": self.last_cycle,
            "config": {
                "model": self.settings.groq_model,
                "approval_required": self.settings.approval_required,
                "max_actions_per_cycle": self.settings.max_actions_per_cycle,
                "cycle_budget": self.settings.cycle_budget,
                "dashboard_host": self.settings.dashboard_host,
                "dashboard_port": self.settings.dashboard_port,
                "agent_mode": self.settings.agent_mode,
                "llm_enabled": self.settings.llm_enabled,
                "llm_configured": reasoner is not None,
            },
        }


def make_handler(state: DashboardState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: Any, status_code: int = 200) -> None:
            body = json.dumps(_json_value(payload)).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path, content_type: str) -> None:
            try:
                body = path.read_bytes()
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            route = urlparse(self.path).path
            if route in {"/", "/index.html"}:
                self._send_file(ROOT / "index.html", "text/html; charset=utf-8")
            elif route == "/static/style.css":
                self._send_file(ROOT / "static" / "style.css", "text/css; charset=utf-8")
            elif route == "/static/app.js":
                self._send_file(ROOT / "static" / "app.js", "text/javascript; charset=utf-8")
            elif route in {"/api/overview", "/health"}:
                self._send_json(state.overview())
            elif route == "/api/proposals":
                self._send_json({"proposals": state.overview()["proposals"]})
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            route = urlparse(self.path).path
            if route != "/api/cycles":
                self.send_error(404)
                return
            try:
                self._send_json({"proposals": state.run_cycle()})
            except (OSError, ValueError) as exc:
                self._send_json({"error": str(exc)}, 500)

        def log_message(self, *_args: Any) -> None:
            return

    return Handler


def serve(
    host: str = "127.0.0.1",
    port: int = 8765,
    state: DashboardState | None = None,
) -> None:
    dashboard_state = state or DashboardState()
    server = ThreadingHTTPServer((host, port), make_handler(dashboard_state))
    print(f"Dashboard available at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    settings = Settings.load(PROJECT_ROOT / "config" / "settings.json")
    serve(settings.dashboard_host, settings.dashboard_port)
