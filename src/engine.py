import subprocess
from pathlib import Path

from src import git
from src import paths
from src import osinfo

ENGINE_REPO_FILE = paths.BASE_DIR / "engine_repo"


def save_repo_url(url):
    paths.ensure_base_dirs()
    ENGINE_REPO_FILE.write_text(url.strip() + "\n")


def load_repo_url():
    if ENGINE_REPO_FILE.exists():
        return ENGINE_REPO_FILE.read_text().strip()

    return ""


def resolve_repo_url(url=None):
    if url:
        save_repo_url(url)
        return url

    saved = load_repo_url()

    if saved:
        return saved

    raise RuntimeError(
        "Engine repository URL is not set. "
        "Run: python main.py engine-sync <repo-url>"
    )


def get_latest_tag():
    source = paths.ENGINE_SOURCE_DIR

    if not git.is_git_repo(source):
        return None

    result = subprocess.run(
        ["git", "tag", "--sort=-v:refname"],
        cwd=source,
        capture_output=True,
        text=True,
        check=True,
    )

    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    if not tags:
        return None

    return tags[0]


def sync(repo_url=None):
    paths.ensure_base_dirs()

    url = resolve_repo_url(repo_url)
    source = paths.ENGINE_SOURCE_DIR

    if git.is_git_repo(source):
        git.fetch_tags(source)
    elif source.exists():
        raise RuntimeError(
            f"{source} exists but is not a git repository"
        )
    else:
        git.clone_repo(url, source)
        git.fetch_tags(source)

    # Auto-checkout latest stable tag
    latest_tag = get_latest_tag()

    if latest_tag:
        git.checkout(source, latest_tag)
        print(f"Auto-checked out latest tag: {latest_tag}")
    else:
        print("Warning: no tags found in engine repository.")
        print("Staying on current branch/commit.")

    return source


def checkout(ref):
    source = paths.ENGINE_SOURCE_DIR

    if not git.is_git_repo(source):
        raise RuntimeError("Engine source is missing. Run engine-sync first.")

    git.fetch_tags(source)
    git.checkout(source, ref)

    return source


def safe_name(name):
    return name.replace("/", "-").replace(" ", "-")


def get_version_name():
    source = paths.ENGINE_SOURCE_DIR

    tag = git.try_get_exact_tag(source)

    if tag:
        return safe_name(tag)

    commit = git.get_short_commit(source)

    return f"untagged-{commit}"


def build():
    source = paths.ENGINE_SOURCE_DIR

    if not git.is_git_repo(source):
        raise RuntimeError("Engine source is missing. Run engine-sync first.")

    cmake_file = source / "CMakeLists.txt"

    if not cmake_file.exists():
        raise RuntimeError(f"CMakeLists.txt not found in {source}")

    version = get_version_name()
    build_dir = paths.BUILDS_DIR / version
    build_dir.mkdir(parents=True, exist_ok=True)

    bin_name = osinfo.binary_name()

    configure_cmd = [
        "cmake",
        "-S", str(source),
        "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DJADIDI_BUILD_PROFILE=generic",
    ]

    if osinfo.detect_platform() == "windows":
        configure_cmd.extend(["-G", "Ninja"])

    build_cmd = [
        "cmake",
        "--build", str(build_dir),
        "--parallel",
    ]

    print("$", " ".join(configure_cmd))
    subprocess.run(configure_cmd, check=True)

    print("$", " ".join(build_cmd))
    subprocess.run(build_cmd, check=True)

    binary = build_dir / bin_name

    print(f"Build directory: {build_dir}")

    if binary.exists():
        print(f"Binary: {binary}")
    else:
        print("Binary file not found at expected path; check CMake output.")

    return 0