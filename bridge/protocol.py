"""Verified TheoTown bridge capability inventory.

This module deliberately separates documented Lua capabilities from unsupported
transport assumptions. No Python-to-game connection is claimed here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Capability:
    name: str
    status: str
    evidence: str
    limitation: str = ""


@dataclass(frozen=True)
class BridgeStatus:
    available: bool
    reason: str
    capabilities: tuple[Capability, ...]


CAPABILITIES = (
    Capability(
        "plugin_scripts",
        "verified",
        "Official scripting quick-start and Script module",
        "Requires a JSON plugin object referencing a Lua script.",
    ),
    Capability(
        "persistent_plugin_storage",
        "documented",
        "TheoTown.getFileStorage() and TheoTown.getStorage()",
        "Storage is game-managed; it is not arbitrary host filesystem access.",
    ),
    Capability(
        "in_game_command_registration",
        "documented",
        "TheoTown.registerCommand(name, action)",
        "Commands are entered inside TheoTown and are not a Python transport.",
    ),
    Capability(
        "http_transport",
        "unsupported",
        "No HTTP API is listed in the official Lua module reference",
        "Do not use LuaSocket or require() unless verified in the target build.",
    ),
    Capability(
        "socket_transport",
        "unsupported",
        "No TCP/UDP socket API is listed in the official Lua module reference",
        "A third-party socket library has not been demonstrated in TheoTown.",
    ),
    Capability(
        "arbitrary_filesystem_ipc",
        "unsupported",
        "The documented storage APIs do not expose arbitrary file paths",
        "File-manager imports are manual deployment, not a live bridge.",
    ),
)


def status() -> BridgeStatus:
    return BridgeStatus(
        available=False,
        reason=(
            "No documented live Python transport is available. "
            "Only game-managed storage and in-game commands are documented."
        ),
        capabilities=CAPABILITIES,
    )


def as_dict() -> dict:
    current = status()
    return {
        "available": current.available,
        "reason": current.reason,
        "capabilities": [asdict(capability) for capability in current.capabilities],
    }
