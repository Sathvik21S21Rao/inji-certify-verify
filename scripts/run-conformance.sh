#!/usr/bin/env bash
# up -> wait-ready -> runner -> gate -> down for one component or both.
# Usage: scripts/run-conformance.sh (--component certify|verify | --combined) [--strict] [--parallel] [--keep] [--out DIR]
# Exit: 0 all gates green, 1 any red, 2 usage / any gate could not evaluate, 3 `up` failed.
# NO locking here: on the shared Docker host wrap the whole call in
#   flock /tmp/inji-conformance.docker.lock scripts/run-conformance.sh ...
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY=${CONFORMANCE_PYTHON:-python3}
driver=${CONFORMANCE_DRIVER:-testrig}   # testrig | runner (direct, for comparison/debugging)
case $driver in testrig|runner) ;; *) echo "run-conformance: CONFORMANCE_DRIVER must be testrig or runner" >&2; exit 2;; esac
usage() { sed -n 2,4p "$0" >&2; exit 2; }

comp= combined= STRICT= parallel= keep= OUT=reports
while [ $# -gt 0 ]; do
  case $1 in
    --component) [ $# -ge 2 ] || usage; comp=$2; shift;;
    --combined) combined=1;;
    --strict) STRICT=--strict;;
    --parallel) parallel=1;;
    --keep) keep=1;;
    --out) [ $# -ge 2 ] || usage; OUT=$2; shift;;
    *) usage;;
  esac
  shift
done
{ [ -n "$comp" ] && [ -z "$combined" ]; } || { [ -z "$comp" ] && [ -n "$combined" ]; } || usage
case $comp in ""|certify|verify) ;; *) usage;; esac
[ -z "$parallel" ] || [ -n "$combined" ] || usage

shim=${CONFORMANCE_CERTIFY_AS_METADATA_SHIM:-false}
certify_cfgs=certify-shim-off; [ "$shim" = true ] && certify_cfgs=certify-shim-on
verify_cfgs="verify-redirect-uri verify-x509"
if [ -n "$combined" ]; then mode=all; else mode=$comp; fi

mkdir -p "$OUT"
info="mode=$mode
certify_configs=$([ "$mode" = verify ] || echo "$certify_cfgs")
verify_configs=$([ "$mode" = certify ] || echo "$verify_cfgs")
CONFORMANCE_CERTIFY_AS_METADATA_SHIM=$shim
CONFORMANCE_FAULT=${CONFORMANCE_FAULT:-none}
driver=$driver
strict=${STRICT:-no}
parallel=${parallel:-no}
git=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "$info" | tee "$OUT/run-info.txt"

TS=$OUT/timing.tsv; : >"$TS"
t0=$SECONDS
phase() { printf '%s\t%s\n' "$1" "$2" | tee -a "$TS"; } # phase seconds

run_config() { # component config
  local comp=$1 cfg=$2 dir=$OUT/$2
  rm -rf "$dir"; mkdir -p "$dir"
  [ "$cfg" != verify-x509 ] || [ -n "${VERIFY_X509_CA_PEM:-}" ] || [ ! -f data/certs/verify-ca.pem ] \
    || export VERIFY_X509_CA_PEM=$(<data/certs/verify-ca.pem)
  # ---- driver selection ------------------------------------------------------
  # testrig (default): the patched module api-test image (OpenIDConformanceTest) runs the runner and
  # leaves results.jsonl under testng-report/conformance/<cfg>/. runner: the runner is called directly.
  if [ "$driver" = runner ]; then
    "$PY" -m runner run "plans/$comp/$cfg.json" --out "$dir" >"$dir/stdout.jsonl" 2>"$dir/stderr.log" || true
  else
    local name=rc-$cfg-$$ mod base img xargs=()
    if [ "$comp" = certify ]; then
      mod=injicertify base=http://localhost:8091 img=$img_certify
      xargs=(-e "conformance.certify.as_metadata_shim=$shim" -e "injiCertifyBaseURL=$base")
    else
      mod=injiverify base=http://localhost:8080 img=$img_verify
      xargs=(-e "injiVerifyBaseUrl=$base")
    fi
    docker run --name "$name" --network host \
      -e MODULES=$mod -e ENV_USER=local -e "ENV_ENDPOINT=$base" -e ENV_TESTLEVEL=smokeAndRegression \
      -e conformance.enabled=yes -e conformance.runner.dir=/home/inji/conformance \
      -e "conformance.plan.template=plans/$comp/$cfg.json" "${xargs[@]}" \
      -e VERIFY_X509_CA_PEM -e CONFORMANCE_FAULT -e CONFORMANCE_CERTIFY_RELEASE \
      -e push-reports-to-s3=yes -e s3-host=http://localhost:9000 -e s3-user-key=minioadmin \
      -e s3-user-secret=minioadmin -e s3-account=automation \
      -v "$PWD/runner:/home/inji/conformance/runner:ro" -v "$PWD/plans:/home/inji/conformance/plans:ro" \
      "$img" >/dev/null 2>"$dir/stderr.log" || true
    docker cp "$name:/home/inji/testng-report" "$dir/testng-report" >/dev/null 2>&1 || true
    docker logs "$name" >"$dir/testrig.log" 2>&1 || true
    docker rm "$name" >/dev/null 2>&1 || true
    cp "$dir/testng-report/conformance/$cfg/results.jsonl" "$dir/results.jsonl" 2>/dev/null || true
  fi
  # ---------------------------------------------------------------------------
  local rc=0
  "$PY" -m runner gate "$dir/results.jsonl" "plans/$comp/$cfg.benchmark.json" $STRICT | tee "$dir/gate.md" || rc=${PIPESTATUS[0]}
  echo "$rc" >"$dir/gate.exit"
}
chain() { local c=$1; shift; for cfg in "$@"; do run_config "$c" "$cfg"; done; }

down() {
  [ -z "$keep" ] || return 0
  [ "$driver" = runner ] || docker compose -p minio --env-file compose/.env.pinned -f compose/minio.yml down -v >/dev/null 2>&1 || true
  local s=$SECONDS
  scripts/env.sh down "$mode" || echo "run-conformance: down failed (ignored)" >&2
  phase down $((SECONDS - s))
  phase total $((SECONDS - t0))
}
trap down EXIT

if [ "$driver" = testrig ]; then
  s=$SECONDS
  # a failed build exits (set -e) before `up`, so there is nothing to tear down
  [ "$mode" = verify ] || img_certify=$(scripts/build-testrig.sh certify | tail -n1)
  [ "$mode" = certify ] || img_verify=$(scripts/build-testrig.sh verify | tail -n1)
  phase build $((SECONDS - s))
fi

s=$SECONDS
if ! scripts/env.sh up "$mode"; then phase up $((SECONDS - s)); echo "run-conformance: up failed" >&2; exit 3; fi
phase up $((SECONDS - s))

if [ "$driver" = testrig ]; then
  s=$SECONDS
  docker compose -p minio --env-file compose/.env.pinned -f compose/minio.yml up -d >&2
  for _ in $(seq 60); do curl -fsS http://127.0.0.1:9000/minio/health/live >/dev/null 2>&1 && break; sleep 1; done
  if ! curl -fsS http://127.0.0.1:9000/minio/health/live >/dev/null 2>&1; then
    phase minio $((SECONDS - s)); echo "run-conformance: minio not live after 60s" >&2; exit 3
  fi
  phase minio $((SECONDS - s))
fi

s=$SECONDS
cfgs=()  # results=benchmark pairs, in order
[ "$mode" = verify ] || cfgs+=($certify_cfgs)
[ "$mode" = certify ] || cfgs+=($verify_cfgs)
if [ -n "$parallel" ]; then
  chain certify $certify_cfgs & p1=$!
  chain verify $verify_cfgs & p2=$!
  wait $p1 || true; wait $p2 || true
else
  [ "$mode" = verify ] || chain certify $certify_cfgs
  [ "$mode" = certify ] || chain verify $verify_cfgs
fi
phase tests $((SECONDS - s))

[ "$driver" = runner ] || curl -fsS --aws-sigv4 "aws:amz:us-east-1:s3" -u minioadmin:minioadmin \
  "http://127.0.0.1:9000/automation?list-type=2" >"$OUT/minio-ls.xml" 2>/dev/null || true

if [ -n "$combined" ]; then
  s=$SECONDS; args=()
  for cfg in "${cfgs[@]}"; do args+=("$OUT/$cfg/results.jsonl=plans/${cfg%%-*}/$cfg.benchmark.json"); done
  "$PY" -m runner combined --out "$OUT/combined" --note "strict=${STRICT:-no} parallel=${parallel:-no} shim=$shim fault=${CONFORMANCE_FAULT:-none} driver=$driver" "${args[@]}" || true
  phase combined $((SECONDS - s))
fi

rc=0
for cfg in "${cfgs[@]}"; do
  g=$(cat "$OUT/$cfg/gate.exit" 2>/dev/null || echo 2)
  case $g in 0) ;; 1) [ $rc = 2 ] || rc=1;; *) rc=2;; esac
done
[ -n "$keep" ] && phase total $((SECONDS - t0))
exit $rc
