# Inji conformance harness

[![Certify ↔ Verify OpenID 1.0 conformance](../../raw/badges/badge.svg)](../../actions/workflows/full-stack-conformance.yml)

<sub>The badge is the combined gate of the latest record run in CI (default branch or tag, no fault, shim off). It is pushed to the `badges` branch; the relative link works on GitHub for anyone who can see the repository.</sub>

An automated OpenID conformance harness for **Inji Certify** (OpenID4VCI issuer) and **Inji Verify** (OpenID4VP verifier). It runs the OpenID Foundation (OIDF) conformance suite against both components unattended, reports each suite module as a TestNG test inside the MOSIP testrig they already use, and gates the build against a recorded benchmark, so CI turns red only when something regresses.

![Architecture](docs/architecture.svg)

What it does, end to end:

1. Brings up Inji Certify, Inji Verify and the OIDF conformance suite with Docker Compose. It reuses the upstream compose files unchanged and adds overlays, with every image pinned by digest.
2. Creates a suite test plan, then runs every module in it. When the suite waits for the component under test, a **handoff plugin** drives Certify or Verify: it creates a credential offer through Certify's `POST /pre-authorized-data`, or an authorization request through Verify's `POST /v1/verify/v2/vp-request`.
3. Streams one JSON Lines record per module (`results.jsonl`, a versioned contract).
4. In the testrig, a new `OpenIDConformanceTest` class turns those records into TestNG results. The existing `EmailableReport` writes the report and the existing `S3Adapter` uploads it to MinIO. Known findings use the testrig's existing known-issue (KI) mechanism.
5. Compares the run with a per-module benchmark (expected outcome, first failing condition, expected warnings) and exits non-zero on a regression, a new failure, a stale entry or an infrastructure fault.
6. Checks the TestNG report module by module against the suite's own plan export, and exits 4 if they disagree ([how it works](docs/how-the-api-automation-works.md#after-the-run-reconciliation-against-the-suite)).

## Quick start

Requirements: Linux with Docker Engine, or macOS / Windows (WSL2) with Docker Desktop and bash 4+ (`brew install bash` on macOS); Docker with Compose v2 (tested with Compose v5.0.0 on Engine 29.1.3), git, openssl, curl, Python 3.12, and JDK 21 with Maven (the default driver builds the patched testrig images; skip both with `CONFORMANCE_DRIVER=runner`). The three stacks together use about 1.9 GiB more host memory than idle (`evidence/sp1/SP1.4/memory.md`), so leave at least 3 GiB free. The first run clones the pinned upstream repos into `upstream/` and pulls the images.

```bash
python3 -m venv .venv && .venv/bin/pip install -r runner/requirements.txt
CONFORMANCE_PYTHON=.venv/bin/python scripts/run-conformance.sh --combined
```

This builds the patched Certify and Verify testrig images (about two minutes each the first time, cached by patch hash after that; `evidence/sp4/SP4.13/build-durations.txt`), brings up all three stacks and MinIO, and runs the three record configs (`certify-shim-off`, `verify-redirect-uri`, `verify-x509`) through `OpenIDConformanceTest` in the testrig. It writes the TestNG reports, the per-config gate results and a combined HTML report and badge under `reports/`, uploads the reports to MinIO, then tears everything down. Exit code 0 means every gate is green and every TestNG report matches the suite's own record (exit 4 means it doesn't). Run one component with `--component certify` or `--component verify`, chosen configs with `--config verify-x509` (comma-separated), and a few modules of one config with `--config NAME --modules a,b`. To test a new Certify or Verify release, set `CERTIFY_IMAGE` or `VERIFY_SERVICE_IMAGE` (the same inputs exist on the GitHub workflow). To test an Inji branch or PR, also set `INJI_CERTIFY_REF` or `INJI_VERIFY_REF`; Inji PR CI can call the workflow as a reusable workflow ([docs/usage.md](docs/usage.md#calling-it-from-inji-pr-ci-workflow_call)). `scripts/run-full-stack-conformance.sh` is an alias with the same flags.

The suite UI is at <https://localhost.emobix.co.uk:8443> while the stacks are up (`--keep` leaves them running). That hostname resolves to 127.0.0.1 in public DNS.

To see the results inside the MOSIP testrig report as well, apply the patches in `testrig-bridge/` and run the api-test image in conformance mode. See [docs/usage.md](docs/usage.md#testrig-integration).

## Supported plans and variants

The harness targets the **non-HAIP** OpenID 1.0 plans at suite tag `release-v5.3.3`. The suite itself labels both plans "alpha tests (not part of certification program)". The HAIP plans, which are the certification plans, are out of scope today: see [docs/self-certification.md](docs/self-certification.md).

| Config (`plans/…`) | Plan | Variant | Modules | Role |
|---|---|---|---|---|
| `certify/certify-shim-off.json` | `oid4vci-1_0-issuer-test-plan` | `vci`, `sd_jwt_vc`, `issuer_initiated`, `pre_authorization_code`, `private_key_jwt`, `dpop`, `simple`, `unsigned`, `plain` | 14 | **Benchmark of record** for Certify |
| `certify/certify-shim-on.json` | same | same | 14 | Diagnostic pass only (AS-metadata shim on, see below) |
| `verify/verify-redirect-uri.json` | `oid4vp-1final-verifier-test-plan` | `plain_vp`, `sd_jwt_vc`, `redirect_uri`, `url_query`, `direct_post` | 9 | Benchmark of record for Verify |
| `verify/verify-x509.json` | same | `plain_vp`, `sd_jwt_vc`, `x509_san_dns`, `request_uri_signed`, `direct_post` | 11 | Benchmark of record for Verify (signed requests) |

Why these variants: pre-authorized code is the only grant the compose stack can complete without a browser login, since it has no separate authorization server. Neither plan tests `ldp_vc` (Certify's default credential format), so the harness seeds an SD-JWT credential configuration into Certify. Verify is tested in both of its client-ID modes, because each mode surfaces different findings. Details: [docs/design-decisions.md](docs/design-decisions.md#adr-001-target-plans-and-variants).

**The AS-metadata shim.** The suite requires `authorization_endpoint` in the authorization-server metadata before it runs any issuance module, and Certify does not publish one (finding F-CERT-1). With the shim off, 12 of the 14 issuer modules stop at that check. The harness can inject a placeholder value through its TLS proxy (`CONFORMANCE_CERTIFY_AS_METADATA_SHIM=true`) to observe the rest of the flow. That pass is labelled diagnostic, every report states the flag value, and the benchmark of record runs with the shim **off**.

**Verifier happy paths end in REVIEW, not PASSED.** Positive OID4VP verifier modules wait for screenshot evidence. The harness uploads a PNG rendering of Verify's own `GET /v1/verify/vp-result/{txn}` response, so those modules end in `REVIEW` and show as skipped ("needs human review") in TestNG. Turn this off with `CONFORMANCE_VERIFY_EVIDENCE=none`.

## Results summary

Every run of the harness against Inji Certify 1.0.x and Inji Verify 1.0.x reproduces the same per-module outcomes and first failing conditions. No module changed between three repeated runs of each config (`evidence/sp2/live/stability.md`).

| Config | Pass | Skip | Fail | Root cause of the failures |
|---|---|---|---|---|
| certify-shim-off (record) | 0 | 0 | 14 | 12 × F-CERT-1 (`CheckServerConfiguration`), 2 × F-CERT-5 (metadata) |
| certify-shim-on (diagnostic) | 3 | 2 | 9 | F-CERT-2, F-CERT-3, F-CERT-4, F-CERT-5 |
| verify-redirect-uri | 0 | 0 | 9 | 9 × F-VER-1 (`VP1FinalValidateVpFormatsSupportedInClientMetadata`) |
| verify-x509 | 0 | 1 | 10 | 10 × F-VER-5 (`ValidateRequestObjectSignatureAgainstX5cHeader`) |

The same counts appear in the testrig report filenames. For example, `…certify-shim-off…full-report_T-14_P-0_S-0_F-13_I-0_KI-1.html` has one failure moved to KI by the existing skip list (`evidence/sp3/SP3.4/counts-check.md`, which checks all four reports against the JSONL).

**Findings** (full detail and evidence in [docs/findings.md](docs/findings.md)):

| ID | Component | Summary |
|---|---|---|
| F-CERT-1 | Certify | AS metadata lacks `authorization_endpoint` while advertising the `authorization_code` grant |
| F-CERT-2 | Certify | Credential endpoint rejects unknown request fields with 400 "Unrecognized field" |
| F-CERT-3 | Certify | Token endpoint ignores client authentication on the pre-authorized grant, then rejects proof `iss` = client_id |
| F-CERT-4 | Certify | Unknown `credential_configuration_id` returns `invalid_credential_request`, not `unknown_credential_configuration` |
| F-CERT-5 | Certify | Issuer metadata emits `null` optional display fields; `Accept: application/jwt` gets an empty 200 without `Content-Type` |
| F-VER-1 | Verify | `url_query` requests carry no `client_metadata` / `vp_formats_supported` |
| F-VER-2 | Verify | KB-JWT `aud` equal to an `x509_san_dns:` client_id rejected as an invalid URI |
| F-VER-3 | Verify | Accepts a credential whose x5c chains to no configured trust anchor |
| F-VER-4 | Verify | Some negative cases are rejected only in `/vp-result`, after `direct_post` returns 200 (permitted; informational) |
| F-VER-5 | OIDF suite / Verify | Request objects are EdDSA-only; the suite's x5c check cannot verify EdDSA (suite limitation); Verify needs ES256 for HAIP |

**The gate goes red when it should.** A gate that never turns red proves nothing, so the harness ships fault injections. Removing `credential_endpoint` from Certify's issuer metadata turns the record gate red (`NEW_FAILURE` on `oid4vci-1_0-issuer-metadata-test`). Removing `nonce_endpoint` turns the diagnostic pass red (`fail-invalid-nonce` PASSED → FAILED). Running Certify v0.14.0, the draft-13 release, against the 1.0 benchmark turns the record gate red through a new suite warning. See [docs/known-limitations.md](docs/known-limitations.md) for what the record pass cannot see while F-CERT-1 stands.

## Deviations from the brief

| The brief says | The harness does | Why |
|---|---|---|
| Java 11 | Java 21 | Both `api-test` modules at the pinned commits build with Java 21, and their testrig base image is `mosipid/openjdk-21-jre`. |
| `OpenIDConformanceTest` in the testrigs "in `mosip-functional-tests`" | One class in each of `inji-certify/api-test` and `inji-verify/api-test` | The Inji testrigs live in the module repos; `mosip-functional-tests` provides only the shared `apitest-commons` library. ([ADR-005](docs/design-decisions.md#adr-005-module-local-bridge-selected-by-conformanceenabled)) |
| Suite containers `server, mongodb, httpd` | `server`, `mongodb`, `nginx` | That is what the suite's own `docker-compose-prebuilt.yml` ships at the pinned tag. |
| "Correct variants for 1.0" | Non-HAIP 1.0 plans; HAIP gaps reported as findings | Certify and Verify 1.0.x lack the features HAIP requires, so the HAIP plans would fail at setup. ([ADR-001](docs/design-decisions.md#adr-001-target-plans-and-variants)) |
| `automationtests` bucket | Bucket set through the existing `s3-account` key (default `automation`) | The name `automationtests` appears nowhere in the testrig code; any bucket works through the existing key. |
| Python runner called from Java | `python3`, `python3-httpx` and `python3-pil` added to the testrig image (+20.2 MB, `evidence/sp3/SP3.1/image-size.log`) | The testrig image has no Python. Adding it costs less than giving a test pod a Docker socket. ([ADR-002](docs/design-decisions.md#adr-002-how-the-runner-subprocess-runs-inside-the-testrig)) |
| Run against Certify | Certify's AS-metadata check is shimmed in a separate, labelled diagnostic pass | Without it, 12 of 14 issuer modules stop at F-CERT-1 and say nothing about issuance. The benchmark of record runs unshimmed. |
| Tests against the pinned source commits | Tests the published images, pinned by digest | The images were built a few commits behind the source pins (Certify `bbd913e`, Verify `5f44a36`), with no `.java` change in either gap. ([ADR-006](docs/design-decisions.md#adr-006-pin-every-image-by-digest)) |
| Report storage in MinIO | MinIO from `cgr.dev/chainguard/minio`, pinned by digest | Docker Hub and Quay refuse anonymous pulls of the official MinIO image. |

Turning conformance off is one line (`conformance.enabled = no`, the default), and the default testrig run is unchanged. The Verify default suite gives the same 279 tests and the same counts before and after the patch (`evidence/sp3/SP3.4/default-suite-compare.md`).

## Repository layout

```
compose/          overlays on the upstream compose files, TLS proxy templates, seeds, .env.pinned (all pins)
runner/           Python runner: suite client, handoff plugins, JSONL emitter, gate, diff, combined report
  schema/         results.schema.json + CONTRACT.md (the JSONL contract)
  _vendor/        the OIDF suite's conformance.py client (MIT), unmodified
plans/            plan templates per component, credential config, benchmark files
testrig-bridge/   patches for inji-certify/api-test and inji-verify/api-test, unit test, image build script
scripts/          env.sh (up/down), wait-ready, seed, cert generation, run-conformance.sh
.github/workflows full-stack-conformance.yml
docs/             the documentation below
evidence/         curated run logs and reports behind every number in these docs
env.sh            JDK 21 + venv on PATH for Maven and Python commands
```

## Documentation

- [Architecture](docs/architecture.md): components, data flow and the network layout.
- [Test data](docs/test-data.md): plan configs, credential, test keys and certificates, service credentials.
- [Test cases and results](docs/test-cases-and-results.md): every test case with its expected and observed result and evidence.
- [How the API automation works](docs/how-the-api-automation-works.md): plan lifecycle, suite REST calls, long-polling, and the reconciliation check.
- [Handoff](docs/handoff.md): how Certify and Verify are driven while the suite waits.
- [Usage](docs/usage.md): every command, flag, environment variable, testrig key and template placeholder.
- [Results contract](docs/results-contract.md): the JSON Lines format between the runner, the bridge and the gate.
- [Design decisions](docs/design-decisions.md): ADR-001 to ADR-006.
- [Findings](docs/findings.md): every non-passing module, with evidence and a suggested owner.
- [Self-certification](docs/self-certification.md): why results are not certifiable today, and the gap list.
- [Troubleshooting](docs/troubleshooting.md) and [known limitations](docs/known-limitations.md).
- [Evidence index](evidence/README.md).

## Pinned upstream

inji-certify `release-1.0.x` @ `0d52155`, inji-verify `release-1.0.x` @ `64b2790`, apitest-commons 1.6.0 (Certify) and 1.5.0 (Verify, unchanged), OIDF conformance suite `release-v5.3.3` @ `7d420f716`. Every image digest is in `compose/.env.pinned`.

## Licence notes

`runner/_vendor/conformance.py` is the OIDF conformance suite's client, MIT-licensed. Its licence is kept in `runner/_vendor/LICENSE.txt`.
