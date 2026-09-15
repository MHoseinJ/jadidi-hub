import json
import shutil
import stat
import subprocess
import datetime
from pathlib import Path

from src import engine
from src import osinfo
from src import paths

def write_project_meta(project_root, version):
    meta_path = project_root / ".jadidi.json"

    meta = {
        "engine_version": version,
        "created_by": "jadidi-hub",
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "schema_version": 1,
    }

    meta_path.write_text(json.dumps(meta, indent=4) + "\n")

def find_template_dir():
    template_dir = paths.ENGINE_SOURCE_DIR / "base_template"

    if template_dir.is_dir():
        return template_dir

    return None


def find_binary(version=None):
    builds_dir = paths.BUILDS_DIR

    if version:
        version = engine.safe_name(version)
        binary = builds_dir / version / osinfo.binary_name()

        if binary.exists():
            return binary

        raise RuntimeError(f"Engine binary not found: {binary}")

    try:
        current_version = engine.get_version_name()
        binary = builds_dir / current_version / osinfo.binary_name()

        if binary.exists():
            return binary
    except Exception:
        pass

    if builds_dir.exists():
        candidates = sorted(
            builds_dir.iterdir(),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for candidate in candidates:
            binary = candidate / osinfo.binary_name()

            if binary.exists():
                return binary

    raise RuntimeError(
        "Engine binary not found. Run: jadidi-hub engine-build"
    )


def run_git_init(project_root):
    if not shutil.which("git"):
        raise RuntimeError("git is not installed")

    subprocess.run(
        ["git", "init"],
        cwd=project_root,
        check=True,
    )


def create_project(path, version=None, git_init=False, force=False):
    project_root = Path(path).expanduser().resolve()

    if project_root.exists() and project_root.is_file():
        raise RuntimeError(f"{project_root} is a file")

    if project_root.exists() and any(project_root.iterdir()) and not force:
        raise RuntimeError(
            f"{project_root} is not empty (use --force to override)"
        )

    template_dir = find_template_dir()

    if not template_dir:
        raise RuntimeError(
            "base_template not found in engine source.\n"
            "This feature requires engine v0.6.0-beta.2 or later.\n"
            f"Current engine source: {paths.ENGINE_SOURCE_DIR}\n"
            "Try: jadidi-hub engine-sync (to get the latest tag)\n"
            "Or: jadidi-hub engine-checkout HEAD (to use the latest commit)"
        )

    shutil.copytree(template_dir, project_root, dirs_exist_ok=True)

    binary_src = find_binary(version)
    binary_dst = project_root / osinfo.binary_name()
    shutil.copy2(binary_src, binary_dst)
    binary_dst.chmod(
        binary_dst.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH
    )

    resolved_version = version or engine.get_version_name()
    write_project_meta(project_root, resolved_version)

    print(f"Project created: {project_root}")

    setup_script = project_root / "setup.sh"
    if setup_script.exists():
        setup_script.chmod(0o755)

    print(f"Project created: {project_root}")
    print(f"Engine binary: {binary_dst}")
    print(f"Binary source: {binary_src}")

    if git_init:
        run_git_init(project_root)
        print(f"Git repository initialized: {project_root / '.git'}")

    return 0