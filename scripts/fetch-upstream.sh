#!/usr/bin/env bash
# Clone the three upstream repos at the pins in compose/.env.pinned; never touches an existing clone.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
set -a; source "$ROOT/compose/.env.pinned"; set +a
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
fetch inji-certify "$INJI_CERTIFY_REPO" "$INJI_CERTIFY_COMMIT"
fetch inji-verify "$INJI_VERIFY_REPO" "$INJI_VERIFY_COMMIT"
fetch conformance-suite "$CONFORMANCE_SUITE_REPO" "$CONFORMANCE_SUITE_COMMIT"
echo "fetch-upstream: ok"
