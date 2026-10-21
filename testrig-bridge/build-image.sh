#!/bin/sh
# Usage: build-image.sh <certify|verify> <api-test dir> <tag>
# Stages a build context (built target/ + testNgXmlFiles/ + the Dockerfile's other COPY sources) and builds the image.
set -eu
[ $# -eq 3 ] || { echo "usage: $0 <certify|verify> <api-test dir> <tag>" >&2; exit 2; }
mod=$1; api=$(readlink -f "$2"); tag=$3
case $mod in certify|verify) ;; *) echo "module must be certify or verify" >&2; exit 2 ;; esac
[ -d "$api/target" ] || { echo "no $api/target: run mvn package first" >&2; exit 1; }
ctx=$(mktemp -d)
trap 'rm -rf "$ctx"' EXIT
mkdir -p "$ctx/api-test"
cp -r "$api/target" "$ctx/api-test/target"
cp -r "$api/testNgXmlFiles" "$ctx/api-test/target/testNgXmlFiles"
# other COPY sources (first source of each COPY, plain or JSON form), taken from the api-test dir
grep '^COPY' "$api/Dockerfile" | sed 's/^COPY *//; tz; :z; s/^\[ *"\([^"]*\)".*/\1/; t; s/ .*//' | grep -v '^\./api-test/target' |
while IFS= read -r src; do
  cp -r "$api/$src" "$ctx/$src"
done
echo "context: $ctx" >&2
docker build -t "$tag" -f "$api/Dockerfile" "$ctx"
