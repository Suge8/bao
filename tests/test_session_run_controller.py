from __future__ import annotations

import asyncio

import pytest

from bao.agent.session_run_controller import SessionRunController

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_session_run_controller_interrupt_and_generation() -> None:
    controller = SessionRunController()
    started = asyncio.Event()
    release = asyncio.Event()

    async def _job() -> None:
        async with controller.run_scope("desktop:local::main"):
            started.set()
            await release.wait()

    controller.schedule("desktop:local::main", _job())
    await started.wait()

    interrupt = controller.request_interrupt("desktop:local::main")

    assert interrupt.has_busy_work is True
    assert interrupt.generation == 1
    assert controller.is_stale("desktop:local::main", 0) is True

    release.set()
    await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_session_run_controller_stop_cancels_scheduled_tasks() -> None:
    controller = SessionRunController()
    started = asyncio.Event()

    async def _job() -> None:
        async with controller.run_scope("desktop:local::main"):
            started.set()
            await asyncio.Event().wait()

    controller.schedule("desktop:local::main", _job())
    await started.wait()

    cancelled = controller.stop_session("desktop:local::main")
    await asyncio.sleep(0)

    assert cancelled == 1
    assert controller.generation("desktop:local::main") == 1
