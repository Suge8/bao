from __future__ import annotations

from ._hub_history_load import ChatServiceHistoryLoadMixin
from ._hub_history_startup import ChatServiceHistoryStartupMixin
from ._hub_history_view import ChatServiceHistoryViewMixin


class ChatServiceHistoryMixin(
    ChatServiceHistoryStartupMixin,
    ChatServiceHistoryViewMixin,
    ChatServiceHistoryLoadMixin,
):
    pass
