from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from bao.agent import plan
from bao.agent.tools.base import Tool
from bao.session.manager import SessionManager


class _PlanToolBase:
    def __init__(self, sessions: SessionManager):
        self._sessions = sessions
        self._origin_channel: ContextVar[str] = ContextVar("plan_origin_channel", default="gateway")
        self._origin_chat_id: ContextVar[str] = ContextVar("plan_origin_chat_id", default="direct")
        self._session_key: ContextVar[str] = ContextVar(
            "plan_session_key", default="gateway:direct"
        )

    def set_context(self, channel: str, chat_id: str, session_key: str | None = None) -> None:
        _ = self._origin_channel.set(channel)
        _ = self._origin_chat_id.set(chat_id)
        _ = self._session_key.set(session_key or f"{channel}:{chat_id}")

    def _get_session_key(self) -> str:
        key = self._session_key.get().strip()
        if key:
            return key
        return f"{self._origin_channel.get()}:{self._origin_chat_id.get()}"


class CreatePlanTool(_PlanToolBase, Tool):
    @property
    def name(self) -> str:
        return "create_plan"

    @property
    def description(self) -> str:
        return "Create a plan with goal and steps, replacing any active plan."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "The overall goal of the plan."},
                "steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Ordered step list, ideally 2-10 items.",
                },
            },
            "required": ["goal", "steps"],
        }

    async def execute(self, **kwargs: Any) -> str:
        goal = kwargs.get("goal")
        steps = kwargs.get("steps")
        if not isinstance(goal, str) or not goal.strip():
            return "Error: goal is required"
        if not isinstance(steps, list) or not steps:
            return "Error: steps must be a non-empty list"
        if not all(isinstance(step, str) and step.strip() for step in steps):
            return "Error: each step must be a non-empty string"

        state = plan.new_plan(goal, steps)
        if not state.get("steps"):
            return "Error: no valid steps after normalization"

        session = self._sessions.get_or_create(self._get_session_key())
        session.metadata[plan.PLAN_STATE_KEY] = state
        session.metadata.pop(plan.PLAN_ARCHIVED_KEY, None)
        self._sessions.save(session)

        total = len(state["steps"])
        return f"Plan created: 0/{total} done; current_step={state['current_step']}"


class UpdatePlanStepTool(_PlanToolBase, Tool):
    @property
    def name(self) -> str:
        return "update_plan_step"

    @property
    def description(self) -> str:
        return "Update one plan step status and advance current_step."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "step_index": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "1-based index of the step to update.",
                },
                "status": {
                    "type": "string",
                    "enum": list(plan.UPDATEABLE_STATUSES),
                    "description": "New status for the step.",
                },
            },
            "required": ["step_index", "status"],
        }

    async def execute(self, **kwargs: Any) -> str:
        step_index = kwargs.get("step_index")
        status = kwargs.get("status")
        if isinstance(step_index, bool):
            return "Error: step_index must be an integer"
        if isinstance(step_index, str) and step_index.strip().isdigit():
            step_index = int(step_index.strip())
        elif isinstance(step_index, float) and step_index.is_integer():
            step_index = int(step_index)
        if not isinstance(step_index, int):
            return "Error: step_index must be an integer"
        if not isinstance(status, str):
            return "Error: status must be a string"
        status = status.strip().lower()
        if status not in plan.UPDATEABLE_STATUSES:
            allowed = ", ".join(plan.UPDATEABLE_STATUSES)
            return f"Error: status must be one of: {allowed}"

        session = self._sessions.get_or_create(self._get_session_key())
        state = session.metadata.get(plan.PLAN_STATE_KEY)
        if not isinstance(state, dict):
            return "Error: no active plan"

        try:
            new_state = plan.set_step_status(state, step_index=step_index, status=status)
        except ValueError as exc:
            return f"Error: {exc}"

        session.metadata[plan.PLAN_STATE_KEY] = new_state
        archived = ""
        if plan.is_plan_done(new_state):
            archived = plan.archive_plan(new_state)
            if archived:
                session.metadata[plan.PLAN_ARCHIVED_KEY] = archived
        self._sessions.save(session)

        done_count = plan.count_status(new_state, plan.STATUS_DONE)
        total = len(new_state["steps"])
        if archived:
            return (
                f"Plan updated: {done_count}/{total} done; current_step={new_state['current_step']}. "
                f"Archived: {archived}"
            )
        return f"Plan updated: {done_count}/{total} done; current_step={new_state['current_step']}"


class ClearPlanTool(_PlanToolBase, Tool):
    @property
    def name(self) -> str:
        return "clear_plan"

    @property
    def description(self) -> str:
        return "Clear the active plan from session metadata."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs: Any) -> str:
        del kwargs
        session = self._sessions.get_or_create(self._get_session_key())
        had_plan = plan.PLAN_STATE_KEY in session.metadata
        session.metadata.pop(plan.PLAN_STATE_KEY, None)
        archived = session.metadata.get(plan.PLAN_ARCHIVED_KEY)
        self._sessions.save(session)
        if not had_plan:
            return "No active plan to clear."
        if isinstance(archived, str) and archived:
            return f"Plan cleared. Archived: {archived}"
        return "Plan cleared."
