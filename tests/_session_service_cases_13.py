# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

def test_service_delete_failure_restores_unread_snapshot():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        sm = _make_mock_session_manager(
            sessions=[
                {"key": "desktop:local::s1", "title": "Chat 1"},
                {"key": "desktop:local::s2", "title": "Chat 2"},
            ],
            active_key="desktop:local::s1",
            fail_delete=True,
        )
        svc.setHubReady()
        svc.initialize(sm)

        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)
        loop.exec()

        sessions = [dict(s) for s in svc._model._sessions]
        for item in sessions:
            item["has_unread"] = str(item.get("key", "")) == "desktop:local::s2"
        svc._model.reset_sessions(sessions, "desktop:local::s1")

        svc.deleteSession("desktop:local::s1")

        loop2 = QEventLoop()
        QTimer.singleShot(300, loop2.quit)
        loop2.exec()

        idx_s2 = _index_by_key(svc, "desktop:local::s2")
        assert idx_s2.isValid()
        assert _sessions_model(svc).data(idx_s2, Qt.UserRole + 1) == "desktop:local::s2"
        assert _sessions_model(svc).data(idx_s2, Qt.UserRole + 6) is True
    finally:
        runner.shutdown(grace_s=1.0)



def test_session_manager_mark_read_does_not_reorder_by_accident(tmp_path):
    sm = SessionManager(tmp_path)

    old_ts = datetime(2024, 1, 1, 0, 0, 0)
    new_ts = datetime(2024, 1, 2, 0, 0, 0)

    s1 = sm.get_or_create("desktop:local::old")
    s1.updated_at = old_ts
    sm.save(s1)

    s2 = sm.get_or_create("desktop:local::new")
    s2.updated_at = new_ts
    sm.save(s2)

    sm.invalidate("desktop:local::old")
    loaded = sm.get_or_create("desktop:local::old")
    loaded.metadata["desktop_last_seen_ai_at"] = datetime.now().isoformat()
    sm.save(loaded)

    sessions = sm.list_sessions()
    assert sessions[0]["key"] == "desktop:local::new"
    old_row = next(s for s in sessions if s["key"] == "desktop:local::old")
    assert old_row["updated_at"] == old_ts.isoformat()



def test_session_manager_delete_clears_active_marker_for_deleted_session(tmp_path):
    sm = SessionManager(tmp_path)

    s1 = sm.get_or_create("telegram:chat::1")
    s1.add_message("user", "hello")
    sm.save(s1)
    s2 = sm.get_or_create("telegram:chat::2")
    s2.add_message("user", "world")
    sm.save(s2)
    sm.set_active_session_key("telegram:chat", "telegram:chat::1")

    assert sm.get_active_session_key("telegram:chat") == "telegram:chat::1"
    assert sm.delete_session("telegram:chat::1") is True
    assert sm.get_active_session_key("telegram:chat") is None



def test_session_manager_delete_rolls_back_when_message_delete_fails(tmp_path):
    sm = SessionManager(tmp_path)
    key = "desktop:local::rollback"

    session = sm.get_or_create(key)
    session.add_message("user", "hello")
    sm.save(session)

    with patch.object(sm._msg_tbl, "delete", side_effect=RuntimeError("boom")):
        assert sm.delete_session(key) is False

    keys = [row["key"] for row in sm.list_sessions()]
    assert key in keys

    sm.invalidate(key)
    loaded = sm.get_or_create(key)
    assert any(msg.get("content") == "hello" for msg in loaded.messages)



def test_session_manager_get_active_key_prefers_latest_marker(tmp_path):
    sm = SessionManager(tmp_path)
    marker = "_active:desktop:local"
    sm._meta_table().add(
        [
            {
                "session_key": marker,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata_json": json.dumps({"active_key": "desktop:local::old"}),
                "last_consolidated": 0,
            },
            {
                "session_key": marker,
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
                "metadata_json": json.dumps({"active_key": "desktop:local::new"}),
                "last_consolidated": 0,
            },
        ]
    )

    assert sm.get_active_session_key("desktop:local") == "desktop:local::new"



def test_service_refresh_without_manager_is_noop():
    runner = AsyncioRunner()
    runner.start()
    try:
        svc = _new_session_service(runner)
        svc.refresh()  # should not raise
        assert _sessions_model(svc).rowCount() == 0
    finally:
        runner.shutdown(grace_s=1.0)
