import argparse
import subprocess
import sys

from src import checks
from src import deps
from src import engine
from src import git
from src import interactive
from src import osinfo
from src import project
from src import sol2
from src import status
from src import editors


def cmd_os(args):
    print(osinfo.distro_name())
    print(osinfo.detect_distro())
    return 0


def cmd_deps(args):
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


def cmd_check_deps(args):
    return checks.cmd_check_deps()


def cmd_doctor(args):
    return checks.cmd_doctor()


def cmd_status(args):
    return status.cmd_status()


def cmd_shell(args):
    return interactive.run_shell()
    

def cmd_install_deps(args):
    distro = osinfo.detect_distro()
    return deps.install_dependencies(distro)


def cmd_install_sol2(args):
    return sol2.install_sol2(args.tag)


def cmd_engine_sync(args):
    source = engine.sync(args.repo_url)
    print(f"Engine source: {source}")
    return 0


def cmd_engine_checkout(args):
    source = engine.checkout(args.ref)
    version = engine.get_version_name()

    print(f"Engine source: {source}")
    print(f"Version: {version}")

    return 0


def cmd_engine_build(args):
    return engine.build()


def cmd_project_new(args):
    return project.create_project(args.path, args.version, args.git_init, args.force)


def cmd_clone(args):
    git.clone_repo(args.url, args.path)
    print(f"Cloned {args.url} into {args.path}")
    return 0


def cmd_current_tag(args):
    tag = git.get_current_tag(args.path)
    print(tag)
    return 0


def cmd_tag(args):
    git.set_tag(args.path, args.tag)
    print(f"Created tag {args.tag} in {args.path}")
    return 0


def cmd_setup_editor(args):
    try:
        return editors.setup_editor(args.path, args.editor)
    except RuntimeError as exc:
        print(f"Editor setup failed: {exc}", file=sys.stderr)
        return 1


def build_parser():
    parser = argparse.ArgumentParser(
        prog="jadidi-hub",
        description="jadidi engine hub",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="command",
        required=True,
    )

    p = subparsers.add_parser(
        "os",
        help="Show detected OS",
    )
    p.set_defaults(func=cmd_os)

    p = subparsers.add_parser(
        "deps",
        help="Show dependencies for current OS",
    )
    p.set_defaults(func=cmd_deps)

    p = subparsers.add_parser(
        "check-deps",
        help="Check required dependencies",
    )
    p.set_defaults(func=cmd_check_deps)

    p = subparsers.add_parser(
        "doctor",
        help="Check dependencies and engine state",
    )
    p.set_defaults(func=cmd_doctor)

    p = subparsers.add_parser(
        "status",
        help="Show current hub status",
    )
    p.set_defaults(func=cmd_status)

    p = subparsers.add_parser(
        "install-deps",
        help="Install dependencies for current OS",
    )
    p.set_defaults(func=cmd_install_deps)

    p = subparsers.add_parser(
        "install-sol2",
        help="Install sol2 into ~/.jadidi",
    )
    p.add_argument(
        "tag",
        nargs="?",
        help="sol2 tag",
    )
    p.set_defaults(func=cmd_install_sol2)

    p = subparsers.add_parser(
        "engine-sync",
        help="Clone or update engine source",
    )
    p.add_argument(
        "repo_url",
        nargs="?",
        help="Engine git repository URL",
    )
    p.set_defaults(func=cmd_engine_sync)

    p = subparsers.add_parser(
        "engine-checkout",
        help="Checkout engine tag/branch/commit",
    )
    p.add_argument(
        "ref",
        help="Tag, branch, or commit",
    )
    p.set_defaults(func=cmd_engine_checkout)

    p = subparsers.add_parser(
        "engine-build",
        help="Build engine in ~/.jadidi/builds/<tag>",
    )
    p.set_defaults(func=cmd_engine_build)

    p = subparsers.add_parser(
        "project-new",
        help="Create a minimal runnable project",
    )
    p.add_argument(
        "path",
        help="Project path",
    )
    p.add_argument(
        "version",
        nargs="?",
        help="Engine build version/tag",
    )
    p.add_argument(
        "--git-init",
        action="store_true",
        help="Run git init in project directory",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Create project in non-empty directory",
    )
    p.set_defaults(func=cmd_project_new)

    p = subparsers.add_parser(
        "clone",
        help="Clone a repository",
    )
    p.add_argument(
        "url",
        help="Repository URL",
    )
    p.add_argument(
        "path",
        help="Destination path",
    )
    p.set_defaults(func=cmd_clone)

    p = subparsers.add_parser(
        "current-tag",
        help="Show latest tag",
    )
    p.add_argument(
        "path",
        help="Repository path",
    )
    p.set_defaults(func=cmd_current_tag)

    p = subparsers.add_parser(
        "tag",
        help="Create a tag",
    )
    p.add_argument(
        "path",
        help="Repository path",
    )
    p.add_argument(
        "tag",
        help="Tag name",
    )
    p.set_defaults(func=cmd_tag)

    p = subparsers.add_parser(
        "shell",
        help="Start interactive shell",
    )
    p.set_defaults(func=cmd_shell)

    p = subparsers.add_parser(
        "setup-editor",
        help="Setup editor integration (VSCode/Zed) for a project",
    )
    p.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project path (default: current directory)",
    )
    p.add_argument(
        "--editor",
        choices=["vscode", "zed"],
        help="Setup only a specific editor (default: both)",
    )
    p.set_defaults(func=cmd_setup_editor)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()

    if not argv:
        parser.print_help()
        return 1

    if argv[0] in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    try:
        return args.func(args) or 0
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() if exc.stderr else str(exc)
        print(f"Command failed: {message}", file=sys.stderr)
        return exc.returncode if exc.returncode else 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


def get_args():
    arg_count = len(sys.argv)
    args = sys.argv[1:]

    return args, arg_count


def parse_args(args, arg_count):
    return main(args)