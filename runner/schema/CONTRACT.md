# Runner output contract v1.0 (frozen 2026-10-20)

Consumer: the testrig bridge (`OpenIDConformanceTest`). Schema: `results.schema.json` (JSON Schema 2020-12). Fixtures: `runner/tests/fixtures/*.jsonl`.

**Stream.** UTF-8 JSON Lines on **stdout**, one record per line, flushed per line. Everything else (suite client chatter, handoff logs) goes to stderr. Order: one `plan`, then one `module` per name in `plan.modules`, in that order, then one `end`. A reader may act on each `module` line as it arrives. A stream without `end` means the runner process died: treat every missing module as `infra`.

**`plan`.** `run_id`; `alias` (= `<component>-<run_id>`, unique per run, because a duplicate alias stops a running test [verified: runner/TestRunner.java:505-521]); `component` `certify|verify`; `config_name` (template file stem under `plans/<component>/`); `plan_name`, `plan_id` (null if plan creation failed), `variant`; `suite_url`; `modules[]`; `started`.
`flags` must be printed in every report:
- `certify_as_metadata_shim`: boolean for certify, as **observed** at run time (does the AS metadata served to the suite contain `authorization_endpoint`?), null for verify.
- `verify_evidence_upload`: boolean for verify (did the harness upload Verify's `/vp-result` rendering as the screenshot?), null for certify.
- On an `exit: 2` abort where the flag could not be observed (e.g. AS metadata unreachable), the runner prints the template's expected value. Read flags as observations only when `end.exit` < 2.

**`module`.** `module`, `test_id`, `status`, `result` (suite enums, null if never reached [verified: testmodule/TestModule.java:18-35]); `outcome`; `message` (one line, ready for the TestNG message); `failed_conditions[]` and `warnings[]` (`{condition, message, requirements[]}`, in suite log order); `log_url`; `started`, `finished` (ISO-8601 UTC); `evidence[]` (paths relative to the runner `--out` dir: the module's `*.log.json`, plus any `*.verify-result.{json,png}`); `infra_reason` (non-null only for `infra`).

**Outcome mapping** (ADR-003; the runner computes it so both bridges stay thin):

| status | result | outcome | message |
|---|---|---|---|
| FINISHED | PASSED | `pass` | `""` |
| FINISHED | WARNING | `warning` | `warnings: <cond>, …` (bridge: pass, or fail under `--strict`) |
| FINISHED | REVIEW | `review` | `needs human review: evidence image uploaded by harness` (bridge: skip) |
| FINISHED | SKIPPED | `skip` | suite skip message |
| any | FAILED | `fail` | `<first failed condition>: <its message>` |
| INTERRUPTED | UNKNOWN or null (null observed on API stop: `evidence/sp2/live/infra-capture/`), or any other pair | `infra` | `INFRA: <reason>` (suite's last log message) |
| runner timeout / HTTP / handoff error | as last seen, or null | `infra` | `INFRA: <reason>` |

**Benchmark fingerprint** (ADR-004): `failed_conditions[0].condition`.

**`end`.** `exit`: `0` every module got a non-infra record; `1` at least one `infra`; `2` run aborted (plan not created, suite unreachable, observed shim flag ≠ config expectation; `error` says why, missing modules get no record). `counts` per outcome; `export` (plan HTML export zip, relative to `--out`, or null); `finished`. The process exit code equals `end.exit`. Conformance failures never change the exit code; gating is the job of `runner/gate.py`.

**Fixtures** (derived from the baseline runs by `runner/tests/make_fixtures.py`, using the runner's own record builder):
`certify-shim-on.jsonl` ← `evidence/sp0/baseline-v0-certify/`; `certify-shim-off.jsonl` ← `evidence/sp0/s04-noshim-fullplan/`; `verify-redirect-uri.jsonl` ← `evidence/sp0/baseline-v0-verify/`; `verify-x509.jsonl` ← `evidence/sp0/baseline-v0-verify-x509/`; `infra-interrupted-unknown.jsonl` ← `evidence/sp2/live/infra-capture/` (a live module stopped via `DELETE /api/runner/{id}`: INTERRUPTED, result null). Baseline runs used fixed aliases (`inji-certify` …); fixtures keep the recorded value.

**Change rule.** Consumers must ignore fields they don't know. Adding a field is v1.x (schema updated, no consumer change). Renaming, removing or changing a field's meaning is v2 and needs a maintainer decision.
