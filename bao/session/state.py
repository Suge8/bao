from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

RUNTIME_STATUS_RUNNING = "running"
RUNTIME_METADATA_KEYS = frozenset({"session_running", "child_status", "active_task_id"})
SESSION_ACTIVITY_SESSION_STARTED = "session_started"
SESSION_ACTIVITY_SESSION_FINISHED = "session_finished"
SESSION_ACTIVITY_CHILD_STARTED = "child_started"
SESSION_ACTIVITY_CHILD_CLEARED = "child_cleared"
CHILD_OUTCOME_METADATA_KEYS = frozenset({"child_status", "last_result_summary", "task_label"})
WORKFLOW_METADATA_KEYS = frozenset({"coding_sessions", "_plan_state", "_plan_archived", "_session_lang"})
ROUTING_METADATA_KEYS = frozenset({"session_kind", "read_only", "parent_session_key"})
READ_RECEIPT_METADATA_KEYS = frozenset({"desktop_last_ai_at", "desktop_last_seen_ai_at"})
VIEW_METADATA_KEYS = frozenset({"title"})
CANONICAL_GROUP_KEYS = frozenset({"routing", "workflow", "view"})


@dataclass(frozen=True)
class SessionRuntimeState:
    session_running: bool = False
    child_status: str = ""
    active_task_id: str = ""

    @property
    def child_running(self) -> bool:
        return self.child_status == RUNTIME_STATUS_RUNNING

    @property
    def is_running(self) -> bool:
        return self.session_running or self.child_running

    def to_metadata(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.session_running:
            payload["session_running"] = True
        if self.child_running:
            payload["child_status"] = RUNTIME_STATUS_RUNNING
            if self.active_task_id:
                payload["active_task_id"] = self.active_task_id
        return payload

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "session_running": self.session_running,
            "child_running": self.child_running,
            "active_task_id": self.active_task_id,
            "is_running": self.is_running,
        }


@dataclass(frozen=True)
class SessionRoutingMetadata:
    session_kind: str = "regular"
    read_only: bool = False
    parent_session_key: str = ""

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "session_kind": self.session_kind,
            "read_only": self.read_only,
            "parent_session_key": self.parent_session_key,
        }


@dataclass(frozen=True)
class SessionChildOutcome:
    status: str = ""
    task_label: str = ""
    last_result_summary: str = ""

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "task_label": self.task_label,
            "last_result_summary": self.last_result_summary,
        }


@dataclass(frozen=True)
class SessionWorkflowState:
    coding_sessions: Any = None
    plan_state: Any = None
    plan_archived: Any = None
    session_lang: str = ""
    child_outcome: SessionChildOutcome = field(default_factory=SessionChildOutcome)

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "coding_sessions": self.coding_sessions,
            "_plan_state": self.plan_state,
            "_plan_archived": self.plan_archived,
            "_session_lang": self.session_lang,
            "child_outcome": self.child_outcome.as_snapshot(),
        }


@dataclass(frozen=True)
class SessionReadReceiptState:
    last_ai_at: str = ""
    last_seen_ai_at: str = ""

    @property
    def has_unread_ai(self) -> bool:
        if not self.last_ai_at:
            return False
        seen_at = self.last_seen_ai_at or self.last_ai_at
        return seen_at < self.last_ai_at

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "last_ai_at": self.last_ai_at,
            "last_seen_ai_at": self.last_seen_ai_at,
            "has_unread_ai": self.has_unread_ai,
        }


@dataclass(frozen=True)
class SessionViewState:
    title: str = ""
    read_receipts: SessionReadReceiptState = field(default_factory=SessionReadReceiptState)

    def as_snapshot(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "read_receipts": self.read_receipts.as_snapshot(),
        }


@dataclass(frozen=True)
class SessionSnapshot:
    metadata: dict[str, Any]
    routing: SessionRoutingMetadata
    runtime: SessionRuntimeState
    workflow: SessionWorkflowState
    view: SessionViewState


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


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


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
    child_running = bool(payload.get("child_running", False))
    child_status = str(payload.get("child_status") or "")
    if child_status != RUNTIME_STATUS_RUNNING and child_running:
        child_status = RUNTIME_STATUS_RUNNING
    if child_status != RUNTIME_STATUS_RUNNING:
        child_status = ""
    return SessionRuntimeState(
        session_running=bool(payload.get("session_running", False)),
        child_status=child_status,
        active_task_id=str(payload.get("active_task_id") or "") if child_status else "",
    )


def nest_flat_persisted_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = _metadata_dict(metadata)
    other = {
        key: value
        for key, value in payload.items()
        if key not in RUNTIME_METADATA_KEYS
        and key not in ROUTING_METADATA_KEYS
        and key not in WORKFLOW_METADATA_KEYS
        and key not in CHILD_OUTCOME_METADATA_KEYS
        and key not in READ_RECEIPT_METADATA_KEYS
        and key not in VIEW_METADATA_KEYS
        and key not in CANONICAL_GROUP_KEYS
    }
    return {
        **other,
        "routing": {
            "session_kind": str(payload.get("session_kind") or "regular"),
            "read_only": bool(payload.get("read_only", False)),
            "parent_session_key": str(payload.get("parent_session_key") or ""),
        },
        "workflow": {
            "coding_sessions": payload.get("coding_sessions"),
            "_plan_state": payload.get("_plan_state"),
            "_plan_archived": payload.get("_plan_archived"),
            "_session_lang": str(payload.get("_session_lang") or ""),
            "child_outcome": {
                "status": (
                    ""
                    if str(payload.get("child_status") or "") == RUNTIME_STATUS_RUNNING
                    else str(payload.get("child_status") or "")
                ),
                "task_label": str(payload.get("task_label") or ""),
                "last_result_summary": str(payload.get("last_result_summary") or ""),
            },
        },
        "view": {
            "title": str(payload.get("title") or ""),
            "read_receipts": {
                "last_ai_at": str(payload.get("desktop_last_ai_at") or ""),
                "last_seen_ai_at": str(payload.get("desktop_last_seen_ai_at") or ""),
            },
        },
    }


def canonicalize_persisted_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    payload = _metadata_dict(metadata)
    routing_payload = _mapping(payload.get("routing"))
    workflow_payload = _mapping(payload.get("workflow"))
    view_payload = _mapping(payload.get("view"))
    child_outcome_payload = _mapping(workflow_payload.get("child_outcome"))
    read_receipts_payload = _mapping(view_payload.get("read_receipts"))
    if "child_outcome" not in workflow_payload:
        workflow_payload["child_outcome"] = child_outcome_payload
    if "read_receipts" not in view_payload:
        view_payload["read_receipts"] = read_receipts_payload

    other = {
        key: value
        for key, value in payload.items()
        if key not in RUNTIME_METADATA_KEYS
        and key not in ROUTING_METADATA_KEYS
        and key not in WORKFLOW_METADATA_KEYS
        and key not in CHILD_OUTCOME_METADATA_KEYS
        and key not in READ_RECEIPT_METADATA_KEYS
        and key not in VIEW_METADATA_KEYS
        and key not in CANONICAL_GROUP_KEYS
    }
    return {
        **other,
        "routing": {
            "session_kind": str(routing_payload.get("session_kind") or "regular"),
            "read_only": bool(routing_payload.get("read_only", False)),
            "parent_session_key": str(routing_payload.get("parent_session_key") or ""),
        },
        "workflow": {
            "coding_sessions": workflow_payload.get("coding_sessions"),
            "_plan_state": workflow_payload.get("_plan_state"),
            "_plan_archived": workflow_payload.get("_plan_archived"),
            "_session_lang": str(workflow_payload.get("_session_lang") or ""),
            "child_outcome": {
                "status": str(child_outcome_payload.get("status") or ""),
                "task_label": str(child_outcome_payload.get("task_label") or ""),
                "last_result_summary": str(child_outcome_payload.get("last_result_summary") or ""),
            },
        },
        "view": {
            "title": str(view_payload.get("title") or ""),
            "read_receipts": {
                "last_ai_at": str(read_receipts_payload.get("last_ai_at") or ""),
                "last_seen_ai_at": str(read_receipts_payload.get("last_seen_ai_at") or ""),
            },
        },
    }


def flatten_persisted_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    canonical = canonicalize_persisted_metadata(metadata)
    routing = _mapping(canonical.get("routing"))
    workflow = _mapping(canonical.get("workflow"))
    child_outcome = _mapping(workflow.get("child_outcome"))
    view = _mapping(canonical.get("view"))
    read_receipts = _mapping(view.get("read_receipts"))
    other = {
        key: value
        for key, value in canonical.items()
        if key not in CANONICAL_GROUP_KEYS
    }
    return {
        **other,
        "session_kind": str(routing.get("session_kind") or "regular"),
        "read_only": bool(routing.get("read_only", False)),
        "parent_session_key": str(routing.get("parent_session_key") or ""),
        "coding_sessions": workflow.get("coding_sessions"),
        "_plan_state": workflow.get("_plan_state"),
        "_plan_archived": workflow.get("_plan_archived"),
        "_session_lang": str(workflow.get("_session_lang") or ""),
        "child_status": str(child_outcome.get("status") or ""),
        "task_label": str(child_outcome.get("task_label") or ""),
        "last_result_summary": str(child_outcome.get("last_result_summary") or ""),
        "title": str(view.get("title") or ""),
        "desktop_last_ai_at": str(read_receipts.get("last_ai_at") or ""),
        "desktop_last_seen_ai_at": str(read_receipts.get("last_seen_ai_at") or ""),
    }


def build_session_snapshot(
    metadata: Mapping[str, Any] | None,
    *,
    runtime_updates: Mapping[str, Any] | SessionRuntimeState | None = None,
) -> SessionSnapshot:
    canonical = canonicalize_persisted_metadata(metadata)
    merged = merge_runtime_metadata(flatten_persisted_metadata(canonical), runtime_updates)
    return SessionSnapshot(
        metadata=merged,
        routing=session_routing_metadata(canonical),
        runtime=session_runtime_state(merged),
        workflow=session_workflow_state(canonical),
        view=session_view_state(canonical),
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
    payload = _mapping(_metadata_dict(metadata).get("routing"))
    return SessionRoutingMetadata(
        session_kind=str(payload.get("session_kind") or "regular"),
        read_only=bool(payload.get("read_only", False)),
        parent_session_key=str(payload.get("parent_session_key") or ""),
    )


def session_child_outcome(metadata: Mapping[str, Any] | None) -> SessionChildOutcome:
    workflow = _mapping(_metadata_dict(metadata).get("workflow"))
    payload = _mapping(workflow.get("child_outcome"))
    return SessionChildOutcome(
        status=str(payload.get("status") or ""),
        task_label=str(payload.get("task_label") or ""),
        last_result_summary=str(payload.get("last_result_summary") or ""),
    )


def session_workflow_state(metadata: Mapping[str, Any] | None) -> SessionWorkflowState:
    payload = _mapping(_metadata_dict(metadata).get("workflow"))
    return SessionWorkflowState(
        coding_sessions=payload.get("coding_sessions"),
        plan_state=payload.get("_plan_state"),
        plan_archived=payload.get("_plan_archived"),
        session_lang=str(payload.get("_session_lang") or ""),
        child_outcome=session_child_outcome(metadata),
    )


def session_read_receipt_state(metadata: Mapping[str, Any] | None) -> SessionReadReceiptState:
    view = _mapping(_metadata_dict(metadata).get("view"))
    payload = _mapping(view.get("read_receipts"))
    return SessionReadReceiptState(
        last_ai_at=str(payload.get("last_ai_at") or ""),
        last_seen_ai_at=str(payload.get("last_seen_ai_at") or ""),
    )


def session_view_state(metadata: Mapping[str, Any] | None) -> SessionViewState:
    payload = _mapping(_metadata_dict(metadata).get("view"))
    return SessionViewState(
        title=str(payload.get("title") or ""),
        read_receipts=session_read_receipt_state(metadata),
    )


def session_metadata_group(metadata: Mapping[str, Any] | None, group: str) -> dict[str, Any]:
    canonical = canonicalize_persisted_metadata(metadata)
    if group == "runtime":
        return session_runtime_state(canonical).to_metadata()
    if group == "routing":
        return session_routing_metadata(canonical).as_snapshot()
    if group == "workflow":
        workflow = session_workflow_state(canonical)
        return {
            "coding_sessions": workflow.coding_sessions,
            "_plan_state": workflow.plan_state,
            "_plan_archived": workflow.plan_archived,
            "_session_lang": workflow.session_lang,
            "child_outcome": workflow.child_outcome.as_snapshot(),
        }
    if group == "child_outcome":
        return session_child_outcome(canonical).as_snapshot()
    if group == "view":
        return session_view_state(canonical).as_snapshot()
    if group == "read_receipts":
        return session_read_receipt_state(canonical).as_snapshot()
    return {key: value for key, value in canonical.items() if key not in CANONICAL_GROUP_KEYS}


def desktop_has_unread_ai(metadata: Mapping[str, Any] | None) -> bool:
    canonical = canonicalize_persisted_metadata(metadata)
    return session_read_receipt_state(canonical).has_unread_ai
