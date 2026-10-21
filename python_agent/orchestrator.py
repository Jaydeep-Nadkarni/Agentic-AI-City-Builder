"""One deterministic observation/planning cycle."""
from __future__ import annotations
from .history import History
from .llm_reasoner import LLMReasoner, LLMReasonerError
from .models import CityState, Proposal
from .planner import Planner
from .registry import Agent

class Orchestrator:
    def __init__(self, registry: dict[str, Agent], planner: Planner,
                 history: History | None = None, reasoner: LLMReasoner | None = None,
                 llm_enabled: bool = False) -> None:
        self.registry, self.planner, self.history = registry, planner, history or History()
        self.reasoner, self.llm_enabled = reasoner, llm_enabled
        self.last_diagnostics: dict = {}

    def cycle(self, state: CityState) -> list[Proposal]:
        observations = []
        activated, skipped = [], {}
        for role, agent in self.registry.items():
            try:
                result = agent.observe(state)
            except Exception as exc:
                self.last_diagnostics = {
                    "city_id": state.city_id, "status": "failure",
                    "failed_role": role, "error": type(exc).__name__,
                }
                self.history.record_cycle(self.last_diagnostics)
                raise
            if result is None:
                relevant = getattr(getattr(agent, "config", None), "relevant_metrics", ())
                missing = [metric for metric in relevant if metric not in state.metrics]
                skipped[role] = (
                    "missing metrics: " + ", ".join(missing)
                    if missing else "no relevant threshold evidence"
                )
            else:
                observations.append(result)
                activated.append(role)
        proposals = self.planner.plan(state, observations)
        llm_proposals: list[Proposal] = []
        llm_error = None
        if self.llm_enabled and self.reasoner and observations:
            try:
                llm_proposals = self.reasoner.propose(state, observations)
            except LLMReasonerError as exc:
                llm_error = str(exc)
        combined, rejected = self.planner.finalize(state, proposals + llm_proposals)
        conflicts = self.planner.detect_conflicts(combined)
        if conflicts:
            rejected.extend({"proposal_id": p.proposal_id, "reason": "cycle conflict: " + ", ".join(conflicts)}
                            for p in combined)
            combined = []
        self.last_diagnostics = {
            "city_id": state.city_id, "considered": list(self.registry),
            "activated": activated, "skipped": skipped,
            "observations": len(observations), "llm_called": bool(self.llm_enabled and self.reasoner and observations),
            "observation_details": [o.__dict__ for o in observations],
            "llm_error": llm_error, "accepted": [p.action for p in combined],
            "proposals": [p.action for p in combined],
            "rejected": rejected, "conflicts": conflicts,
        }
        self.history.record_cycle(self.last_diagnostics)
        return combined
