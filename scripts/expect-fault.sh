#!/usr/bin/env bash
# Turn a fault-injection run green when the gate catches the fault for the expected reason.
# usage: expect-fault.sh TARGET FAULT SHIM STRICT RC REPORTS_DIR
# FAULT=none: exit RC unchanged. RC 2/4 (infra, reconcile) is always red.
set -u
target=$1 fault=$2 shim=$3 strict=$4 rc=$5 dir=$6

[ "$fault" = none ] && exit "$rc"
{ [ "$rc" = 2 ] || [ "$rc" = 4 ]; } && exit "$rc"

say() {
  echo "negative control: $1"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then echo "negative control: $1" >> "$GITHUB_STEP_SUMMARY"; fi
}
# has_row GATE_MD MODULE VERDICT: a table row for MODULE carrying VERDICT as a cell.
has_row() { grep -F -e "| $2 |" "$1" 2>/dev/null | grep -qF -e "| $3 |"; }

want="" cfg="" module="" verdict=""
if [ "$strict" != true ]; then
  case "$fault/$shim" in
    strip-credential-endpoint/false) want=1 cfg=certify-shim-off module=oid4vci-1_0-issuer-metadata-test verdict=NEW_FAILURE ;;
    strip-nonce-endpoint/true)       want=1 cfg=certify-shim-on  module=oid4vci-1_0-issuer-fail-invalid-nonce verdict=REGRESSION ;;
    strip-nonce-endpoint/false)      want=0 ;;
  esac
fi
if [ -z "$want" ]; then
  say "no recorded expectation for $fault/shim=$shim/strict=$strict; reporting raw rc"
  exit "$rc"
fi
[ "$target" = verify ] && want=0   # the faults only touch Certify

if [ "$rc" != "$want" ]; then
  say "FAILED (expected rc=$want, got rc=$rc for $target, $fault, shim=$shim)"
  exit 1
fi
if [ "$want" = 1 ] && ! has_row "$dir/$cfg/gate.md" "$module" "$verdict"; then
  say "FAILED (expected rc=1 with $module $verdict in $cfg/gate.md, got rc=1 without it: red for the wrong reason)"
  exit 1
fi
if [ "$want" = 1 ]; then
  # Every other config's gate must not be RED (combined/ is an aggregate of the per-config gates, skip it).
  others=""
  for g in "$dir"/*/gate.md; do
    c=$(basename "$(dirname "$g")")
    { [ "$c" = "$cfg" ] || [ "$c" = combined ]; } && continue
    grep -q '^### Gate .*: RED' "$g" && others="$others $c"
  done
  if [ -n "$others" ]; then
    say "FAILED (expected only $cfg red, also red:$others: red for the wrong reason)"
    exit 1
  fi
fi
if [ "$want" = 1 ]; then
  say "PASSED ($fault, shim=$shim: gate red with $module $verdict)"
else
  say "PASSED ($fault, shim=$shim: gate green, fault outside this target's reach)"
fi
