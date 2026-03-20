from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkSnapshotRequest:
    profile_context: object
    session_key: str
    snapshot_profile_id: str | None = None


def write_work_snapshot(snapshot_filename: str, request: WorkSnapshotRequest) -> None:
    profile_context = request.profile_context
    profile_id = str(request.snapshot_profile_id or profile_context.profile_id)
    avatar_source = "../resources/profile-avatars/mochi.svg"
    session_key = request.session_key
    payload = {
        "schema_version": 1,
        "profile_id": profile_id,
        "display_name": "Work",
        "avatar_key": "mochi",
        "updated_at": "2026-03-14T12:02:00+00:00",
        "hub": {"state": "running", "detail": "", "channels": ["telegram"], "is_live": False},
        "inventory": {"totalSessionCount": 1, "totalChildSessionCount": 0, "channelKeys": ["telegram"]},
        "workers": [_worker_payload(profile_id, avatar_source, session_key)],
        "working": [_session_card(profile_id, avatar_source, session_key)],
        "automation": [_automation_card(profile_id, avatar_source)],
        "attention": [],
    }
    snapshot_path = profile_context.state_root / snapshot_filename
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _session_card(profile_id: str, avatar_source: str, session_key: str) -> dict[str, object]:
    return {
        "id": f"{profile_id}:session_reply:{session_key}",
        "profileId": profile_id,
        "kind": "session_reply",
        "title": "Work Ops",
        "summary": "回复中",
        "sessionKey": session_key,
        "parentSessionKey": "",
        "visualChannel": "telegram",
        "accentKey": "telegram",
        "glyphSource": "../resources/icons/channel-telegram.svg",
        "statusKey": "running",
        "statusLabel": "运行中",
        "updatedAt": "2026-03-14T12:01:00+00:00",
        "updatedLabel": "刚刚",
        "relativeLabel": "刚刚",
        "isLive": False,
        "personaVariant": "primary",
        "avatarSource": avatar_source,
        "routeKind": "session",
        "routeValue": session_key,
        "canOpen": True,
        "canToggleCron": False,
        "canRunHeartbeat": False,
        "isRunning": True,
    }


def _automation_card(profile_id: str, avatar_source: str) -> dict[str, object]:
    return {
        "id": f"{profile_id}:cron:daily-review",
        "profileId": profile_id,
        "kind": "cron_job",
        "title": "Daily Review",
        "summary": "每 30 分钟",
        "sessionKey": "cron:daily-review",
        "visualChannel": "cron",
        "accentKey": "cron",
        "glyphSource": "../resources/icons/sidebar-cron.svg",
        "statusKey": "scheduled",
        "statusLabel": "已调度",
        "updatedAt": "2026-03-14T12:01:00+00:00",
        "updatedLabel": "2 小时后",
        "relativeLabel": "2 小时后",
        "isLive": False,
        "personaVariant": "automation",
        "avatarSource": avatar_source,
        "routeKind": "cron",
        "routeValue": "daily-review",
        "canOpen": True,
        "canToggleCron": True,
        "canRunHeartbeat": False,
        "isRunning": False,
    }


def _worker_payload(profile_id: str, avatar_source: str, session_key: str) -> dict[str, object]:
    return {
        "workerId": f"{profile_id}:session",
        "profileId": profile_id,
        "avatarSource": avatar_source,
        "title": "Work Ops",
        "variant": "primary",
        "accentKey": "telegram",
        "glyphSource": "../resources/icons/channel-telegram.svg",
        "statusKey": "running",
        "statusLabel": "运行中",
        "routeKind": "session",
        "routeValue": session_key,
    }
