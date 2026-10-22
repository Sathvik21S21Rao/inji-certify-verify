# SP5.2 evidence: reconcile on live and doctored testrig reports

Run date: 2026-10-22. Run from the repository root, under the shared Docker lock (`flock`).

| check | expected | got | file |
|---|---|---|---|
| doctored a-baseline (unchanged SP4.14 report) | exit 0, MATCH | exit 0, `# Reconciliation: MATCH (14 modules)` | `doctored/a-baseline.md`, `doctored/a-baseline.exit` |
| doctored b-row-flip (happy-flow FAIL->PASS) | exit 1, that module MISMATCH | exit 1, `MISMATCH (14 modules)`; `oid4vci-1_0-issuer-happy-flow` row: TestNG `PASS`, verdict `MISMATCH` | `doctored/b-row-flip.md`, `doctored/b-row-flip.exit`, `doctored/doctored.diff` |
| doctored c-count (EmailableReport renamed P-1 F-12) | exit 1, counts MISMATCH | exit 1, `MISMATCH`; `EmailableReport {'T': 14, 'P': 1, 'S': 0, 'F+KI': 13, 'I': 0} vs suite-derived {'T': 14, 'P': 0, 'S': 0, 'F+KI': 14, 'I': 0}: MISMATCH` | `doctored/c-count.md`, `doctored/c-count.exit`, `doctored/doctored.diff` |
| live `--combined` run exit | exit 0 | exit 0 (`live.exit`); timing `build 0, up 70, minio 2, tests 155, combined 0, down 14, total 242` s | `live.log`, `live.exit`, `live/timing.tsv` |
| live certify-shim-off reconcile | MATCH, reconcile.exit 0 | `MATCH (14 modules)`, reconcile.exit 0 | `live/certify-shim-off/reconcile.md`, `live/certify-shim-off/reconcile.exit` |
| live verify-redirect-uri reconcile | MATCH, reconcile.exit 0 | `MATCH (9 modules)`, reconcile.exit 0 | `live/verify-redirect-uri/reconcile.md`, `live/verify-redirect-uri/reconcile.exit` |
| live verify-x509 reconcile | MATCH, reconcile.exit 0 | `MATCH (11 modules)`, reconcile.exit 0 | `live/verify-x509/reconcile.md`, `live/verify-x509/reconcile.exit` |
| live gate certify-shim-off | GREEN | `Gate certify-shim-off: GREEN (14 ok)`, gate.exit 0 | `live/certify-shim-off/gate.md` |
| live gate verify-redirect-uri | GREEN | `Gate verify-redirect-uri: GREEN (9 ok)`, gate.exit 0 | `live/verify-redirect-uri/gate.md` |
| live gate verify-x509 | GREEN | `Gate verify-x509: GREEN (11 ok)`, gate.exit 0 | `live/verify-x509/gate.md` |
| preflight: no stale containers, avail >= 3000 MiB | none, >= 3000 | `docker ps` empty; available 9061 MiB | (command output in this session, not saved as a file) |
| peak memory during live run | sampled | peak used 8785 MiB, min available 6614 MiB, 50 samples at 5 s | `live-mem.tsv` |
| containers after teardown | none of `certify-/verify-/oidf-/minio/rc-` | 0 matching; only four unrelated `manim`/`sandbox-` containers from 2 months ago | `docker-ps-after.txt` |

Notes:
- The live run was not re-run. Step 3 (stop on exit 4 or MISMATCH) did not trigger.
- The doctored diff for c-count is a rename, recorded as text in `doctored/doctored.diff`.
- Scratch copies of the reports were deleted after the offline run.
- `upstream` and `.venv` symlinks were created in the worktree (git-ignored) per step 0.
- Driver for the live run: `driver-live.sh`. Doctor script: `doctored/doctor.py`.
