"""Shared immutable models exchanged by agents, planners, and the dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CityState:
    city_id: str
    population: int = 0
    budget: int = 0
    happiness: float = 0.0
    metrics: Mapping[str, float] = field(default_factory=dict)
    available_services: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Observation:
    agent_role: str
    topic: str
    summary: str
    severity: int = 0
    data: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    action: str
    parameters: Mapping[str, Any]
    reason: str
    cost: int = 0
    agent_role: str = ""
    requires_approval: bool = True
    available: bool = True
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class Action:
    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    cost: int = 0


@dataclass(frozen=True)
class Message:
    sender: str
    recipient: str
    kind: str
    payload: Mapping[str, Any]
    created_at: str = field(default_factory=utc_now)

