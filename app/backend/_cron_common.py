from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from bao.cron.types import CronJob

_DRAFT_PREVIEW_ID = "__draft__"


def _format_timestamp(value_ms: int | None) -> str:
    if not value_ms:
        return ""
    try:
        return datetime.fromtimestamp(value_ms / 1000).strftime("%Y-%m-%d %H:%M")
    except (OSError, OverflowError, ValueError):
        return ""


def _format_at_input(value_ms: int | None) -> str:
    if not value_ms:
        return ""
    try:
        return datetime.fromtimestamp(value_ms / 1000).strftime("%Y-%m-%dT%H:%M")
    except (OSError, OverflowError, ValueError):
        return ""


def _parse_at_input(raw: str) -> int | None:
    text = raw.strip()
    if not text:
        return None
    normalized = text.replace(" ", "T") if "T" not in text else text
    dt = datetime.fromisoformat(normalized)
    return int(dt.timestamp() * 1000)


def _tr(lang: str, zh: str, en: str) -> str:
    return zh if lang == "zh" else en


def _normalized_store_path(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return str(Path(text).expanduser())


def _schedule_summary(job: CronJob, lang: str) -> str:
    schedule = job.schedule
    if schedule.kind == "at":
        if schedule.at_ms:
            return _tr(
                lang,
                f"单次 · {_format_timestamp(schedule.at_ms)}",
                f"One-shot · {_format_timestamp(schedule.at_ms)}",
            )
        return _tr(lang, "单次执行", "One-shot")
    if schedule.kind == "every":
        minutes = int((schedule.every_ms or 0) / 60000)
        if minutes <= 0:
            return _tr(lang, "循环执行", "Repeats")
        if minutes < 60:
            return _tr(lang, f"每 {minutes} 分钟", f"Every {minutes}m")
        hours, remainder = divmod(minutes, 60)
        if remainder == 0:
            return _tr(lang, f"每 {hours} 小时", f"Every {hours}h")
        return _tr(lang, f"每 {hours} 小时 {remainder} 分钟", f"Every {hours}h {remainder}m")
    expr = schedule.expr or ""
    if schedule.tz:
        return f"{expr} · {schedule.tz}" if expr else schedule.tz
    return expr or _tr(lang, "Cron 表达式", "Cron")


def _status_key(job: CronJob) -> str:
    if not job.enabled:
        return "disabled"
    if job.state.last_status == "error":
        return "error"
    if job.state.next_run_at_ms:
        return "scheduled"
    if job.state.last_status == "ok":
        return "idle_ok"
    return "draft"


def _status_label(job: CronJob, lang: str) -> str:
    key = _status_key(job)
    if key == "disabled":
        return _tr(lang, "已停用", "Disabled")
    if key == "error":
        return _tr(lang, "异常", "Error")
    if key == "scheduled":
        return _tr(lang, "已调度", "Scheduled")
    if key == "idle_ok":
        return _tr(lang, "已就绪", "Ready")
    return _tr(lang, "未安排", "Not scheduled")


def _last_result_text(job: CronJob, lang: str) -> str:
    if job.state.last_status == "error":
        return (
            _tr(
                lang,
                f"失败 · {_format_timestamp(job.state.last_run_at_ms)}",
                f"Failed · {_format_timestamp(job.state.last_run_at_ms)}",
            )
            if job.state.last_run_at_ms
            else _tr(lang, "失败", "Failed")
        )
    if job.state.last_status == "ok":
        return (
            _tr(
                lang,
                f"成功 · {_format_timestamp(job.state.last_run_at_ms)}",
                f"OK · {_format_timestamp(job.state.last_run_at_ms)}",
            )
            if job.state.last_run_at_ms
            else _tr(lang, "成功", "OK")
        )
    if not job.state.last_run_at_ms:
        return _tr(lang, "从未执行", "Never run")
    return _format_timestamp(job.state.last_run_at_ms)


def _serialize_job(job: CronJob, lang: str) -> dict[str, Any]:
    return {
        "id": job.id,
        "name": job.name,
        "enabled": job.enabled,
        "schedule_kind": job.schedule.kind,
        "schedule_summary": _schedule_summary(job, lang),
        "schedule": {
            "kind": job.schedule.kind,
            "at_ms": job.schedule.at_ms,
            "every_ms": job.schedule.every_ms,
            "expr": job.schedule.expr or "",
            "tz": job.schedule.tz or "",
        },
        "message": job.payload.message,
        "deliver": job.payload.deliver,
        "channel": job.payload.channel or "",
        "target": job.payload.to or "",
        "delete_after_run": job.delete_after_run,
        "next_run_at_ms": job.state.next_run_at_ms,
        "next_run_text": _format_timestamp(job.state.next_run_at_ms),
        "last_run_at_ms": job.state.last_run_at_ms,
        "last_run_text": _format_timestamp(job.state.last_run_at_ms),
        "last_status": job.state.last_status or "",
        "last_error": job.state.last_error or "",
        "last_result_text": _last_result_text(job, lang),
        "status_key": _status_key(job),
        "status_label": _status_label(job, lang),
        "session_key": f"cron:{job.id}",
        "created_at_ms": job.created_at_ms,
        "updated_at_ms": job.updated_at_ms,
    }


def _empty_draft() -> dict[str, Any]:
    return {
        "id": "",
        "name": "",
        "enabled": True,
        "schedule_kind": "every",
        "at_input": "",
        "every_minutes": "60",
        "cron_expr": "0 9 * * *",
        "timezone": "",
        "message": "",
        "deliver": False,
        "channel": "",
        "target": "",
        "delete_after_run": False,
    }


def _draft_from_task(task: dict[str, Any]) -> dict[str, Any]:
    raw_schedule = task.get("schedule")
    schedule: dict[str, Any] = {}
    if isinstance(raw_schedule, dict):
        schedule = {str(key): value for key, value in raw_schedule.items()}
    return {
        "id": str(task.get("id", "")),
        "name": str(task.get("name", "")),
        "enabled": bool(task.get("enabled", True)),
        "schedule_kind": str(task.get("schedule_kind", "every")),
        "at_input": _format_at_input(schedule.get("at_ms")),
        "every_minutes": str(max(1, int((schedule.get("every_ms") or 60000) / 60000))),
        "cron_expr": str(schedule.get("expr", "") or ""),
        "timezone": str(schedule.get("tz", "") or ""),
        "message": str(task.get("message", "")),
        "deliver": bool(task.get("deliver", False)),
        "channel": str(task.get("channel", "")),
        "target": str(task.get("target", "")),
        "delete_after_run": bool(task.get("delete_after_run", False)),
    }


def _draft_schedule_summary(draft: dict[str, Any], lang: str) -> str:
    kind = str(draft.get("schedule_kind", "every") or "every")
    if kind == "at":
        at_input = str(draft.get("at_input", "")).strip()
        return at_input or _tr(lang, "单次执行", "One-shot")
    if kind == "cron":
        expr = str(draft.get("cron_expr", "")).strip()
        tz = str(draft.get("timezone", "")).strip()
        if expr and tz:
            return f"{expr} · {tz}"
        return expr or _tr(lang, "高级规则", "Advanced")
    minutes_raw = str(draft.get("every_minutes", "")).strip()
    try:
        minutes = int(minutes_raw)
    except ValueError:
        minutes = 0
    if minutes <= 0:
        return _tr(lang, "循环执行", "Repeats")
    if minutes < 60:
        return _tr(lang, f"每 {minutes} 分钟", f"Every {minutes}m")
    hours, remainder = divmod(minutes, 60)
    if remainder == 0:
        return _tr(lang, f"每 {hours} 小时", f"Every {hours}h")
    return _tr(lang, f"每 {hours} 小时 {remainder} 分钟", f"Every {hours}h {remainder}m")


def _draft_preview_task(draft: dict[str, Any], lang: str) -> dict[str, Any]:
    enabled = bool(draft.get("enabled", True))
    return {
        "id": _DRAFT_PREVIEW_ID,
        "name": str(draft.get("name", "")).strip() or _tr(lang, "未命名任务", "Untitled task"),
        "enabled": enabled,
        "schedule_kind": str(draft.get("schedule_kind", "every") or "every"),
        "schedule": {
            "kind": str(draft.get("schedule_kind", "every") or "every"),
            "at_ms": None,
            "every_ms": None,
            "expr": str(draft.get("cron_expr", "") or ""),
            "tz": str(draft.get("timezone", "") or ""),
        },
        "schedule_summary": _draft_schedule_summary(draft, lang),
        "message": str(draft.get("message", "")),
        "deliver": bool(draft.get("deliver", False)),
        "channel": str(draft.get("channel", "")),
        "target": str(draft.get("target", "")),
        "delete_after_run": bool(draft.get("delete_after_run", False)),
        "next_run_at_ms": None,
        "next_run_text": _tr(lang, "保存后生成", "Created after save"),
        "last_run_at_ms": None,
        "last_run_text": "",
        "last_status": "",
        "last_error": "",
        "last_result_text": _tr(lang, "尚未保存", "Not saved yet"),
        "status_key": "draft",
        "status_label": _tr(lang, "新草稿", "New draft"),
        "session_key": "",
        "created_at_ms": None,
        "updated_at_ms": None,
        "is_draft": True,
    }
