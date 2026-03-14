from bao.session.state import (
    RUNTIME_STATUS_RUNNING,
    SESSION_ACTIVITY_CHILD_CLEARED,
    SESSION_ACTIVITY_CHILD_STARTED,
    SESSION_ACTIVITY_SESSION_FINISHED,
    SESSION_ACTIVITY_SESSION_STARTED,
    SessionActivityEvent,
    apply_runtime_activity,
    desktop_has_unread_ai,
    filter_persisted_metadata_updates,
    merge_runtime_metadata,
    session_metadata_group,
    session_routing_metadata,
    split_runtime_metadata,
)


def test_split_runtime_metadata_strips_only_running_overlay() -> None:
    persisted, runtime = split_runtime_metadata(
        {
            "title": "main",
            "session_running": True,
            "child_status": RUNTIME_STATUS_RUNNING,
            "active_task_id": "task-1",
        }
    )

    assert persisted == {"title": "main"}
    assert runtime.to_metadata() == {
        "session_running": True,
        "child_status": RUNTIME_STATUS_RUNNING,
        "active_task_id": "task-1",
    }

    persisted_done, runtime_done = split_runtime_metadata(
        {"child_status": "completed", "active_task_id": "task-2"}
    )
    assert persisted_done == {"child_status": "completed"}
    assert runtime_done.to_metadata() == {}


def test_state_helpers_preserve_routing_and_persisted_groups() -> None:
    metadata = {
        "title": "default",
        "desktop_last_ai_at": "2026-03-14T10:00:00",
        "desktop_last_seen_ai_at": "2026-03-14T09:00:00",
        "session_kind": "subagent_child",
        "read_only": True,
        "parent_session_key": "desktop:local::main",
        "_plan_state": {"goal": "ship"},
        "session_running": True,
    }

    assert desktop_has_unread_ai(metadata) is True
    assert filter_persisted_metadata_updates(metadata) == {
        "title": "default",
        "desktop_last_ai_at": "2026-03-14T10:00:00",
        "desktop_last_seen_ai_at": "2026-03-14T09:00:00",
        "session_kind": "subagent_child",
        "read_only": True,
        "parent_session_key": "desktop:local::main",
        "_plan_state": {"goal": "ship"},
    }
    assert merge_runtime_metadata({"title": "default"}, {"session_running": True}) == {
        "title": "default",
        "session_running": True,
    }
    assert session_routing_metadata(metadata).parent_session_key == "desktop:local::main"
    assert session_metadata_group(metadata, "workflow") == {
        "_plan_state": {"goal": "ship"},
        "parent_session_key": "desktop:local::main",
        "read_only": True,
        "session_kind": "subagent_child",
    }
    assert session_metadata_group(metadata, "view") == {
        "title": "default",
        "desktop_last_ai_at": "2026-03-14T10:00:00",
        "desktop_last_seen_ai_at": "2026-03-14T09:00:00",
    }


def test_apply_runtime_activity_updates_snapshot_without_persisted_status() -> None:
    runtime = apply_runtime_activity(
        None,
        SessionActivityEvent(kind=SESSION_ACTIVITY_SESSION_STARTED),
    )
    assert runtime.to_metadata() == {"session_running": True}

    child_runtime = apply_runtime_activity(
        runtime,
        SessionActivityEvent(kind=SESSION_ACTIVITY_CHILD_STARTED, task_id="task-1"),
    )
    assert child_runtime.to_metadata() == {
        "session_running": True,
        "child_status": RUNTIME_STATUS_RUNNING,
        "active_task_id": "task-1",
    }

    cleared_child = apply_runtime_activity(
        child_runtime,
        SessionActivityEvent(kind=SESSION_ACTIVITY_CHILD_CLEARED),
    )
    assert cleared_child.to_metadata() == {"session_running": True}

    stopped = apply_runtime_activity(
        cleared_child,
        SessionActivityEvent(kind=SESSION_ACTIVITY_SESSION_FINISHED),
    )
    assert stopped.to_metadata() == {}
