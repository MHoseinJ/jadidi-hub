from pathlib import Path

FAMILY_MAP = {
    "debian": "debian",
    "ubuntu": "debian",
    "linuxmint": "debian",
    "pop": "debian",
    "elementary": "debian",
    "zorin": "debian",
    "kali": "debian",
    "raspbian": "debian",
    "fedora": "fedora",
    "nobara": "fedora",
    "centos": "fedora",
    "rhel": "fedora",
    "rocky": "fedora",
    "alma": "fedora",
    "amzn": "fedora",
    "arch": "arch",
    "manjaro": "arch",
    "endeavouros": "arch",
    "cachyos": "arch",
    "garuda": "arch",
    "artix": "arch",
}


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


def _resolve_family(dist_id):
    dist_id = dist_id.lower()

    if dist_id in FAMILY_MAP:
        return FAMILY_MAP[dist_id]

    return None


def detect_distro():
    release = read_os_release()

    candidates = []

    main_id = release.get("ID", "")
    if main_id:
        candidates.append(main_id)

    id_like = release.get("ID_LIKE", "")
    if id_like:
        candidates.extend(id_like.lower().split())

    for candidate in candidates:
        family = _resolve_family(candidate)
        if family:
            return family

    return "unknown"


def distro_name():
    return read_os_release().get("PRETTY_NAME", "unknown")


def distro_id():
    release = read_os_release()
    return release.get("ID", "unknown")