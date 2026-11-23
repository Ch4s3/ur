#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. ../strata/scripts/env.sh
mkdir -p .march/verify
run() {
    name=$1
    shift
    if "$@" > ".march/verify/$name.log" 2>&1; then
        tail -n 2 ".march/verify/$name.log"
    else
        cat ".march/verify/$name.log"
        exit 1
    fi
}
run check forge check
# `forge test` compiles only the first test file as its entry point, so run
# each suite on its own.
for suite in test/*_test.march; do
    name=$(basename "$suite" .march)
    echo "$name"
    run "$name" forge test "$suite"
done
run lint forge lint --strict
run build forge build --release
UR_BENCH=10000 .march/build/release/ur
if [ "${UR_VERIFY_RENDER:-0}" = 1 ]; then
    MARCH_PIN_MAIN=1 UR_DEMO=1 UR_FRAMES=180 STRATA_SHOT="$PWD/.march/verify/region.ppm" .march/build/release/ur
fi
