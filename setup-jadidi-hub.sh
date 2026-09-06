#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$SCRIPT_DIR/main.py" ]]; then
    ROOT_DIR="$SCRIPT_DIR"
else
    ROOT_DIR="$(dirname "$SCRIPT_DIR")"
fi

if [[ ! -f "$ROOT_DIR/main.py" ]]; then
    echo "Error: main.py not found in $ROOT_DIR" >&2
    exit 1
fi

BIN_DIR="$ROOT_DIR/bin"
COMPLETION_DIR="$ROOT_DIR/completion"
LAUNCHER="$BIN_DIR/jadidi-hub"
BASH_COMPLETION="$COMPLETION_DIR/jadidi-hub.bash"
FISH_COMPLETION="$COMPLETION_DIR/jadidi-hub.fish"

mkdir -p "$BIN_DIR" "$COMPLETION_DIR"

cat > "$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$SCRIPT_DIR/../main.py" "$@"
fi

exec python "$SCRIPT_DIR/../main.py" "$@"
EOF

chmod +x "$LAUNCHER"

cat > "$BASH_COMPLETION" <<'EOF'
_jadidi_hub() {
    local cur prev commands cmd
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="help os deps check-deps doctor install-deps install-sol2 status shell engine-sync engine-checkout engine-build project-new clone current-tag tag setup-editor"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        if [[ "${cur}" == -* ]]; then
            COMPREPLY=( $(compgen -W "--help" -- "${cur}") )
        else
            COMPREPLY=( $(compgen -W "${commands}" -- "${cur}") )
        fi
        return 0
    fi

    cmd="${COMP_WORDS[1]}"

    if [[ "${cur}" == -* ]]; then
        case "${cmd}" in
            project-new)
                COMPREPLY=( $(compgen -W "--git-init --force --help" -- "${cur}") )
                ;;
            setup-editor)
                COMPREPLY=( $(compgen -W "--editor --help" -- "${cur}") )
                ;;
            *)
                COMPREPLY=( $(compgen -W "--help" -- "${cur}") )
                ;;
        esac
        return 0
    fi

    case "${cmd}" in
        project-new)
            COMPREPLY=( $(compgen -d -- "${cur}") )
            return 0
            ;;
        setup-editor)
            if [[ "${prev}" == "--editor" ]]; then
                COMPREPLY=( $(compgen -W "vscode zed" -- "${cur}") )
            else
                COMPREPLY=( $(compgen -d -- "${cur}") )
            fi
            return 0
            ;;
        clone)
            if [[ ${COMP_CWORD} -eq 3 ]]; then
                COMPREPLY=( $(compgen -d -- "${cur}") )
            fi
            return 0
            ;;
        current-tag)
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=( $(compgen -d -- "${cur}") )
            fi
            return 0
            ;;
        tag)
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=( $(compgen -d -- "${cur}") )
            fi
            return 0
            ;;
    esac

    return 0
}

complete -F _jadidi_hub jadidi-hub
EOF

cat > "$FISH_COMPLETION" <<'EOF'
function __jadidi_hub_no_subcommand
    not __fish_seen_subcommand_from help os deps check-deps doctor install-deps install-sol2 status shell engine-sync engine-checkout engine-build project-new clone current-tag tag setup-editor
end

complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a help -d "Show help"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a os -d "Show detected OS"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a deps -d "Show dependencies for current OS"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a check-deps -d "Check required dependencies"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a doctor -d "Check dependencies and engine state"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a install-deps -d "Install dependencies for current OS"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a install-sol2 -d "Install sol2 into ~/.jadidi"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a status -d "Show current hub status"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a shell -d "Start interactive shell"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a engine-sync -d "Clone or update engine source"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a engine-checkout -d "Checkout engine tag/branch/commit"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a engine-build -d "Build engine in ~/.jadidi/builds/<tag>"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a project-new -d "Create a minimal runnable project"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a clone -d "Clone a repository"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a current-tag -d "Show latest tag"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a tag -d "Create a tag"
complete -c jadidi-hub -n "__jadidi_hub_no_subcommand" -a setup-editor -d "Setup editor integration (VSCode/Zed)"

complete -c jadidi-hub -n "__fish_seen_subcommand_from project-new" -l git-init -d "Run git init in project directory"
complete -c jadidi-hub -n "__fish_seen_subcommand_from project-new" -l force -d "Create project in non-empty directory"
complete -c jadidi-hub -n "__fish_seen_subcommand_from project-new" -xa "(__fish_complete_directories)"

complete -c jadidi-hub -n "__fish_seen_subcommand_from setup-editor" -l editor -d "Setup only a specific editor" -xa "vscode zed"
complete -c jadidi-hub -n "__fish_seen_subcommand_from setup-editor" -xa "(__fish_complete_directories)"

complete -c jadidi-hub -n "__fish_seen_subcommand_from clone" -xa "(__fish_complete_directories)"
complete -c jadidi-hub -n "__fish_seen_subcommand_from current-tag" -xa "(__fish_complete_directories)"
complete -c jadidi-hub -n "__fish_seen_subcommand_from tag" -xa "(__fish_complete_directories)"
EOF

add_line_once() {
    local file="$1"
    local line="$2"

    mkdir -p "$(dirname "$file")"
    touch "$file"

    if ! grep -qxF "$line" "$file"; then
        printf '\n%s\n' "$line" >> "$file"
        echo "Added to $file:"
        echo "  $line"
    fi
}

BASH_RC="$HOME/.bashrc"
FISH_CONFIG_DIR="$HOME/.config/fish"
FISH_CONFIG="$FISH_CONFIG_DIR/config.fish"
FISH_COMPLETIONS="$FISH_CONFIG_DIR/completions"

if command -v bash >/dev/null 2>&1 || [[ -f "$BASH_RC" ]]; then
    add_line_once "$BASH_RC" "export PATH=\"$BIN_DIR:\$PATH\""
    add_line_once "$BASH_RC" "source \"$BASH_COMPLETION\""
fi

if command -v fish >/dev/null 2>&1 || [[ -d "$FISH_CONFIG_DIR" ]]; then
    mkdir -p "$FISH_COMPLETIONS"
    cp "$FISH_COMPLETION" "$FISH_COMPLETIONS/jadidi-hub.fish"
    add_line_once "$FISH_CONFIG" "fish_add_path \"$BIN_DIR\""
fi

echo "Setup complete."

case "${SHELL:-}" in
    */fish)
        echo "Reload fish config:"
        echo "  source $FISH_CONFIG"
        ;;
    */bash)
        echo "Reload bash config:"
        echo "  source $BASH_RC"
        ;;
    *)
        echo "Restart your shell to use the new completions and PATH."
        ;;
esac