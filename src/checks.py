import shutil
import subprocess
from pathlib import Path

from src import engine
from src import git
from src import osinfo
from src import paths

SDL_CHECKS = [
    ("SDL2", ["sdl2", "SDL2"]),
    ("SDL2_image", ["SDL2_image", "sdl2_image"]),
    ("SDL2_ttf", ["SDL2_ttf", "sdl2_ttf"]),
    ("SDL2_mixer", ["SDL2_mixer", "sdl2_mixer"]),
]

LUA_CANDIDATES = [
    "lua5.4",
    "lua-5.4",
    "lua54",
    "lua",
]


def first_tool(names):
    for name in names:
        if shutil.which(name):
            return name

    return None


def pkg_config_tool():
    return shutil.which("pkg-config") or shutil.which("pkgconf")


def pkg_config_exists(module):
    tool = pkg_config_tool()

    if not tool:
        return False

    result = subprocess.run(
        [tool, "--exists", module],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def pkg_config_version(module):
    tool = pkg_config_tool()

    if not tool:
        return ""

    result = subprocess.run(
        [tool, "--modversion", module],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def find_pkg(candidates):
    for module in candidates:
        if pkg_config_exists(module):
            return module, pkg_config_version(module)

    return None, ""


def find_lua():
    wrong_module = None
    wrong_version = ""

    for module in LUA_CANDIDATES:
        if pkg_config_exists(module):
            version = pkg_config_version(module)

            if version.startswith("5.4"):
                return module, version, True

            wrong_module = module
            wrong_version = version

    if wrong_module:
        return wrong_module, wrong_version, False

    return None, "", False


def find_sol2_header():
    candidates = [
        paths.INCLUDE_DIR / "sol" / "sol.hpp",
        Path("/usr/local/include/sol/sol.hpp"),
        Path("/usr/include/sol/sol.hpp"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def dependency_checks():
    checks = []

    git_tool = first_tool(["git"])
    checks.append(("git", bool(git_tool), git_tool or ""))

    cmake_tool = first_tool(["cmake"])
    checks.append(("cmake", bool(cmake_tool), cmake_tool or ""))

    compiler = first_tool(["c++", "g++", "gcc", "clang++"])
    checks.append(("compiler", bool(compiler), compiler or ""))

    build_tool = first_tool(["make", "ninja"])
    checks.append(("build-tool", bool(build_tool), build_tool or ""))

    pkg_tool = pkg_config_tool()
    checks.append(("pkg-config", bool(pkg_tool), pkg_tool or ""))

    if pkg_tool:
        for name, candidates in SDL_CHECKS:
            module, version = find_pkg(candidates)
            detail = f"{module} {version}".strip() if module else ""
            checks.append((name, bool(module), detail))

        lua_module, lua_version, lua_ok = find_lua()
        detail = f"{lua_module} {lua_version}".strip() if lua_module else ""
        checks.append(("lua-5.4", lua_ok, detail))
    else:
        for name, _ in SDL_CHECKS:
            checks.append((name, False, "pkg-config missing"))

        checks.append(("lua-5.4", False, "pkg-config missing"))

    sol2_header = find_sol2_header()
    checks.append(("sol2", bool(sol2_header), str(sol2_header) if sol2_header else ""))

    return checks


def engine_checks():
    checks = []

    repo_file = paths.BASE_DIR / "engine_repo"
    repo_ok = False

    if repo_file.exists():
        repo_ok = bool(repo_file.read_text().strip())

    checks.append(("engine-repo-config", repo_ok, str(repo_file)))

    source = paths.ENGINE_SOURCE_DIR
    source_ok = git.is_git_repo(source)
    checks.append(("engine-source", source_ok, str(source)))

    cmake_path = source / "CMakeLists.txt"
    cmake_ok = source_ok and cmake_path.exists()
    checks.append(("engine-cmake", cmake_ok, str(cmake_path)))

    if source_ok:
        try:
            version = engine.get_version_name()
            checks.append(("engine-version", True, version))
        except Exception:
            checks.append(("engine-version", False, ""))
    else:
        checks.append(("engine-version", False, "engine source missing"))

    return checks


def print_checks(checks):
    failed = []

    for name, ok, detail in checks:
        status = "ok" if ok else "missing"
        line = f"[{status}] {name}"

        if detail:
            line += f" - {detail}"

        print(line)

        if not ok:
            failed.append(name)

    return failed


def print_missing_help(failed):
    if not failed:
        return

    print("")

    if any(name != "sol2" for name in failed):
        print("Run: python main.py install-deps")

    if "sol2" in failed:
        print("Run: python main.py install-sol2")


def cmd_check_deps():
    print(osinfo.distro_name())
    print("")

    checks = dependency_checks()
    failed = print_checks(checks)

    if failed:
        print_missing_help(failed)
        return 1

    print("")
    print("All dependency checks passed.")

    return 0


def cmd_doctor():
    print(osinfo.distro_name())
    print(osinfo.detect_distro())

    if osinfo.detect_platform() == "windows":
        print("")
        print("Windows detected.")
        print("Doctor checks are designed for Linux.")
        print("On Windows, ensure the following are installed:")
        print("  - CMake")
        print("  - A C++17 compiler (MSVC or MinGW)")
        print("  - Ninja")
        print("  - SDL2, SDL2_image, SDL2_ttf, SDL2_mixer (via vcpkg or manual)")
        print("  - Lua 5.4")
        print("  - OpenGL")
        print("")
        print("Doctor finished.")
        return 0

    print("")
    print("Dependencies:")
    dep_failed = print_checks(dependency_checks())

    print("")
    print("Engine:")
    engine_failed = print_checks(engine_checks())

    if dep_failed:
        print_missing_help(dep_failed)

    if engine_failed:
        print("")
        print("Engine state is incomplete.")

    if dep_failed or engine_failed:
        return 1

    print("")
    print("Doctor finished successfully.")

    return 0