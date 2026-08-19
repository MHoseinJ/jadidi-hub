import shutil
import subprocess
from pathlib import Path

from src import paths

SOL2_REPO_URL = "https://github.com/ThePhD/sol2.git"
SOL2_SOURCE_DIR = paths.SOURCES_DIR / "sol2"


def run_git(args):
    print("$ git", " ".join(args))
    subprocess.run(
        ["git", *args],
        cwd=SOL2_SOURCE_DIR,
        check=True,
    )


def clone_or_update():
    paths.ensure_base_dirs()

    if SOL2_SOURCE_DIR.exists():
        if not (SOL2_SOURCE_DIR / ".git").exists():
            raise RuntimeError(
                f"{SOL2_SOURCE_DIR} exists but is not a git repository"
            )

        run_git(["fetch", "--tags", "--prune"])
        return

    SOL2_SOURCE_DIR.parent.mkdir(parents=True, exist_ok=True)

    print("$ git clone", SOL2_REPO_URL, str(SOL2_SOURCE_DIR))
    subprocess.run(
        ["git", "clone", SOL2_REPO_URL, str(SOL2_SOURCE_DIR)],
        check=True,
    )

    run_git(["fetch", "--tags", "--prune"])


def is_stable_tag(tag):
    lowered = tag.lower()

    for bad in ("alpha", "beta", "rc", "pre", "dev"):
        if bad in lowered:
            return False

    return True


def latest_stable_tag():
    result = subprocess.run(
        ["git", "tag", "--list", "--sort=-v:refname"],
        cwd=SOL2_SOURCE_DIR,
        capture_output=True,
        text=True,
        check=True,
    )

    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    for tag in tags:
        if is_stable_tag(tag):
            return tag

    if tags:
        return tags[0]

    raise RuntimeError("No tags found in sol2 repository")


def checkout_tag(tag):
    run_git(["checkout", "-f", tag])


def install_headers():
    src = SOL2_SOURCE_DIR / "include" / "sol"

    if not src.exists():
        raise RuntimeError(f"sol2 include directory not found: {src}")

    dst = paths.INCLUDE_DIR / "sol"

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

    return dst


def write_cmake_package(tag):
    cmake_file = paths.CMAKE_DIR / "sol2Config.cmake"

    content = f"""set(SOL2_VERSION "{tag}")
set(SOL2_INCLUDE_DIR "${{CMAKE_CURRENT_LIST_DIR}}/../../../include")

if(NOT TARGET sol2)
    add_library(sol2 INTERFACE IMPORTED)
    set_target_properties(sol2 PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${{SOL2_INCLUDE_DIR}}")
endif()

set(sol2_FOUND TRUE)
"""

    cmake_file.write_text(content)

    return cmake_file


def install_sol2(tag=None):
    clone_or_update()

    if not tag:
        tag = latest_stable_tag()

    checkout_tag(tag)

    include_path = install_headers()
    cmake_file = write_cmake_package(tag)

    print(f"sol2 version: {tag}")
    print(f"sol2 headers installed: {include_path}")
    print(f"sol2 CMake package installed: {cmake_file}")
    print("To use it with CMake, add this prefix:")
    print(f"  -DCMAKE_PREFIX_PATH={paths.BASE_DIR}")

    return 0