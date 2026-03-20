from __future__ import annotations

from typing import Any

from PySide6.QtCore import Slot

from app.backend._session_discovery_projection import (
    normalize_discovery_items,
    normalize_discovery_snapshot,
)

_DISCOVERY_METHODS = (
    "list_recent_sessions",
    "lookup_sessions",
    "get_default_session",
    "resolve_session_ref",
)
_EMPTY_DISCOVERY_PAYLOAD = {
    "recent_sessions": [],
    "lookup_results": [],
    "default_session": {},
    "resolved_session": {},
}


class SessionServiceDiscoveryMixin:
    def _directory_supports_discovery(self) -> bool:
        directory = self._current_hub_directory()
        if directory is None:
            return False
        return all(callable(getattr(directory, name, None)) for name in _DISCOVERY_METHODS)

    def _request_session_discovery_refresh(self) -> None:
        if self._disposed:
            return
        if not self._directory_supports_discovery():
            self._clear_session_discovery_payload()
            return
        self._discovery_request_seq += 1
        seq = self._discovery_request_seq
        self._discovery_latest_seq = seq
        future = self._submit_safe(
            self._load_session_discovery(
                seq=seq,
                lookup_query=self._lookup_query,
                resolved_session_ref=self._resolved_session_ref,
            )
        )
        if future is not None:
            future.add_done_callback(self._on_discovery_done)

    def _handle_discovery_result(self, ok: bool, error: str, data: Any) -> None:
        if self._disposed:
            return
        if not ok:
            self.errorOccurred.emit(error)
            return
        if not (isinstance(data, tuple) and len(data) == 5):
            return
        seq, recent_raw, lookup_raw, default_raw, resolved_raw = data
        if seq != self._discovery_latest_seq:
            return
        self._apply_session_discovery_payload(
            recent_sessions=normalize_discovery_items(recent_raw),
            lookup_results=normalize_discovery_items(lookup_raw),
            default_session=normalize_discovery_snapshot(default_raw),
            resolved_session=normalize_discovery_snapshot(resolved_raw),
        )

    def _apply_session_discovery_payload(
        self,
        *,
        recent_sessions: list[dict[str, Any]],
        lookup_results: list[dict[str, Any]],
        default_session: dict[str, Any],
        resolved_session: dict[str, Any],
    ) -> None:
        if (
            recent_sessions == self._recent_sessions
            and lookup_results == self._lookup_results
            and default_session == self._default_session
            and resolved_session == self._resolved_session
        ):
            return
        self._recent_sessions = recent_sessions
        self._lookup_results = lookup_results
        self._default_session = default_session
        self._resolved_session = resolved_session
        self._recent_sessions_model.sync_items(recent_sessions)
        self._lookup_results_model.sync_items(lookup_results)
        self.sessionDiscoveryChanged.emit()

    def _clear_session_discovery_payload(self) -> None:
        self._apply_session_discovery_payload(**_EMPTY_DISCOVERY_PAYLOAD)

    def _set_lookup_query(self, value: str) -> bool:
        next_value = str(value or "").strip()
        if next_value == self._lookup_query:
            return False
        self._lookup_query = next_value
        return True

    def _set_resolved_session_ref(self, value: str) -> bool:
        next_ref = str(value or "").strip()
        if next_ref == self._resolved_session_ref:
            return False
        self._resolved_session_ref = next_ref
        return True

    @Slot()
    def refreshSessionDiscovery(self) -> None:
        self._request_session_discovery_refresh()

    @Slot(str)
    def setSessionLookupQuery(self, value: str) -> None:
        if not self._set_lookup_query(value):
            return
        self.sessionDiscoveryChanged.emit()
        self._request_session_discovery_refresh()

    @Slot()
    def clearSessionLookup(self) -> None:
        self.setSessionLookupQuery("")

    @Slot(str)
    def resolveSessionReference(self, value: str) -> None:
        if not self._set_resolved_session_ref(value):
            return
        self.sessionDiscoveryChanged.emit()
        self._request_session_discovery_refresh()
