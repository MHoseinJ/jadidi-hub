import subprocess
import sys

from src import checks
from src import deps
from src import engine
from src import git
from src import osinfo
from src import project
from src import sol2

USAGE = """Usage: python main.py <command> [options]

Commands:
  help                          Show this help
  os                            Show detected OS
  deps                          Show dependencies for current OS
  check-deps                    Check required dependencies
  doctor                        Check dependencies and engine state
  install-deps                  Install dependencies for current OS
  install-sol2 [tag]            Install sol2 into ~/.jadidi
  engine-sync [repo-url]        Clone or update engine source
  engine-checkout <ref>         Checkout engine tag/branch/commit
  engine-build                  Build engine in ~/.jadidi/builds/<tag>
  clone <url> <path>            Clone a repository
  current-tag <path>            Show latest tag
  tag <path> <tag>              Create a tag
  project-new <path> [version]  Create a minimal runnable project
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

    if command == "check-deps":
        if arg_count != 2:
            print("Usage: python main.py check-deps")
            return 1

        return checks.cmd_check_deps()

    if command == "doctor":
        if arg_count != 2:
            print("Usage: python main.py doctor")
            return 1

        return checks.cmd_doctor()

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

    if command == "engine-sync":
        if arg_count > 3:
            print("Usage: python main.py engine-sync [repo-url]")
            return 1

        url = args[1] if arg_count >= 3 else None

        try:
            source = engine.sync(url)
            print(f"Engine source: {source}")
            return 0
        except subprocess.CalledProcessError as exc:
            print(f"engine sync failed: {exc}", file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(f"engine sync failed: {exc}", file=sys.stderr)
            return 1

    if command == "engine-checkout":
        if arg_count != 3:
            print("Usage: python main.py engine-checkout <ref>")
            return 1

        try:
            source = engine.checkout(args[1])
            version = engine.get_version_name()

            print(f"Engine source: {source}")
            print(f"Version: {version}")

            return 0
        except subprocess.CalledProcessError as exc:
            print(f"engine checkout failed: {exc}", file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(f"engine checkout failed: {exc}", file=sys.stderr)
            return 1

    if command == "engine-build":
        if arg_count != 2:
            print("Usage: python main.py engine-build")
            return 1

        try:
            return engine.build()
        except subprocess.CalledProcessError as exc:
            print(f"engine build failed: {exc}", file=sys.stderr)
            return 1
        except RuntimeError as exc:
            print(f"engine build failed: {exc}", file=sys.stderr)
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

    if command == "project-new":
        if arg_count < 3 or arg_count > 4:
            print("Usage: python main.py project-new <path> [version]")
            return 1

        path = args[1]
        version = args[2] if arg_count == 4 else None

        try:
            return project.create_project(path, version)
        except RuntimeError as exc:
            print(f"project creation failed: {exc}", file=sys.stderr)
            return 1

    print(f"Unknown command: {command}")
    print(USAGE)

    return 1