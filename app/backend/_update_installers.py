from __future__ import annotations

import hashlib
import os
import platform
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from .update_core import ReleaseInfo


@dataclass(frozen=True)
class MacosApplyScriptRequest:
    pid: int
    target_app: Path
    staged_app: Path
    workdir: Path


class UpdateInstallersMixin:
    async def _download_release(self, release: ReleaseInfo, workdir: Path) -> Path:
        parsed = urlparse(release.asset.url)
        file_name = Path(parsed.path).name or "bao-update.bin"
        package_path = workdir / file_name
        digest = hashlib.sha256()
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as client:
            async with client.stream("GET", release.asset.url) as response:
                _ = response.raise_for_status()
                with package_path.open("wb") as fh:
                    async for chunk in response.aiter_bytes():
                        if not chunk:
                            continue
                        fh.write(chunk)
                        digest.update(chunk)
        if digest.hexdigest().lower() != release.asset.sha256.lower():
            raise ValueError("Downloaded update failed SHA-256 verification.")
        return package_path

    def _launch_windows_installer(self, package_path: Path, release: ReleaseInfo) -> None:
        if not getattr(sys, "frozen", False):
            self._open_release_url(release)
            return
        args = [str(package_path)]
        args.extend(
            release.asset.silent_args or ("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-")
        )
        _ = subprocess.Popen(args, close_fds=True)

    def _launch_macos_installer(self, package_path: Path, workdir: Path) -> None:
        target_app = self._current_app_bundle()
        if target_app is None or package_path.suffix.lower() != ".zip":
            self._open_release_url(self._release)
            return
        staged_root = workdir / "staged"
        staged_root.mkdir(parents=True, exist_ok=True)
        _ = subprocess.run(
            ["/usr/bin/ditto", "-x", "-k", str(package_path), str(staged_root)],
            check=True,
        )
        staged_app = next((path for path in staged_root.iterdir() if path.suffix == ".app"), None)
        if staged_app is None:
            raise ValueError("Update archive does not contain an app bundle.")
        script_path = workdir / "apply_update.sh"
        script_text = self._build_macos_apply_script(
            MacosApplyScriptRequest(
                pid=os.getpid(),
                target_app=target_app,
                staged_app=staged_app,
                workdir=workdir,
            )
        )
        script_path.write_text(script_text, encoding="utf-8")
        _ = script_path.chmod(0o755)
        _ = subprocess.Popen(
            ["open", "-a", "Terminal", str(script_path)],
            close_fds=True,
        )
        self.quitRequested.emit()

    def _build_macos_apply_script(self, request: MacosApplyScriptRequest) -> str:
        target_app = shlex.quote(str(request.target_app))
        staged_app = shlex.quote(str(request.staged_app))
        workdir = shlex.quote(str(request.workdir))
        return (
            "#!/bin/bash\n"
            "set -euo pipefail\n"
            f"PID={request.pid}\n"
            "while kill -0 \"$PID\" >/dev/null 2>&1; do sleep 1; done\n"
            f"TARGET_APP={target_app}\n"
            f"STAGED_APP={staged_app}\n"
            f"WORKDIR={workdir}\n"
            "rm -rf \"$TARGET_APP\"\n"
            "cp -R \"$STAGED_APP\" \"$TARGET_APP\"\n"
            "open \"$TARGET_APP\"\n"
            "rm -rf \"$WORKDIR\"\n"
        )

    def _current_app_bundle(self) -> Path | None:
        executable = Path(sys.executable).resolve()
        if executable.suffix == ".app":
            return executable
        if executable.parent.name == "MacOS" and executable.parent.parent.suffix == ".app":
            return executable.parent.parent
        if executable.parent.parent.parent.name == "MacOS" and executable.parent.parent.parent.parent.suffix == ".app":
            return executable.parent.parent.parent.parent
        if getattr(sys, "frozen", False) and platform.system() == "Darwin":
            app_path = Path(sys.argv[0]).resolve()
            if app_path.parent.name == "MacOS" and app_path.parent.parent.suffix == ".app":
                return app_path.parent.parent
        return None
