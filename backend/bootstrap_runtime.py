"""Runtime bootstrap for packaged DolphinPhoto desktop installs.

This script creates/updates a local virtual environment, installs backend
dependencies, optionally pre-pulls the default model, and launches the backend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> None:
    completed = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(cmd)}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_venv(runtime_dir: Path) -> Path:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    venv_dir = runtime_dir / "venv"
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    if not venv_python.exists():
        run([sys.executable, "-m", "venv", str(venv_dir)])

    return venv_python


def ensure_dependencies(venv_python: Path, requirements_file: Path, runtime_dir: Path) -> None:
    state_file = runtime_dir / "bootstrap-state.json"
    requirements_hash = file_sha256(requirements_file)
    state: dict[str, str] = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}

    if state.get("requirements_hash") == requirements_hash:
        return

    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)])

    state["requirements_hash"] = requirements_hash
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def ensure_default_model(
    venv_python: Path, runtime_dir: Path, model_name: str, models_dir: Path, hf_token: str | None
) -> None:
    marker_dir = runtime_dir / "models"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_name = model_name.replace("/", "--")
    marker_file = marker_dir / f"{marker_name}.done"
    if marker_file.exists():
        return

    script = (
        "from huggingface_hub import snapshot_download;"
        "from pathlib import Path;"
        "snapshot_download("
        f"repo_id={model_name!r}, "
        f"local_dir={str((models_dir / marker_name))!r}, "
        "local_dir_use_symlinks=False, "
        f"token={hf_token!r});"
    )
    run([str(venv_python), "-c", script])
    marker_file.write_text("ok\n", encoding="utf-8")


def launch_backend(venv_python: Path, backend_dir: Path, workspace: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    env.setdefault("HF_HOME", str(workspace / "cache" / "huggingface"))
    env.setdefault("HUGGINGFACE_HUB_CACHE", str(workspace / "cache" / "huggingface"))
    os.execve(
        str(venv_python),
        [str(venv_python), str(backend_dir / "main.py")],
        env,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-dir", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--pull-default-model", action="store_true")
    parser.add_argument("--launch-backend", action="store_true")
    args = parser.parse_args()

    backend_dir = Path(args.backend_dir).resolve()
    runtime_dir = Path(args.runtime_dir).resolve()
    workspace = Path(args.workspace).resolve()

    requirements = backend_dir / "requirements-runtime.txt"
    if not requirements.exists():
        requirements = backend_dir / "requirements.txt"
    if not requirements.exists():
        raise FileNotFoundError(f"Backend requirements not found: {requirements}")

    workspace.mkdir(parents=True, exist_ok=True)
    models_dir = workspace / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    venv_python = ensure_venv(runtime_dir)
    ensure_dependencies(venv_python, requirements, runtime_dir)

    if args.pull_default_model:
        model_name = os.getenv("DOLPHINPHOTO_DEFAULT_MODEL", "stabilityai/stable-diffusion-2-1")
        hf_token = os.getenv("HF_TOKEN")
        ensure_default_model(venv_python, runtime_dir, model_name, models_dir, hf_token)

    if args.launch_backend:
        launch_backend(venv_python, backend_dir, workspace)


if __name__ == "__main__":
    main()
