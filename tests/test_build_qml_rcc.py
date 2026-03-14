from __future__ import annotations

from pathlib import Path

from app.scripts.build_qml_rcc import build_qrc_text


def test_build_qrc_text_excludes_output_rcc_from_resources(tmp_path: Path) -> None:
    qml_root = tmp_path / "qml"
    resources_root = tmp_path / "resources"
    cache_root = tmp_path / "cache"
    output_rcc = resources_root / "desktop_qml.rcc"

    qml_root.mkdir(parents=True)
    resources_root.mkdir(parents=True)
    cache_root.mkdir(parents=True)

    (qml_root / "Main.qml").write_text("import QtQuick\nItem {}\n", encoding="utf-8")
    (resources_root / "logo.svg").write_text("<svg />\n", encoding="utf-8")
    output_rcc.write_bytes(b"old-rcc")

    qrc_text = build_qrc_text(
        qml_root,
        resources_root,
        cache_root=cache_root,
        with_qml_cache=False,
        skip_resource_paths={output_rcc},
    )

    assert "logo.svg" in qrc_text
    assert "desktop_qml.rcc" not in qrc_text
