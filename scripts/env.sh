#!/usr/bin/env bash
# Usage:
#   scripts/env.sh up    certify|verify|all            # OIDF suite is always included
#   scripts/env.sh down  certify|verify|all [--purge]  # suite is always taken down too
#   scripts/env.sh compose suite|certify|verify <docker compose args...>
# NO locking here: on the shared Docker host wrap calls yourself:
#   flock /tmp/inji-conformance.docker.lock scripts/env.sh up all
# (nested flock would deadlock).
set -euo pipefail
CONFORMANCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export CONFORMANCE_ROOT
cd "$CONFORMANCE_ROOT"
set -a; source compose/.env.pinned; set +a
U=upstream
BASE_suite=$U/conformance-suite/docker-compose-prebuilt.yml
BASE_certify=$U/inji-certify/docker-compose/docker-compose-injistack/docker-compose.yaml
BASE_verify=$U/inji-verify/docker-compose/docker-compose.yml
die() { echo "env.sh: $*" >&2; exit 2; }

dc() { # project args...
  local p=$1; shift; local b=BASE_$p
  docker compose -p "$([ "$p" = suite ] && echo oidf || echo "$p")" --env-file compose/.env.pinned \
    -f "${!b}" -f "compose/$p.yml" "$@"
}
parts() { case $1 in certify) echo certify;; verify) echo verify;; all) echo certify verify;; *) die "mode must be certify|verify|all";; esac; }

cmd=${1:-}; mode=${2:-}
case $cmd in
  up)
    parts "$mode" >/dev/null
    shim=${CONFORMANCE_CERTIFY_AS_METADATA_SHIM:-false}
    case $shim in true|false) ;; *) die "CONFORMANCE_CERTIFY_AS_METADATA_SHIM must be true|false, got '$shim'";; esac
    export CONFORMANCE_CERTIFY_AS_METADATA_SHIM=$shim
    echo "env.sh: CONFORMANCE_CERTIFY_AS_METADATA_SHIM=$shim"
    start=$SECONDS
    scripts/fetch-upstream.sh
    docker network inspect mosip_network >/dev/null 2>&1 || docker network create mosip_network
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
