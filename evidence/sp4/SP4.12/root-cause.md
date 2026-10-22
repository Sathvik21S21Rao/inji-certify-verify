Root cause: stale report files, not EmailableReport state and not (only) listFiles order.
- Report names were "mosip-local-<tag>-<seq>-report.html" with seq restarting at 1 each JVM; the test picked the report by prefix in ./testng-report with last-match-wins.
- If testng-report/ already holds reports from an earlier run in the same cwd (other fixture order/set), two files match "...c1-2-full-report_" (e.g. T-14 and T-1) and listFiles order picks either.
- Evidence: SP4.9 work dir listed both mosip-local-c1-2-full-report_T-14_... and _T-1_...; reproduced in before-stale-reused-cwd.txt (original test, reused cwd, two orders -> FAIL case1 infra-interrupted-unknown ... T-14).
- Note: run-unit-tests.sh itself uses a fresh mktemp dir, so before-{certify,verify}.txt pass (exit 0) on this tree; the SP4.9 control used a reused work dir.
Fix (test only): fixtures sorted; report name carries a per-JVM unique token (nanoTime base36), so only this run's files match. After: after-*.txt, order-*.txt all exit 0; order-c-reused-cwd.txt has three runs in one cwd, all exit 0.
