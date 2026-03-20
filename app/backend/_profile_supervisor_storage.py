from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.backend.cron import _serialize_job
from app.backend.session_projection import normalize_session_items, project_session_item
from bao.cron.service import CronService
from bao.profile import ProfileContext

from ._profile_supervisor_common import _NATURAL_KEY, _SNAPSHOT_FILENAME


def _snapshot_path(context: ProfileContext) -> Path:
    return context.state_root / _SNAPSHOT_FILENAME


def _read_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_snapshot(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _load_sessions_from_root(state_root: Path) -> list[dict[str, Any]]:
    from bao.session.manager import SessionManager

    session_manager = SessionManager(state_root)
    try:
        raw_sessions = session_manager.list_sessions()
    finally:
        session_manager.close()
    projected = [
        project_session_item(session, natural_key=_NATURAL_KEY, current_sessions=[])
        for session in raw_sessions
    ]
    return normalize_session_items(projected)


def _has_directory_entries(path: Path) -> bool:
    try:
        return path.is_dir() and any(path.iterdir())
    except OSError:
        return False


def _has_session_storage_roots(state_root: Path) -> bool:
    root = Path(state_root).expanduser()
    return any(_has_directory_entries(path) for path in (root / "sessions", root / "lancedb"))


def _load_cron_items(cron_store_path: Path) -> list[dict[str, Any]]:
    cron_service = CronService(cron_store_path)
    store = cron_service._load_store()
    return [_serialize_job(job, "zh") for job in store.jobs]


def _heartbeat_static_snapshot(heartbeat_file: Path) -> dict[str, Any]:
    return {
        "enabled": heartbeat_file.exists(),
        "running": False,
        "heartbeat_file": str(heartbeat_file),
        "heartbeat_file_exists": heartbeat_file.exists(),
        "last_checked_at_ms": None,
        "last_run_at_ms": None,
        "last_decision": "",
        "last_error": "",
    }
