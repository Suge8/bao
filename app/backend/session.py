"""SessionService — desktop Hub read/control adapter."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, QObject, Signal

from app.backend import session_projection
from app.backend._hub_access import DesktopHubAccess
from app.backend._session_list_model import SessionListModel
from app.backend._session_service_action_results import SessionServiceActionResultsMixin
from app.backend._session_service_async import SessionServiceAsyncMixin
from app.backend._session_service_bootstrap import SessionServiceBootstrapMixin
from app.backend._session_service_change_events import SessionServiceChangeEventsMixin
from app.backend._session_service_discovery import SessionServiceDiscoveryMixin
from app.backend._session_service_entry_results import SessionServiceEntryResultsMixin
from app.backend._session_service_list_results import SessionServiceListResultsMixin
from app.backend._session_service_mutations import SessionServiceMutationMixin
from app.backend._session_service_view import SessionServiceViewMixin
from app.backend._session_sidebar_model import SidebarRowsModel
from app.backend._session_state import PendingDeleteState, SessionUiState
from app.backend.asyncio_runner import AsyncioRunner
from app.backend.list_model import KeyValueListModel
from app.backend.session_projection import ActiveSessionProjection, visible_sidebar_items

_format_display_title = session_projection.format_display_title
_format_updated_label = session_projection.format_updated_label
_visible_sidebar_items = visible_sidebar_items


class SessionService(
    SessionServiceBootstrapMixin,
    SessionServiceViewMixin,
    SessionServiceAsyncMixin,
    SessionServiceChangeEventsMixin,
    SessionServiceDiscoveryMixin,
    SessionServiceListResultsMixin,
    SessionServiceEntryResultsMixin,
    SessionServiceActionResultsMixin,
    SessionServiceMutationMixin,
    QObject,
):
    sessionsChanged = Signal()
    sidebarProjectionWillChange = Signal()
    sidebarProjectionChanged = Signal()
    activeKeyChanged = Signal(str)
    activeSummaryChanged = Signal(str, object, object)
    activeReady = Signal(str)
    startupTargetReady = Signal(str)
    activeSessionMetaChanged = Signal()
    sessionsLoadingChanged = Signal(bool)
    errorOccurred = Signal(str)
    deleteCompleted = Signal(str, bool, str)
    hubLocalPortsReady = Signal(object)
    sessionDiscoveryChanged = Signal()

    _bootstrapResult = Signal(bool, str, object)
    _listResult = Signal(bool, str, object)
    _selectResult = Signal(bool, str, str)
    _createResult = Signal(bool, str, str)
    _deleteResult = Signal(str, bool, str)
    _sessionChange = Signal(object)
    _sessionEntryResult = Signal(bool, str, object)
    _discoveryResult = Signal(bool, str, object)

    def __init__(self, runner: AsyncioRunner, parent: Any = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._hub_access = DesktopHubAccess()
        self._local_hub_ports: Any = None
        self._bound_hub_directory: Any = None
        self._natural_key = "desktop:local"
        self._ui_state = SessionUiState()
        self._last_emitted_active_key = ""
        self._model = SessionListModel()
        self._sidebar_model = SidebarRowsModel()
        self._recent_sessions_model = KeyValueListModel(self)
        self._lookup_results_model = KeyValueListModel(self)
        self._list_request_seq = 0
        self._list_latest_seq = 0
        self._list_inflight_count = 0
        self._refresh_inflight = False
        self._refresh_requested = False
        self._active_commit_seq = 0
        self._bootstrap_storage_root = ""
        self._session_entry_generation = 0
        self._session_entry_request_seq: dict[str, int] = {}
        self._discovery_request_seq = 0
        self._discovery_latest_seq = 0
        self._disposed = False
        self._active_session_read_only = False
        self._recent_sessions: list[dict[str, Any]] = []
        self._lookup_results: list[dict[str, Any]] = []
        self._lookup_query = ""
        self._default_session: dict[str, Any] = {}
        self._resolved_session: dict[str, Any] = {}
        self._resolved_session_ref = ""
        self._active_session_projection = ActiveSessionProjection(
            key="",
            message_count=None,
            has_messages=None,
            read_only=False,
        )
        self._bootstrapResult.connect(self._handle_bootstrap_result)
        self._listResult.connect(self._handle_list_result)
        self._selectResult.connect(self._handle_select_result)
        self._createResult.connect(self._handle_create_result)
        self._deleteResult.connect(self._handle_delete_result)
        self._sessionChange.connect(self._handle_session_change)
        self._sessionEntryResult.connect(self._handle_session_entry_result)
        self._discoveryResult.connect(self._handle_discovery_result)

    @Property(QObject, constant=True)
    def sessionsModel(self) -> SessionListModel:
        return self._model

    @Property(QObject, constant=True)
    def sidebarModel(self) -> SidebarRowsModel:
        return self._sidebar_model

    @Property(QObject, constant=True)
    def recentSessionsModel(self) -> QObject:
        return self._recent_sessions_model

    @Property(QObject, constant=True)
    def lookupResultsModel(self) -> QObject:
        return self._lookup_results_model

    @Property(list, notify=sessionDiscoveryChanged)
    def recentSessions(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._recent_sessions]

    @Property(list, notify=sessionDiscoveryChanged)
    def lookupResults(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._lookup_results]

    @Property(str, notify=sessionDiscoveryChanged)
    def sessionLookupQuery(self) -> str:
        return self._lookup_query

    @Property(dict, notify=sessionDiscoveryChanged)
    def defaultSession(self) -> dict[str, Any]:
        return dict(self._default_session)

    @Property(dict, notify=sessionDiscoveryChanged)
    def resolvedSession(self) -> dict[str, Any]:
        return dict(self._resolved_session)

    @Property(str, notify=sessionDiscoveryChanged)
    def resolvedSessionRef(self) -> str:
        return self._resolved_session_ref

    @Property(int, notify=sidebarProjectionChanged)
    def sidebarUnreadCount(self) -> int:
        return self._ui_state.unread_count

    @Property(str, notify=sidebarProjectionChanged)
    def sidebarUnreadFingerprint(self) -> str:
        return self._ui_state.unread_fingerprint

    @Property(str, notify=activeKeyChanged)
    def activeKey(self) -> str:
        return self._ui_state.active_key

    @Property(bool, notify=sessionsLoadingChanged)
    def sessionsLoading(self) -> bool:
        return self._ui_state.loading

    @Property(bool, notify=activeSessionMetaChanged)
    def activeSessionReadOnly(self) -> bool:
        return self._active_session_read_only

    def supervisorSessionsSnapshot(self) -> list[dict[str, Any]]:
        return [dict(item) for item in self._ui_state.session_rows if isinstance(item, dict)]

    def _current_hub_directory(self) -> Any:
        self._sync_hub_directory_binding()
        return self._bound_hub_directory

    def _current_hub_control(self) -> Any:
        return self._hub_access.current_control()

    def _sync_hub_directory_binding(self) -> None:
        next_directory = self._hub_access.current_directory()
        previous = self._bound_hub_directory
        if previous is next_directory:
            return
        if previous is not None:
            previous.remove_change_listener(self._on_session_change)
        self._bound_hub_directory = next_directory
        if next_directory is not None:
            next_directory.add_change_listener(self._on_session_change)

    def _has_hub_directory(self) -> bool:
        return self._current_hub_directory() is not None

    def _has_hub_control(self) -> bool:
        return self._current_hub_control() is not None

    @property
    def _active_key(self) -> str:
        return self._ui_state.active_key

    @_active_key.setter
    def _active_key(self, value: str) -> None:
        self._ui_state.active_key = str(value or "")

    @property
    def _pending_select_key(self) -> str | None:
        return self._ui_state.pending_select_key or None

    @_pending_select_key.setter
    def _pending_select_key(self, value: str | None) -> None:
        self._ui_state.pending_select_key = str(value or "")

    @property
    def _pending_deletes(self) -> dict[str, PendingDeleteState]:
        return self._ui_state.pending_deletes

    @_pending_deletes.setter
    def _pending_deletes(self, value: dict[str, PendingDeleteState]) -> None:
        self._ui_state.pending_deletes = value

    @property
    def _pending_creates(self) -> set[str]:
        return self._ui_state.pending_creates

    @_pending_creates.setter
    def _pending_creates(self, value: set[str]) -> None:
        self._ui_state.pending_creates = value

    @property
    def _sidebar_expanded_groups(self) -> dict[str, bool]:
        return self._ui_state.expanded_groups

    @_sidebar_expanded_groups.setter
    def _sidebar_expanded_groups(self, value: dict[str, bool]) -> None:
        self._ui_state.expanded_groups = dict(value)

    @property
    def _sidebar_unread_count(self) -> int:
        return self._ui_state.unread_count

    @_sidebar_unread_count.setter
    def _sidebar_unread_count(self, value: int) -> None:
        self._ui_state.unread_count = int(value)

    @property
    def _sidebar_unread_fingerprint(self) -> str:
        return self._ui_state.unread_fingerprint

    @_sidebar_unread_fingerprint.setter
    def _sidebar_unread_fingerprint(self, value: str) -> None:
        self._ui_state.unread_fingerprint = str(value or "")

    @property
    def _sessions_loading(self) -> bool:
        return self._ui_state.loading

    @_sessions_loading.setter
    def _sessions_loading(self, value: bool) -> None:
        self._ui_state.loading = bool(value)

    @property
    def _hub_ready(self) -> bool:
        return self._ui_state.hub_ready

    @_hub_ready.setter
    def _hub_ready(self, value: bool) -> None:
        self._ui_state.hub_ready = bool(value)


__all__ = [
    "PendingDeleteState",
    "SessionListModel",
    "SessionService",
    "SidebarRowsModel",
    "_format_display_title",
    "_format_updated_label",
    "_visible_sidebar_items",
]
