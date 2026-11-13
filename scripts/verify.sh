#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. ../strata/scripts/env.sh
mkdir -p .march/verify
for action in check test 'lint --strict' 'build --release'; do
    name=${action%% *}
    # Intentional word splitting: these commands are fixed above.
    if forge $action > ".march/verify/$name.log" 2>&1; then
        tail -n 2 ".march/verify/$name.log"
    else
        cat ".march/verify/$name.log"
        exit 1
    fi
done
UR_BENCH=10000 .march/build/release/ur
if [ "${UR_VERIFY_RENDER:-0}" = 1 ]; then
    MARCH_PIN_MAIN=1 UR_DEMO=1 UR_FRAMES=180 STRATA_SHOT="$PWD/.march/verify/region.ppm" .march/build/release/ur
fi
