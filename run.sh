#!/bin/sh
set -eu
cd "$(dirname "$0")"
. ../strata/scripts/env.sh
forge build --release
MARCH_PIN_MAIN=1 exec ./.march/build/release/ur "$@"
