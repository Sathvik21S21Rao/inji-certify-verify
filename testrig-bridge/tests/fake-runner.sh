#!/bin/sh
# Stand-in for the conformance runner: replays a JSONL fixture ($1), ignores the other args.
# FAKE_EXIT sets the exit code (default 0).
cat "$1"
exit "${FAKE_EXIT:-0}"
