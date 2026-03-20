# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

@pytest.mark.smoke
def test_model_empty_initially():
    m = _new_session_model()
    assert m.rowCount() == 0



def test_model_reset_sessions():
    m = _new_session_model()
    sessions = [
        {"key": "desktop:local::s1", "title": "Session 1", "updated_at": 100},
        {"key": "desktop:local::s2", "title": "Session 2", "updated_at": 200},
    ]
    m.reset_sessions(sessions, "desktop:local::s1")
    assert m.rowCount() == 2



def test_model_data_roles():
    m = _new_session_model()
    sessions = [
        {
            "key": "k1",
            "title": "T1",
            "updated_at": 42,
            "updated_label": "<1m",
            "message_count": 0,
            "has_messages": False,
        }
    ]
    m.reset_sessions(sessions, "k1")
    idx = m.index(0)
    assert m.data(idx, Qt.UserRole + 1) == "k1"  # key
    assert m.data(idx, Qt.UserRole + 2) == "T1"  # title
    assert m.data(idx, Qt.UserRole + 3) is True  # isActive
    assert m.data(idx, Qt.UserRole + 4) == 42  # updatedAt
    assert m.data(idx, Qt.UserRole + 7) == "<1m"
    assert m.data(idx, Qt.UserRole + 8) == 0
    assert m.data(idx, Qt.UserRole + 9) is False
    assert m.data(idx, Qt.UserRole + 15) is False



def test_model_exposes_child_session_roles():
    m = _new_session_model()
    sessions = [
        {
            "key": "subagent:desktop:local::child-1",
            "title": "research",
            "updated_at": 42,
            "session_kind": "subagent_child",
            "is_read_only": True,
            "parent_session_key": "desktop:local::main",
            "parent_title": "main",
            "child_status": "running",
            "is_running": True,
        }
    ]
    m.reset_sessions(sessions, "subagent:desktop:local::child-1")
    idx = m.index(0)
    assert m.data(idx, Qt.UserRole + 10) == "subagent_child"
    assert m.data(idx, Qt.UserRole + 11) is True
    assert m.data(idx, Qt.UserRole + 12) == "desktop:local::main"
    assert m.data(idx, Qt.UserRole + 13) == "main"
    assert m.data(idx, Qt.UserRole + 14) == "running"
    assert m.data(idx, Qt.UserRole + 15) is True



def test_model_inactive_session():
    m = _new_session_model()
    sessions = [{"key": "k1", "title": "T1", "updated_at": 0}]
    m.reset_sessions(sessions, "k2")  # k2 is active, not k1
    idx = m.index(0)
    assert m.data(idx, Qt.UserRole + 3) is False



def test_model_set_active():
    m = _new_session_model()
    sessions = [
        {"key": "k1", "title": "T1", "updated_at": 0},
        {"key": "k2", "title": "T2", "updated_at": 0},
    ]
    m.reset_sessions(sessions, "k1")
    m.set_active("k2")
    assert m.data(m.index(0), Qt.UserRole + 3) is False
    assert m.data(m.index(1), Qt.UserRole + 3) is True



def test_model_invalid_index_returns_none():
    m = _new_session_model()
    idx = m.index(99)
    assert m.data(idx, Qt.UserRole + 1) is None



def test_format_display_title_for_desktop_default_key():
    from app.backend.session import _format_display_title

    assert _format_display_title("desktop:local", None) == "default"



def test_format_display_title_uses_named_session_suffix():
    from app.backend.session import _format_display_title

    assert _format_display_title("desktop:local::planning", "") == "planning"



def test_format_updated_label_uses_compact_relative_units():
    from app.backend.session import _format_updated_label

    assert _format_updated_label(datetime.now().isoformat()) == "<1m"
    assert (
        _format_updated_label((datetime.now() - timedelta(hours=1, minutes=5)).isoformat()) == "1h"
    )
