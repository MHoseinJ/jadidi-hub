import subprocess
import sys

from src import deps
from src import git
from src import osinfo
from src import sol2

USAGE = """Usage: python main.py <command> [options]

Commands:
  help                          Show this help
  os                            Show detected OS
  deps                          Show dependencies for current OS
  install-deps                  Install dependencies for current OS
  install-sol2 [tag]            Install sol2 into ~/.jadidi
  clone <url> <path>            Clone a repository
  current-tag <path>            Show latest tag
  tag <path> <tag>              Create a tag
"""


def get_args():
    arg_count = len(sys.argv)
    args = sys.argv[1:]

    return args, arg_count


def parse_args(args, arg_count):
    if arg_count == 1:
        print(USAGE)
        return 1

    command = args[0]

    if command in ("help", "--help", "-h"):
        print(USAGE)
        return 0

    if command == "os":
        print(osinfo.distro_name())
        print(osinfo.detect_distro())
        return 0

    if command == "deps":
        distro = osinfo.detect_distro()
        packages = deps.get_dependencies(distro)

        if not packages:
            print(f"Unsupported distro: {distro}", file=sys.stderr)
            return 1

        print(f"Distro: {distro}")
        print("Dependencies:")

        for package in packages:
            print(f"  {package}")

        return 0

    if command == "install-deps":
        distro = osinfo.detect_distro()
        return deps.install_dependencies(distro)

    if command == "install-sol2":
        if arg_count > 3:
            print("Usage: python main.py install-sol2 [tag]")
            return 1

        tag = args[1] if arg_count >= 3 else None

        try:
            return sol2.install_sol2(tag)
        except subprocess.CalledProcessError as exc:
            print(f"sol2 installation failed: {exc}", file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(f"sol2 installation failed: {exc}", file=sys.stderr)
            return 1

    if command == "clone":
        if arg_count != 4:
            print("Usage: python main.py clone <url> <path>")
            return 1

        try:
            git.clone_repo(args[1], args[2])
            print(f"Cloned {args[1]} into {args[2]}")
            return 0
        except subprocess.CalledProcessError as exc:
            print(f"git clone failed: {exc}", file=sys.stderr)
            return 1

    if command == "current-tag":
        if arg_count != 3:
            print("Usage: python main.py current-tag <path>")
            return 1

        try:
            tag = git.get_current_tag(args[1])
            print(tag)
            return 0
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() if exc.stderr else str(exc)
            print(f"git describe failed: {message}", file=sys.stderr)
            return 1

    if command == "tag":
        if arg_count != 4:
            print("Usage: python main.py tag <path> <tag>")
            return 1

        try:
            git.set_tag(args[1], args[2])
            print(f"Created tag {args[2]} in {args[1]}")
            return 0
        except subprocess.CalledProcessError as exc:
            print(f"git tag failed: {exc}", file=sys.stderr)
            return 1

    print(f"Unknown command: {command}")
    print(USAGE)

    return 1