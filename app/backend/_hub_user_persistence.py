from __future__ import annotations

import uuid
from typing import Any

from loguru import logger

from app.backend.asyncio_runner import AsyncioRunner
from bao.hub import HubUserMessageStatusRequest


class ChatServiceUserPersistenceMixin:
    async def _prepare_user_message_metadata(
        self,
        session_key: str,
        text: str,
        *,
        client_token: str = "",
    ) -> dict[str, Any]:
        if not session_key or not text.strip():
            return {}
        token = str(client_token or "").strip() or uuid.uuid4().hex
        return {"_pre_saved_token": token}

    def _finalize_active_user_message(self, *, ok: bool) -> None:
        active_user = self._active_user
        final_status = "done" if ok else "error"
        if (
            active_user.session_key
            and active_user.session_key == self._committed_session_key
            and active_user.row >= 0
        ):
            self._model.set_status(active_user.row, final_status)
        self._active_user = self._active_user.__class__()
        if not active_user.session_key or not active_user.token:
            return
        runtime = self._current_hub_runtime()
        if runtime is None:
            return
        request = HubUserMessageStatusRequest(
            session_key=active_user.session_key,
            token=active_user.token,
            status=final_status,
        )
        try:
            if isinstance(self._runner, AsyncioRunner):
                future = self._runner.submit(
                    self._run_bg_io(runtime.update_user_message_status, request)
                )
                future.add_done_callback(self._on_finalize_user_message_done)
                return
        except RuntimeError:
            pass
        try:
            runtime.update_user_message_status(request)
        except Exception as exc:
            logger.warning("Failed to finalize desktop user message status: {}", exc)

    def _on_finalize_user_message_done(self, future: Any) -> None:
        try:
            future.result()
        except Exception as exc:
            logger.warning("Failed to finalize desktop user message status: {}", exc)
