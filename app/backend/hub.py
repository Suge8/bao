"""Desktop ChatService facade for hub lifecycle, history, and message IO."""

from __future__ import annotations

import asyncio
import concurrent.futures
import queue
import threading
import uuid
from collections import OrderedDict
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication

from app.backend._hub_access import DesktopHubAccess
from app.backend._hub_access_mixin import ChatServiceHubAccessMixin
from app.backend._hub_common import _normalize_hub_channels
from app.backend._hub_history import ChatServiceHistoryMixin
from app.backend._hub_message_persistence import ChatServiceMessagePersistenceMixin
from app.backend._hub_notifications import ChatServiceNotificationsMixin
from app.backend._hub_runtime import ChatServiceRuntimeMixin
from app.backend._hub_send import ChatServiceSendMixin
from app.backend._hub_state import ChatServiceStateMixin
from app.backend._hub_streaming import ChatServiceStreamingMixin
from app.backend._hub_types import (
    _ActiveUserMessage,
    _HistorySnapshot,
    _QueuedSendRequest,
    _QueuedUiMessage,
)
from app.backend._hub_user_persistence import ChatServiceUserPersistenceMixin
from app.backend.asyncio_runner import AsyncioRunner
from app.backend.attachment import AttachmentDraftModel
from app.backend.chat import ChatMessageModel


class ChatService(
    ChatServiceHubAccessMixin,
    ChatServiceHistoryMixin,
    ChatServiceSendMixin,
    ChatServiceStreamingMixin,
    ChatServiceUserPersistenceMixin,
    ChatServiceNotificationsMixin,
    ChatServiceMessagePersistenceMixin,
    ChatServiceRuntimeMixin,
    ChatServiceStateMixin,
    QObject,
):
    stateChanged = Signal(str)
    errorChanged = Signal(str)
    hubDetailChanged = Signal(str)
    hubChannelsChanged = Signal()
    cronServiceChanged = Signal(object)
    heartbeatServiceChanged = Signal(object)
    hubReady = Signal()
    historyLoadingChanged = Signal(bool)
    activeSessionStateChanged = Signal()
    viewPhaseChanged = Signal(str)
    sessionViewApplied = Signal(str)
    sessionSwitchedApplied = Signal(str)
    historyReady = Signal(str)
    appendAtBottom = Signal(int)
    incrementalContent = Signal(int)
    statusSettled = Signal(int, str)
    draftAttachmentCountChanged = Signal()
    startupActivityChanged = Signal()

    _initResult = Signal(int, bool, str, object, list)
    _sendResult = Signal(int, bool, str)  # row, ok, content_or_error
    _historyResult = Signal(bool, str, object)  # ok, error, messages_list
    _progressUpdate = Signal(int, str)  # row, accumulated_content (asyncio → Qt)
    _toolHintUpdate = Signal(str)
    _systemResponse = Signal(str, str)
    _startupMessage = Signal(object)
    _startupActivityUpdate = Signal(object)
    _controlPlaneError = Signal(str)
    _sessionChange = Signal(object)

    def __init__(self, model: ChatMessageModel, runner: AsyncioRunner, parent: Any = None) -> None:
        super().__init__(parent)
        self._model = model
        self._runner = runner
        self._state = "idle"
        self._last_error = ""
        self._hub_detail = ""
        self._hub_channels: list[dict[str, Any]] = []
        self._configured_hub_channels: list[str] = []
        self._enabled_hub_channels: list[str] = []
        self._channel_errors: dict[str, str] = {}
        self._agent, self._channels, self._cron, self._heartbeat = (None, None, None, None)
        self._dispatcher = None
        self._hub_access = DesktopHubAccess()
        self._background_tasks: list[asyncio.Task[Any]] = []
        self._session_key = "desktop:local"
        self._desired_session_key = self._session_key
        self._committed_session_key = self._session_key
        self._startup_target_key = ""
        self._startup_pending: list[_QueuedUiMessage] = []
        self._startup_activity: dict[str, Any] = {}
        self._history_initialized = False
        self._history_fingerprint: tuple[int, str] | None = None
        self._history_cache: OrderedDict[str, _HistorySnapshot] = OrderedDict()
        self._history_loading = False
        self._active_session_ready = False
        self._active_session_has_messages = False
        self._active_summary_key = ""
        self._active_summary_message_count: int | None = None
        self._active_summary_has_messages: bool | None = None
        self._active_session_read_only = False
        self._current_nav_id = 0
        self._history_future: Any = None
        self._send_queue: queue.Queue[_QueuedSendRequest] = queue.Queue()
        self._processing = False
        self._lang = "en"
        self._lock = threading.Lock()
        self._cron_status: dict[str, Any] = {}
        self._bound_hub_directory: Any = None
        self._bound_hub_runtime: Any = None
        self._hot_session_managers: OrderedDict[str, Any] = OrderedDict()
        self._config_data: dict[str, Any] | None = None
        self._profile_context_data: dict[str, Any] | None = None
        self._pending_notifications: list[_QueuedUiMessage] = []
        self._active_streaming_row, self._active_streaming_session_key = -1, None
        self._active_user = _ActiveUserMessage()
        self._active_send_future: Any = None
        self._active_has_content = False
        self._pending_split = False
        self._lifecycle_request_id = 0
        self._init_future: concurrent.futures.Future[Any] | None = None
        self._shutdown_future: concurrent.futures.Future[Any] | None = None
        self._restart_requested = False
        self._draft_attachments = AttachmentDraftModel(self)
        self._draft_attachments.countChanged.connect(self.draftAttachmentCountChanged)
        self._initResult.connect(self._handle_init_result)
        self._sendResult.connect(self._handle_send_result)
        self._historyResult.connect(self._handle_history_result)
        self._progressUpdate.connect(self._handle_progress_update)
        self._toolHintUpdate.connect(self._handle_tool_hint_update)
        self._systemResponse.connect(self._handle_system_response)
        self._startupMessage.connect(self._handle_startup_message)
        self._startupActivityUpdate.connect(self._handle_startup_activity_update)
        self._controlPlaneError.connect(self._handle_control_plane_error)
        self._sessionChange.connect(self._handle_session_change)

    @Property(str, notify=stateChanged)
    def state(self) -> str:
        return self._state

    @Property(str, notify=stateChanged)
    def hubState(self) -> str:
        return self._project_hub_state()

    @Property(str, notify=errorChanged)
    def lastError(self) -> str:
        return self._last_error

    @Property(bool, notify=errorChanged)
    def hubDetailIsError(self) -> bool:
        return bool(self._last_error)

    @Property(str, notify=hubDetailChanged)
    def hubDetail(self) -> str:
        return self._hub_detail

    @Property(dict, notify=startupActivityChanged)
    def startupActivity(self) -> dict[str, Any]:
        return dict(self._startup_activity)

    @Property(list, notify=hubChannelsChanged)
    def hubChannels(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._hub_channels]

    @Property(QObject, constant=True)
    def messages(self) -> ChatMessageModel:
        return self._model

    @Property(bool, notify=historyLoadingChanged)
    def historyLoading(self) -> bool:
        return self._history_loading

    @Property(bool, notify=activeSessionStateChanged)
    def activeSessionReady(self) -> bool:
        return self._active_session_ready

    @Property(bool, notify=activeSessionStateChanged)
    def activeSessionHasMessages(self) -> bool:
        return self._active_session_has_messages

    @Property(str, notify=viewPhaseChanged)
    def viewPhase(self) -> str:
        return self._compute_view_phase()

    @Property(QObject, constant=True)
    def draftAttachments(self) -> AttachmentDraftModel:
        return self._draft_attachments

    @Property(int, notify=draftAttachmentCountChanged)
    def draftAttachmentCount(self) -> int:
        return self._draft_attachments.rowCount()

    @Slot(str)
    def setLanguage(self, lang: str) -> None:
        self._lang = lang if lang in ("zh", "en") else "en"

    @Slot(list)
    def setConfiguredHubChannels(self, channels: list[str]) -> None:
        normalized = _normalize_hub_channels(
            [
                channel.strip()
                for channel in channels
                if isinstance(channel, str) and channel.strip()
            ]
        )
        if self._configured_hub_channels == normalized:
            return
        self._configured_hub_channels = normalized
        if self._state in ("idle", "stopped", "starting"):
            self._refresh_hub_channels()

    @Slot(str)
    def sendMessage(self, text: str) -> None:
        if self._active_session_read_only:
            return
        raw_text = text.strip()
        media_paths = self._draft_attachments.snapshot_paths()
        if not raw_text and not media_paths:
            return
        client_token = uuid.uuid4().hex
        display_text = self._compose_user_display_text(
            raw_text, self._draft_attachments.snapshot_names()
        )
        row = self._model.append_user(display_text, status="pending", client_token=client_token)
        self._draft_attachments.clear()
        self.appendAtBottom.emit(row)
        self._enqueue(
            _QueuedSendRequest(
                session_key=self._session_key,
                raw_text=raw_text,
                display_text=display_text,
                media_paths=media_paths,
                row=row,
                client_token=client_token,
            )
        )

    @Slot("QVariant")
    def addDraftAttachments(self, values: Any) -> None:
        paths = self._coerce_local_paths(values)
        if paths:
            self._draft_attachments.add_local_paths(paths)

    @Slot(int)
    def removeDraftAttachment(self, index: int) -> None:
        self._draft_attachments.remove_at(index)

    @Slot()
    def clearDraftAttachments(self) -> None:
        self._draft_attachments.clear()

    @Slot(result=bool)
    def pasteClipboardAttachment(self) -> bool:
        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            return False
        mime_data = clipboard.mimeData()
        if mime_data is None:
            return False

        local_paths: list[str] = []
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if not url.isLocalFile():
                    continue
                local_file = url.toLocalFile()
                if local_file:
                    local_paths.append(local_file)
        if local_paths:
            return self._draft_attachments.add_local_paths(local_paths)

        if not mime_data.hasImage():
            return False
        image_obj = clipboard.image()
        if image_obj.isNull():
            return False
        saved_path = self._save_clipboard_image(image_obj)
        if not saved_path:
            return False
        return self._draft_attachments.add_local_paths([saved_path])
