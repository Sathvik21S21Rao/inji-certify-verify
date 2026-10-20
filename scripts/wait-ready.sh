#!/usr/bin/env bash
# wait-ready.sh [certify|verify|all] [--timeout SECONDS]
# Exit 0 = all checks pass, 1 = timeout, 2 = bad args.
set -uo pipefail

MODE=all; TIMEOUT=300
while [ $# -gt 0 ]; do
  case "$1" in
    certify|verify|all) MODE=$1 ;;
    --timeout) shift; TIMEOUT=${1:-}; [[ "$TIMEOUT" =~ ^[0-9]+$ ]] || { echo "bad --timeout" >&2; exit 2; } ;;
    *) echo "usage: $0 [certify|verify|all] [--timeout SECONDS]" >&2; exit 2 ;;
  esac
  shift
done

SUITE=https://localhost.emobix.co.uk:8443
SRV=oidf-server-1

# jget URL-JSON-on-stdin: exits 0 iff json[key] == value
jeq() { python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get(sys.argv[1])==sys.argv[2] else 1)' "$1" "$2"; }

c_suite-api()            { curl -fsk -o /dev/null "$SUITE/api/plan/info/oid4vci-1_0-issuer-test-plan" && curl -fsk -o /dev/null "$SUITE/api/plan/info/oid4vp-1final-verifier-test-plan"; }
c_certify-host()         { curl -fs -o /dev/null http://localhost:8091/v1/certify/.well-known/openid-credential-issuer; }
c_certify-from-suite()   { docker exec $SRV curl -fsk https://certify-tls/.well-known/openid-credential-issuer | jeq credential_issuer https://certify-tls; }
c_certify-as-from-suite(){ docker exec $SRV curl -fsk https://certify-tls/.well-known/oauth-authorization-server | jeq issuer https://certify-tls; }
c_verify-host()          { curl -fs http://localhost:8080/v1/verify/actuator/health | jeq status UP; }
c_verify-from-suite()    { docker exec $SRV curl -fsk https://verify-tls/v1/verify/actuator/health | jeq status UP; }

CHECKS=(suite-api)
case $MODE in
  certify) CHECKS+=(certify-host certify-from-suite certify-as-from-suite) ;;
  verify)  CHECKS+=(verify-host verify-from-suite) ;;
  all)     CHECKS+=(certify-host certify-from-suite certify-as-from-suite verify-host verify-from-suite) ;;
esac

declare -A STATE
start=$SECONDS
while :; do
  failing=()
  for c in "${CHECKS[@]}"; do
    if "c_$c" >/dev/null 2>&1; then s=ok; else s=FAIL; failing+=("$c"); fi
    [ "${STATE[$c]:-}" = "$s" ] || { echo "wait-ready: $c $s"; STATE[$c]=$s; }
  done
  el=$((SECONDS - start))
  if [ ${#failing[@]} -eq 0 ]; then echo "wait-ready: OK (${el}s)"; exit 0; fi
  if [ "$el" -ge "$TIMEOUT" ]; then echo "wait-ready: TIMEOUT after ${el}s; failing: ${failing[*]}"; exit 1; fi
  sleep 5
done
