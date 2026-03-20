# ruff: noqa: E402, N802, N815, F403, F405, I001
from __future__ import annotations

from tests._chat_view_integration_shared import *

class DummyConfigService(QObject):
    configLoaded = Signal()
    saveDone = Signal()
    saveError = Signal(str)
    stateChanged = Signal()

    def __init__(self, parent: QObject | None = None, **options: object) -> None:
        super().__init__(parent)
        self._is_valid = bool(options.get("is_valid", True))
        self._needs_setup = bool(options.get("needs_setup", False))
        self._language = str(options.get("language", "en"))
        self._ui_update: dict[str, object] = {}
        providers = options.get("providers")
        channels = options.get("channels")
        self._providers: list[dict[str, object]] = [
            dict(item) for item in cast(list[dict[str, object]], providers or [])
        ]
        plain_channels = self._to_plain(channels or {})
        self._channels: dict[str, object] = (
            plain_channels if isinstance(plain_channels, dict) else {}
        )
        self._agents_defaults: dict[str, object] = {}
        self._config_file_path = str(
            options.get("config_file_path", "/tmp/.bao/config.jsonc")
        )
        self.opened_config_directory = False
        model = options.get("model")
        if model is not None:
            self._agents_defaults["model"] = str(model)
        self.last_saved_changes: object | None = None

    def _to_plain(self, value: object) -> object:
        to_variant = getattr(value, "toVariant", None)
        if callable(to_variant):
            return self._to_plain(to_variant())
        if isinstance(value, dict):
            return {str(k): self._to_plain(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._to_plain(item) for item in value]
        return value

    def _deep_merge(self, target: dict[str, object], patch: dict[str, object]) -> None:
        for key, value in patch.items():
            existing = target.get(key)
            if isinstance(value, dict) and isinstance(existing, dict):
                self._deep_merge(existing, value)
            else:
                target[key] = self._to_plain(value)

    @Property(bool, constant=True)
    def isValid(self) -> bool:
        return self._is_valid

    @Property(bool, constant=True)
    def needsSetup(self) -> bool:
        return self._needs_setup

    @Slot(str, result="QVariant")
    def getValue(self, path: str) -> object | None:
        data = {
            "ui": {"language": self._language, "update": dict(self._ui_update)},
            "channels": self._to_plain(self._channels),
            "providers": {
                provider.get("name", f"provider{index + 1}"): {
                    key: value for key, value in provider.items() if key != "name"
                }
                for index, provider in enumerate(self._providers)
                if isinstance(provider, dict)
            },
            "agents": {"defaults": dict(self._agents_defaults)},
        }
        node: object = data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    @Slot(result="QVariant")
    def getProviders(self) -> list[object]:
        return [dict(item) for item in self._providers]

    @Slot("QVariant", result=bool)
    def save(self, changes: object) -> bool:
        changes = self._to_plain(changes)
        self.last_saved_changes = changes
        if isinstance(changes, dict):
            ui = changes.get("ui")
            if isinstance(ui, dict):
                if isinstance(ui.get("language"), str):
                    self._language = ui["language"]
                update = ui.get("update")
                if isinstance(update, dict):
                    self._ui_update.update(update)

            providers = changes.get("providers")
            if isinstance(providers, dict):
                next_providers: list[dict[str, object]] = []
                for name, provider in providers.items():
                    if not isinstance(provider, dict):
                        continue
                    next_providers.append({"name": name, **provider})
                self._providers = next_providers

            channels = changes.get("channels")
            if isinstance(channels, dict):
                self._deep_merge(self._channels, channels)

            agents = changes.get("agents")
            if isinstance(agents, dict):
                defaults = agents.get("defaults")
                if isinstance(defaults, dict):
                    self._agents_defaults.update(defaults)

        self.saveDone.emit()
        self.configLoaded.emit()
        self.stateChanged.emit()
        return True

    @Slot(str, result=bool)
    def removeProvider(self, name: str) -> bool:
        _ = name
        return True

    @Slot(result=str)
    def getConfigFilePath(self) -> str:
        return self._config_file_path

    @Slot()
    def openConfigDirectory(self) -> None:
        self.opened_config_directory = True


class DummyDesktopPreferences(QObject):
    uiLanguageChanged = Signal()
    effectiveLanguageChanged = Signal()
    themeModeChanged = Signal()
    isDarkChanged = Signal()

    def __init__(self, parent: QObject | None = None, **options: object) -> None:
        super().__init__(parent)
        self._ui_language = str(options.get("ui_language", "en"))
        self._theme_mode = str(options.get("theme_mode", "light"))
        self._is_dark = bool(options.get("is_dark", False))

    @Property(str, notify=uiLanguageChanged)
    def uiLanguage(self) -> str:
        return self._ui_language

    @Property(str, notify=effectiveLanguageChanged)
    def effectiveLanguage(self) -> str:
        return self._ui_language

    @Property(str, notify=themeModeChanged)
    def themeMode(self) -> str:
        return self._theme_mode

    @Property(bool, notify=isDarkChanged)
    def isDark(self) -> bool:
        return self._is_dark

    @Slot(str, result=bool)
    def setUiLanguage(self, value: str) -> bool:
        self._ui_language = value
        self.uiLanguageChanged.emit()
        self.effectiveLanguageChanged.emit()
        return True

    @Slot(str, result=bool)
    def setThemeMode(self, value: str) -> bool:
        self._theme_mode = value
        self._is_dark = value == "dark"
        self.themeModeChanged.emit()
        self.isDarkChanged.emit()
        return True

    @Slot()
    def toggleTheme(self) -> None:
        _ = self.setThemeMode("light" if self._is_dark else "dark")

__all__ = [name for name in globals() if name != "__all__" and not (name.startswith("__") and name.endswith("__"))]
