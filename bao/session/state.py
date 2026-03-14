from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

RUNTIME_STATUS_RUNNING = "running"
RUNTIME_METADATA_KEYS = frozenset({"session_running", "child_status", "active_task_id"})
SESSION_ACTIVITY_SESSION_STARTED = "session_started"
SESSION_ACTIVITY_SESSION_FINISHED = "session_finished"
SESSION_ACTIVITY_CHILD_STARTED = "child_started"
SESSION_ACTIVITY_CHILD_CLEARED = "child_cleared"
WORKFLOW_METADATA_KEYS = frozenset(
    {
        "session_kind",
        "read_only",
        "parent_session_key",
        "coding_sessions",
        "_plan_state",
        "_plan_archived",
        "_session_lang",
    }
)
VIEW_METADATA_KEYS = frozenset({"title", "desktop_last_ai_at", "desktop_last_seen_ai_at"})


@dataclass(frozen=True)
class SessionRuntimeState:
    session_running: bool = False
    child_status: str = ""
    active_task_id: str = ""

    @property
    def is_running(self) -> bool:
        return self.session_running or self.child_status == RUNTIME_STATUS_RUNNING

    def to_metadata(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.session_running:
            payload["session_running"] = True
        if self.child_status == RUNTIME_STATUS_RUNNING:
            payload["child_status"] = RUNTIME_STATUS_RUNNING
            if self.active_task_id:
                payload["active_task_id"] = self.active_task_id
        return payload


@dataclass(frozen=True)
class SessionRoutingMetadata:
    session_kind: str = "regular"
    read_only: bool = False
    parent_session_key: str = ""


SessionActivityKind = Literal[
    "session_started",
    "session_finished",
    "child_started",
    "child_cleared",
]


@dataclass(frozen=True)
class SessionActivityEvent:
    kind: SessionActivityKind
    task_id: str = ""


def _metadata_dict(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def normalize_runtime_metadata(
    runtime_updates: Mapping[str, Any] | SessionRuntimeState | None,
) -> SessionRuntimeState:
    if isinstance(runtime_updates, SessionRuntimeState):
        return SessionRuntimeState(
            session_running=bool(runtime_updates.session_running),
            child_status=(
                RUNTIME_STATUS_RUNNING
                if runtime_updates.child_status == RUNTIME_STATUS_RUNNING
                else ""
            ),
            active_task_id=(
                str(runtime_updates.active_task_id or "")
                if runtime_updates.child_status == RUNTIME_STATUS_RUNNING
                else ""
            ),
        )
    payload = _metadata_dict(runtime_updates)
    child_status = (
        RUNTIME_STATUS_RUNNING
        if str(payload.get("child_status") or "") == RUNTIME_STATUS_RUNNING
        else ""
    )
    return SessionRuntimeState(
        session_running=bool(payload.get("session_running", False)),
        child_status=child_status,
        active_task_id=str(payload.get("active_task_id") or "") if child_status else "",
    )


def apply_runtime_activity(
    runtime: Mapping[str, Any] | SessionRuntimeState | None,
    activity: SessionActivityEvent,
) -> SessionRuntimeState:
    current = normalize_runtime_metadata(runtime)
    if activity.kind == SESSION_ACTIVITY_SESSION_STARTED:
        return SessionRuntimeState(
            session_running=True,
            child_status=current.child_status,
            active_task_id=current.active_task_id,
        )
    if activity.kind == SESSION_ACTIVITY_SESSION_FINISHED:
        return SessionRuntimeState(
            session_running=False,
            child_status=current.child_status,
            active_task_id=current.active_task_id if current.child_status else "",
        )
    if activity.kind == SESSION_ACTIVITY_CHILD_STARTED:
        task_id = str(activity.task_id or "").strip()
        return SessionRuntimeState(
            session_running=current.session_running,
            child_status=RUNTIME_STATUS_RUNNING,
            active_task_id=task_id,
        )
    if activity.kind == SESSION_ACTIVITY_CHILD_CLEARED:
        return SessionRuntimeState(
            session_running=current.session_running,
            child_status="",
            active_task_id="",
        )
    return current


def split_runtime_metadata(
    metadata: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], SessionRuntimeState]:
    persisted = _metadata_dict(metadata)
    session_running = bool(persisted.pop("session_running", False))
    child_status = str(persisted.get("child_status") or "")
    active_task_id = str(persisted.pop("active_task_id", "") or "")
    runtime = SessionRuntimeState(session_running=session_running)
    if child_status == RUNTIME_STATUS_RUNNING:
        persisted.pop("child_status", None)
        runtime = SessionRuntimeState(
            session_running=session_running,
            child_status=RUNTIME_STATUS_RUNNING,
            active_task_id=active_task_id,
        )
    return persisted, runtime


def merge_runtime_metadata(
    metadata: Mapping[str, Any] | None,
    runtime_updates: Mapping[str, Any] | SessionRuntimeState | None,
) -> dict[str, Any]:
    merged = _metadata_dict(metadata)
    runtime = normalize_runtime_metadata(runtime_updates)
    merged.update(runtime.to_metadata())
    return merged


def filter_persisted_metadata_updates(metadata_updates: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        field: value
        for field, value in _metadata_dict(metadata_updates).items()
        if field not in RUNTIME_METADATA_KEYS
    }


def session_runtime_state(metadata: Mapping[str, Any] | None) -> SessionRuntimeState:
    return normalize_runtime_metadata(metadata)


def session_routing_metadata(metadata: Mapping[str, Any] | None) -> SessionRoutingMetadata:
    payload = _metadata_dict(metadata)
    return SessionRoutingMetadata(
        session_kind=str(payload.get("session_kind") or "regular"),
        read_only=bool(payload.get("read_only", False)),
        parent_session_key=str(payload.get("parent_session_key") or ""),
    )


def session_metadata_group(metadata: Mapping[str, Any] | None, group: str) -> dict[str, Any]:
    payload = _metadata_dict(metadata)
    if group == "runtime":
        return session_runtime_state(payload).to_metadata()
    if group == "workflow":
        return {key: payload[key] for key in WORKFLOW_METADATA_KEYS if key in payload}
    if group == "view":
        return {key: payload[key] for key in VIEW_METADATA_KEYS if key in payload}
    return {
        key: value
        for key, value in payload.items()
        if key not in RUNTIME_METADATA_KEYS
        and key not in WORKFLOW_METADATA_KEYS
        and key not in VIEW_METADATA_KEYS
    }


def desktop_has_unread_ai(metadata: Mapping[str, Any] | None) -> bool:
    payload = _metadata_dict(metadata)
    last_ai = payload.get("desktop_last_ai_at")
    if not isinstance(last_ai, str) or not last_ai:
        return False
    last_seen_ai = payload.get("desktop_last_seen_ai_at")
    seen_ai = last_seen_ai if isinstance(last_seen_ai, str) and last_seen_ai else last_ai
    return seen_ai < last_ai
