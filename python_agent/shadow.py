"""Auditable, read-only shadow planning pipeline."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .history import History
from .observation_bridge import ObservationBridge, ObservationSnapshot
from .models import utc_now
from .orchestrator import Orchestrator


class ShadowModePipeline:
    """Ingest simulated snapshots and produce proposals, never dispatching them."""

    execution_enabled = False
    shadow_mode = True

    def __init__(
        self, orchestrator: Orchestrator, bridge: ObservationBridge | None = None,
        history: History | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.bridge = bridge or ObservationBridge()
        self.history = history or orchestrator.history
        self.last_diagnostics: dict[str, Any] = {}

    def cycle(self, payload: Mapping[str, Any]) -> list[Any]:
        try:
            snapshot = self.bridge.ingest(payload)
        except Exception as exc:
            diagnostics = {
                "type": "shadow_cycle", "status": "rejected",
                "snapshot_id": payload.get("snapshot_id") if isinstance(payload, Mapping) else None,
                "source": payload.get("source") if isinstance(payload, Mapping) else None,
                "simulated": False, "observations": [], "proposals": [],
                "validation": {"rejected": True, "error": str(exc)},
                "execution_enabled": False, "shadow_mode": True,
                "execution": "not executed", "created_at": utc_now(),
            }
            self.last_diagnostics = diagnostics
            self.history.record_cycle(diagnostics)
            raise
        proposals = self.orchestrator.cycle(snapshot.state)
        base = dict(self.orchestrator.last_diagnostics)
        diagnostics = {
            "type": "shadow_cycle", "status": "ok",
            "snapshot_id": snapshot.snapshot_id, "source": dict(snapshot.source),
            "simulated": snapshot.simulated, "metadata": snapshot.metadata,
            "observations": base.get("observations", 0),
            "observation_details": base.get("observation_details", []),
            "proposals": [p.action for p in proposals],
            "proposal_details": [p.__dict__ for p in proposals],
            "validation": {"rejected": base.get("rejected", [])},
            "diagnostics": base,
            "execution_enabled": False, "shadow_mode": True,
            "execution": "not executed", "created_at": utc_now(),
        }
        self.last_diagnostics = diagnostics
        self.history.record_cycle(diagnostics)
        return proposals


ShadowPipeline = ShadowModePipeline
ShadowOrchestrator = ShadowModePipeline

__all__ = ["ShadowModePipeline", "ShadowPipeline", "ShadowOrchestrator"]
