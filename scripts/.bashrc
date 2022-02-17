#!/bin/bash

ENV_FILE=.env

# Load dotenv file
if [[ -f "$ENV_FILE" ]]; then
    export $(cat "$ENV_FILE" | sed 's/#.*//g'| xargs)
fi

# Invoke tab completion definitions
source <(inv --print-completion-script bash)


# Useful aliases
# Example: sendapi POST /loglevel --data "level=DEBUG"
alias msapi='c8y api --host http://127.0.0.1:5000 --raw'
