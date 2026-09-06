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
