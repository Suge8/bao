from __future__ import annotations

from assets._build_svg_shared import LOGO_B64, IconSpec, common_defs_template, esc, get_icon


def _hero_copy(lang: str) -> dict[str, object]:
    if lang == "zh":
        return {
            "subtitles": (
                "记得住，能并行，会进化",
                "真正的持久记忆 · 闭环经验学习",
                "并行长任务引擎 · 无缝接入编程代理体系",
            ),
            "rows": (
                ("持久记忆", "LanceDB 向量检索", "database", "accent"),
                ("经验引擎", "策略复用与置信度", "brain", "mint"),
                ("长任务系统", "压实轨迹, 自动收口", "timer", "sky"),
                ("子代理编排", "后台并行静默跑活", "git-branch", "violet"),
                ("编码代理", "Codex / Claude Code", "terminal", "rose"),
                ("九大平台", "一套能力随处可用", "globe", "accent"),
            ),
        }
    return {
        "subtitles": (
            "Remembers more, runs longer, evolves faster",
            "True persistent memory · closed-loop learning",
            "Parallel long-task engine · seamless coding agents",
        ),
        "rows": (
            ("Persistent Memory", "LanceDB vector recall", "database", "accent"),
            ("Experience Engine", "Strategy reuse & scoring", "brain", "mint"),
            ("Long-Run Engine", "Compression & checkpoints", "timer", "sky"),
            ("Subagent Scheduler", "Silent background work", "git-branch", "violet"),
            ("Coding Agent", "Codex / Claude Code", "terminal", "rose"),
            ("9 Platforms", "One capability everywhere", "globe", "accent"),
        ),
    }


def _hero_rows_svg(theme: dict[str, str], rows: tuple[tuple[str, str, str, str], ...]) -> str:
    row_height = 50
    row_gap = 6
    panel_padding = 16
    panel_inner_width = 280
    rows_svg = ""
    for index, (label, desc, icon_name, color_key) in enumerate(rows):
        row_y = panel_padding + index * (row_height + row_gap)
        bg_key = f"{color_key}_bg"
        color = theme[color_key]
        color_bg = theme.get(bg_key, theme["accent_bg"])
        rows_svg += f"""
      <g transform="translate({panel_padding}, {row_y})">
        <rect width="{panel_inner_width}" height="{row_height}" rx="12" fill="{theme['card_bg']}" stroke="{theme['card_border']}" />
        <rect x="10" y="11" width="28" height="28" rx="8" fill="{color_bg}" />
        <g transform="translate(14, 15)">{get_icon(IconSpec(icon_name, color=color, size=20))}</g>
        <text x="48" y="22" class="font-sans fw-bold text-primary" font-size="13">{esc(label)}</text>
        <text x="48" y="38" class="font-sans fw-medium text-muted" font-size="11">{esc(desc)}</text>
      </g>"""
    return rows_svg


def render_hero(theme: dict[str, str], lang: str, _theme_name: str) -> str:
    width = 840
    height = 440
    copy = _hero_copy(lang)
    sub1, sub2, sub3 = copy["subtitles"]
    rows = copy["rows"]
    panel_width = 312
    panel_height = 338
    panel_x = width - panel_width - 40
    panel_y = (height - panel_height) // 2
    rows_svg = _hero_rows_svg(theme, rows)
    logo_uri = f"data:image/png;base64,{LOGO_B64}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="100%" height="100%">
{common_defs_template.format(**theme, height=height)}
  <circle cx="200" cy="180" r="220" fill="url(#glow-grad)" class="animate-pulse" />
  <circle cx="660" cy="260" r="220" fill="url(#glow-grad)" class="animate-pulse" style="animation-delay: 2s;" />
  <g transform="translate(48, 56)">
    <image href="{logo_uri}" x="0" y="0" width="56" height="56" />
    <text x="66" y="30" class="font-sans fw-bold tracking-wide text-accent" font-size="12">PERSONAL AI THAT HOLDS UP</text>
    <text x="66" y="48" class="font-sans fw-medium text-muted" font-size="11">Your Personal AI Framework</text>
    <text y="120" class="font-sans fw-bold tracking-tight text-primary" font-size="78">Bao</text>
    <text y="160" class="font-sans fw-bold tracking-tight text-secondary" font-size="20">{sub1}</text>
    <text y="192" class="font-sans fw-medium text-muted" font-size="14">{sub2}</text>
    <text y="214" class="font-sans fw-medium text-muted" font-size="14">{sub3}</text>
    <rect y="240" width="60" height="4" rx="2" fill="{theme['accent']}" />
    <rect y="240" x="68" width="30" height="4" rx="2" fill="{theme['accent']}" opacity="0.4" />
  </g>
  <path d="M 420 220 C 440 220, {panel_x - 20} 220, {panel_x} 220" fill="none" class="animate-flow" stroke="{theme['line']}" stroke-width="2" />
  <circle cx="420" cy="220" r="4" fill="{theme['accent']}" />
  <g transform="translate({panel_x}, {panel_y})" filter="url(#shadow-md)">
    <rect width="{panel_width}" height="{panel_height}" rx="20" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" stroke-width="1.5" />
    {rows_svg}
  </g>
</svg>"""
