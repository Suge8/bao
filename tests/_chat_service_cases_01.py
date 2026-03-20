# ruff: noqa: F401,F403,F405,I001
from __future__ import annotations

from tests._chat_service_testkit import *

def test_initial_state():
    svc, _ = make_service()
    assert svc.state == "idle"
    assert svc.lastError == ""
    assert svc.viewPhase == "idle"


def test_view_phase_uses_loading_for_starting_and_history_windows() -> None:
    svc, _ = make_service()

    svc._set_state("starting")
    assert svc.viewPhase == "loading"

    svc._set_state("running")
    assert svc.viewPhase == "loading"

    svc._set_history_loading(True)
    assert svc.viewPhase == "loading"


def test_view_phase_becomes_ready_when_active_session_ready() -> None:
    svc, _ = make_service()

    svc._set_state("running")
    svc._set_active_session_state(True, False)

    assert svc.viewPhase == "ready"


def test_view_phase_prefers_error() -> None:
    svc, _ = make_service()

    svc._set_state("running")
    svc._set_active_session_state(True, True)
    svc._set_state("error")

    assert svc.viewPhase == "error"


def test_call_agent_passes_runtime_token_metadata_without_desktop_presave() -> None:
    from types import SimpleNamespace
    from bao.agent._loop_user_message_models import ProcessDirectRequest

    svc, _model = make_service()
    sm = MagicMock()
    svc._session_manager = sm
    svc._profile_context_data = {"profile_id": "work"}

    captured: dict[str, Any] = {}

    async def _process_direct(request: ProcessDirectRequest) -> str:
        captured["text"] = request.content
        captured["session_key"] = request.session_key
        captured["channel"] = request.channel
        captured["chat_id"] = request.chat_id
        captured["profile_id"] = request.profile_id
        captured["route"] = request.to_route_key()
        captured["metadata"] = request.metadata
        return "ok"

    svc._agent = SimpleNamespace(process_direct=_process_direct)

    result = asyncio.run(svc._call_agent("hello", "desktop:local::s1"))

    assert result == "ok"
    assert captured["text"] == "hello"
    assert captured["session_key"] == "desktop:local::s1"
    assert captured["channel"] == "desktop"
    assert captured["chat_id"] == "local"
    assert captured["profile_id"] == "work"
    assert captured["route"].profile_id == "work"
    token = captured["metadata"].get("_pre_saved_token")
    assert isinstance(token, str) and token


def test_call_agent_passes_media_paths_to_process_direct() -> None:
    from pathlib import Path
    from types import SimpleNamespace
    from bao.agent._loop_user_message_models import ProcessDirectRequest

    svc, _model = make_service()
    sm = MagicMock()
    svc._session_manager = sm

    captured: dict[str, Any] = {}

    async def _process_direct(request: ProcessDirectRequest) -> str:
        captured["text"] = request.content
        captured["media"] = request.media
        captured["metadata"] = request.metadata
        return "ok"

    svc._agent = SimpleNamespace(process_direct=_process_direct)

    media_path = str(Path("/tmp") / "sample.png")
    result = asyncio.run(
        svc._call_agent(
            "describe this",
            "desktop:local::s1",
            display_text="describe this\n\n[Attachments] sample.png",
            media_paths=[media_path],
        )
    )

    assert result == "ok"
    assert captured["text"] == "describe this"
    assert captured["media"] == [media_path]
    assert isinstance(captured["metadata"].get("_pre_saved_token"), str)


def test_call_agent_metadata_is_independent_from_local_manager_failures() -> None:
    from types import SimpleNamespace
    from bao.agent._loop_user_message_models import ProcessDirectRequest

    svc, _model = make_service()
    svc._session_manager = MagicMock()

    captured: dict[str, Any] = {}

    async def _process_direct(request: ProcessDirectRequest) -> str:
        captured["text"] = request.content
        captured["metadata"] = request.metadata
        return "ok"

    svc._agent = SimpleNamespace(process_direct=_process_direct)

    result = asyncio.run(svc._call_agent("hello", "desktop:local::s1"))

    assert result == "ok"
    assert isinstance(captured["metadata"].get("_pre_saved_token"), str)


def test_send_message_appends_user_row():
    svc, model = make_service()
    svc.sendMessage("hello")
    assert model.rowCount() == 1
    assert model._messages[0]["role"] == "user"
    assert model._messages[0]["content"] == "hello"
    assert model._messages[0]["status"] == "pending"


def test_send_empty_message_ignored():
    svc, model = make_service()
    svc.sendMessage("   ")
    assert model.rowCount() == 0


def test_send_message_ignored_for_read_only_session():
    svc, model = make_service()
    svc.setActiveSessionReadOnly(True)
    svc.sendMessage("hello")
    assert model.rowCount() == 0


def test_send_message_with_attachments_uses_single_queue_path(tmp_path) -> None:
    svc, model = make_service()
    attachment = tmp_path / "image.png"
    attachment.write_bytes(b"png")

    svc.addDraftAttachments([attachment.as_uri()])
    svc.sendMessage("")

    assert model.rowCount() == 1
    assert model._messages[0]["role"] == "user"
    assert model._messages[0]["status"] == "pending"
    assert "image.png" in model._messages[0]["content"]
    assert svc.draftAttachmentCount == 0


def test_paste_clipboard_attachment_adds_local_file_urls(tmp_path, monkeypatch) -> None:
    svc, _model = make_service()
    attachment = tmp_path / "note.txt"
    attachment.write_text("hello", encoding="utf-8")

    fake_mime_data = type(
        "FakeMimeData",
        (),
        {
            "hasUrls": lambda self: True,
            "urls": lambda self: [QtCore.QUrl.fromLocalFile(str(attachment))],
            "hasImage": lambda self: False,
        },
    )()
    fake_clipboard = type(
        "FakeClipboard",
        (),
        {
            "mimeData": lambda self: fake_mime_data,
            "image": lambda self: QImage(),
        },
    )()

    monkeypatch.setattr(QGuiApplication, "clipboard", staticmethod(lambda: fake_clipboard))

    assert svc.pasteClipboardAttachment() is True
    assert svc.draftAttachmentCount == 1
    draft_attachments = svc.property("draftAttachments")
    assert draft_attachments is not None
    assert draft_attachments.rowCount() == 1
    assert draft_attachments.snapshot_names() == ["note.txt"]


def test_paste_clipboard_attachment_saves_image_to_draft(monkeypatch) -> None:
    svc, _model = make_service()
    image = QImage(8, 8, QImage.Format.Format_ARGB32)
    image.fill(0xFFCC8844)

    fake_mime_data = type(
        "FakeMimeData",
        (),
        {
            "hasUrls": lambda self: False,
            "urls": lambda self: [],
            "hasImage": lambda self: True,
        },
    )()
    fake_clipboard = type(
        "FakeClipboard",
        (),
        {
            "mimeData": lambda self: fake_mime_data,
            "image": lambda self: image,
        },
    )()

    monkeypatch.setattr(QGuiApplication, "clipboard", staticmethod(lambda: fake_clipboard))

    assert svc.pasteClipboardAttachment() is True
    assert svc.draftAttachmentCount == 1
    draft_attachments = svc.property("draftAttachments")
    assert draft_attachments is not None
    saved_path = draft_attachments.snapshot_paths()[0]
    assert saved_path.endswith(".png")
