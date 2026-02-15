"""Tests for Telegram channel implementation."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.telegram import TelegramChannel, _markdown_to_telegram_html
from nanobot.config.schema import TelegramConfig


def _make_config() -> TelegramConfig:
    return TelegramConfig(
        enabled=True,
        token="fake-token",
        allow_from=[],
        proxy=None,
    )


class TestMarkdownToTelegramHtml:
    """Tests for markdown to Telegram HTML conversion."""

    def test_empty_text(self) -> None:
        assert _markdown_to_telegram_html("") == ""

    def test_plain_text_passthrough(self) -> None:
        text = "Hello world"
        assert _markdown_to_telegram_html(text) == "Hello world"

    def test_bold_double_asterisks(self) -> None:
        text = "This is **bold** text"
        assert _markdown_to_telegram_html(text) == "This is <b>bold</b> text"

    def test_bold_double_underscore(self) -> None:
        text = "This is __bold__ text"
        assert _markdown_to_telegram_html(text) == "This is <b>bold</b> text"

    def test_italic_underscore(self) -> None:
        text = "This is _italic_ text"
        assert _markdown_to_telegram_html(text) == "This is <i>italic</i> text"

    def test_italic_not_inside_words(self) -> None:
        text = "some_var_name"
        assert _markdown_to_telegram_html(text) == "some_var_name"

    def test_strikethrough(self) -> None:
        text = "This is ~~deleted~~ text"
        assert _markdown_to_telegram_html(text) == "This is <s>deleted</s> text"

    def test_inline_code(self) -> None:
        text = "Use `print()` function"
        result = _markdown_to_telegram_html(text)
        assert "<code>print()</code>" in result

    def test_inline_code_escapes_html(self) -> None:
        text = "Use `<div>` tag"
        result = _markdown_to_telegram_html(text)
        assert "<code>&lt;div&gt;</code>" in result

    def test_code_block(self) -> None:
        text = """Here is code:
```python
def hello():
    return "world"
```
Done.
"""
        result = _markdown_to_telegram_html(text)
        assert "<pre><code>" in result
        assert "def hello():" in result
        assert "</code></pre>" in result

    def test_code_block_escapes_html(self) -> None:
        text = """```
<div>test</div>
```"""
        result = _markdown_to_telegram_html(text)
        assert "&lt;div&gt;test&lt;/div&gt;" in result

    def test_headers_stripped(self) -> None:
        text = "# Header 1\n## Header 2\n### Header 3"
        result = _markdown_to_telegram_html(text)
        assert "# Header 1" not in result
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Header 3" in result

    def test_blockquotes_stripped(self) -> None:
        text = "> This is a quote\nMore text"
        result = _markdown_to_telegram_html(text)
        assert "> " not in result
        assert "This is a quote" in result

    def test_links_converted(self) -> None:
        text = "Check [this link](https://example.com) out"
        result = _markdown_to_telegram_html(text)
        assert '<a href="https://example.com">this link</a>' in result

    def test_bullet_list_converted(self) -> None:
        text = "- Item 1\n* Item 2"
        result = _markdown_to_telegram_html(text)
        assert "• Item 1" in result
        assert "• Item 2" in result

    def test_html_special_chars_escaped(self) -> None:
        text = "5 < 10 and 10 > 5"
        result = _markdown_to_telegram_html(text)
        assert "5 &lt; 10" in result
        assert "10 &gt; 5" in result

    def test_complex_nested_formatting(self) -> None:
        text = "**Bold _and italic_** and `code`"
        result = _markdown_to_telegram_html(text)
        assert "<b>Bold <i>and italic</i></b>" in result
        assert "<code>code</code>" in result


class TestTelegramChannelSend:
    """Tests for TelegramChannel.send() method."""

    @pytest.mark.asyncio
    async def test_send_short_message_single_chunk(self, monkeypatch) -> None:
        """Short messages are sent as a single message."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content="Hello world"
        ))

        assert len(sent_messages) == 1
        assert sent_messages[0]["chat_id"] == 123456
        assert "Hello world" in sent_messages[0]["text"]
        assert sent_messages[0]["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_send_long_message_split_into_chunks(self, monkeypatch) -> None:
        """Long messages exceeding 4000 chars are split."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        # Create a message longer than 4000 chars
        long_content = "A" * 1000 + "\n" + "B" * 1000 + "\n" + "C" * 1000 + "\n" + "D" * 1000 + "\n" + "E" * 1000

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content=long_content
        ))

        assert len(sent_messages) == 2  # Should be split into 2 messages
        assert all(m["chat_id"] == 123456 for m in sent_messages)

    @pytest.mark.asyncio
    async def test_send_splits_at_newline_when_possible(self, monkeypatch) -> None:
        """Message splitting prefers newline boundaries."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        # Create content with clear paragraph breaks
        paragraphs = [f"Paragraph {i}: " + "x" * 100 for i in range(50)]
        content = "\n".join(paragraphs)

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content=content
        ))

        # Each chunk should end with a complete paragraph (no partial lines)
        for msg in sent_messages:
            # Message should not start with whitespace after stripping
            text = msg["text"]
            assert text == text.lstrip()

    @pytest.mark.asyncio
    async def test_send_falls_back_to_space_boundary(self, monkeypatch) -> None:
        """When no newline available, split at space boundary."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        # Long content without newlines but with spaces
        content = "word " * 2000  # ~10000 chars

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content=content
        ))

        assert len(sent_messages) >= 2

    @pytest.mark.asyncio
    async def test_send_forces_split_when_no_good_boundary(self, monkeypatch) -> None:
        """When no newline or space, force split at max length."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        # Long content without any spaces or newlines
        content = "A" * 10000

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content=content
        ))

        assert len(sent_messages) >= 2
        # Verify all chunks combined equal original
        combined = "".join(m["text"] for m in sent_messages)
        assert combined == content

    @pytest.mark.asyncio
    async def test_send_invalid_chat_id_logs_error(self, monkeypatch) -> None:
        """Invalid chat_id should log error and not send."""
        sent_messages = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                sent_messages.append({"chat_id": chat_id, "text": text})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="not-a-number",
            content="Hello"
        ))

        assert len(sent_messages) == 0

    @pytest.mark.asyncio
    async def test_send_html_parse_error_falls_back_to_plain_text(self, monkeypatch) -> None:
        """When HTML parsing fails, fall back to plain text."""
        sent_messages = []
        call_count = 0

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                nonlocal call_count
                call_count += 1
                if parse_mode == "HTML" and call_count == 1:
                    raise Exception("Bad markup")
                sent_messages.append({"chat_id": chat_id, "text": text, "parse_mode": parse_mode})

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content="Hello **world**"
        ))

        # Should have 2 calls: first HTML (fails), second plain text (succeeds)
        assert call_count == 2
        assert len(sent_messages) == 1
        assert sent_messages[0]["parse_mode"] is None  # Plain text
        assert "Hello **world**" in sent_messages[0]["text"]

    @pytest.mark.asyncio
    async def test_send_not_running_warns(self, monkeypatch) -> None:
        """If bot not running, log warning."""
        warning_logged = []

        def mock_warning(msg, *args):
            warning_logged.append(msg)

        monkeypatch.setattr("nanobot.channels.telegram.logger", MagicMock(warning=mock_warning))

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = None  # Not running

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content="Hello"
        ))

        assert any("not running" in str(m) for m in warning_logged)

    @pytest.mark.asyncio
    async def test_send_stops_typing_indicator(self, monkeypatch) -> None:
        """Sending message should stop typing indicator."""
        stopped_chats = []

        class FakeBot:
            async def send_message(self, chat_id, text, parse_mode=None):
                pass

        fake_app = MagicMock()
        fake_app.bot = FakeBot()

        channel = TelegramChannel(_make_config(), MessageBus())
        channel._app = fake_app
        channel._stop_typing = lambda chat_id: stopped_chats.append(chat_id)

        await channel.send(OutboundMessage(
            channel="telegram",
            chat_id="123456",
            content="Hello"
        ))

        assert "123456" in stopped_chats


class TestTelegramChannelTyping:
    """Tests for typing indicator functionality."""

    @pytest.mark.asyncio
    async def test_start_typing_creates_task(self) -> None:
        channel = TelegramChannel(_make_config(), MessageBus())
        
        # Mock _typing_loop to avoid actual async execution
        channel._typing_loop = AsyncMock()
        
        channel._start_typing("123456")
        
        assert "123456" in channel._typing_tasks
        assert not channel._typing_tasks["123456"].done()
        
        # Clean up
        channel._stop_typing("123456")

    def test_stop_typing_cancels_task(self) -> None:
        channel = TelegramChannel(_make_config(), MessageBus())
        
        # Create a mock task
        mock_task = MagicMock()
        mock_task.done.return_value = False
        channel._typing_tasks["123456"] = mock_task
        
        channel._stop_typing("123456")
        
        mock_task.cancel.assert_called_once()
        assert "123456" not in channel._typing_tasks


class TestTelegramChannelMediaExtensions:
    """Tests for media file extension detection."""

    def test_get_extension_from_mime_type(self) -> None:
        channel = TelegramChannel(_make_config(), MessageBus())
        
        assert channel._get_extension("image", "image/jpeg") == ".jpg"
        assert channel._get_extension("image", "image/png") == ".png"
        assert channel._get_extension("image", "image/gif") == ".gif"
        assert channel._get_extension("audio", "audio/ogg") == ".ogg"
        assert channel._get_extension("audio", "audio/mpeg") == ".mp3"

    def test_get_extension_fallback_to_type(self) -> None:
        channel = TelegramChannel(_make_config(), MessageBus())
        
        assert channel._get_extension("image", None) == ".jpg"
        assert channel._get_extension("voice", None) == ".ogg"
        assert channel._get_extension("audio", None) == ".mp3"

    def test_get_extension_unknown_type(self) -> None:
        channel = TelegramChannel(_make_config(), MessageBus())
        
        assert channel._get_extension("unknown", None) == ""
