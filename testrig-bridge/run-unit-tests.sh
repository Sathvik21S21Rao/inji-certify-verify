#!/bin/sh
# Usage: run-unit-tests.sh <certify|verify> <path-to-jar-with-dependencies>
# Compiles tests/OpenIDConformanceBridgeTest.java and runs it from a scratch dir (reports land in ./testng-report).
set -eu
mod=$1; jar=$(readlink -f "$2")
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
case $mod in
  certify) bridge=io.inji.testrig.apirig.injicertify.testscripts.OpenIDConformanceTest ;;
  verify)  bridge=io.inji.testrig.apirig.injiverify.testscripts.OpenIDConformanceTest ;;
  *) echo "module must be certify or verify" >&2; exit 2 ;;
esac
work=$(mktemp -d)
mkdir "$work/classes"
javac -proc:none -cp "$jar" -d "$work/classes" "$here/tests/OpenIDConformanceBridgeTest.java"
cd "$work"
java -cp "$jar:$work/classes" -Dbridge.class="$bridge" -Dfixtures="$root/runner/tests/fixtures" \
  -Dfake.runner="$here/tests/fake-runner.sh" -Dcomponent="$mod" OpenIDConformanceBridgeTest
