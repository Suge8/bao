"""Subagent manager for background task execution with progress tracking."""

import asyncio
import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from bao.agent.artifacts import apply_tool_output_budget
from bao.agent.tools.filesystem import EditFileTool, ListDirTool, ReadFileTool, WriteFileTool
from bao.agent.tools.registry import ToolRegistry
from bao.agent.tools.shell import ExecTool
from bao.agent.tools.web import WebFetchTool, WebSearchTool
from bao.bus.events import InboundMessage, OutboundMessage
from bao.bus.queue import MessageBus
from bao.providers.base import LLMProvider

if TYPE_CHECKING:
    from bao.config.schema import ExecToolConfig, WebSearchConfig


@dataclass
class TaskStatus:
    task_id: str
    label: str
    task_description: str
    origin: dict[str, str]
    status: str = "running"  # running | completed | failed | cancelled
    iteration: int = 0
    max_iterations: int = 15
    tool_steps: int = 0
    phase: str = "starting"  # starting | thinking | tool:<name> | summarizing
    started_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    result_summary: str | None = None
    offloaded_count: int = 0
    offloaded_chars: int = 0
    clipped_count: int = 0
    clipped_chars: int = 0
    recent_actions: list[str] = field(default_factory=list)  # last N tool call summaries


class SubagentManager:
    _MAX_COMPLETED: int = 50  # retain at most N finished tasks
    _PROGRESS_INTERVAL: int = 5  # push progress every N iterations

    def __init__(
        self,
        provider: LLMProvider,
        workspace: Path,
        bus: MessageBus,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        search_config: "WebSearchConfig | None" = None,
        exec_config: "ExecToolConfig | None" = None,
        restrict_to_workspace: bool = False,
        tool_output_hard_chars: int = 6000,
    ):
        from bao.config.schema import ExecToolConfig

        self.provider = provider
        self.workspace = workspace
        self.bus = bus
        self.model = model or provider.get_default_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.search_config = search_config
        self.exec_config = exec_config or ExecToolConfig()
        self.restrict_to_workspace = restrict_to_workspace
        self._tool_hard_chars = max(500, int(tool_output_hard_chars))
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
        self._task_statuses: dict[str, TaskStatus] = {}
        self._session_tasks: dict[str, set[str]] = {}  # session_key -> {task_id, ...}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def spawn(
        self,
        task: str,
        label: str | None = None,
        origin_channel: str = "gateway",
        origin_chat_id: str = "direct",
        session_key: str | None = None,
    ) -> str:
        task_id = str(uuid.uuid4())[:8]
        display_label = label or (task[:30] + ("..." if len(task) > 30 else "")) or "unnamed task"
        origin = {"channel": origin_channel, "chat_id": origin_chat_id}

        self._task_statuses[task_id] = TaskStatus(
            task_id=task_id,
            label=display_label,
            task_description=task[:200],
            origin=origin,
            max_iterations=15,
        )
        self._cleanup_completed()

        bg_task = asyncio.create_task(self._run_subagent(task_id, task, display_label, origin))
        self._running_tasks[task_id] = bg_task
        if session_key:
            self._session_tasks.setdefault(session_key, set()).add(task_id)

        def _cleanup(_: asyncio.Task[None]) -> None:
            self._running_tasks.pop(task_id, None)
            if session_key and (ids := self._session_tasks.get(session_key)):
                ids.discard(task_id)
                if not ids:
                    del self._session_tasks[session_key]

        bg_task.add_done_callback(_cleanup)

        logger.info("Spawned subagent [{}]: {}", task_id, display_label)
        return f"Subagent [{display_label}] started (id: {task_id}). I'll notify you when it completes."

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        return self._task_statuses.get(task_id)

    def get_all_statuses(self) -> list[TaskStatus]:
        return list(self._task_statuses.values())

    def get_running_count(self) -> int:
        return len(self._running_tasks)

    async def _cancel_by_session(self, session_key: str, *, wait: bool) -> int:
        task_ids = list(self._session_tasks.get(session_key, []))  # snapshot
        tasks = [
            self._running_tasks[tid]
            for tid in task_ids
            if tid in self._running_tasks and not self._running_tasks[tid].done()
        ]
        for t in tasks:
            t.cancel()
        if wait and tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return len(tasks)

    async def cancel_by_session(self, session_key: str, *, wait: bool = True) -> int:
        """Cancel all subagents for the given session. Returns count cancelled."""
        return await self._cancel_by_session(session_key, wait=wait)

    async def cancel_task(self, task_id: str) -> str:
        at = self._running_tasks.get(task_id)
        if not at:
            return f"No running task with id '{task_id}'."
        at.cancel()
        self._running_tasks.pop(task_id, None)
        for session_key, ids in list(self._session_tasks.items()):
            if task_id in ids:
                ids.discard(task_id)
                if not ids:
                    self._session_tasks.pop(session_key, None)
        if st := self._task_statuses.get(task_id):
            st.status = "cancelled"
            st.updated_at = time.time()
        logger.info("Cancelled subagent [{}]", task_id)
        return f"Task '{task_id}' cancelled."

    # ------------------------------------------------------------------
    # Internal: status helpers
    # ------------------------------------------------------------------

    _MAX_RECENT_ACTIONS: int = 6  # keep last N tool call summaries

    def _update_status(
        self,
        task_id: str,
        *,
        iteration: int | None = None,
        phase: str | None = None,
        tool_steps: int | None = None,
        status: str | None = None,
        result_summary: str | None = None,
        action: str | None = None,
    ) -> None:
        st = self._task_statuses.get(task_id)
        if not st:
            return
        if iteration is not None:
            st.iteration = iteration
        if phase is not None:
            st.phase = phase
        if tool_steps is not None:
            st.tool_steps = tool_steps
        if status is not None:
            st.status = status
        if result_summary is not None:
            st.result_summary = result_summary
        if action is not None:
            st.recent_actions.append(action)
            if len(st.recent_actions) > self._MAX_RECENT_ACTIONS:
                st.recent_actions = st.recent_actions[-self._MAX_RECENT_ACTIONS :]
        st.updated_at = time.time()

    def _accumulate_budget(
        self, task_id: str, *, offloaded_chars: int = 0, clipped_chars: int = 0
    ) -> None:
        st = self._task_statuses.get(task_id)
        if not st:
            return
        if offloaded_chars > 0:
            st.offloaded_count += 1
            st.offloaded_chars += offloaded_chars
        if clipped_chars > 0:
            st.clipped_count += 1
            st.clipped_chars += clipped_chars
        st.updated_at = time.time()

    async def _push_milestone(
        self, task_id: str, label: str, iteration: int, max_iter: int, origin: dict[str, str]
    ) -> None:
        st = self._task_statuses.get(task_id)
        content = f"⏳ [{label}] {iteration}/{max_iter}"
        if st:
            content += f", {st.tool_steps} tools"
            if st.phase.startswith("tool:"):
                content += f" — {st.phase}"
            # Append recent actions for transparency
            if st.recent_actions:
                recent = st.recent_actions[-3:]  # show last 3 actions in milestone
                content += "\n" + "\n".join(f"  → {a}" for a in recent)
            if st.clipped_count or st.offloaded_count:
                content += (
                    f"\n  budget clip:{st.clipped_count}/{st.clipped_chars} "
                    f"offload:{st.offloaded_count}/{st.offloaded_chars}"
                )
        try:
            await self.bus.publish_outbound(
                OutboundMessage(
                    channel=origin["channel"],
                    chat_id=origin["chat_id"],
                    content=content,
                    metadata={"_progress": True, "_subagent_progress": True, "task_id": task_id},
                )
            )
        except Exception:
            logger.debug("Subagent [{}] milestone push failed (non-fatal)", task_id)

    def _cleanup_completed(self) -> None:
        finished = [(tid, st) for tid, st in self._task_statuses.items() if st.status != "running"]
        if len(finished) <= self._MAX_COMPLETED:
            return
        finished.sort(key=lambda x: x[1].updated_at)
        for tid, _ in finished[: len(finished) - self._MAX_COMPLETED]:
            self._task_statuses.pop(tid, None)

    # ------------------------------------------------------------------
    # Internal: subagent execution
    # ------------------------------------------------------------------

    async def _run_subagent(
        self,
        task_id: str,
        task: str,
        label: str,
        origin: dict[str, str],
    ) -> None:
        logger.info("Subagent [{}] starting task: {}", task_id, label)

        try:
            tools = ToolRegistry()
            allowed_dir = self.workspace if self.restrict_to_workspace else None
            tools.register(ReadFileTool(workspace=self.workspace, allowed_dir=allowed_dir))
            tools.register(WriteFileTool(workspace=self.workspace, allowed_dir=allowed_dir))
            tools.register(EditFileTool(workspace=self.workspace, allowed_dir=allowed_dir))
            tools.register(ListDirTool(workspace=self.workspace, allowed_dir=allowed_dir))
            tools.register(
                ExecTool(
                    working_dir=str(self.workspace),
                    timeout=self.exec_config.timeout,
                    restrict_to_workspace=self.restrict_to_workspace,
                    path_append=self.exec_config.path_append,
                )
            )
            channel = origin.get("channel", "gateway")
            chat_id = origin.get("chat_id", "direct")
            if shutil.which("opencode"):
                from bao.agent.tools.opencode import OpenCodeDetailsTool, OpenCodeTool

                oc_tool = OpenCodeTool(workspace=self.workspace, allowed_dir=allowed_dir)
                oc_details = OpenCodeDetailsTool()
                oc_tool.set_context(channel, chat_id)
                oc_details.set_context(channel, chat_id)
                tools.register(oc_tool)
                tools.register(oc_details)
            if shutil.which("codex"):
                from bao.agent.tools.codex import CodexDetailsTool, CodexTool

                cx_tool = CodexTool(workspace=self.workspace, allowed_dir=allowed_dir)
                cx_details = CodexDetailsTool()
                cx_tool.set_context(channel, chat_id)
                cx_details.set_context(channel, chat_id)
                tools.register(cx_tool)
                tools.register(cx_details)
            if shutil.which("claude"):
                from bao.agent.tools.claudecode import ClaudeCodeDetailsTool, ClaudeCodeTool

                cc_tool = ClaudeCodeTool(workspace=self.workspace, allowed_dir=allowed_dir)
                cc_details = ClaudeCodeDetailsTool()
                cc_tool.set_context(channel, chat_id)
                cc_details.set_context(channel, chat_id)
                tools.register(cc_tool)
                tools.register(cc_details)
            search_tool = WebSearchTool(search_config=self.search_config)
            has_search = bool(
                search_tool.brave_key or search_tool.tavily_key or search_tool.exa_key
            )
            if has_search:
                tools.register(search_tool)
            tools.register(WebFetchTool())

            # Build messages with subagent-specific prompt
            system_prompt = self._build_subagent_prompt(
                task,
                channel=origin.get("channel"),
                has_search=has_search,
            )
            messages: list[dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ]

            max_iterations = 15
            iteration = 0
            final_result: str | None = None
            failed_directions: list[str] = []
            tool_step = 0

            while iteration < max_iterations:
                iteration += 1

                self._update_status(task_id, iteration=iteration, phase="thinking")

                response = await self.provider.chat(
                    messages=messages,
                    tools=tools.get_definitions(),
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

                if response.has_tool_calls:
                    tool_call_dicts = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                            },
                        }
                        for tc in response.tool_calls
                    ]
                    messages.append(
                        {
                            "role": "assistant",
                            "content": response.content or "",
                            "tool_calls": tool_call_dicts,
                        }
                    )

                    for tool_call in response.tool_calls:
                        # Build action summary: tool_name(first_arg_preview)
                        first_arg = (
                            str(next(iter(tool_call.arguments.values()), ""))[:50]
                            if tool_call.arguments
                            else ""
                        )
                        action_summary = f"{tool_call.name}({first_arg})"
                        self._update_status(
                            task_id,
                            phase=f"tool:{tool_call.name}",
                            tool_steps=tool_step + 1,
                            action=action_summary,
                        )

                        args_str = json.dumps(tool_call.arguments, ensure_ascii=False)
                        logger.debug(
                            "Subagent [{}] executing: {} with arguments: {}",
                            task_id,
                            tool_call.name,
                            args_str,
                        )
                        raw_result = await tools.execute(tool_call.name, tool_call.arguments)
                        result_text = raw_result if isinstance(raw_result, str) else str(raw_result)
                        result, budget_event = apply_tool_output_budget(
                            store=None,
                            tool_name=tool_call.name,
                            tool_call_id=tool_call.id,
                            result=result_text,
                            offload_chars=self._tool_hard_chars + 1,
                            preview_chars=0,
                            hard_chars=self._tool_hard_chars,
                            ctx_mgmt="observe",
                        )
                        self._accumulate_budget(
                            task_id,
                            offloaded_chars=budget_event.offloaded_chars,
                            clipped_chars=budget_event.hard_clipped_chars,
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.name,
                                "content": result,
                            }
                        )
                        tool_step += 1
                        has_error = isinstance(result, str) and any(
                            kw in result.lower()
                            for kw in ("error", "traceback", "exception", "failed")
                        )
                        if has_error:
                            first_arg = (
                                next(iter(tool_call.arguments.values()), "")
                                if tool_call.arguments
                                else ""
                            )
                            failed_directions.append(f"{tool_call.name}({str(first_arg)[:60]})")

                    if len(failed_directions) >= 2:
                        messages.append(
                            {
                                "role": "user",
                                "content": (
                                    f"Already tried and failed: {'; '.join(failed_directions[-3:])}."
                                    " Try a different approach."
                                ),
                            }
                        )
                    elif tool_step >= 8 and tool_step % 4 == 0:
                        messages.append(
                            {
                                "role": "user",
                                "content": (
                                    f"[Progress: {tool_step} steps completed]"
                                    " Focus on completing the task efficiently."
                                ),
                            }
                        )

                    if iteration % self._PROGRESS_INTERVAL == 0:
                        await self._push_milestone(
                            task_id, label, iteration, max_iterations, origin
                        )
                else:
                    final_result = response.content
                    break

            if final_result is None:
                final_result = "Task completed but no final response was generated."

            self._update_status(
                task_id,
                phase="completed",
                status="completed",
                iteration=iteration,
                tool_steps=tool_step,
                result_summary=final_result[:500] if final_result else None,
            )

            logger.info("Subagent [{}] completed successfully", task_id)
            await self._announce_result(task_id, label, task, final_result, origin, "ok")

        except asyncio.CancelledError:
            self._update_status(task_id, status="cancelled", phase="cancelled")
            logger.info("Subagent [{}] was cancelled", task_id)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self._update_status(
                task_id,
                status="failed",
                phase="failed",
                result_summary=error_msg[:500],
            )
            logger.error("Subagent [{}] failed: {}", task_id, e)
            await self._announce_result(task_id, label, task, error_msg, origin, "error")

    async def _announce_result(
        self,
        task_id: str,
        label: str,
        task: str,
        result: str,
        origin: dict[str, str],
        status: str,
    ) -> None:
        status_text = "completed successfully" if status == "ok" else "failed"

        announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences). Do not mention technical details like "subagent" or task IDs."""

        msg = InboundMessage(
            channel="system",
            sender_id="subagent",
            chat_id=f"{origin['channel']}:{origin['chat_id']}",
            content=announce_content,
        )

        await self.bus.publish_inbound(msg)
        logger.debug(
            "Subagent [{}] announced result to {}:{}", task_id, origin["channel"], origin["chat_id"]
        )

    def _build_subagent_prompt(
        self,
        task: str,
        *,
        channel: str | None,
        has_search: bool = False,
    ) -> str:
        """Build a focused system prompt for the subagent."""
        import time as _time
        from datetime import datetime

        from bao.agent.context import ContextBuilder

        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"

        search_capability = (
            "- Search the web and fetch web pages"
            if has_search
            else "- Fetch web pages (use `web_fetch` to access URLs; `web_search` is NOT available)"
        )

        format_hint = ContextBuilder.get_channel_format_hint(channel)
        format_section = f"\n\n## Response Format\n{format_hint}" if format_hint else ""

        return f"""# Subagent

## Current Time
{now} ({tz})

You are a subagent spawned by the main agent to complete a specific task.

## Rules
1. Stay focused - complete only the assigned task, nothing else
2. Your final response will be reported back to the main agent
3. Do not initiate conversations or take on side tasks
4. Be concise but informative in your findings

## What You Can Do
- Read and write files in the workspace
- Execute shell commands
{search_capability}
- Complete the task thoroughly

## What You Cannot Do
- Send messages directly to users (no message tool available)
- Spawn other subagents
- Access the main agent's conversation history

## Workspace
Your workspace is at: {self.workspace}
Skills are available at: {self.workspace}/skills/ (read SKILL.md files as needed)

When you have completed the task, provide a clear summary of your findings or actions.{format_section}"""
