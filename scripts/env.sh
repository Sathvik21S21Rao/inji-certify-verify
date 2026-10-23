#!/usr/bin/env bash
# Usage:
#   scripts/env.sh up    certify|verify|all            # OIDF suite is always included
#   scripts/env.sh down  certify|verify|all [--purge]  # suite is always taken down too
#   scripts/env.sh compose suite|certify|verify <docker compose args...>
# NO locking here: on the shared Docker host wrap calls yourself:
#   flock /tmp/inji-conformance.docker.lock scripts/env.sh up all
# (nested flock would deadlock).
set -euo pipefail
# bash 4+ (wait-ready.sh uses an associative array; empty arrays under set -u). macOS ships 3.2: brew install bash
[ "${BASH_VERSINFO[0]}" -ge 4 ] || { echo "env.sh: needs bash 4+, this is $BASH_VERSION (macOS: brew install bash)" >&2; exit 2; }
CONFORMANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CONFORMANCE_ROOT
cd "$CONFORMANCE_ROOT"
# Pins from .env.pinned. A variable already set (non-empty) in the environment wins, e.g.
# CERTIFY_IMAGE=... or VERIFY_SERVICE_IMAGE=... to test a new release without editing the file.
while IFS='=' read -r k v; do
  case $k in ''|\#*) continue;; esac
  [ -n "${!k:-}" ] || export "$k=$v"
done < compose/.env.pinned
U=upstream
BASE_suite=$U/conformance-suite/docker-compose-prebuilt.yml
BASE_certify=$U/inji-certify/docker-compose/docker-compose-injistack/docker-compose.yaml
BASE_verify=$U/inji-verify/docker-compose/docker-compose.yml
die() { echo "env.sh: $*" >&2; exit 2; }

dc() { # project args...
  local p=$1; shift; local b=BASE_$p x=()
  [ "$p" = certify ] && [ "$fault" != none ] && x+=(-f compose/certify-fault.yml)
  [ "$p" = certify ] && [ "$release" = 0.14 ] && x+=(-f compose/certify-014.yml)
  docker compose -p "$([ "$p" = suite ] && echo oidf || echo "$p")" --env-file compose/.env.pinned \
    -f "${!b}" -f "compose/$p.yml" "${x[@]}" "$@"
}
fault=${CONFORMANCE_FAULT:-none}
[ "$fault" = none ] || [ -f "compose/tls/fault-$fault.conf" ] || die "CONFORMANCE_FAULT '$fault' has no compose/tls/fault-$fault.conf"
export CONFORMANCE_FAULT=$fault
release=${CONFORMANCE_CERTIFY_RELEASE:-1.0}
[ "$release" = 0.14 ] && [ "${CONFORMANCE_CERTIFY_AS_METADATA_SHIM:-false}" = true ] && die "0.14 control runs with the shim off only"
case $release in 1.0) ;; 0.14) # negative control (b): v0.14.0 upstream compose, same overlay
  d=data/upstream-0.14/inji-certify; c=docker-compose/docker-compose-injistack
  if [ ! -d "$d/$c" ]; then
    git -C $U/inji-certify cat-file -e "$CERTIFY_014_COMMIT^{commit}" 2>/dev/null \
      || die "commit $CERTIFY_014_COMMIT not in $U/inji-certify; fetch it yourself (this script never fetches into the shared clone)"
    mkdir -p "$d"; git -C $U/inji-certify archive "$CERTIFY_014_COMMIT" $c | tar -x -C "$d"
  fi
  BASE_certify=$d/$c/docker-compose.yaml; export CERTIFY_IMAGE=$CERTIFY_014_IMAGE;;
*) die "CONFORMANCE_CERTIFY_RELEASE must be 1.0|0.14, got '$release'";; esac
parts() { case $1 in certify) echo certify;; verify) echo verify;; all) echo certify verify;; *) die "mode must be certify|verify|all";; esac; }

cmd=${1:-}; mode=${2:-}
case $cmd in
  up)
    parts "$mode" >/dev/null
    shim=${CONFORMANCE_CERTIFY_AS_METADATA_SHIM:-false}
    case $shim in true|false) ;; *) die "CONFORMANCE_CERTIFY_AS_METADATA_SHIM must be true|false, got '$shim'";; esac
    export CONFORMANCE_CERTIFY_AS_METADATA_SHIM=$shim
    echo "env.sh: CONFORMANCE_CERTIFY_AS_METADATA_SHIM=$shim CONFORMANCE_FAULT=$fault CONFORMANCE_CERTIFY_RELEASE=$release"
    start=$SECONDS
    scripts/fetch-upstream.sh
    docker network inspect mosip_network >/dev/null 2>&1 || docker network create mosip_network
    # the keystore is shared with 1.0; one from another Certify version must not be reused
    [ "$release" = 1.0 ] || rm -rf data/certify/CERTIFY_PKCS12/* 2>/dev/null || true
    mkdir -p data/certify/CERTIFY_PKCS12 && chmod 0777 data/certify/CERTIFY_PKCS12
    scripts/gen-certs.sh
    dc suite up -d --wait --wait-timeout 600
    for p in $(parts "$mode"); do dc "$p" up -d --wait --wait-timeout 600; done
    [ -x scripts/wait-ready.sh ] && scripts/wait-ready.sh "$mode"
    if [ "$mode" != verify ] && [ -x scripts/seed-certify.sh ]; then scripts/seed-certify.sh; fi
    echo "env.sh: ready in $((SECONDS - start))s"
    ;;
  down)
    parts "$mode" >/dev/null
    purge=; [ "${3:-}" = --purge ] && purge=-v
    for p in $(parts "$mode") suite; do dc "$p" down --remove-orphans $purge; done
    if [ -n "$purge" ] && [ -e data ]; then
      rm -rf data 2>/dev/null || true
      if [ -e data ]; then
        docker run --rm -v "$CONFORMANCE_ROOT/data:/d" "$NGINX_IMAGE" sh -c 'rm -rf /d/* /d/.[!.]*' || true
        rm -rf data
      fi
    fi
    ;;
  compose)
    case $mode in suite|certify|verify) shift 2; dc "$mode" "$@";; *) die "compose target must be suite|certify|verify";; esac
    ;;
  *) die "usage: env.sh up|down certify|verify|all | compose suite|certify|verify ...";;
esac
