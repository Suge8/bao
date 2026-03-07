from __future__ import annotations

import os
import shutil
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

_REQUIRED_RELATIVE_FILES = (
    Path("Default.isl"),
    Path("Languages") / "ChineseSimplified.isl",
)


def _append_unique(candidates: list[Path], seen: set[str], candidate: Path) -> None:
    normalized = os.path.normcase(str(candidate))
    if normalized in seen:
        return
    seen.add(normalized)
    candidates.append(candidate)


def _looks_like_chocolatey_shim(candidate: Path, env: Mapping[str, str]) -> bool:
    if candidate.name.lower() not in {"iscc", "iscc.exe"}:
        return False

    candidate_parent = candidate.parent.name.lower()
    candidate_grandparent = candidate.parent.parent.name.lower()
    if candidate_parent == "bin" and candidate_grandparent == "chocolatey":
        return True

    chocolatey_root = env.get("ChocolateyInstall")
    if not chocolatey_root:
        return False

    try:
        return candidate.is_relative_to(Path(chocolatey_root))
    except ValueError:
        return False


def _chocolatey_roots(candidate: Path, env: Mapping[str, str]) -> list[Path]:
    roots: list[Path] = []

    configured_root = env.get("ChocolateyInstall")
    if configured_root:
        roots.append(Path(configured_root))

    if candidate.parent.name.lower() == "bin":
        roots.append(candidate.parent.parent)

    unique_roots: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        normalized = os.path.normcase(str(root))
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_roots.append(root)

    return unique_roots


def _expand_candidate(candidate: Path, env: Mapping[str, str]) -> list[Path]:
    expanded = [candidate]
    if not _looks_like_chocolatey_shim(candidate, env):
        return expanded

    for root in _chocolatey_roots(candidate, env):
        package_root = root / "lib" / "innosetup" / "tools"
        expanded.extend(
            [
                package_root / "ISCC.exe",
                package_root / "Inno Setup 6" / "ISCC.exe",
            ]
        )

    return expanded


def candidate_compiler_paths(
    env: Mapping[str, str],
    *,
    which_fn: Callable[[str], str | None] = shutil.which,
) -> list[Path]:
    candidates: list[Path] = []
    seen: set[str] = set()

    override = env.get("BAO_ISCC_EXE")
    if override:
        for candidate in _expand_candidate(Path(override), env):
            _append_unique(candidates, seen, candidate)

    for command in ("iscc.exe", "iscc"):
        found = which_fn(command)
        if found:
            for candidate in _expand_candidate(Path(found), env):
                _append_unique(candidates, seen, candidate)

    for key in ("ProgramFiles(x86)", "ProgramFiles"):
        base = env.get(key)
        if not base:
            continue
        _append_unique(candidates, seen, Path(base) / "Inno Setup 6" / "ISCC.exe")

    return candidates


def missing_inno_files(compiler_path: Path) -> list[str]:
    missing: list[str] = []
    if not compiler_path.is_file():
        missing.append("ISCC.exe")
        return missing

    compiler_root = compiler_path.parent
    for rel_path in _REQUIRED_RELATIVE_FILES:
        if not (compiler_root / rel_path).is_file():
            missing.append(rel_path.as_posix())

    return missing


def resolve_inno_setup(
    env: Mapping[str, str],
    *,
    which_fn: Callable[[str], str | None] = shutil.which,
) -> Path | None:
    for candidate in candidate_compiler_paths(env, which_fn=which_fn):
        if not missing_inno_files(candidate):
            return candidate
    return None


def main() -> int:
    env = dict(os.environ)
    candidates = candidate_compiler_paths(env)
    resolved = resolve_inno_setup(env)
    if resolved is not None:
        print(resolved)
        return 0

    if not candidates:
        print(
            "Inno Setup compiler was not found in BAO_ISCC_EXE, PATH, or standard install directories.",
            file=sys.stderr,
        )
        return 1

    for candidate in candidates:
        missing = ", ".join(missing_inno_files(candidate)) or "unknown"
        print(f"Rejected Inno Setup candidate: {candidate} (missing: {missing})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
