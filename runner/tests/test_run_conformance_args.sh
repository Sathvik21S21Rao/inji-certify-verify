#!/usr/bin/env bash
# Argument checks of run-conformance.sh (all fail before any build or `up`) and the env.sh image override.
# Usage: runner/tests/test_run_conformance_args.sh   (needs upstream/ cloned for the override check)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 2
fails=0
expect() { # want_rc want_stderr_substring args...
  local want=$1 msg=$2; shift 2
  local err rc; err=$(scripts/run-conformance.sh "$@" 2>&1 >/dev/null); rc=$?
  if [ "$rc" = "$want" ] && [[ $err == *"$msg"* ]]; then echo "ok   $*"
  else echo "FAIL $* -> rc=$rc: $err"; fails=$((fails + 1)); fi
}
expect 2 "Usage"                                   --component certify --config verify-x509
expect 2 "Usage"                                   --combined --component verify
expect 2 "no config plans/verify/verify-nope.json" --config verify-nope
expect 2 "bad config name"                         --config ../verify-x509
expect 2 "different AS-metadata shim states"       --config certify-shim-off,certify-shim-on
expect 2 "needs exactly one --config"              --component verify --modules oid4vp-1final-verifier-happy-flow
expect 2 "needs exactly one --config"              --config verify-x509,verify-redirect-uri --modules x
expect 2 "not in plans/verify/verify-x509.benchmark.json: nope" --config verify-x509 --modules nope
expect 2 "comma-separated module names"            --config verify-x509 --modules 'a b'
CONFORMANCE_DOCKER_NETWORK=nat expect 2 "must be host or bridge" --config verify-x509

if [ -d upstream/inji-verify ]; then
  img=$(VERIFY_SERVICE_IMAGE=example/verify:test scripts/env.sh compose verify config 2>/dev/null | grep -c 'image: example/verify:test')
  pinned=$(scripts/env.sh compose verify config 2>/dev/null | grep -c 'image: injistackqa/inji-verify-service')
  if [ "$img" = 1 ] && [ "$pinned" = 1 ]; then echo "ok   VERIFY_SERVICE_IMAGE override reaches compose"
  else echo "FAIL image override: override=$img pinned=$pinned"; fails=$((fails + 1)); fi
fi
[ $fails = 0 ] && echo "ALL PASSED" || { echo "$fails FAILED"; exit 1; }
