from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator, Awaitable


@dataclass(frozen=True)
class SessionInterruptRequest:
    session_key: str
    generation: int
    busy_task_count: int
    had_running_task: bool

    @property
    def has_busy_work(self) -> bool:
        return self.busy_task_count > 0 or self.had_running_task


@dataclass
class _SessionRunState:
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    generation: int = 0
    scheduled_tasks: set[asyncio.Task[None]] = field(default_factory=set)
    running_task: asyncio.Task[None] | None = None


class SessionRunController:
    def __init__(self) -> None:
        self._states: dict[str, _SessionRunState] = {}
        self._interrupted_tasks: set[asyncio.Task[None]] = set()

    def _ensure_state(self, session_key: str) -> _SessionRunState:
        state = self._states.get(session_key)
        if state is None:
            state = _SessionRunState()
            self._states[session_key] = state
        return state

    def generation(self, session_key: str) -> int:
        state = self._states.get(session_key)
        return 0 if state is None else state.generation

    def is_stale(self, session_key: str, expected_generation: int | None) -> bool:
        if expected_generation is None:
            return False
        return self.generation(session_key) != expected_generation

    def is_interrupted(self, task: asyncio.Task[None] | None) -> bool:
        return task is not None and task in self._interrupted_tasks

    def schedule(self, session_key: str, coro: Awaitable[None]) -> asyncio.Task[None]:
        state = self._ensure_state(session_key)
        task = asyncio.create_task(coro)
        state.scheduled_tasks.add(task)

        def _on_done(done_task: asyncio.Task[None], key: str = session_key) -> None:
            current = self._states.get(key)
            if current is None:
                self._interrupted_tasks.discard(done_task)
                return
            current.scheduled_tasks.discard(done_task)
            self._interrupted_tasks.discard(done_task)
            self._drop_state_if_idle(key, current)

        task.add_done_callback(_on_done)
        return task

    def request_interrupt(
        self,
        session_key: str,
        *,
        cancel_running: bool = False,
    ) -> SessionInterruptRequest:
        state = self._states.get(session_key)
        if state is None:
            return SessionInterruptRequest(
                session_key=session_key,
                generation=0,
                busy_task_count=0,
                had_running_task=False,
            )

        busy_tasks = [task for task in state.scheduled_tasks if not task.done()]
        running_task = state.running_task if state.running_task and not state.running_task.done() else None
        if not busy_tasks and running_task is None:
            return SessionInterruptRequest(
                session_key=session_key,
                generation=state.generation,
                busy_task_count=0,
                had_running_task=False,
            )

        state.generation += 1
        for task in busy_tasks:
            self._interrupted_tasks.add(task)
        if running_task is not None:
            self._interrupted_tasks.add(running_task)
        if cancel_running:
            for task in busy_tasks:
                if not task.done():
                    task.cancel()

        return SessionInterruptRequest(
            session_key=session_key,
            generation=state.generation,
            busy_task_count=len(busy_tasks),
            had_running_task=running_task is not None,
        )

    def stop_session(self, session_key: str) -> int:
        state = self._states.get(session_key)
        if state is None:
            return 0

        state.generation += 1
        if state.running_task is not None:
            self._interrupted_tasks.discard(state.running_task)
            state.running_task = None

        cancelled = 0
        for task in list(state.scheduled_tasks):
            self._interrupted_tasks.discard(task)
            if not task.done() and task.cancel():
                cancelled += 1

        self._drop_state_if_idle(session_key, state)
        return cancelled

    @asynccontextmanager
    async def run_scope(self, session_key: str) -> AsyncIterator[asyncio.Task[None] | None]:
        state = self._ensure_state(session_key)
        async with state.lock:
            current_task = asyncio.current_task()
            if current_task is not None:
                state.running_task = current_task
            try:
                yield current_task
            finally:
                if current_task is not None:
                    self._interrupted_tasks.discard(current_task)
                    if state.running_task is current_task:
                        state.running_task = None
        self._drop_state_if_idle(session_key, state)

    def _drop_state_if_idle(self, session_key: str, state: _SessionRunState) -> None:
        if state.lock.locked() or state.running_task is not None:
            return
        if any(not task.done() for task in state.scheduled_tasks):
            return
        if self._states.get(session_key) is state:
            self._states.pop(session_key, None)
