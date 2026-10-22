# Results contract (JSON Lines)

The runner and its consumers talk through one stream. The consumers are the TestNG bridge in each api-test, the gate, the diff and the combined report. This page explains the stream. The normative files are `runner/schema/results.schema.json` (JSON Schema 2020-12) and `runner/schema/CONTRACT.md`. The fixtures in `runner/tests/fixtures/*.jsonl` are real runs converted by the runner's own record builder.

Current version: **1.1**. 1.0 was frozen on 20 Oct 2026; 1.1 (21 Oct 2026) adds the optional `plan.environment` field. Every 1.0 stream is also a valid 1.1 stream.

## Stream rules

- UTF-8, one JSON object per line, flushed after each line, on the runner's **stdout**. Everything else, such as suite client output and handoff logs, goes to stderr. The same lines are written to `<out>/results.jsonl`.
- Order: exactly one `plan`, then one `module` per name in `plan.modules`, in that order, then one `end`.
- A reader may act on each `module` line as it arrives. The bridge does this: it yields one TestNG test per line.
- **A stream without `end` means the runner died.** Treat every module in `plan.modules` that has no record as `infra`.
- Consumers must ignore fields they don't know.

## `plan` record

| Field | Type | Meaning |
|---|---|---|
| `type` | `"plan"` | |
| `schema_version` | `"1.0"` or `"1.1"` | |
| `run_id` | string | Unique per run |
| `alias` | string | `<component>-<run_id>`. It must be unique, because a suite test with a duplicate alias stops the running one. |
| `component` | `certify` or `verify` | |
| `config_name` | string | Template file stem, e.g. `certify-shim-off` |
| `plan_name`, `plan_id` | string, string or null | Suite plan; `plan_id` is null if plan creation failed |
| `variant` | object | Suite variant selection |
| `environment` | object, optional (1.1) | `{fault, certify_release}` from `CONFORMANCE_FAULT` (default `none`) and `CONFORMANCE_CERTIFY_RELEASE` (default `1.0`). The gate prints it but doesn't key benchmarks on it. |
| `flags` | object | Must be printed in every report; see below |
| `suite_url` | string | |
| `modules` | string[] | Module names, in run order |
| `started` | ISO-8601 UTC | |

`flags`:
- `certify_as_metadata_shim`: for Certify, a boolean **observed** at run time (does the AS metadata served to the suite contain `authorization_endpoint`?); null for Verify.
- `verify_evidence_upload`: for Verify, a boolean (does the harness upload Verify's `/vp-result` rendering as the screenshot?); null for Certify.
- When a run aborts with `exit: 2` before the flag could be observed (for example, the AS metadata was unreachable), the runner prints the template's expected value instead. Read flags as observations only when `end.exit` < 2. The bridge prints `not observed` in that case.

## `module` record

| Field | Meaning |
|---|---|
| `module`, `test_id` | Suite module name and test id |
| `status`, `result` | The suite's own enums (`FINISHED`/`INTERRUPTED`/…, `PASSED`/`FAILED`/`WARNING`/`REVIEW`/`SKIPPED`/`UNKNOWN`), or null if never reached |
| `outcome` | `pass`, `warning`, `review`, `skip`, `fail` or `infra` (mapping below) |
| `message` | One line, ready to use as the TestNG message |
| `failed_conditions[]`, `warnings[]` | `{condition, message, requirements[]}`, in suite log order. `requirements` holds the suite's spec references, e.g. `OID4VCI-1FINAL-12.2.3`. |
| `log_url` | The module's log page in the suite |
| `started`, `finished` | ISO-8601 UTC |
| `evidence[]` | Paths relative to `--out`: `<module>.log.json`, plus `<module>.verify-result.{json,png}` when evidence was uploaded |
| `infra_reason` | Non-null only when `outcome` is `infra` |

## Outcome mapping

The runner computes the outcome, so both bridges stay thin ([ADR-003](design-decisions.md#adr-003-mapping-suite-outcomes-to-testng-results)).

| status | result | outcome | message | TestNG (bridge) |
|---|---|---|---|---|
| FINISHED | PASSED | `pass` | `""` | pass |
| FINISHED | WARNING | `warning` | `warnings: <cond>, …` | pass; fail if `conformance.strict=yes` |
| FINISHED | REVIEW | `review` | `needs human review: evidence image uploaded by harness` | skip |
| FINISHED | SKIPPED | `skip` | the suite's skip message | skip |
| any | FAILED | `fail` | `<first failed condition>: <its message>` | fail with log URL, or KI skip if listed in `testCaseSkippedList.txt` |
| INTERRUPTED | UNKNOWN or null, or any other pair | `infra` | `INFRA: <reason>` (the suite's last log message) | fail, never KI |
| (runner timeout, HTTP or handoff error) | as last seen, or null | `infra` | `INFRA: <reason>` | fail, never KI |

`INTERRUPTED` + `FAILED` is ordinary non-conformance: the module stopped at a failed condition. Only an interruption without a verdict counts as infrastructure. A test stopped through the API reports `result: null`, which also maps to `infra`.

**Benchmark fingerprint.** The gate takes `failed_conditions[0].condition` of a `fail` record as its first failing condition, and the sorted set of `warnings[].condition` as its warning set.

## `end` record

| Field | Meaning |
|---|---|
| `exit` | `0` every module got a non-infra record; `1` at least one `infra`; `2` the run aborted (plan not created, suite unreachable, observed shim flag ≠ the template's expectation, unknown `--modules`, unresolved placeholder). Missing modules get no record on an abort. |
| `counts` | `{pass, warning, review, skip, fail, infra}` |
| `error` | Why the run aborted, or null |
| `export` | File name of the suite's plan HTML export (zip) in `--out`, or null |
| `finished` | ISO-8601 UTC |

The process exit code equals `end.exit`. Conformance failures never change it: the gate decides whether a build is red.

## Example (shortened)

```json
{"type":"plan","schema_version":"1.1","run_id":"20261021184445-8ebf","alias":"certify-20261021184445-8ebf","component":"certify","config_name":"certify-shim-off","plan_name":"oid4vci-1_0-issuer-test-plan","plan_id":"…","variant":{"vci_grant_type":"pre_authorization_code","…":"…"},"environment":{"fault":"none","certify_release":"1.0"},"flags":{"certify_as_metadata_shim":false,"verify_evidence_upload":null},"suite_url":"https://localhost.emobix.co.uk:8443/","modules":["oid4vci-1_0-issuer-metadata-test","…"],"started":"…"}
{"type":"module","module":"oid4vci-1_0-issuer-metadata-test","test_id":"…","status":"FINISHED","result":"FAILED","outcome":"fail","message":"VCICredentialIssuerMetadataValidation: Found invalid entries in OID4VCI Credential Issuer metadata input","failed_conditions":[{"condition":"VCICredentialIssuerMetadataValidation","message":"Found invalid entries in OID4VCI Credential Issuer metadata input","requirements":["OID4VCI-1FINAL-12.2.3"]}],"warnings":[{"condition":"CheckForUnexpectedParametersInCredentialIssuerMetadata","message":"…","requirements":["OID4VCI-1FINAL-12.2.3"]}],"log_url":"…","started":"…","finished":"…","evidence":["oid4vci-1_0-issuer-metadata-test.log.json"],"infra_reason":null}
{"type":"end","exit":0,"counts":{"pass":0,"warning":0,"review":0,"skip":0,"fail":14,"infra":0},"error":null,"export":"oid4vci-1_0-issuer-test-plan-…-20-Oct-2026.zip","finished":"…"}
```

## Change rule

Adding a field is a 1.x change: update the schema; no consumer has to change. Renaming or removing a field, or changing what it means, is a 2.0 change, and every consumer must be updated together. Validate a stream with `jsonschema` against `runner/schema/results.schema.json`. The live runs behind the benchmarks validated with no errors: 168 lines across 12 runs (`evidence/sp2/live/schema-validation.txt`).
