#!/usr/bin/env bash
# SP5.2 step 2 (test-runner): one live --combined testrig run under the shared Docker lock, memory sampler, exit capture.
set -uo pipefail
W=~/wt/sp5-verification
O=$W/evidence/sp5/SP5.2
cd "$W"
source "$W/env.sh"
export CONFORMANCE_PYTHON=~/wt/sp4-orchestration/.venv-sp4/bin/python
printf 'ts\tused_mib\tavail_mib\n' >"$O/live-mem.tsv"
( while :; do printf '%s\t%s\n' "$(date -Is)" "$(free -m | awk 'NR==2{print $3"\t"$7}')" >>"$O/live-mem.tsv"; sleep 5; done ) &
sp=$!
echo "== $(date -Is) start live" >"$O/live.phase"
flock /tmp/inji-conformance.docker.lock scripts/run-conformance.sh --combined --out "$O/live" >"$O/live.log" 2>&1
rc=$?
echo "$rc" >"$O/live.exit"
echo "== $(date -Is) end live rc=$rc" >>"$O/live.phase"
kill $sp 2>/dev/null; wait $sp 2>/dev/null
exit $rc
