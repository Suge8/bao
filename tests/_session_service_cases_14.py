# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._session_service_testkit import *

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
