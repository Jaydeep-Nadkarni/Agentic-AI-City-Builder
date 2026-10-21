# TheoTown bridge feasibility

The current bridge is intentionally marked unavailable. TheoTown's documented
Lua API verifies scripts, game-managed storage, and in-game command registration,
but does not document HTTP, TCP/UDP sockets, or arbitrary filesystem access.

The authoritative inventory is in [capabilities.json](./capabilities.json), and
the typed Python representation is in [protocol.py](./protocol.py).

## What is verified

- A JSON plugin can load a Lua script.
- `TheoTown.getFileStorage()` and `TheoTown.getStorage()` provide persistent
  game-managed tables.
- `TheoTown.registerCommand()` can register a command handled inside the game.

## What remains unavailable

There is no verified live path for Python to send a message to Lua or for Lua
to send a message to Python. Do not add a network library or assume host file
access without testing it in the exact TheoTown/LDPlayer build.
