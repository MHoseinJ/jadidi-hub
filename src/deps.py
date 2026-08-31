import os
import shutil
import subprocess
import sys

from src import osinfo

DEPENDENCIES = {
    "debian": [
        "build-essential",
        "cmake",
        "git",
        "pkg-config",
        "libsdl2-dev",
        "libsdl2-image-dev",
        "libsdl2-ttf-dev",
        "libsdl2-mixer-dev",
        "liblua5.4-dev",
    ],
    "fedora": [
        "gcc-c++",
        "cmake",
        "git",
        "pkgconf-pkg-config",
        "SDL2-devel",
        "SDL2_image-devel",
        "SDL2_ttf-devel",
        "SDL2_mixer-devel",
        "lua-devel",
    ],
    "arch": [
        "base-devel",
        "cmake",
        "git",
        "pkgconf",
        "sdl2",
        "sdl2_image",
        "sdl2_ttf",
        "sdl2_mixer",
        "lua54",
    ],
    "void": [
        "base-devel",
        "cmake",
        "git",
        "pkg-config",
        "SDL2-devel",
        "SDL2_image-devel",
        "SDL2_ttf-devel",
        "SDL2_mixer-devel",
        "lua54-devel",
    ],
}


def with_sudo(command):
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return command

    if shutil.which("sudo"):
        return ["sudo", *command]

    return command


def run_command(command):
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def get_dependencies(distro):
    return DEPENDENCIES.get(distro, [])


def install_dependencies(distro):
    packages = get_dependencies(distro)

    if not packages:
        from src import osinfo
        real_id = osinfo.distro_id()
        print(f"Unsupported distro: {real_id} (resolved as '{distro}')", file=sys.stderr)
        print("Supported families: debian, fedora, arch", file=sys.stderr)
        return 1

    if distro == "windows":
        print("Windows detected.", file=sys.stderr)
        print("Automatic dependency installation is not supported on Windows.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please install the following manually or via vcpkg/winget:", file=sys.stderr)
        print("  - SDL2", file=sys.stderr)
        print("  - SDL2_image", file=sys.stderr)
        print("  - SDL2_ttf", file=sys.stderr)
        print("  - SDL2_mixer", file=sys.stderr)
        print("  - Lua 5.4", file=sys.stderr)
        print("  - OpenGL", file=sys.stderr)
        print("  - sol2", file=sys.stderr)
        print("", file=sys.stderr)
        print("Recommended: use vcpkg with:", file=sys.stderr)
        print("  vcpkg install sdl2 sdl2-image sdl2-ttf sdl2-mixer lua", file=sys.stderr)
        return 1

    try:
        if distro == "debian":
            run_command(with_sudo(["apt", "update"]))
            run_command(with_sudo(["apt", "install", "-y", *packages]))

        elif distro == "fedora":
            run_command(with_sudo(["dnf", "install", "-y", *packages]))

        elif distro == "arch":
            run_command(with_sudo(["pacman", "-S", "--needed", *packages]))
            
        elif distro == "void":
            run_command(with_sudo(["xbps-install", "-Su"]))
            run_command(with_sudo(["xbps-install", "-y", *packages]))

        else:
            print(f"Unsupported distro: {distro}", file=sys.stderr)
            return 1

    except subprocess.CalledProcessError as exc:
        print(f"Dependency installation failed: {exc}", file=sys.stderr)
        return 1

    print("Dependencies installed.")
    print("Note: run install-sol2 to install sol2 into ~/.jadidi.")

    return 0