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
complete -c jadidi-hub -n "__fish_seen_subcommand_from project-new" -xa "(__fish_complete_directories)"

complete -c jadidi-hub -n "__fish_seen_subcommand_from setup-editor" -l editor -d "Setup only a specific editor" -xa "vscode zed"
complete -c jadidi-hub -n "__fish_seen_subcommand_from setup-editor" -xa "(__fish_complete_directories)"

complete -c jadidi-hub -n "__fish_seen_subcommand_from clone" -xa "(__fish_complete_directories)"
complete -c jadidi-hub -n "__fish_seen_subcommand_from current-tag" -xa "(__fish_complete_directories)"
complete -c jadidi-hub -n "__fish_seen_subcommand_from tag" -xa "(__fish_complete_directories)"