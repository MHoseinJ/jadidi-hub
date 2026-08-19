import shlex
import sys

from src import cli

PROMPT = "jadidi-hub> "

HELP_TEXT = """Interactive shell for jadidi-hub.

Type any command as you would on the command line.

Examples:
  status
  doctor
  install-deps
  install-sol2
  engine-sync
  engine-checkout v0.1.0
  engine-build
  project-new ~/Projects/MyGame --git-init

Special commands:
  help    - Show this help
  clear   - Clear the screen
  exit    - Exit the shell
  quit    - Exit the shell
"""


def print_help():
    print(HELP_TEXT)


def run_shell():
    print("jadidi-hub interactive shell")
    print("Type 'help' for available commands, 'exit' to quit.")
    print("")

    while True:
        try:
            line = input(PROMPT).strip()
        except EOFError:
            print("")
            break
        except KeyboardInterrupt:
            print("")
            continue

        if not line:
            continue

        if line in ("exit", "quit"):
            break

        if line == "help":
            print_help()
            continue

        if line in ("clear", "cls"):
            print("\033[H\033[J", end="")
            continue

        try:
            argv = shlex.split(line)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            continue

        if not argv:
            continue

        try:
            cli.main(argv)
        except SystemExit:
            pass

    print("Bye!")
    return 0