from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from dataclasses import dataclass

LOGO_SOURCE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "app",
    "resources",
    "logo-circle.png",
)


def _build_logo_b64() -> str:
    tmp_path = tempfile.mktemp(suffix=".png")
    subprocess.run(["sips", "-z", "72", "72", LOGO_SOURCE, "--out", tmp_path], capture_output=True)
    with open(tmp_path, "rb") as file_handle:
        encoded = base64.b64encode(file_handle.read()).decode()
    os.unlink(tmp_path)
    return encoded


LOGO_B64 = _build_logo_b64()

themes = {
    "dark": {
        "bg": "#0a0a0c",
        "bg_gradient_start": "#18181b",
        "bg_gradient_end": "#09090b",
        "panel_bg": "#141417",
        "panel_border": "#27272a",
        "card_bg": "#1c1c21",
        "card_border": "#3f3f46",
        "text_primary": "#ffffff",
        "text_secondary": "#a1a1aa",
        "text_muted": "#71717a",
        "accent": "#f59e0b",
        "accent_muted": "#b45309",
        "accent_bg": "#451a03",
        "line": "rgba(245, 158, 11, 0.4)",
        "glow": "rgba(245, 158, 11, 0.15)",
        "shadow": "rgba(0, 0, 0, 0.6)",
        "mint": "#34d399",
        "sky": "#38bdf8",
        "violet": "#a78bfa",
        "rose": "#fb7185",
        "mint_bg": "#022c22",
        "sky_bg": "#082f49",
        "violet_bg": "#2e1065",
        "rose_bg": "#4c0519",
    },
    "light": {
        "bg": "#fafafa",
        "bg_gradient_start": "#ffffff",
        "bg_gradient_end": "#f4f4f5",
        "panel_bg": "#ffffff",
        "panel_border": "#e4e4e7",
        "card_bg": "#ffffff",
        "card_border": "#d4d4d8",
        "text_primary": "#09090b",
        "text_secondary": "#52525b",
        "text_muted": "#a1a1aa",
        "accent": "#d97706",
        "accent_muted": "#f59e0b",
        "accent_bg": "#fef3c7",
        "line": "rgba(217, 119, 6, 0.3)",
        "glow": "rgba(245, 158, 11, 0.08)",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "mint": "#10b981",
        "sky": "#0ea5e9",
        "violet": "#8b5cf6",
        "rose": "#f43f5e",
        "mint_bg": "#d1fae5",
        "sky_bg": "#e0f2fe",
        "violet_bg": "#ede9fe",
        "rose_bg": "#ffe4e6",
    },
}

icons = {
    "database": '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5M3 5c0 1.66 4 3 9 3s9-1.34 9-3M3 5c0-1.66 4-3 9-3s9 1.34 9 3M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    "brain": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/>',
    "timer": '<circle cx="12" cy="14" r="8"/><path d="M12 10v4l2 2"/><path d="M10 2h4"/><path d="M12 2v2"/>',
    "git-branch": '<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "terminal": '<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "server": '<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "message-square": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
}


@dataclass(frozen=True)
class IconSpec:
    name: str
    color: str = "#ffffff"
    size: int = 24
    stroke_width: int = 2


def get_icon(spec: IconSpec) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{spec.size}" height="{spec.size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{spec.color}" stroke-width="{spec.stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{icons.get(spec.name, "")}</svg>'
    )


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


common_defs_template = """
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap');
      .font-sans {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
      .font-mono {{ font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace; }}
      .text-primary {{ fill: {text_primary}; }}
      .text-secondary {{ fill: {text_secondary}; }}
      .text-muted {{ fill: {text_muted}; }}
      .text-accent {{ fill: {accent}; }}
      .fw-medium {{ font-weight: 500; }}
      .fw-semibold {{ font-weight: 600; }}
      .fw-bold {{ font-weight: 700; }}
      .tracking-tight {{ letter-spacing: -0.02em; }}
      .tracking-wide {{ letter-spacing: 0.1em; }}

      @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
      @keyframes float-delayed {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
      @keyframes pulse {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}
      @keyframes line-flow {{ 0% {{ stroke-dashoffset: 24; }} 100% {{ stroke-dashoffset: 0; }} }}

      .animate-float {{ animation: float 6s ease-in-out infinite; }}
      .animate-float-delayed {{ animation: float-delayed 7s ease-in-out infinite; animation-delay: 1.5s; }}
      .animate-pulse {{ animation: pulse 4s ease-in-out infinite; }}
      .animate-flow {{ animation: line-flow 1.5s linear infinite; stroke-dasharray: 6 6; }}
    </style>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_gradient_start}" />
      <stop offset="100%" stop-color="{bg_gradient_end}" />
    </linearGradient>
    <radialGradient id="glow-grad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{glow}" />
      <stop offset="100%" stop-color="{glow}" stop-opacity="0" />
    </radialGradient>
    <filter id="shadow-md" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="{shadow}" />
    </filter>
    <filter id="shadow-sm" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="{shadow}" />
    </filter>
  </defs>
  <rect width="100%" height="{height}" fill="{bg}" rx="16" />
  <rect width="100%" height="{height}" fill="url(#bg-grad)" rx="16" opacity="0.6" />
  <rect width="100%" height="{height}" fill="transparent" stroke="{panel_border}" stroke-width="2" rx="16" />
"""
