#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. ../strata/scripts/env.sh
mkdir -p .march/verify
# `forge test` on its own runs only one test file, so each runs by name;
# optimised, the whole suite runs faster than an unoptimised build compiles.
for test in test/*_test.march; do
    name=$(basename "$test" .march)
    if forge test --release "$test" > ".march/verify/$name.log" 2>&1; then
        tail -n 1 ".march/verify/$name.log"
    else
        cat ".march/verify/$name.log"
        exit 1
    fi
done
for action in check 'lint --strict' 'build --release'; do
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
