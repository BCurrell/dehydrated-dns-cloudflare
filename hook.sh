#!/bin/bash

HOOK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

poetry run python "${HOOK_DIR}/hook.py" "${@}"
