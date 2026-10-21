"""Read-only adapter for explicitly simulated city observations.

This module intentionally does not provide a TheoTown transport.  Its input is
an auditable, versioned fixture/snapshot envelope that can be used by tests and
shadow planning.
"""
from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any, Mapping

from .models import CityState


class ObservationValidationError(ValueError):
    """Raised when an observation envelope is malformed or untrusted."""


@dataclass(frozen=True)
class ObservationSnapshot:
    state: CityState
    snapshot_id: str
    source: Mapping[str, Any]
    simulated: bool
    captured_at: str

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "source": dict(self.source),
            "simulated": self.simulated,
            "captured_at": self.captured_at,
        }

    @property
    def provenance(self) -> Mapping[str, Any]:
        """Compatibility name for callers that refer to source provenance."""
        return self.source


class ObservationBridge:
    """Validate and map a simulated snapshot without ever executing actions."""

    _ROOT = {"snapshot_id", "source", "captured_at", "observations"}
    _SOURCE = {"name", "kind", "simulated", "version"}
    _OBSERVATIONS = {
        "city_id", "population", "budget", "happiness", "metrics",
        "available_services",
    }

    def ingest(self, payload: Mapping[str, Any]) -> ObservationSnapshot:
        if not isinstance(payload, Mapping):
            raise ObservationValidationError("observation payload must be an object")
        self._keys(payload, self._ROOT, "payload")
        snapshot_id = self._text(payload.get("snapshot_id"), "snapshot_id")
        source = payload.get("source")
        if not isinstance(source, Mapping):
            raise ObservationValidationError("source must be an object")
        self._keys(source, self._SOURCE, "source")
        source_name = self._text(source.get("name"), "source.name")
        source_kind = self._text(source.get("kind"), "source.kind")
        if source_kind not in {"fixture", "simulated"}:
            raise ObservationValidationError("only simulated fixture sources are supported")
        if source.get("simulated") is not True:
            raise ObservationValidationError("source.simulated must be true")
        captured_at = self._text(payload.get("captured_at"), "captured_at")
        observations = payload.get("observations")
        if not isinstance(observations, Mapping):
            raise ObservationValidationError("observations must be an object")
        self._keys(observations, self._OBSERVATIONS, "observations")
        city_id = self._text(observations.get("city_id"), "observations.city_id")
        population = self._integer(observations.get("population"), "observations.population")
        budget = self._integer(observations.get("budget"), "observations.budget")
        happiness = self._number(observations.get("happiness"), "observations.happiness")
        metrics = observations.get("metrics")
        if not isinstance(metrics, Mapping):
            raise ObservationValidationError("observations.metrics must be an object")
        clean_metrics: dict[str, float] = {}
        for name, value in metrics.items():
            if not isinstance(name, str) or not name.strip():
                raise ObservationValidationError("metric names must be non-empty strings")
            clean_metrics[name] = self._number(value, f"observations.metrics.{name}")
        services = observations.get("available_services", [])
        if not isinstance(services, (list, tuple)) or not all(isinstance(x, str) for x in services):
            raise ObservationValidationError("available_services must be a list of strings")
        clean_source = dict(source)
        clean_source["name"] = source_name
        return ObservationSnapshot(
            CityState(city_id, population, budget, happiness, clean_metrics, frozenset(services)),
            snapshot_id, clean_source, True, captured_at,
        )

    @staticmethod
    def _keys(value: Mapping[str, Any], allowed: set[str], label: str) -> None:
        unknown = set(value) - allowed
        if unknown:
            raise ObservationValidationError(f"unknown {label} field(s): {', '.join(sorted(unknown))}")

    @staticmethod
    def _text(value: Any, label: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ObservationValidationError(f"{label} must be a non-empty string")
        return value

    @staticmethod
    def _integer(value: Any, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ObservationValidationError(f"{label} must be an integer")
        return value

    @staticmethod
    def _number(value: Any, label: str) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ObservationValidationError(f"{label} must be numeric")
        return float(value)


def load_observation(payload: Mapping[str, Any]) -> ObservationSnapshot:
    """Convenience adapter entry point for callers that do not need an instance."""
    return ObservationBridge().ingest(payload)


ObservationAdapter = ObservationBridge


__all__ = [
    "ObservationBridge", "ObservationAdapter", "ObservationSnapshot", "ObservationValidationError",
    "load_observation",
]
