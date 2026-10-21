# TheoTown Python agent

This is a dependency-free planning layer. It validates configuration, emits structured
logs, shares typed city models, registers 16 roles over one interface, and produces
deterministic proposals with allowlisting, manual approval, conflicts, and budgets.
The Groq client is optional and remains the only external integration. No TheoTown
bridge is claimed: game actions are explicitly unavailable.

Run from the repository root:

```powershell
python -m unittest discover -s python_agent -p "test*.py"
python -m py_compile python_agent\*.py dashboard\*.py bridge\*.py
```

The stdlib dashboard is a browser-based command center. Start it from the repository
root with:

```powershell
python -m dashboard.app
```

Then open `http://127.0.0.1:8765`. It displays agent registration, city-state values,
planning proposals, audit history, configuration, and bridge readiness. Use **Run
planning cycle** to execute the local deterministic planner. The dashboard does not claim TheoTown control: the bridge remains explicitly
unavailable until a real transport is verified. See
[bridge/README.md](bridge/README.md) and
[bridge/capabilities.json](bridge/capabilities.json) for the verified capability
inventory.
