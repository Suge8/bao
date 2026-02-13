"""Test session management with cache-friendly message handling."""

import pytest
from pathlib import Path
from typing import Callable
from nanobot.session.manager import Session, SessionManager


class TestSessionLastConsolidated:
    """Test last_consolidated tracking to avoid duplicate processing."""

    def test_initial_last_consolidated_zero(self) -> None:
        """Test that new session starts with last_consolidated=0."""
        session = Session(key="test:initial")
        assert session.last_consolidated == 0

    def test_last_consolidated_persistence(self, tmp_path) -> None:
        """Test that last_consolidated persists across save/load."""
        manager = SessionManager(Path(tmp_path))

        session1 = Session(key="test:persist")
        for i in range(20):
            session1.add_message("user", f"msg{i}")
        session1.last_consolidated = 15  # Simulate consolidation
        manager.save(session1)

        session2 = manager.get_or_create("test:persist")
        assert session2.last_consolidated == 15
        assert len(session2.messages) == 20

    def test_clear_resets_last_consolidated(self) -> None:
        """Test that clear() resets last_consolidated to 0."""
        session = Session(key="test:clear")
        for i in range(10):
            session.add_message("user", f"msg{i}")
        session.last_consolidated = 5

        session.clear()
        assert len(session.messages) == 0
        assert session.last_consolidated == 0


class TestSessionImmutableHistory:
    """Test Session message immutability for cache efficiency."""

    def test_initial_state(self) -> None:
        """Test that new session has empty messages list."""
        session = Session(key="test:initial")
        assert len(session.messages) == 0

    def test_add_messages_appends_only(self) -> None:
        """Test that adding messages only appends, never modifies."""
        session = Session(key="test:preserve")
        session.add_message("user", "msg1")
        session.add_message("assistant", "resp1")
        session.add_message("user", "msg2")
        assert len(session.messages) == 3
        # First message should always be the first message added
        assert session.messages[0]["content"] == "msg1"

    def test_get_history_returns_most_recent(self) -> None:
        """Test get_history returns the most recent messages."""
        session = Session(key="test:history")
        for i in range(10):
            session.add_message("user", f"msg{i}")
            session.add_message("assistant", f"resp{i}")
        history = session.get_history(max_messages=6)
        # Should return last 6 messages
        assert len(history) == 6
        # First returned should be resp4 (messages 7-12: msg7/resp7, msg8/resp8, msg9/resp9)
        # Actually: 20 messages total, last 6 are indices 14-19
        assert history[0]["content"] == "msg7"  # Index 14 (7th user msg after 7 pairs)
        assert history[-1]["content"] == "resp9"  # Index 19 (last assistant msg)

    def test_get_history_with_all_messages(self) -> None:
        """Test get_history with max_messages larger than actual."""
        session = Session(key="test:all")
        for i in range(5):
            session.add_message("user", f"msg{i}")
        history = session.get_history(max_messages=100)
        assert len(history) == 5
        assert history[0]["content"] == "msg0"

    def test_get_history_stable_for_same_session(self) -> None:
        """Test that get_history returns same content for same max_messages."""
        session = Session(key="test:stable")
        for i in range(20):
            session.add_message("user", f"msg{i}")

        # Multiple calls with same max_messages should return identical content
        history1 = session.get_history(max_messages=10)
        history2 = session.get_history(max_messages=10)
        assert history1 == history2

    def test_messages_list_never_modified(self) -> None:
        """Test that messages list is never modified after creation."""
        session = Session(key="test:immutable")
        original_len = 0

        # Add some messages
        for i in range(5):
            session.add_message("user", f"msg{i}")
            original_len += 1

        assert len(session.messages) == original_len

        # get_history should not modify the list
        session.get_history(max_messages=2)
        assert len(session.messages) == original_len

        # Multiple calls should not affect messages
        for _ in range(10):
            session.get_history(max_messages=3)
        assert len(session.messages) == original_len


class TestSessionPersistence:
    """Test Session persistence and reload."""

    @pytest.fixture
    def temp_manager(self, tmp_path):
        return SessionManager(Path(tmp_path))

    def test_persistence_roundtrip(self, temp_manager):
        """Test that messages persist across save/load."""
        session1 = Session(key="test:persistence")
        for i in range(20):
            session1.add_message("user", f"msg{i}")
        temp_manager.save(session1)

        session2 = temp_manager.get_or_create("test:persistence")
        assert len(session2.messages) == 20
        assert session2.messages[0]["content"] == "msg0"
        assert session2.messages[-1]["content"] == "msg19"

    def test_get_history_after_reload(self, temp_manager):
        """Test that get_history works correctly after reload."""
        session1 = Session(key="test:reload")
        for i in range(30):
            session1.add_message("user", f"msg{i}")
        temp_manager.save(session1)

        session2 = temp_manager.get_or_create("test:reload")
        history = session2.get_history(max_messages=10)
        # Should return last 10 messages (indices 20-29)
        assert len(history) == 10
        assert history[0]["content"] == "msg20"
        assert history[-1]["content"] == "msg29"

    def test_clear_resets_session(self, temp_manager):
        """Test that clear() properly resets session."""
        session = Session(key="test:clear")
        for i in range(10):
            session.add_message("user", f"msg{i}")
        assert len(session.messages) == 10

        session.clear()
        assert len(session.messages) == 0

