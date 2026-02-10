import asyncio
import logging
from typing import Any

from loguru import logger
from nio import (
    AsyncClient,
    AsyncClientConfig,
    InviteEvent,
    JoinError,
    MatrixRoom,
    RoomMessageText,
    RoomSendError,
    SyncError,
)

from nanobot.bus.events import OutboundMessage
from nanobot.channels.base import BaseChannel
from nanobot.config.loader import get_data_dir


class _NioLoguruHandler(logging.Handler):
    """Route stdlib logging records from matrix-nio into Loguru output."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _configure_nio_logging_bridge() -> None:
    """Ensure matrix-nio logs are emitted through the project's Loguru format."""
    nio_logger = logging.getLogger("nio")
    if any(isinstance(handler, _NioLoguruHandler) for handler in nio_logger.handlers):
        return

    nio_logger.handlers = [_NioLoguruHandler()]
    nio_logger.propagate = False


class MatrixChannel(BaseChannel):
    """
    Matrix (Element) channel using long-polling sync.
    """

    name = "matrix"

    def __init__(self, config: Any, bus):
        super().__init__(config, bus)
        self.client: AsyncClient | None = None
        self._sync_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start Matrix client and begin sync loop."""
        self._running = True
        _configure_nio_logging_bridge()

        store_path = get_data_dir() / "matrix-store"
        store_path.mkdir(parents=True, exist_ok=True)

        self.client = AsyncClient(
            homeserver=self.config.homeserver,
            user=self.config.user_id,
            store_path=store_path,  # Where tokens are saved
            config=AsyncClientConfig(
                store_sync_tokens=True,  # Auto-persists next_batch tokens
                encryption_enabled=True,
            ),
        )

        self.client.user_id = self.config.user_id
        self.client.access_token = self.config.access_token
        self.client.device_id = self.config.device_id

        self._register_event_callbacks()
        self._register_response_callbacks()

        if self.config.device_id:
            try:
                self.client.load_store()
            except Exception as e:
                logger.warning(
                    "Matrix store load failed ({}: {}); sync token restore is disabled and "
                    "restart may replay recent messages.",
                    type(e).__name__,
                    str(e),
                )
        else:
            logger.warning(
                "Matrix device_id is empty; sync token restore is disabled and restart may "
                "replay recent messages."
            )

        self._sync_task = asyncio.create_task(self._sync_loop())

    async def stop(self) -> None:
        """Stop the Matrix channel with graceful sync shutdown."""
        self._running = False

        if self.client:
            # Request sync_forever loop to exit cleanly.
            self.client.stop_sync_forever()

        if self._sync_task:
            try:
                await asyncio.wait_for(
                    asyncio.shield(self._sync_task),
                    timeout=self.config.sync_stop_grace_seconds,
                )
            except asyncio.TimeoutError:
                self._sync_task.cancel()
                try:
                    await self._sync_task
                except asyncio.CancelledError:
                    pass
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.close()

    async def send(self, msg: OutboundMessage) -> None:
        if not self.client:
            return

        await self.client.room_send(
            room_id=msg.chat_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": msg.content},
            ignore_unverified_devices=True,
        )

    def _register_event_callbacks(self) -> None:
        """Register Matrix event callbacks used by this channel."""
        self.client.add_event_callback(self._on_message, RoomMessageText)
        self.client.add_event_callback(self._on_room_invite, InviteEvent)

    def _register_response_callbacks(self) -> None:
        """Register response callbacks for operational error observability."""
        self.client.add_response_callback(self._on_sync_error, SyncError)
        self.client.add_response_callback(self._on_join_error, JoinError)
        self.client.add_response_callback(self._on_send_error, RoomSendError)

    @staticmethod
    def _is_auth_error(errcode: str | None) -> bool:
        """Return True if the Matrix errcode indicates auth/token problems."""
        return errcode in {"M_UNKNOWN_TOKEN", "M_FORBIDDEN", "M_UNAUTHORIZED"}

    async def _on_sync_error(self, response: SyncError) -> None:
        """Log sync errors with clear severity."""
        if self._is_auth_error(response.status_code) or response.soft_logout:
            logger.error("Matrix sync failed: {}", response)
            return
        logger.warning("Matrix sync warning: {}", response)

    async def _on_join_error(self, response: JoinError) -> None:
        """Log room-join errors from invite handling."""
        if self._is_auth_error(response.status_code):
            logger.error("Matrix join failed: {}", response)
            return
        logger.warning("Matrix join warning: {}", response)

    async def _on_send_error(self, response: RoomSendError) -> None:
        """Log message send failures."""
        if self._is_auth_error(response.status_code):
            logger.error("Matrix send failed: {}", response)
            return
        logger.warning("Matrix send warning: {}", response)

    async def _sync_loop(self) -> None:
        while self._running:
            try:
                # full_state applies only to the first sync inside sync_forever and helps
                # rebuild room state when restoring from stored sync tokens.
                await self.client.sync_forever(timeout=30000, full_state=True)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(2)

    async def _on_room_invite(self, room: MatrixRoom, event: InviteEvent) -> None:
        allow_from = self.config.allow_from or []
        if allow_from and event.sender not in allow_from:
            return

        await self.client.join(room.room_id)

    async def _on_message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        # Ignore self messages
        if event.sender == self.config.user_id:
            return

        await self._handle_message(
            sender_id=event.sender,
            chat_id=room.room_id,
            content=event.body,
            metadata={"room": room.display_name},
        )
