#!/usr/bin/env bash
# Build the patched module testrig image from a clone at the pin (ADR-005). Last stdout line = image tag.
# Usage: scripts/build-testrig.sh <certify|verify>   (CONFORMANCE_MVN_OFFLINE=1 adds mvn -o)
# Run under the docker lock on the shared host: flock /tmp/inji-conformance.docker.lock scripts/build-testrig.sh certify
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
[ $# -eq 1 ] || { sed -n 2,3p "$0" >&2; exit 2; }
case $1 in certify|verify) c=$1;; *) sed -n 2,3p "$0" >&2; exit 2;; esac
patch=testrig-bridge/inji-$c.patch
pin_var=INJI_$(echo "$c" | tr a-z A-Z)_COMMIT
pin=$(sed -n "s/^$pin_var=//p" compose/.env.pinned)
[ -n "$pin" ] && [ -f "$patch" ] || { echo "build-testrig: missing $pin_var or $patch" >&2; exit 2; }
tag=inji-conformance/testrig-$c:$(sha256sum "$patch" | cut -c1-12)
if docker image inspect "$tag" >/dev/null 2>&1; then echo "build-testrig: $tag exists, skipping" >&2; echo "$tag"; exit 0; fi

src=data/testrig-build/inji-$c
[ -d "$src/.git" ] || { mkdir -p data/testrig-build; git clone --quiet "upstream/inji-$c" "$src"; }
git -C "$src" checkout --quiet --detach "$pin"
git -C "$src" reset --hard --quiet; git -C "$src" clean -fdq   # keeps api-test/target (ignored) for a faster rebuild
git -C "$src" apply "$PWD/$patch"

[ ! -d "$HOME/.local/jdks" ] || . ./env.sh   # local JDK 21; CI gets it from setup-java
mvn_args=(-q -DskipTests package); [ "${CONFORMANCE_MVN_OFFLINE:-}" != 1 ] || mvn_args=(-o "${mvn_args[@]}")
(cd "$src/api-test" && mvn "${mvn_args[@]}") >&2
testrig-bridge/build-image.sh "$c" "$src/api-test" "$tag" >&2
echo "$tag"
