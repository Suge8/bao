from __future__ import annotations

from assets._build_svg_shared import IconSpec, common_defs_template, esc, get_icon


def _arch_copy(lang: str) -> dict[str, str]:
    if lang == "zh":
        return {
            "eyebrow": "ARCHITECTURE",
            "title": "底层数据流与模块协作架构",
            "subtitle": "高内聚、低耦合，从交互输入到记忆更新的生命周期一致性管理。",
            "input_a": "用户界面请求",
            "input_a_desc": "桌面应用、系统指令快捷抓取",
            "input_b": "第三方渠道分流",
            "input_b_desc": "9大主流平台消息接驳与格式化",
            "core_a": "核心运行时 AgentLoop",
            "core_b": "长期记忆 (LanceDB)",
            "core_c": "闭环经验反馈引擎",
            "core_d": "任务编排/轨迹压缩",
            "core_e": "子代理调度层",
            "output_a": "MCP 协议生态",
            "output_b": "桌面端自动化执行",
        }
    return {
        "eyebrow": "ARCHITECTURE",
        "title": "Information Flow and Module Collaboration",
        "subtitle": "Highly cohesive yet decoupled lifecycle management from input to memory updates.",
        "input_a": "User Interfaces",
        "input_a_desc": "Desktop app, system hooks",
        "input_b": "3rd Party Channels",
        "input_b_desc": "9 mainstream platforms formatting",
        "core_a": "Core Runtime AgentLoop",
        "core_b": "LanceDB Persistence",
        "core_c": "Experience Engine",
        "core_d": "Task & Trajectory",
        "core_e": "Subagent Scheduler",
        "output_a": "MCP Ecosystem",
        "output_b": "Desktop GUI Automation",
    }


def render_arch(theme: dict[str, str], lang: str, _theme_name: str) -> str:
    copy = _arch_copy(lang)
    width = 800
    height = 520
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
{common_defs_template.format(**theme, height=height)}
  <g transform="translate(60, 50)">
    <text y="0" class="font-sans fw-bold tracking-wide text-accent" font-size="12">{esc(copy['eyebrow'])}</text>
    <text y="32" class="font-sans fw-bold tracking-tight text-primary" font-size="24">{esc(copy['title'])}</text>
    <text y="56" class="font-sans fw-medium text-secondary" font-size="14">{esc(copy['subtitle'])}</text>
  </g>
    <g transform="translate(50, 150)">
    <rect width="200" height="80" rx="12" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" filter="url(#shadow-sm)" />
    <rect x="0" y="24" width="4" height="32" rx="2" fill="{theme['sky']}" />
    <g transform="translate(16, 28)">{get_icon(IconSpec('users', color=theme['sky'], size=24))}</g>
    <text x="50" y="44" class="font-sans fw-bold text-primary" font-size="14">{esc(copy['input_a'])}</text>
    <text x="20" y="68" class="font-sans fw-medium text-muted" font-size="11">{esc(copy['input_a_desc'])}</text>
    <path d="M200 40 L 260 40" stroke="{theme['line']}" stroke-width="2" class="animate-flow" />
    <circle cx="260" cy="40" r="4" fill="{theme['accent']}" />
  </g>
  <g transform="translate(50, 260)">
    <rect width="200" height="80" rx="12" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" filter="url(#shadow-sm)" />
    <rect x="0" y="24" width="4" height="32" rx="2" fill="{theme['violet']}" />
    <g transform="translate(16, 28)">{get_icon(IconSpec('message-square', color=theme['violet'], size=24))}</g>
    <text x="50" y="44" class="font-sans fw-bold text-primary" font-size="14">{esc(copy['input_b'])}</text>
    <text x="20" y="68" class="font-sans fw-medium text-muted" font-size="11">{esc(copy['input_b_desc'])}</text>
    <path d="M200 40 L 260 40" stroke="{theme['line']}" stroke-width="2" class="animate-flow" />
    <circle cx="260" cy="40" r="4" fill="{theme['accent']}" />
  </g>
  <g transform="translate(280, 130)" filter="url(#shadow-md)">
    <rect width="250" height="280" rx="20" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" stroke-width="2" />
    <g transform="translate(112, 12)">{get_icon(IconSpec('cpu', color=theme['text_primary'], size=26))}</g>
    <text x="125" y="58" class="font-sans fw-bold text-primary" font-size="15" text-anchor="middle">{esc(copy['core_a'])}</text>
    <g transform="translate(25, 76)"><rect width="200" height="40" rx="8" fill="{theme['card_bg']}" stroke="{theme['card_border']}" /><g transform="translate(12, 10)">{get_icon(IconSpec('database', color=theme['accent'], size=20))}</g><text x="44" y="25" class="font-sans fw-semibold text-secondary" font-size="13">{esc(copy['core_b'])}</text></g>
    <g transform="translate(25, 126)"><rect width="200" height="40" rx="8" fill="{theme['card_bg']}" stroke="{theme['card_border']}" /><g transform="translate(12, 10)">{get_icon(IconSpec('brain', color=theme['mint'], size=20))}</g><text x="44" y="25" class="font-sans fw-semibold text-secondary" font-size="13">{esc(copy['core_c'])}</text></g>
    <g transform="translate(25, 176)"><rect width="200" height="40" rx="8" fill="{theme['card_bg']}" stroke="{theme['card_border']}" /><g transform="translate(12, 10)">{get_icon(IconSpec('timer', color=theme['rose'], size=20))}</g><text x="44" y="25" class="font-sans fw-semibold text-secondary" font-size="13">{esc(copy['core_d'])}</text></g>
    <g transform="translate(25, 226)"><rect width="200" height="40" rx="8" fill="{theme['card_bg']}" stroke="{theme['card_border']}" /><g transform="translate(12, 10)">{get_icon(IconSpec('git-branch', color=theme['sky'], size=20))}</g><text x="44" y="25" class="font-sans fw-semibold text-secondary" font-size="13">{esc(copy['core_e'])}</text></g>
  </g>
  <g transform="translate(560, 150)">
    <path d="M -30 40 L 0 40" stroke="{theme['line']}" stroke-width="2" class="animate-flow" />
    <circle cx="-30" cy="40" r="4" fill="{theme['accent']}" />
    <rect width="180" height="80" rx="12" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" filter="url(#shadow-sm)" />
    <rect x="176" y="24" width="4" height="32" rx="2" fill="{theme['rose']}" />
    <g transform="translate(16, 28)">{get_icon(IconSpec('box', color=theme['rose'], size=24))}</g>
    <text x="50" y="44" class="font-sans fw-bold text-primary" font-size="14">{esc(copy['output_a'])}</text>
    <text x="20" y="68" class="font-sans fw-medium text-muted" font-size="11">Tools, Files, Cloud</text>
  </g>
  <g transform="translate(560, 260)">
    <path d="M -30 40 L 0 40" stroke="{theme['line']}" stroke-width="2" class="animate-flow" />
    <circle cx="-30" cy="40" r="4" fill="{theme['accent']}" />
    <rect width="180" height="80" rx="12" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" filter="url(#shadow-sm)" />
    <rect x="176" y="24" width="4" height="32" rx="2" fill="{theme['accent']}" />
    <g transform="translate(16, 28)">{get_icon(IconSpec('monitor', color=theme['accent'], size=24))}</g>
    <text x="50" y="44" class="font-sans fw-bold text-primary" font-size="14">{esc(copy['output_b'])}</text>
    <text x="20" y="68" class="font-sans fw-medium text-muted" font-size="11">Screen &amp; Controls</text>
  </g>
  <rect x="50" y="450" width="700" height="40" rx="8" fill="{theme['accent_bg']}" />
  <text x="400" y="475" class="font-sans fw-semibold text-accent_muted" font-size="13" text-anchor="middle">Fully type-safe execution and strictly bounded contexts.</text>
</svg>"""
