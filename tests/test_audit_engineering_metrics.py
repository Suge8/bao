from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "audit_engineering_metrics.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("audit_engineering_metrics_test_module", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_audit_root_reports_file_and_function_violations(tmp_path: Path) -> None:
    module = _load_module()
    script_path = tmp_path / "sample.py"
    script_path.write_text(
        "\n".join(
            [
                "def oversized_function(a, b, c, d):",
                *["    x = 1" for _ in range(61)],
                "    return x",
                *["# filler" for _ in range(340)],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    violations = module.audit_root(tmp_path)
    kinds = {(item.kind, item.name) for item in violations}

    assert ("file_lines", "") in kinds
    assert ("function_lines", "oversized_function") in kinds
    assert ("parameter_count", "oversized_function") in kinds


def test_audit_root_ignores_self_for_parameter_limit(tmp_path: Path) -> None:
    module = _load_module()
    script_path = tmp_path / "sample.py"
    script_path.write_text(
        "\n".join(
            [
                "class Example:",
                "    def ok(self, first, second, third):",
                "        return first + second + third",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    violations = module.audit_root(tmp_path)
    assert not [item for item in violations if item.kind == "parameter_count"]


def test_audit_root_ignores_common_generated_directories(tmp_path: Path) -> None:
    module = _load_module()
    generated = tmp_path / ".venv" / "ignored.py"
    generated.parent.mkdir(parents=True)
    generated.write_text("\n".join(["x = 1" for _ in range(450)]) + "\n", encoding="utf-8")

    violations = module.audit_root(tmp_path)
    assert violations == []
