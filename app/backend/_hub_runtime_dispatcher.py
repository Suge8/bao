from __future__ import annotations

from typing import Any

from bao.profile import profile_context_from_mapping


def sync_dispatcher_profile_context(service: Any) -> None:
    dispatcher = getattr(service, "_dispatcher", None)
    if dispatcher is None:
        return
    profile_context = profile_context_from_mapping(getattr(service, "_profile_context_data", None))
    dispatcher.set_current_profile(profile_context.profile_id if profile_context is not None else "")
    sync_dispatcher_runtime_state(
        service,
        update_hub_bindings=False,
        emit_hub_ready=False,
    )


def sync_dispatcher_after_request(service: Any, profile_id: str) -> None:
    dispatcher = getattr(service, "_dispatcher", None)
    if dispatcher is None:
        return
    if getattr(dispatcher, "current_profile_id", "") != str(profile_id or "").strip():
        return
    sync_dispatcher_runtime_state(
        service,
        update_hub_bindings=True,
        emit_hub_ready=True,
    )


def sync_dispatcher_runtime_state(
    service: Any,
    *,
    update_hub_bindings: bool,
    emit_hub_ready: bool,
) -> None:
    dispatcher = getattr(service, "_dispatcher", None)
    if dispatcher is None:
        return
    runtime_agent = getattr(dispatcher, "agent", None)
    if runtime_agent is not None:
        service._agent = runtime_agent
    next_cron = getattr(dispatcher, "cron", None)
    if service._cron is not next_cron:
        service._cron = next_cron
        service.cronServiceChanged.emit(service._cron)
    next_heartbeat = getattr(dispatcher, "heartbeat", None)
    if service._heartbeat is not next_heartbeat:
        service._heartbeat = next_heartbeat
        service.heartbeatServiceChanged.emit(service._heartbeat)
    if service._cron is not None:
        try:
            service._cron_status = service._cron.status()
        except Exception:
            service._cron_status = {}
    runtime_port = getattr(dispatcher, "runtime_port", None)
    directory = getattr(dispatcher, "directory", None)
    if update_hub_bindings and (runtime_port is not None or directory is not None):
        service._sync_hub_bindings()
    if emit_hub_ready and runtime_port is not None:
        service.hubReady.emit()
