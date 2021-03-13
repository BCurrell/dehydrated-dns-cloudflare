#!/bin/bash

HOOK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [[ "${1}" =~ ^(deploy_challenge|clean_challenge)$ ]]; then
    poetry run python "${HOOK_DIR}/hook.py" "${@}"
fi
