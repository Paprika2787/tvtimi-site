#!/bin/bash
# Sans argument : CI complète (--all), comme la CI GitHub.
exec "${SOCLE_ROOT:-$HOME/Project/projetMere}/plugin/bin/socle" ci "${@:---all}"
