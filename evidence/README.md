# Evidence index

These are curated outputs of real runs against the pinned stack (20–22 Oct 2026). Every number in the docs points to a file listed here. The directories are named after the order in which the runs were made: `sp0` holds the first baselines and variant probes, `sp1` the environment checks, `sp2` the runner's repeated live runs, `sp3` the testrig and MinIO runs, and `sp4` the gate, the negative controls and the end-to-end entry script. Raw suite logs, container logs and per-module `*.log.json` files were left out to keep the repository small. Each summary below says what it was built from.

## First baselines and variant probes (`sp0/`)

| File | What it shows |
|---|---|
| `sp0/baseline-v0-certify/reasons.md`, `summary.json` | Certify, issuer plan, AS-metadata shim on, 14 modules: per module the status/result, the first FAILURE condition with its message, and Certify's HTTP response. 3 PASSED, 2 SKIPPED, 9 FAILED. Source of F-CERT-2…5. |
| `sp0/baseline-v0-verify/reasons.md`, `summary.json` | Verify, `redirect_uri` / `url_query` / `direct_post`, 9 modules: failing conditions, the `direct_post` response and the `/vp-result` verdict. All 9 FAILED on F-VER-1. Source of F-VER-1, F-VER-3, F-VER-4. |
| `sp0/baseline-v0-verify-x509/reasons.md`, `summary.json` | Verify, `x509_san_dns` / `request_uri_signed`, 11 modules (10 FAILED, 1 SKIPPED). This run used Verify's bundled self-signed sample key; later runs with a CA-issued leaf fail at the same condition for the EdDSA reason (F-VER-5). Shows F-VER-2's symptom: `direct_post` 200, `/vp-result` INVALID. |
| `sp0/s04-noshim-fullplan/summary.json` | Full issuer plan with the shim off: 12 of 14 modules INTERRUPTED/FAILED (F-CERT-1). |
| `sp0/s04-v1-preauth-pkjwt-dpop/summary.json` | First pre-authorized attempt, unshimmed: `happy-flow` stops on F-CERT-1. |
| `sp0/s04-v2-preauth-pkjwt-dpop-asshim/summary.json` | Same variant with the AS-metadata shim applied (`metadata-test`, `happy-flow`). |
| `sp0/s04-v3-preauth-pkjwt-dpop-txcode/summary.json` | Same with a transaction code: `fail-missing-proof` PASSED. |
| `sp0/s05-v1…v4-redirecturi-urlquery-directpost*/summary.json` | Verifier probes: v1 against the stale compose database (`direct_post` 500), v2/v3 after the schema fix, v4 with the screenshot-evidence upload. |
| `sp0/s05-v5-x509sandns-signed-directpost/summary.json` | First signed-request (`x509_san_dns`) probe. |

## Environment (`sp1/`)

| File | What it shows |
|---|---|
| `sp1/SP1.4/memory.md` | Host memory for all three stacks over three cold starts: peak 9925 MiB used, +1882 MiB over idle; per-container `docker stats`. |
| `sp1/SP1.4/digests.log` | Every running container's image digest compared with `compose/.env.pinned`. |

## Runner (`sp2/`)

| File | What it shows |
|---|---|
| `sp2/live/stability.md` | 4 configs × 3 unattended runs: outcome and first failed condition per module, wall-clock per run, and "no module flipped" for every config. The main source for the results table and for the 2-of-14 limitation. |
| `sp2/live/schema-validation.txt` | All 12 runs' `results.jsonl` validated against `runner/schema/results.schema.json`: 168 lines, 0 errors; plan-flag check OK. |
| `sp2/sp2.1-pytest.txt`, `sp2/sp2.2-pytest.txt` | Runner unit-test output (22, then 51 tests passed). |

## Testrig bridge and reporting (`sp3/`)

| File | What it shows |
|---|---|
| `sp3/SP3.4/<config>/testng-report/*-full-report_T-…html` | The `EmailableReport` HTML for each config run through the patched api-test image. The counts are in the file names: certify-shim-off `T-14_P-0_S-0_F-13_I-0_KI-1`, certify-shim-on `T-14_P-3_S-2_F-8_I-0_KI-1`, verify-redirect-uri `T-9_P-0_S-0_F-9_I-0_KI-0`, verify-x509 `T-11_P-0_S-1_F-10_I-0_KI-0`. |
| `sp3/SP3.4/counts-check.md` | For all four reports: T, P, S and F+KI equal the JSONL counts, and the test names are `OIDF_<component>_<module>`. Overall PASS. |
| `sp3/SP3.4/default-suite-compare.md`, `sp3/SP3.4/default/verify-{before,after}/…T-279_P-0_S-112_F-167…html` | The default (non-conformance) suite before and after the patch. Verify: same 279 tests and the same counts. Certify: both stop at the same point before TestNG (no Keycloak in the stack), with identical logs apart from resource-copy order. |
| `sp3/SP3.1/revalidate/compare.md` | The runner re-run after merging, compared with the earlier live runs: 0 differences across the 4 configs. |
| `sp3/SP3.1/image-size.log` | Testrig base image + `python3 python3-httpx` (+ `python3-pil`): 228,329,533 → 245,925,953 → 248,553,533 bytes, plus installed versions. Source of the +20.2 MB figure. |
| `sp3/commons-diff/jar-bytecode-compare.txt` | apitest-commons 1.5.0 vs 1.6.0: the classes the bridge reuses are byte-identical. |
| `sp3/SP3.2/unit-tests.txt`, `sp3/SP3.3/unit-tests-{certify,verify}.txt` | Bridge unit tests (`testrig-bridge/run-unit-tests.sh`) for both modules: ALL PASSED. |
| `sp3/SP3.5/minio-ls-{certify,verify}.xml` | MinIO bucket `automation` listings after a testrig run with `push-reports-to-s3=yes`: `injicertify/…certify-shim-off…full-report_T-14_P-0_S-0_F-13_I-0_KI-1.html` and `injiverify/…verify-redirect-uri…full-report_T-9_P-0_S-0_F-9_I-0_KI-0.html`, each with its error report. |
| `sp3/SP3.5/<config>/testng-report/*.html` | The reports that were uploaded in those runs. |

## Gate, negative controls and the entry script (`sp4/`)

Per-run directories (`<run>/<config>/`) hold `results.jsonl` and `gate.md`; `<run>/combined/` holds `index.html`, `badge.json` and `gate.md`. Benchmark reasons in these gate tables are verbatim from the time of the run.

| File | What it shows |
|---|---|
| `sp4/SP4.4/kg-combined-{seq,par}{1,2,3}/` | Six known-good `--combined` runs with the runner driver: certify-shim-off 14 ok, verify-redirect-uri 9 ok, verify-x509 11 ok, every time. Badge "benchmark green · 34 modules". |
| `sp4/SP4.4/kg-certify-shim-on/` | The diagnostic shim-on pass against its own benchmark: 14 ok. |
| `sp4/SP4.4/timing.md` | Sequential vs parallel, three runs each: 102.7 s vs 95.7 s mean total; bringing the stacks up (about 68 s) dominates. |
| `sp4/SP4.4/fault-certify-shim-on/`, `sp4/SP4.4/diff-fault-certify-shim-on.md` | `strip-nonce-endpoint` with the shim on: RED, `fail-invalid-nonce` PASSED → FAILED. |
| `sp4/SP4.4/fault-certify-shim-off/`, `sp4/SP4.4/diff-fault-certify-shim-off.md` | The same fault with the shim off: still green, because F-CERT-1 stops 12 of 14 modules first. This is why the record pass needs its own control. |
| `sp4/SP4.4b/red-combined/` | A red combined run: badge "red · 1 of 34 modules off benchmark". |
| `sp4/SP4.8/fault-i/`, `sp4/SP4.8/diff-fault-i.md` | `strip-credential-endpoint`, shim off (the benchmark of record): RED, `NEW_FAILURE` on `oid4vci-1_0-issuer-metadata-test` (`VCICheckRequiredMetadataFields`). |
| `sp4/SP4.8/c014-r2/` | Certify v0.14.0 against the 1.0 benchmark: the same 14 outcomes and first failing conditions, plus one new suite warning. |
| `sp4/SP4.10/warning-stability.md` | Warning set of each of the 48 modules (four configs) across 4–9 known-good runs: one distinct set per module, so a warning-set gate does not flap. |
| `sp4/SP4.11/gate-c014.md` | The 0.14 run against the benchmark with expected warnings: RED, `NEW_WARNING` `VCICheckForOldSdJwtFormatInCredentialConfigurations`. |
| `sp4/SP4.12/root-cause.md` | A bridge unit-test failure traced to stale reports in a reused working directory; fixed in the test. |
| `sp4/SP4.13/build-durations.txt` | First build of each patched testrig image: Certify 114 s, Verify 111 s. |
| `sp4/SP4.14/tr-kg-combined/` | `--combined` with the default testrig driver: all three gates GREEN, exit 0; TestNG reports per config. |
| `sp4/SP4.14/tr-fault-i/`, `sp4/SP4.14/tr-c014/` | Both record-pass negative controls through the testrig driver: RED (`NEW_FAILURE`; `NEW_WARNING`). |
| `sp4/SP4.14/exits.txt`, `sp4/SP4.14/minio-keys.txt` | Exit codes of the three runs (0, 1, 1) and the MinIO objects each run uploaded. |
| `sp4/SP4.14/parity-*.md` | `runner diff` between the runner driver and the testrig driver for the same scenario: "no changes" in all five comparisons. |
| `sp4/SP4.3/actionlint.txt` | actionlint on the workflow: exit 0. |
| `sp4/pytest-final.txt` | Runner unit tests: 103 passed. |
