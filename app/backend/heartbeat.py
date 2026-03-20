from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from app.backend._heartbeat_common import _normalized_path, _tr
from app.backend._heartbeat_runtime import HeartbeatBridgeRuntimeMixin
from app.backend._profile_bootstrap import initial_active_profile_context
from app.backend.asyncio_runner import AsyncioRunner
from bao.heartbeat.service import HeartbeatService


class HeartbeatBridgeService(HeartbeatBridgeRuntimeMixin, QObject):
    stateChanged = Signal()
    busyChanged = Signal(bool)
    noticeChanged = Signal(str, bool)
    profileChanged = Signal()
    _refreshRequested = Signal()
    _refreshResult = Signal(object)
    _runResult = Signal(bool, str)

    def __init__(self, runner: AsyncioRunner, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._session_service: Any = None
        self._hub_running = False
        self._lang = "en"
        self._current_profile_id = ""
        self._current_profile_name = ""
        self._local_heartbeat_file = initial_active_profile_context().heartbeat_file
        self._live_heartbeat: HeartbeatService | None = None
        self._live_listener = lambda: self._refreshRequested.emit()
        self._busy = False
        self._notice_text = ""
        self._notice_success = True
        self._snapshot: dict[str, Any] = self._empty_snapshot()

        self._refreshRequested.connect(self.refresh)
        self._refreshResult.connect(self._handle_refresh_result)
        self._runResult.connect(self._handle_run_result)

    @Property(str, notify=profileChanged)
    def currentProfileId(self) -> str:
        return self._current_profile_id

    @Property(str, notify=profileChanged)
    def currentProfileName(self) -> str:
        return self._current_profile_name

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=noticeChanged)
    def noticeText(self) -> str:
        return self._notice_text

    @Property(bool, notify=noticeChanged)
    def noticeSuccess(self) -> bool:
        return self._notice_success

    @Property(str, notify=stateChanged)
    def heartbeatFilePath(self) -> str:
        return str(self._snapshot.get("heartbeat_file", ""))

    @Property(bool, notify=stateChanged)
    def heartbeatFileExists(self) -> bool:
        return bool(self._snapshot.get("heartbeat_file_exists", False))

    @Property(str, notify=stateChanged)
    def heartbeatPreview(self) -> str:
        return str(self._snapshot.get("heartbeat_preview", ""))

    @Property(bool, notify=stateChanged)
    def enabled(self) -> bool:
        return bool(self._snapshot.get("enabled", False))

    @Property(str, notify=stateChanged)
    def intervalText(self) -> str:
        return str(self._snapshot.get("interval_text", ""))

    @Property(str, notify=stateChanged)
    def lastCheckedText(self) -> str:
        return str(self._snapshot.get("last_checked_text", ""))

    @Property(str, notify=stateChanged)
    def lastDecisionLabel(self) -> str:
        return str(self._snapshot.get("last_decision_label", ""))

    @Property(str, notify=stateChanged)
    def lastError(self) -> str:
        return str(self._snapshot.get("last_error", ""))

    @Property(bool, notify=stateChanged)
    def canRunNow(self) -> bool:
        return self._run_now_state()[0]

    @Property(str, notify=stateChanged)
    def runNowBlockedReason(self) -> str:
        return self._run_now_state()[1]

    def supervisorSnapshot(self) -> dict[str, Any]:
        live = self._effective_live()
        live_status = live.status() if live is not None else {}
        snapshot = dict(self._snapshot)
        snapshot["running"] = bool(live_status.get("running", False))
        snapshot["enabled"] = bool(live_status.get("enabled", snapshot.get("enabled", False)))
        snapshot["last_checked_at_ms"] = live_status.get(
            "last_checked_at_ms",
            snapshot.get("last_checked_at_ms"),
        )
        snapshot["last_run_at_ms"] = live_status.get(
            "last_run_at_ms",
            snapshot.get("last_run_at_ms"),
        )
        snapshot["last_decision"] = str(
            live_status.get("last_decision", snapshot.get("last_decision", ""))
            or ""
        )
        return snapshot

    @Slot(object)
    def setSessionService(self, service: object) -> None:
        self._session_service = service

    @Slot(str, str)
    def setProfileInfo(self, profile_id: str, profile_name: str) -> None:
        next_profile_id = profile_id.strip()
        next_profile_name = profile_name.strip()
        if (
            self._current_profile_id == next_profile_id
            and self._current_profile_name == next_profile_name
        ):
            return
        self._current_profile_id = next_profile_id
        self._current_profile_name = next_profile_name
        self.profileChanged.emit()

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        normalized = "zh" if lang == "zh" else "en"
        if self._lang == normalized:
            return
        self._lang = normalized
        self.refresh()

    @Slot(str)
    def setLocalHeartbeatFilePath(self, path: str) -> None:
        normalized = _normalized_path(path)
        if not normalized:
            return
        if _normalized_path(self._local_heartbeat_file) == normalized:
            self.refresh()
            return
        self._local_heartbeat_file = Path(normalized)
        self.refresh()

    @Slot(object)
    def setLiveHeartbeatService(self, service: object) -> None:
        next_service = service if isinstance(service, HeartbeatService) else None
        if self._live_heartbeat is next_service:
            return
        if self._live_heartbeat is not None:
            self._live_heartbeat.remove_change_listener(self._live_listener)
        self._live_heartbeat = next_service
        if self._live_heartbeat is not None:
            self._live_heartbeat.add_change_listener(self._live_listener)
        self.refresh()

    @Slot(bool)
    def setHubRunning(self, running: bool) -> None:
        self._hub_running = bool(running)
        self.stateChanged.emit()

    @Slot()
    def refresh(self) -> None:
        future = self._submit_safe(self._refresh_snapshot())
        if future is None:
            return
        future.add_done_callback(self._on_refresh_done)

    @Slot()
    def runNow(self) -> None:
        if self._busy:
            return
        self._set_busy(True)
        future = self._submit_safe(self._run_now())
        if future is None:
            self._set_busy(False)
            return
        future.add_done_callback(self._on_run_done)

    @Slot()
    def openHeartbeatSession(self) -> None:
        if self._session_service is None:
            return
        select_session = getattr(self._session_service, "selectSession", None)
        if callable(select_session):
            select_session("heartbeat")

    @Slot()
    def openHeartbeatFile(self) -> None:
        try:
            heartbeat_file = self._ensure_local_heartbeat_file()
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(heartbeat_file))):
                self._set_notice(
                    _tr(
                        self._lang,
                        "无法打开检查说明文件，请稍后重试",
                        "Unable to open the check instructions right now",
                    ),
                    False,
                )
                return
            self.refresh()
        except Exception as exc:
            self._set_notice(str(exc), False)
