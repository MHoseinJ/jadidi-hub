import subprocess
from pathlib import Path


def clone_repo(url, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["git", "clone", url, str(path)],
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


def set_tag(path, tag):
    subprocess.run(
        ["git", "tag", tag],
        cwd=path,
        check=True,
    )