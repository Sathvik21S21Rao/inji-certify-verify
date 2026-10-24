#!/usr/bin/env bash
# Clone the three upstream repos at the pins in compose/.env.pinned; never touches an existing clone.
# INJI_CERTIFY_REF / INJI_VERIFY_REF (a SHA, branch, tag or refs/pull/N/head of INJI_*_REPO) test that ref
# instead: it is fetched into data/upstream-ref/inji-<c>, which the harness owns, and upstream/ stays at the pin.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
while IFS='=' read -r k v; do   # a non-empty variable in the environment wins, as in env.sh
  case $k in ''|\#*) continue;; esac
  [ -n "${!k:-}" ] || export "$k=$v"
done < "$ROOT/compose/.env.pinned"
fetch() { # name repo commit
  local dir="$ROOT/upstream/$1"
  if [ ! -e "$dir" ]; then
    mkdir -p "$ROOT/upstream"
    git clone "$2" "$dir"
    git -C "$dir" checkout --detach "$3"
  fi
  local head; head="$(git -C "$dir" rev-parse HEAD)"
  [ "$head" = "$3" ] || { echo "fetch-upstream: $dir is at $head, pin is $3 (not touching it)" >&2; exit 1; }
}
fetch_ref() { # name repo ref
  local dir="$ROOT/data/upstream-ref/$1"
  [ -d "$dir/.git" ] || git init -q "$dir"
  git -C "$dir" fetch -q --depth 1 "$2" "$3" || { echo "fetch-upstream: cannot fetch $3 from $2" >&2; exit 1; }
  git -C "$dir" checkout -q --force --detach FETCH_HEAD
  git -C "$dir" clean -fdq
  echo "fetch-upstream: $1 at $3 = $(git -C "$dir" rev-parse HEAD)" >&2
}
if [ -n "${INJI_CERTIFY_REF:-}" ]; then fetch_ref inji-certify "$INJI_CERTIFY_REPO" "$INJI_CERTIFY_REF"
else fetch inji-certify "$INJI_CERTIFY_REPO" "$INJI_CERTIFY_COMMIT"; fi
if [ -n "${INJI_VERIFY_REF:-}" ]; then fetch_ref inji-verify "$INJI_VERIFY_REPO" "$INJI_VERIFY_REF"
else fetch inji-verify "$INJI_VERIFY_REPO" "$INJI_VERIFY_COMMIT"; fi
fetch conformance-suite "$CONFORMANCE_SUITE_REPO" "$CONFORMANCE_SUITE_COMMIT"
echo "fetch-upstream: ok"
