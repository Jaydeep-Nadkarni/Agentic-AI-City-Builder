"""Structured Groq reasoning for bounded planning proposals."""

from __future__ import annotations

import json
from typing import Any

from .actions import ALLOWLIST
from .llm_client import GroqClient, GroqClientError
from .models import CityState, Observation, Proposal


ALLOWED_ACTIONS = frozenset(
    {"review_budget", "prioritize_housing", "inspect_transport"}
)


class LLMReasonerError(ValueError):
    """Raised when the model response is unavailable or invalid."""


class LLMReasoner:
    def __init__(self, client: GroqClient) -> None:
        self.client = client

    def propose(
        self,
        state: CityState,
        observations: list[Observation],
    ) -> list[Proposal]:
        context = {
            "city": {
                "city_id": state.city_id,
                "population": state.population,
                "budget": state.budget,
                "happiness": state.happiness,
                "metrics": dict(state.metrics),
                "available_services": sorted(state.available_services),
            },
            "observations": [
                {
                    "agent_role": observation.agent_role,
                    "topic": observation.topic,
                    "summary": observation.summary,
                    "severity": observation.severity,
                    "data": dict(observation.data),
                }
                for observation in observations
            ],
        }
        prompt = (
            "You are the Mayor AI assisting a city planner. Return JSON only, "
            "with this shape: {\"proposals\": [{\"action\": \"review_budget\", "
            "\"parameters\": {}, \"reason\": \"Short evidence-based reason\", "
            "\"cost\": 0, \"agent_role\": \"mayor\"}]}. "
            "Allowed actions are exactly: review_budget, prioritize_housing, "
            "inspect_transport. Costs must be non-negative integers and must "
            "not exceed the city's stated budget. Use concise reasons. Do not "
            "include Markdown fences. Input data: "
            + json.dumps(context, ensure_ascii=False, sort_keys=True)
        )

        try:
            raw = self.client.complete(prompt)
        except GroqClientError as exc:
            raise LLMReasonerError(f"LLM request failed: {exc}") from exc

        try:
            result: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMReasonerError("LLM did not return valid JSON") from exc

        if not isinstance(result, dict) or not isinstance(
            result.get("proposals"), list
        ):
            raise LLMReasonerError("Expected an object containing a proposals list")

        proposals: list[Proposal] = []
        for index, item in enumerate(result["proposals"]):
            proposals.append(self._parse_proposal(item, state, index))
        return proposals

    @staticmethod
    def _parse_proposal(
        item: Any,
        state: CityState,
        index: int,
    ) -> Proposal:
        if not isinstance(item, dict):
            raise LLMReasonerError(f"Proposal {index} must be an object")

        action = item.get("action")
        parameters = item.get("parameters", {})
        reason = item.get("reason", "")
        agent_role = item.get("agent_role", "mayor")
        cost = item.get("cost", 0)

        if action not in ALLOWED_ACTIONS or action not in ALLOWLIST:
            raise LLMReasonerError(f"Unsupported action: {action!r}")
        if not isinstance(parameters, dict):
            raise LLMReasonerError("Proposal parameters must be an object")
        if not isinstance(reason, str) or not reason.strip():
            raise LLMReasonerError("Proposal reason must be non-empty text")
        if not isinstance(agent_role, str) or not agent_role.strip():
            raise LLMReasonerError("agent_role must be non-empty text")
        if type(cost) is not int or cost < 0:
            raise LLMReasonerError(
                "Proposal cost must be a non-negative integer"
            )
        if cost > state.budget:
            raise LLMReasonerError("Proposal cost exceeds the city budget")

        return Proposal(
            proposal_id=f"llm-{state.city_id}-{index + 1}",
            action=action,
            parameters=parameters,
            reason=reason.strip(),
            cost=cost,
            agent_role=agent_role.strip(),
            requires_approval=True,
        )
