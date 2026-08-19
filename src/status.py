from src import checks
from src import engine
from src import git
from src import osinfo
from src import paths


def build_entries():
    builds_dir = paths.BUILDS_DIR

    if not builds_dir.exists():
        return []

    entries = []

    for path in sorted(
        builds_dir.iterdir(),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        if not path.is_dir():
            continue

        binary = path / "jadidi"
        entries.append((path.name, binary.exists(), path.stat().st_mtime))

    return entries


def cmd_status():
    print(f"OS: {osinfo.distro_name()}")
    print(f"Distro: {osinfo.detect_distro()}")
    print("")

    repo_url = engine.load_repo_url()
    print(f"Engine repo URL: {repo_url or 'not set'}")

    source = paths.ENGINE_SOURCE_DIR
    source_ok = git.is_git_repo(source)

    print(f"Engine source: {source}")
    print(f"Engine source state: {'ok' if source_ok else 'missing'}")

    if source_ok:
        try:
            print(f"Engine version: {engine.get_version_name()}")
        except Exception:
            print("Engine version: unknown")
    else:
        print("Engine version: unknown")

    print("")

    sol2_header = checks.find_sol2_header()

    if sol2_header:
        print(f"sol2: {sol2_header}")
    else:
        print("sol2: missing")

    dependency_checks = checks.dependency_checks()
    failed = [name for name, ok, detail in dependency_checks if not ok]

    if failed:
        print("Dependency checks: failed")
        print("Missing: " + ", ".join(failed))
    else:
        print("Dependency checks: passed")

    print("")

    entries = build_entries()

    if not entries:
        print("Builds: none")
        return 0

    print("Builds:")

    for name, has_binary, _ in entries:
        binary_state = "binary ok" if has_binary else "binary missing"
        print(f"  {name} - {binary_state}")

    return 0