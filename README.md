# jadidi-hub

A command line tool to manage the jadidi engine on Linux.

It handles dependency installation, engine source synchronization, building the
engine, and creating new projects.

Supported distributions:

- Debian
- Fedora
- Arch Linux

## Requirements

- Python 3.10 or newer
- git
- cmake
- A C++17 compiler

The rest of the dependencies can be installed through the hub itself.

## Setup

Clone the repository:

    git clone https://github.com/MHoseinJ/jadidi-hub.git
    cd jadidi-hub

Run the setup script to create the launcher and install shell completions:

    ./setup-jadidi-hub.sh

Then reload your shell configuration:

    source ~/.bashrc

or for fish:

    source ~/.config/fish/config.fish

You can also run the tool directly without the launcher:

    python main.py <command>

## Quick start

    jadidi-hub install-deps
    jadidi-hub install-sol2
    jadidi-hub engine-sync https://github.com/MHoseinJ/jadidi.git
    jadidi-hub engine-build
    jadidi-hub project-new ~/Projects/MyGame --git-init

Then run your project:

    cd ~/Projects/MyGame
    ./jadidi

## Commands

| Command | Description |
|---|---|
| `os` | Show detected OS |
| `deps` | Show dependencies for current OS |
| `check-deps` | Check required dependencies |
| `doctor` | Check dependencies and engine state |
| `status` | Show current hub status |
| `install-deps` | Install dependencies for current OS |
| `install-sol2 [tag]` | Install sol2 into `~/.jadidi` |
| `engine-sync [repo-url]` | Clone or update engine source |
| `engine-checkout <ref>` | Checkout engine tag, branch, or commit |
| `engine-build` | Build engine into `~/.jadidi/builds/<tag>` |
| `project-new <path> [version]` | Create a minimal runnable project |
| `clone <url> <path>` | Clone a repository |
| `current-tag <path>` | Show latest tag |
| `tag <path> <tag>` | Create a tag |

Use `jadidi-hub <command> --help` to see options for each command.

## Data layout

All hub data is stored under the user home directory:

    ~/.jadidi/
    ├── engine_repo
    ├── sources/
    │   ├── jadidi/
    │   └── sol2/
    ├── include/
    │   └── sol/
    ├── lib/
    │   └── cmake/
    │       └── sol2/
    ├── builds/
    │   └── <tag>/
    │       └── jadidi
    └── assets/
        ├── icon.bmp
        └── font.ttf

You can place a custom `icon.bmp` and `font.ttf` in `~/.jadidi/assets/` to use
them as defaults for new projects.

## Project structure

A project created with `project-new` has this layout:

    MyGame/
    ├── config.json
    ├── icon.bmp
    ├── jadidi
    ├── Fonts/
    │   └── font.ttf
    ├── Scenes/
    │   └── home.json
    ├── Scripts/
    └── Shaders/
        ├── sprite.frag
        └── sprite.vert

The `ide autocompletion` directory is copied from the engine repository and
contains the Lua API definitions used by editors.

## Shell completion

The setup script installs completions for bash and fish.

For bash, it adds the completion source to `~/.bashrc`.

For fish, it copies the completion file to:

    ~/.config/fish/completions/jadidi-hub.fish

## License

GNU Affero General Public License