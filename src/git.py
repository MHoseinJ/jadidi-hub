import subprocess
from pathlib import Path


def is_git_repo(path):
    path = Path(path)

    if not path.exists():
        return False

    if (path / ".git").exists():
        return True

    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=path,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0 and result.stdout.strip() == "true"


def clone_repo(url, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["git", "clone", url, str(path)],
        check=True,
    )


def fetch_tags(path):
    subprocess.run(
        ["git", "fetch", "--tags", "--prune"],
        cwd=path,
        check=True,
    )


def checkout(path, ref):
    subprocess.run(
        ["git", "checkout", "-f", ref],
        cwd=path,
        check=True,
    )


def get_current_tag(path):
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def get_exact_tag(path):
    result = subprocess.run(
        ["git", "describe", "--tags", "--exact-match"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def try_get_current_tag(path):
    try:
        return get_current_tag(path)
    except subprocess.CalledProcessError:
        return None


def try_get_exact_tag(path):
    try:
        return get_exact_tag(path)
    except subprocess.CalledProcessError:
        return None


def get_short_commit(path):
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def set_tag(path, tag):
    subprocess.run(
        ["git", "tag", tag],
        cwd=path,
        check=True,
    )