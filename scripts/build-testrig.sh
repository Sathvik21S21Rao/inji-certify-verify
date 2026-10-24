#!/usr/bin/env bash
# Build the patched module testrig image from a clone at the pin, or at INJI_<C>_REF (ADR-005). Last stdout line = image tag.
# Usage: scripts/build-testrig.sh <certify|verify>   (CONFORMANCE_MVN_OFFLINE=1 adds mvn -o)
# Run under the docker lock on the shared host: flock /tmp/inji-conformance.docker.lock scripts/build-testrig.sh certify
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
[ $# -eq 1 ] || { sed -n 2,3p "$0" >&2; exit 2; }
case $1 in certify|verify) c=$1;; *) sed -n 2,3p "$0" >&2; exit 2;; esac
patch=testrig-bridge/inji-$c.patch
[ -f "$patch" ] || { echo "build-testrig: missing $patch" >&2; exit 2; }
ref_var=INJI_$(echo "$c" | tr a-z A-Z)_REF
up=upstream/inji-$c; [ -z "${!ref_var:-}" ] || up=data/upstream-ref/inji-$c   # same choice as fetch-upstream.sh
scripts/fetch-upstream.sh >&2   # a fresh checkout has no upstream/ yet (run-conformance.sh builds before env.sh up)
commit=$(git -C "$up" rev-parse HEAD)
# the tag names patch and source commit, so a cached image is never reused for another ref
tag=inji-conformance/testrig-$c:$( (sha256sum "$patch" 2>/dev/null || shasum -a 256 "$patch") | cut -c1-12)-${commit:0:12}  # macOS: shasum
if docker image inspect "$tag" >/dev/null 2>&1; then echo "build-testrig: $tag exists, skipping" >&2; echo "$tag"; exit 0; fi

src=data/testrig-build/inji-$c
[ -d "$src/.git" ] || { mkdir -p data/testrig-build; git init -q "$src"; }
git -C "$src" fetch -q --update-shallow "$PWD/$up" HEAD   # the ref clone is shallow
git -C "$src" checkout --quiet --force --detach FETCH_HEAD
git -C "$src" reset --hard --quiet; git -C "$src" clean -fdq   # keeps api-test/target (ignored) for a faster rebuild
git -C "$src" apply "$PWD/$patch" \
  || { echo "build-testrig: $patch does not apply to inji-$c at $commit (api-test changed; refresh the patch)" >&2; exit 2; }

. ./env.sh   # finds a JDK 21+ (JAVA_HOME, macOS java_home, ~/.local/jdks); CI sets JAVA_HOME via setup-java
mvn_args=(-q -DskipTests package); [ "${CONFORMANCE_MVN_OFFLINE:-}" != 1 ] || mvn_args=(-o "${mvn_args[@]}")
(cd "$src/api-test" && mvn "${mvn_args[@]}") >&2
testrig-bridge/build-image.sh "$c" "$src/api-test" "$tag" >&2
echo "$tag"
