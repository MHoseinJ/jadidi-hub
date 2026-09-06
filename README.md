# jadidi-hub

A command line tool to manage the jadidi engine.

It handles dependency installation, engine source synchronization, building the
engine, creating new projects, and editor integration.

Supported platforms:

- Linux (Debian, Fedora, Arch, Void, and their derivatives)
- Windows (basic support, manual dependency installation)

## Requirements

- Python 3.10 or newer
- git
- cmake
- A C++17 compiler

The rest of the dependencies can be installed through the hub itself on Linux.
On Windows, dependencies must be installed manually (recommended via vcpkg).

## Setup

Clone the repository:

    git clone https://github.com/MHoseinJ/jadidi-hub.git
    cd jadidi-hub

Run the setup script to create the launcher and install shell completions
(Linux only):

    ./setup-jadidi-hub.sh

Then reload your shell configuration:

    source ~/.bashrc

or for fish:

    source ~/.config/fish/config.fish

On Windows, or if you prefer not to use the launcher, you can run the tool
directly:

    python main.py <command>

## Quick start

### Linux

    jadidi-hub install-deps
    jadidi-hub install-sol2
    jadidi-hub engine-sync https://github.com/MHoseinJ/jadidi.git
    jadidi-hub engine-build
    jadidi-hub project-new ~/Projects/MyGame --git-init
    jadidi-hub setup-editor ~/Projects/MyGame

Then run your project:

    cd ~/Projects/MyGame
    ./jadidi

### Windows

Install dependencies manually via vcpkg:

    vcpkg install sdl2 sdl2-image sdl2-ttf sdl2-mixer lua

Then use the hub as normal:

    python main.py engine-sync https://github.com/MHoseinJ/jadidi.git
    python main.py install-sol2
    python main.py engine-build
    python main.py project-new C:\Projects\MyGame --git-init

Then run your project:

    cd C:\Projects\MyGame
    .\jadidi.exe

## Commands

| Command | Description |
|---|---|
| `os` | Show detected OS |
| `deps` | Show dependencies for current OS |
| `check-deps` | Check required dependencies |
| `doctor` | Check dependencies and engine state |
| `status` | Show current hub status |
| `install-deps` | Install dependencies for current OS (Linux only) |
| `install-sol2 [tag]` | Install sol2 into `~/.jadidi` |
| `engine-sync [repo-url]` | Clone or update engine source |
| `engine-checkout <ref>` | Checkout engine tag, branch, or commit |
| `engine-build` | Build engine into `~/.jadidi/builds/<tag>` |
| `project-new <path> [version]` | Create a minimal runnable project |
| `project-new --force` | Create project in non-empty directory |
| `setup-editor [path]` | Setup VSCode/Zed editor integration |
| `shell` | Start interactive shell |
| `clone <url> <path>` | Clone a repository |
| `current-tag <path>` | Show latest tag |
| `tag <path> <tag>` | Create a tag |

Use `jadidi-hub <command> --help` to see options for each command.

### Interactive shell

You can start an interactive shell instead of prefixing every command:

    jadidi-hub shell

Inside the shell, type any command directly:

    jadidi-hub> status
    jadidi-hub> engine-build
    jadidi-hub> project-new ~/Projects/MyGame --git-init
    jadidi-hub> clear
    jadidi-hub> help
    jadidi-hub> exit

Special commands inside the shell: `help`, `clear`, `exit`, `quit`.

## Supported Linux distributions

The hub uses family-based detection, so derivatives are supported
automatically:

| Family | Derivatives |
|---|---|
| debian | ubuntu, linuxmint, pop, elementary, zorin, kali, raspbian |
| fedora | nobara, centos, rhel, rocky, alma, amzn |
| arch | manjaro, endeavouros, cachyos, garuda, artix |
| void | void |

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
    │       └── jadidi (or jadidi.exe on Windows)
    └── assets/
        ├── icon.bmp
        └── font.ttf

You can place a custom `icon.bmp` and `font.ttf` in `~/.jadidi/assets/` to use
them as defaults for new projects.

## Project structure

A project created with `project-new` has this layout:

    MyGame/
    ├── .vscode/
    │   ├── settings.json
    │   └── schemas/
    │       ├── animation.schema.json
    │       └── scene.schema.json
    ├── .zed/
    │   └── settings.json
    ├── config.json
    ├── icon.bmp
    ├── jadidi (or jadidi.exe on Windows)
    ├── ide autocompletion/
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

Run `setup-editor` to configure VSCode or Zed with the JSON schemas for
`Scenes/` and `Animations/` files, enabling auto-completion and validation.

## Shell completion

The setup script installs completions for bash and fish (Linux only).

For bash, it adds the completion source to `~/.bashrc`.

For fish, it copies the completion file to:

    ~/.config/fish/completions/jadidi-hub.fish

After updating completions, remember to re-run `./setup-jadidi-hub.sh` to
copy the latest version to the fish completions directory.

## License

GNU Affero General Public License