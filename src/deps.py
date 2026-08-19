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
        print(f"Unsupported distro: {distro}", file=sys.stderr)
        return 1

    try:
        if distro == "debian":
            run_command(with_sudo(["apt", "update"]))
            run_command(with_sudo(["apt", "install", "-y", *packages]))

        elif distro == "fedora":
            run_command(with_sudo(["dnf", "install", "-y", *packages]))

        elif distro == "arch":
            run_command(with_sudo(["pacman", "-S", "--needed", *packages]))

        else:
            print(f"Unsupported distro: {distro}", file=sys.stderr)
            return 1

    except subprocess.CalledProcessError as exc:
        print(f"Dependency installation failed: {exc}", file=sys.stderr)
        return 1

    print("Dependencies installed.")
    print("Note: sol2 is not handled by system package installation yet.")

    return 0