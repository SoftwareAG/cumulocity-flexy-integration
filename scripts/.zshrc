#!/bin/zsh

PROMPT='%(?.%F{green}✓.%F{red}✗%?)%f %B%F{240}%1~%f%b %# '

ENV_FILE=.env

if [[ ! -f "${fpath[1]}/_c8y" ]]; then
    c8y completion zsh > "${fpath[1]}/_c8y"
fi

# Invoke tab completion definitions
source <(inv --print-completion-script zsh)

# Load dotenv file
if [[ -f "$ENV_FILE" ]]; then
    export $(cat "$ENV_FILE" | sed 's/#.*//g'| xargs)
fi

autoload -U compinit; compinit

# Useful aliases
# Example: sendapi POST /loglevel --data "level=DEBUG"
alias msapi='c8y api --host http://127.0.0.1:5000 --raw'
