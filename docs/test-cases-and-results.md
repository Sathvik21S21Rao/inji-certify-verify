# Test cases and results

One page that collects every test the harness was put through and where its result is recorded. All runs were made in October 2026 against Inji Certify 1.0.x and Inji Verify 1.0.x at the pinned images. Paths are relative to the repository root.

## 1. Conformance runs (what the harness reports about Inji)

The OIDF suite is the test oracle. Each module is one test case; the harness reports it as one TestNG test.

| Config | Modules | Pass | Skip / review | Fail | Root cause of the failures | Gate |
|---|---|---|---|---|---|---|
| certify-shim-off (record) | 14 | 0 | 0 | 14 | 12 × F-CERT-1, 2 × F-CERT-5 | GREEN (matches benchmark) |
| certify-shim-on (diagnostic) | 14 | 3 | 2 | 9 | F-CERT-2, -3, -4, -5 | GREEN (diagnostic benchmark) |
| verify-redirect-uri | 9 | 0 | 0 | 9 | 9 × F-VER-1 | GREEN |
| verify-x509 | 11 | 0 | 1 | 10 | 10 × F-VER-5 | GREEN |

"GREEN" means the run matches the recorded benchmark, not that Inji passes. The failures are real findings, each with a spec clause, evidence and suggested owner in [findings.md](findings.md). Module-level results: `evidence/sp2/live/stability.md`; live gate tables: `evidence/sp5/SP5.2/live/*/gate.md`.

## 2. Does the harness report the right thing?

| # | Test case | Expected | Result | Evidence |
|---|---|---|---|---|
| R1 | TestNG report vs the suite's own plan export, live combined run | MATCH on every module | MATCH 14 + 9 + 11 = 34/34 | `evidence/sp5/SP5.2/live/*/reconcile.md` |
| R2 | Doctored report: one module flipped FAIL→PASS | MISMATCH, exit 1 | MISMATCH on that module, exit 1 | `evidence/sp5/SP5.2/doctored/b-row-flip.md` |
| R3 | Doctored report: counts in the EmailableReport filename changed | MISMATCH, exit 1 | MISMATCH on counts, exit 1 | `evidence/sp5/SP5.2/doctored/c-count.md` |
| R4 | Testrig report counts vs JSONL, all four configs | equal | equal | `evidence/sp3/SP3.4/counts-check.md` |
| R5 | Default Verify testrig suite with the patch applied, conformance off | unchanged | same 279 tests and counts before and after | `evidence/sp3/SP3.4/default-suite-compare.md` |
| R6 | Runner driver vs testrig driver on the same targets | identical gate results | no differences | `evidence/sp4/SP4.14/parity-*.md` |

## 3. Negative controls (does the gate go red when it should?)

| # | Known-bad target | Pass | Expected | Result | Evidence |
|---|---|---|---|---|---|
| N1 | `credential_endpoint` removed from issuer metadata | certify-shim-off | RED | RED, `NEW_FAILURE` on `oid4vci-1_0-issuer-metadata-test` | `evidence/sp4/SP4.14/tr-fault-i/certify-shim-off/gate.md` |
| N2 | `nonce_endpoint` removed | certify-shim-on | RED | RED, `fail-invalid-nonce` PASSED→FAILED | `evidence/sp4/SP4.4/fault-certify-shim-on/certify-shim-on/gate.md` |
| N2′ | `nonce_endpoint` removed | certify-shim-off | — | GREEN: known blind spot while F-CERT-1 stands ([known-limitations.md](known-limitations.md)) | `evidence/sp4/SP4.4/diff-fault-certify-shim-off.md` |
| N3 | Certify v0.14.0 (draft 13) against the 1.0 benchmark | certify-shim-off | RED | RED, `NEW_WARNING` on the metadata test | `evidence/sp4/SP4.11/gate-c014.md` |
| N4 | Known-good control for the same batch | combined | GREEN | GREEN, 3 gates | `evidence/sp4/SP4.14/exits.txt` |

Details: `evidence/sp5/negative-controls.md`.

## 4. Stability

| # | Test case | Expected | Result | Evidence |
|---|---|---|---|---|
| S1 | Each config run 3 times | same outcome and first failing condition per module | no module changed | `evidence/sp2/live/stability.md` |
| S2 | Suite warning sets on known-good runs | stable | 48/48 stable | `evidence/sp4/SP4.10/warning-stability.md` |

## 5. CI (GitHub Actions, fresh runners)

| Run | Inputs | Expected | Result | Evidence |
|---|---|---|---|---|
| 39909614848 | known-good | all gates GREEN, run succeeds | GREEN 14 / 9 / 11, success | `evidence/sp5/ci/README.md` |
| 39909618292 | `fault=strip-credential-endpoint` | certify gate RED for the recorded reason, run succeeds | RED `NEW_FAILURE`, "negative control: PASSED", success | `evidence/sp5/ci/README.md` |
| — | `scripts/expect-fault.sh` decision table | 13 cases (caught, not caught, wrong reason, exit 2/4 passthrough, …) | 13/13 ok | `evidence/sp5/SP5.3/test-output.txt` |

## 6. Unit tests

| Suite | Command | Result | Evidence |
|---|---|---|---|
| Python runner (gate, handoff, reconcile, records, templates, evidence, run) | `.venv/bin/python -m pytest runner/tests` | 129 passed | `evidence/sp5/pytest-final.txt` |
| Java bridge (`OpenIDConformanceTest`) | `testrig-bridge/run-unit-tests.sh` | all passed, for both the Certify and the Verify module | `evidence/sp3/SP3.3/unit-tests-certify.txt`, `evidence/sp3/SP3.3/unit-tests-verify.txt` |

## Edge cases covered

- A module that times out, or has no record because the runner died, gets the verdict INFRA and turns the gate red.
- A module that changes outcome or first failing condition is `REGRESSION` or `NEW_FAILURE`; a new suite warning is `NEW_WARNING`; an expected result that no longer happens is `STALE`. All are red.
- A benchmark entry with an empty reason makes the gate exit 2 (cannot evaluate) until someone reviews it.
- A shim-on run cannot be gated against the shim-off benchmark: the variant key must match, or the gate exits 2.
- A fault run that goes red for a different reason than recorded stays red in CI.
