from pathlib import Path


def read_os_release():
    path = Path("/etc/os-release")
    values = {}

    if not path.exists():
        return values

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')

    return values


def detect_distro():
    release = read_os_release()

    ids = [release.get("ID", "").lower()]
    ids += release.get("ID_LIKE", "").lower().split()

    if "debian" in ids or "ubuntu" in ids:
        return "debian"

    if "fedora" in ids:
        return "fedora"

    if "arch" in ids:
        return "arch"

    return "unknown"


def distro_name():
    return read_os_release().get("PRETTY_NAME", "unknown")