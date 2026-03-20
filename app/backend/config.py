"""ConfigService — reads/validates/saves ~/.bao/config.jsonc for the desktop app."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import ClassVar, TypeVar, cast

from PySide6.QtCore import Property, QObject, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from app.backend._config_common import (
    _apply_ui_defaults,
    _as_dict,
    _as_str,
    _bootstrap_config_path,
    _inject_provider_comments,
    _resolved_config_path,
    _typed_slot,
    _write_text_atomic,
)
from app.backend._config_save import _collapse_missing_intermediates, _normalize_changes, _validate
from app.backend.jsonc_patch import patch_jsonc, strip_comments
from bao.config.schema import Config as RuntimeConfig

_T = TypeVar("_T")


class ConfigService(QObject):
    configLoaded: ClassVar[Signal] = Signal()
    saveError: ClassVar[Signal] = Signal(str)
    saveDone: ClassVar[Signal] = Signal()
    stateChanged: ClassVar[Signal] = Signal()  # notify for isValid / needsSetup

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._raw_text: str = ""
        self._data: dict[str, object] = {}
        self._config_path: Path | None = None
        self._valid: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @Property(bool, notify=stateChanged)
    def isValid(self) -> bool:
        return self._valid

    @Property(bool, notify=stateChanged)
    def needsSetup(self) -> bool:
        """True if config exists but is not fully configured (no model or no apiKey)."""
        if not self._valid:
            return True
        model = self.get("agents.defaults.model", "")
        if not isinstance(model, str) or not model:
            return True
        providers = _as_dict(self._data.get("providers", {}))
        if providers is None:
            return True
        for provider in providers.values():
            provider_dict = _as_dict(provider)
            if provider_dict and _as_str(provider_dict.get("apiKey", "")):
                return False
        return True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @_typed_slot()
    def load(self) -> None:
        from bao.runtime_diagnostics import get_runtime_diagnostics_store
        from bao.runtime_diagnostics_models import RuntimeEventRequest

        path = _bootstrap_config_path(self._config_path)
        self._config_path = path
        try:
            self._raw_text = path.read_text(encoding="utf-8")
            stripped = strip_comments(self._raw_text)
            raw_data = cast(object, json.loads(stripped))
            parsed_data = _as_dict(raw_data)
            if parsed_data is None:
                raise ValueError("Top-level config must be an object")
            self._data = parsed_data
            validated = RuntimeConfig.model_validate(self._data)
            _apply_ui_defaults(self._data, validated)
            self._valid = True
            self.stateChanged.emit()
            self.configLoaded.emit()
        except Exception as e:
            self._valid = False
            get_runtime_diagnostics_store().record_event(
                RuntimeEventRequest(
                    source="config",
                    stage="load",
                    message=f"Failed to load config: {e}",
                    level="error",
                    code="config_load_failed",
                    retryable=False,
                    details={"config_path": str(path)},
                )
            )
            self.saveError.emit(f"Failed to load config: {e}")

    def get(self, dotpath: str, default: _T | None = None) -> object | _T | None:
        """Read a value by dot-separated path."""
        parts = dotpath.split(".")
        node: object = self._data
        for part in parts:
            current = _as_dict(node)
            if current is None or part not in current:
                return default
            node = current[part]
        return node

    @_typed_slot(str, result="QVariant")
    def getValue(self, dotpath: str) -> object | None:
        return self.get(dotpath)

    @_typed_slot(result="QVariant")
    def getFirstProvider(self) -> dict[str, object]:
        """Return {name, type, apiKey, apiBase} of the first provider, or empty dict."""
        providers = _as_dict(self._data.get("providers", {}))
        if providers is None or not providers:
            return {}
        name = next(iter(providers))
        provider = _as_dict(providers[name])
        if provider is None:
            return {}
        return {
            "name": name,
            "type": _as_str(provider.get("type", "")),
            "apiKey": _as_str(provider.get("apiKey", "")),
            "apiBase": _as_str(provider.get("apiBase", "")),
        }

    @_typed_slot(result="QVariant")
    def getProviders(self) -> list[dict[str, object]]:
        providers = _as_dict(self._data.get("providers", {}))
        if providers is None:
            return []
        visible: list[dict[str, object]] = []
        for name, provider in providers.items():
            provider_dict = _as_dict(provider)
            if provider_dict is None:
                continue
            visible.append(
                {
                    "name": name,
                    "type": _as_str(provider_dict.get("type", "")),
                    "apiKey": _as_str(provider_dict.get("apiKey", "")),
                    "apiBase": _as_str(provider_dict.get("apiBase", "")),
                }
            )
        return visible

    @_typed_slot(result="QVariant")
    def exportData(self) -> dict[str, object]:
        return copy.deepcopy(self._data)

    @_typed_slot(result=str)
    def getConfigFilePath(self) -> str:
        return str(_resolved_config_path(self._config_path))

    @_typed_slot()
    def openConfigDirectory(self) -> None:
        config_path = _resolved_config_path(self._config_path)
        _ = QDesktopServices.openUrl(QUrl.fromLocalFile(str(config_path.parent)))

    @_typed_slot(str, result=bool)
    def removeProvider(self, name: str) -> bool:
        """Remove a provider by name. Rewrites the providers object."""
        providers = _as_dict(self._data.get("providers", {}))
        if providers is None or name not in providers:
            return False
        return self.save(
            {"providers": {key: value for key, value in providers.items() if key != name}}
        )

    @_typed_slot("QVariantMap", result=bool)
    def save(self, changes: dict[str, object]) -> bool:
        """Apply *changes* (dotpath -> value) and write back preserving comments."""
        if self._config_path is None:
            self.saveError.emit("Config path not set — call load() first")
            return False

        changes = _normalize_changes(changes)

        err = _validate(changes, self.get)
        if err:
            self.saveError.emit(err)
            return False

        changes = _collapse_missing_intermediates(self._data, changes)

        text = self._raw_text or "{}"
        try:
            result, errors = patch_jsonc(text, changes)
        except Exception as e:
            self.saveError.emit(f"Patch failed: {e}")
            return False
        if "providers" in changes:
            result = _inject_provider_comments(result)
        if errors:
            msgs = "; ".join(e.message for e in errors)
            self.saveError.emit(f"Patch errors: {msgs}")
            return False

        try:
            stripped = strip_comments(result)
            raw_candidate = cast(object, json.loads(stripped))
            candidate = _as_dict(raw_candidate)
            if candidate is None:
                raise ValueError("Top-level config must be an object")
            _ = RuntimeConfig.model_validate(candidate)
        except Exception as e:
            self.saveError.emit(f"Config validation failed: {e}")
            return False

        try:
            _write_text_atomic(self._config_path, result)
            self._raw_text = result
            self._data = candidate
            self._valid = True
            self.stateChanged.emit()
            self.saveDone.emit()
            return True
        except Exception as e:
            self.saveError.emit(f"Write failed: {e}")
            return False
