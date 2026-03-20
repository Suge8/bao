"""Shared helpers for ConfigService tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import patch

pytest = importlib.import_module("pytest")

QtGui = pytest.importorskip("PySide6.QtGui")
QGuiApplication = QtGui.QGuiApplication

MINIMAL_CONFIG = """{
  // provider config
  "providers": {
    "openaiCompatible": {
      "apiKey": "sk-test",
      "baseUrl": "https://api.openai.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o",
      "temperature": 0.7,
      "maxTokens": 4096
    }
  }
}"""


@pytest.fixture(scope="module", autouse=True)
def qt_app():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    yield app


def load_service(tmp_path: Path, config_text: str = MINIMAL_CONFIG):
    from app.backend.config import ConfigService

    cfg = tmp_path / "config.jsonc"
    cfg.write_text(config_text, encoding="utf-8")
    svc = ConfigService()
    with patch("bao.config.loader.get_config_path", return_value=cfg):
        svc.load()
    return svc, cfg
