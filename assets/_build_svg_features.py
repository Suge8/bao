from __future__ import annotations

from dataclasses import dataclass

from assets._build_svg_shared import IconSpec, common_defs_template, get_icon

CARD_GEOMETRY = (
    (0, 0, "accent", "database", False),
    (240, 0, "mint", "brain", True),
    (480, 0, "sky", "timer", False),
    (0, 140, "violet", "git-branch", True),
    (240, 140, "rose", "terminal", False),
    (480, 140, "accent", "monitor", False),
)


@dataclass(frozen=True)
class FeatureCardSpec:
    x: int
    y: int
    color_key: str
    icon_name: str
    animate: bool
    title: str
    summary: str


def _feature_copy(lang: str) -> tuple[str, str, str, tuple[tuple[str, str], ...]]:
    if lang == "zh":
        return (
            "核心引擎组合",
            "不只是聊天，而是一套完整的长效智能层",
            "从底层的 LanceDB 持久记忆到顶层的多代理协作机制，保障核心生产力。",
            (
                ("持久记忆系统", "LanceDB 向量检索 • 偏好分离 • 智能召回"),
                ("经验学习引擎", "自动提取教训 • 策略复用 • 置信度校准"),
                ("长任务引擎", "轨迹压缩 • 自动校验 • 不阻塞主对话"),
                ("子代理并行", "后台分流并行 • 进度透明可追溯 • 无缝续接"),
                ("原生编码代理", "支持 Codex / Claude Code • Schema自适配"),
                ("桌面端自动化", "跨 9 大平台 • 截图/点击原生感知 • 工具流融合"),
            ),
        )
    return (
        "CORE CAPABILITIES",
        "Built for long-term use, not just chat",
        "From LanceDB persistence at the bottom to multi-agent collaboration at the top.",
        (
            ("Persistent Memory", "LanceDB vector recall • Segmented preferences"),
            ("Experience Engine", "Auto-extract lessons • Strategy reuse • Confidence scoring"),
            ("Long-Run Engine", "Trajectory compression • Auto checkpoints • Non-blocking"),
            ("Parallel Subagents", "Background execution • Visible progress • Resumable"),
            ("Native Coding Agent", "Codex / Claude Code ready • Auto schema routing"),
            ("Desktop Automation", "Across 9 platforms • Screen/click native • Tool fusion"),
        ),
    )


def _feature_detail_tspans(summary: str) -> str:
    parts = [part.strip() for part in summary.split("•")]
    first = parts[0]
    second = " • ".join(parts[1:]).strip() if len(parts) > 1 else ""
    return (
        f'<tspan x="20" dy="0">{first}</tspan>'
        f'<tspan x="20" dy="16">{second}</tspan>'
    )


def _feature_card(theme: dict[str, str], card: FeatureCardSpec) -> str:
    animation_class = (
        ' class="animate-float"'
        if card.animate and card.y == 0
        else ' class="animate-float-delayed"' if card.animate else ""
    )
    bg_key = f"{card.color_key}_bg"
    return f"""
    <g transform="translate({card.x}, {card.y})">
      <g filter="url(#shadow-sm)"{animation_class}>
        <rect width="220" height="120" rx="16" fill="{theme['panel_bg']}" stroke="{theme['panel_border']}" />
        <rect x="20" y="20" width="36" height="36" rx="8" fill="{theme[bg_key]}" />
        <g transform="translate(26, 26)">
          {get_icon(IconSpec(card.icon_name, color=theme[card.color_key], size=24))}
        </g>
        <text x="20" y="80" class="font-sans fw-bold text-primary" font-size="15">{card.title}</text>
        <text x="20" y="100" class="font-sans fw-medium text-muted" font-size="12">
          {_feature_detail_tspans(card.summary)}
        </text>
      </g>
    </g>"""


def render_features(theme: dict[str, str], lang: str, _theme_name: str) -> str:
    width = 800
    height = 480
    eyebrow, title, subtitle, features = _feature_copy(lang)
    cards_svg = "".join(
        _feature_card(
            theme,
            FeatureCardSpec(x, y, color_key, icon_name, animate, feature_title, feature_summary),
        )
        for (x, y, color_key, icon_name, animate), (feature_title, feature_summary) in zip(
            CARD_GEOMETRY, features, strict=True
        )
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
{common_defs_template.format(**theme, height=height)}
  <circle cx="150" cy="150" r="200" fill="url(#glow-grad)" class="animate-pulse" />
  <circle cx="650" cy="400" r="200" fill="url(#glow-grad)" class="animate-pulse" style="animation-delay: 1s;" />
  <g transform="translate(50, 60)">
    <text y="0" class="font-sans fw-bold tracking-wide text-accent" font-size="12">{eyebrow}</text>
    <text y="36" class="font-sans fw-bold tracking-tight text-primary" font-size="28">{title}</text>
    <text y="64" class="font-sans fw-medium text-secondary" font-size="15">{subtitle}</text>
  </g>
  <g transform="translate(50, 160)">
    {cards_svg}
  </g>
</svg>"""
