# SP5 evidence index (22 Oct 2026)

Task specs are in `subplans/SP5-tasks/`.

| Item | Result | Evidence |
|---|---|---|
| Oracle 1: reconcile code + unit tests | `runner reconcile`; 129 tests pass (24 of them new) | `SP5.1/pytest.txt`, `pytest-final.txt`, `runner/tests/test_reconcile.py` |
| Oracle 1: wired into the entry script / CI | exit 4 on mismatch; CI job summary prints `reconcile.md` | `scripts/run-conformance.sh`, `.github/workflows/full-stack-conformance.yml`, `SP5.1/bash-n.txt` |
| Oracle 1: live `--combined`, testrig driver | exit 0; MATCH 14/14, 9/9, 11/11; EmailableReport counts match; gates GREEN | `SP5.2/live/*/reconcile.md`, `SP5.2/live.exit` |
| Oracle 1: catches a mismatch | flipped row and doctored counts each give exit 1 | `SP5.2/doctored/` |
| Oracle 3: negative controls | linked, no new runs | `negative-controls.md` |
| Oracle 2: manual vs harness | **human**; procedure ready | `manual-vs-harness-procedure.md` |
| Triage F-CERT-3, F-CERT-5 (b), F-VER-5 | Certify defect, Certify defect, suite limitation (+ Verify HAIP gap) | `triage.md`, `specs/` |
| Submission sources | official guidelines + evaluation PDFs, Unstop JSON | `submission-sources/`, `../../submission/sources.md` |
