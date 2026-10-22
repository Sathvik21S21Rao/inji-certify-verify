# How the API automation works

This page follows one plan through the runner (`python -m runner run`), from template to `results.jsonl`. It covers the suite REST calls, the long-poll, the WAITING loop that the handoff plugins hook into, timeouts and infrastructure errors, the export, and the reconciliation check that runs afterwards.

The handoff plugins themselves are in [handoff.md](handoff.md). The record format is in [results-contract.md](results-contract.md).

Suite paths are relative to `upstream/conformance-suite/src/main/java/net/openid/conformance/` at tag `release-v5.3.3`. `scripts/fetch-upstream.sh` clones it there.

## The suite client
The runner doesn't write its own HTTP client for the suite. It vendors the suite's own `scripts/conformance.py` (MIT), unmodified, as `runner/_vendor/conformance.py`; the sha256 is in `runner/_vendor/README.md`. `runner/suite.py` is a thin async wrapper over it, about 70 lines.

The suite's `run-test-plan.py` was not used. It handles WAITING with hard-coded logic per test family, and it can't be imported, so there would be nowhere to attach the handoff plugins (`runner/_vendor/README.md`).

| Step | Wrapper (`runner/suite.py`) | Vendored call | Suite REST call |
|---|---|---|---|
| create plan | `create_plan` | `create_test_plan` | `POST /api/plan?planName=…&variant=…`, body = config JSON, expects 201 |
| create module | `create_module` | `create_test_from_plan` | `POST /api/runner?test=<module>&plan=<planId>`, expects 201 |
| start | `start` | `start_test` | `POST /api/runner/{id}` |
| wait | `wait` | `wait_for_state` | `GET /api/runner/{id}/wait-state?states=…&timeoutMs=…` (long-poll, below) |
| exposed values | `status` | — | `GET /api/runner/{id}`; 404 once the test has left the runner, read as `{}` |
| verdict | `info` | `get_module_info` | `GET /api/info/{id}` |
| log | `log` | `get_test_log` | `GET /api/log/{id}` |
| screenshot placeholders | `images`, `upload_image` | — | `GET /api/log/{id}/images`, `POST /api/log/{id}/images/{placeholder}` |
| stop (on infra) | `stop` | — | `DELETE /api/runner/{id}` |
| export | `export_html` | `exporthtml` | `GET /api/plan/exporthtml/{planId}`, saved as a zip |

The suite-side endpoints are defined in `runner/TestRunner.java` (the wait-state mapping is at line 633), and `GET /api/runner/{id}` returns 404 for a finished test (`TestRunner.getTestStatus`).

## Plan lifecycle (`runner/run.py`, `run_plan`)
1. **Load the template.** `runner/templates.py` substitutes `${NAME}` and `${NAME:-default}` in string values of the parsed JSON. An unresolved required name aborts with exit 2, still emitting `plan` and `end` records.
2. **Prepare the environment.** `runner/setup.py` `prepare`, called at `run.py:101`:
   - Certify: read `/.well-known/oauth-authorization-server` and check that the AS-metadata shim state matches the template's `expect` (a mismatch aborts), then seed the SD-JWT credential configuration idempotently (GET, then POST).
   - Verify: validate the evidence mode.
   - The observed values become the record's `flags`.
3. **Create the plan.** The alias is `<component>-<run_id>`, and `run_id` is unique per run (`run.py`, `alias = …`). A new test with the same alias stops a running one (`runner/TestRunner.java:505-521`), so parallel runs never share an alias. The resolved config is saved as `plan-config.json`.
4. **Select modules.** `--modules` keeps the plan order. A name that isn't in the plan aborts (`run.py:114`).
5. **Run each module in sequence.** The `module` record is emitted as soon as each module finishes, so the testrig bridge can stream results.
6. **Export.** The plan export zip is saved next to the results (`run.py:126`) and named in the `end` record. If the export fails, it is logged and `export` is `null`.
7. **End record.** Exit 0 means every module reached a suite verdict. Exit 1 means at least one `infra` record. Exit 2 means the plan was aborted before it ran (`records.end_record`).

## Module loop and long-polling (`run.py:25-66`)
```
create module ─► wait {CONFIGURED, WAITING, FINISHED}
   CONFIGURED ─► start ─► wait {WAITING, FINISHED}
   while WAITING:
       read exposed values (GET /api/runner/{id})
       evidence uploader (Verify only) ─► handoff plugin
       nothing done? sleep ≤ 2 s
       wait {WAITING, FINISHED}      ← returns once the suite has processed the action and waits again
   FINISHED/INTERRUPTED ─► GET info + log ─► module record
```
- **Long-poll.** `wait_for_state` calls `/api/runner/{id}/wait-state` with each call capped at 30 s, and repeats while the server answers `{"timeout": true}`. `INTERRUPTED` is always added to the wanted states, so a stopped test releases the poll at once (`runner/_vendor/conformance.py:299-402`).
  - If the endpoint returns 404, the client reads `/api/info/{id}`. A persisted `FINISHED` or `INTERRUPTED` is returned. A non-terminal persisted state means the server restarted, and the client raises `ServerUnavailableError` (same lines).
  - On the server, `TestStatusWaiterService` resolves the request as soon as the status matches (`runner/TestStatusWaiterService.java`).
- **Why the loop waits again after acting.** A handoff call makes the suite run the next step, so it goes RUNNING and then WAITING again or FINISHED. The handler sets RUNNING before the HTTP call returns (comment at `run.py:49`). So the next `wait` only returns once the suite is ready for the next action. Some modules wait more than once: issuer modules can ask for a transaction code after the offer, and verifier modules wait for the screenshot. The plugins keep per-module state in `ModuleCtx.state` for that (`runner/handoff.py`).
- **Modules that need no action** (issuer metadata tests) sit in WAITING with nothing exposed. The loop sleeps up to 2 s and re-polls (`run.py:48`).

## Timeouts and infrastructure errors
- Each module has one budget for all of its waits: `--module-timeout`, else the template's `module_timeout_s`, else 180 s (`run.py:118`).
- On a runner timeout or any exception, the runner stops the test (`DELETE /api/runner/{id}`) and emits an `infra` record naming the state it was stuck in (`run.py:54-66`). An `infra` record is never confused with a conformance failure.
- Mapping suite outcomes is ADR-003 (`runner/records.py` `outcome_for`). `FAILED` is `fail` whether the module FINISHED or was INTERRUPTED: the suite stops a module on a `callAndStopOnFailure`, which is real non-conformance. `INTERRUPTED` with result `UNKNOWN` or `null` (API stop, alias clash, idle timeout) is `infra`. See [design-decisions.md](design-decisions.md).

## After the run: reconciliation against the suite
`results.jsonl` is the harness's own output, so it can't prove itself right. After each testrig run, `scripts/run-conformance.sh` calls `python -m runner reconcile <cfg>/testng-report` (`runner/reconcile.py`). It compares two independent records module by module:
- **The TestNG side.** `testng-results.xml` rows produced by `OpenIDConformanceTest`, named by the `testCaseName` in each row's first parameter. The XML attribute `test-instance-name` repeats the last name on every row, so it isn't used. The EmailableReport filename counts (`T-…_P-…_S-…_F-…_I-…_KI-…`) are also checked.
- **The suite side.** `testInfo.status` and `testInfo.result` of every `test-log-<module>-<id>.json` inside the plan export zip, which the suite signs (`.sig` files next to each entry).

The suite pair is mapped with the same ADR-003 function, and the allowed TestNG statuses are:

| Suite outcome | Allowed TestNG status |
|---|---|
| pass | PASS |
| warning | PASS (or FAIL under `conformance.strict`) |
| review, skip | SKIP |
| fail | FAIL, or SKIP with the known-issue message |
| infra | FAIL with an `INFRA:` message |

A module that appears on only one side counts as a mismatch. The only exception is an `INFRA:` row for a module the suite never recorded.

Any mismatch makes the whole run exit **4**. A missing XML or zip exits 2. The output is in `<cfg>/reconcile.md` and in the CI job summary.

Evidence:
- MATCH on all 34 modules of a live combined run: `evidence/sp5/SP5.2/live/*/reconcile.md`.
- A single flipped TestNG row and a doctored report filename both give exit 1: `evidence/sp5/SP5.2/doctored/`.
