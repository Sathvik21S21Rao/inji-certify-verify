# Usage

All commands run from the repository root. Paths are relative to it.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r runner/requirements.txt       # httpx 0.26.0, pillow 10.2.0
.venv/bin/pip install -r runner/requirements-dev.txt   # + pytest, jsonschema (unit tests only)
```

Docker with Compose v2, git, openssl and curl must be installed. The default testrig driver also needs JDK 21 and Maven on `PATH` (or `source env.sh`), because it builds the patched api-test images. The first `up` clones the three upstream repos into `upstream/` (git-ignored) at the commits in `compose/.env.pinned`.

`source env.sh` puts `.venv/bin` and a JDK 21 on `PATH`. The JDK path in the file is `~/.local/jdks/jdk-21.0.12.1+1`; edit it to match your machine. `scripts/build-testrig.sh` sources it only when `~/.local/jdks` exists, and otherwise uses the `java` and `mvn` already on `PATH` (CI gets them from `actions/setup-java`).

## One command: `scripts/run-conformance.sh`

```
scripts/run-conformance.sh (--component certify|verify | --combined) [--strict] [--parallel] [--keep] [--out DIR]
```

`scripts/run-full-stack-conformance.sh` is the same script under a second name.

**Driver.** `CONFORMANCE_DRIVER` picks how each config runs:
- `testrig` (default): `scripts/build-testrig.sh` builds the patched api-test image for each component in the run (clone at the pin under `data/testrig-build/`, apply `testrig-bridge/inji-<component>.patch`, `mvn package`, `testrig-bridge/build-image.sh`). The image is tagged by the patch hash, so later runs reuse it. MinIO starts after the stacks. Each config then runs as one `docker run` of that image in conformance mode with `push-reports-to-s3=yes`; the script copies the TestNG report out and takes `results.jsonl` from `testng-report/conformance/<config>/`.
- `runner`: calls `python -m runner run` directly. No Java, no images, no MinIO. Useful for debugging a plan template.

Both drivers produce the same gate result: on the known-good run, the `strip-credential-endpoint` run and the 0.14 run, `runner diff` between the two drivers' `results.jsonl` reports no changes (`evidence/sp4/SP4.14/parity-*.md`).

| Flag | Meaning |
|---|---|
| `--component certify` | Certify only: brings up the suite and Certify, runs the Certify config, gates it. |
| `--component verify` | Verify only: brings up the suite and Verify, runs `verify-redirect-uri` then `verify-x509`, gates both. |
| `--combined` | Everything: all three stacks, all configs, plus the combined report in `<out>/combined/`. |
| `--strict` | A suite WARNING fails the gate (`STRICT_WARNING`). |
| `--parallel` | With `--combined` only: run the Certify and Verify configs at the same time. |
| `--keep` | Don't tear the stacks down at the end. |
| `--out DIR` | Output directory (default `reports/`). |

Exactly one of `--component` or `--combined` is required. Exit codes: `0` all gates green, `1` at least one gate red, `2` usage error or a gate could not evaluate (for example a missing `results.jsonl` or an invalid benchmark), `3` `env.sh up` failed, `4` (testrig driver) the TestNG report disagrees with the suite's own plan export for at least one module. `4` outranks `1` and `2`. A reconcile check that can't read its inputs counts like a gate `2`.

Which Certify config runs depends on `CONFORMANCE_CERTIFY_AS_METADATA_SHIM`: `certify-shim-off` by default (the benchmark of record), `certify-shim-on` when it is `true`. For `verify-x509`, the script exports `VERIFY_X509_CA_PEM` from `data/certs/verify-ca.pem` when it is not already set.

Output:

```
reports/run-info.txt                 mode, configs, shim, fault, driver, strict, parallel, git commit
reports/timing.tsv                   seconds per phase: build, up, minio, tests, combined, down, total
reports/minio-ls.xml                 bucket listing after the uploads (testrig driver)
reports/<config>/results.jsonl       the runner's records (see results-contract.md)
reports/<config>/stdout.jsonl        the same stream as printed on stdout (runner driver)
reports/<config>/stderr.log          runner and handoff log
reports/<config>/<module>.log.json   suite log per module, plus *.verify-result.{json,png} for Verify
reports/<config>/gate.md, gate.exit  gate table and its exit code
reports/<config>/reconcile.md, reconcile.exit  TestNG vs suite export, per module (testrig driver)
reports/<config>/testng-report/      EmailableReport output, plus conformance/<config>/ from the runner (testrig driver)
reports/<config>/testrig.log         container log (testrig driver)
reports/combined/index.html, badge.json, gate.md   (--combined)
```

Examples:

```bash
CONFORMANCE_PYTHON=.venv/bin/python scripts/run-conformance.sh --component certify
CONFORMANCE_PYTHON=.venv/bin/python scripts/run-conformance.sh --component verify --keep
CONFORMANCE_PYTHON=.venv/bin/python scripts/run-conformance.sh --combined --parallel --out /tmp/conf
```

The scripts take no lock. If several people or jobs share one Docker host, wrap the whole call, for example `flock /tmp/inji-conformance.docker.lock scripts/run-conformance.sh --combined`. Two concurrent `up`s would recreate each other's containers.

## The shim diagnostic pass

```bash
CONFORMANCE_CERTIFY_AS_METADATA_SHIM=true CONFORMANCE_PYTHON=.venv/bin/python \
  scripts/run-conformance.sh --component certify
```

This recreates `certify-tls` with `compose/tls/proxy-shim-true.conf.template`, which adds a placeholder `authorization_endpoint` to Certify's AS metadata. It then runs `plans/certify/certify-shim-on.json` and gates it against `certify-shim-on.benchmark.json`. The runner observes the flag itself: it reads the AS metadata before creating the plan, and aborts with exit 2 if the observation doesn't match the template's `expect.certify_as_metadata_shim`. The observed value is printed in every report. Results from this pass are diagnostic only: they show what Certify does after the F-CERT-1 check, and they are never the result of record.

## Fault injection and negative controls

| Variable | Values | Effect |
|---|---|---|
| `CONFORMANCE_FAULT` | `none` (default), `strip-nonce-endpoint`, `strip-credential-endpoint`, `strip-credential-configurations`, `rewrite-credential-issuer` | Mounts `compose/tls/fault-<name>.conf` into `certify-tls` (via `compose/certify-fault.yml`). That snippet rewrites Certify's issuer metadata on its way to the suite. Any name without a matching file: exit 2. |
| `CONFORMANCE_CERTIFY_RELEASE` | `1.0` (default), `0.14` | `0.14` runs Certify v0.14.0 (draft-13 OpenID4VCI) from its own upstream compose file, with the same overlay. It adds `compose/certify-014.yml`, which routes `/.well-known/oauth-authorization-server` to Certify because v0.14.0's compose nginx doesn't, and it seeds `compose/seed/certify-sdjwt-config-0.14.json`. It can't be combined with the shim (exit 2). |

Both variables need a fresh `env.sh up certify`, which `run-conformance.sh` always does. Both are recorded in `run-info.txt` and in each plan record's `environment` field.

```bash
# the benchmark of record must turn red
CONFORMANCE_FAULT=strip-credential-endpoint scripts/run-conformance.sh --component certify; echo $?   # 1
# the diagnostic pass must turn red
CONFORMANCE_FAULT=strip-nonce-endpoint CONFORMANCE_CERTIFY_AS_METADATA_SHIM=true \
  scripts/run-conformance.sh --component certify; echo $?                                             # 1
# draft-13 Certify against the 1.0 benchmark
git -C upstream/inji-certify fetch origin tag v0.14.0
CONFORMANCE_CERTIFY_RELEASE=0.14 scripts/run-conformance.sh --component certify; echo $?              # 1
```

The 0.14 control needs commit `CERTIFY_014_COMMIT` (from `compose/.env.pinned`) in `upstream/inji-certify`. `env.sh` never fetches into that clone itself; it extracts the v0.14.0 compose directory into `data/upstream-0.14/` with `git archive`. `rewrite-credential-issuer` makes `wait-ready.sh` time out on purpose, because readiness checks `credential_issuer`.

## Environment only: `scripts/env.sh`

```
scripts/env.sh up    certify|verify|all            # the suite is always included
scripts/env.sh down  certify|verify|all [--purge]  # the suite is always taken down too
scripts/env.sh compose suite|certify|verify <docker compose args…>
```

- `up` runs, in order: `fetch-upstream.sh`; create `mosip_network` if missing; create `data/certify/CERTIFY_PKCS12/`; `gen-certs.sh`; `docker compose up -d --wait` for the suite, then each component; `wait-ready.sh`; `seed-certify.sh` (unless the mode is `verify`). It prints `env.sh: ready in <n>s`.
- `down certify` (or `verify`) stops that component and the suite, and leaves the other component running. `--purge` also removes volumes and `data/` (a cold start next time); images are kept. `mosip_network` is never removed.
- `compose` passes arguments to the right compose project, for example `scripts/env.sh compose certify logs -f certify` or `scripts/env.sh compose verify ps`.
- Bad arguments or bad variable values exit 2.

Helpers:

```
scripts/wait-ready.sh [certify|verify|all] [--timeout SECONDS]   # default all, 300; exit 0 ready, 1 timeout, 2 bad args
scripts/seed-certify.sh [--api http://localhost:8091/v1/certify]  # idempotent; exits non-zero unless status is active
scripts/gen-certs.sh [--force]                                    # test certs in data/certs/; --force regenerates
scripts/fetch-upstream.sh                                         # clone missing upstream repos at the pins
```

## Runner CLI: `python -m runner`

### `run`
```
python -m runner run <template.json> --out DIR [--run-id ID] [--modules a,b,…] [--module-timeout SECONDS]
```
Runs one plan config. stdout carries JSON Lines only (everything else goes to stderr), and the same records are written to `DIR/results.jsonl`. `--run-id` defaults to `<YYYYmmddHHMMSS>-<4 hex>`; the suite alias is `<component>-<run_id>`. `--modules` runs a subset; any name not in the plan aborts with exit 2. `--module-timeout` overrides the template's `module_timeout_s` (default 180). The exit code equals `end.exit`: `0` no infrastructure problem, `1` at least one `infra` module, `2` aborted. A conformance failure never changes the exit code.

### `gate`
```
python -m runner gate <results.jsonl> <benchmark.json> [--strict]
```
Prints a Markdown table and exits `0` green, `1` red, `2` cannot evaluate (unreadable input, no plan record, invalid benchmark, or a variant key that differs from the benchmark's). Verdicts are listed in [architecture.md](architecture.md#gate-diff-and-combined-report-runnergatepy-runnercombinedpy).

### `benchmark init`
```
python -m runner benchmark init <results.jsonl> --out <benchmark.json> [--label TEXT] [--force]
```
Writes a benchmark skeleton from a clean run (it refuses a run with `infra` modules or an abort). Then fill in, by hand, `reason` for every entry, and `finding` (`F-CERT-n` / `F-VER-n`) and `ki` for each FAILED entry. An empty `reason` makes the gate exit 2. `--force` overwrites an existing file. Update a benchmark only by a reviewed edit, once a `STALE`, `REGRESSION` or `NEW_*` verdict is understood. The shim-on benchmark is diagnostic only.

### `diff`
```
python -m runner diff <A.jsonl> <B.jsonl>
```
Lists the modules whose outcome or first failing condition changed, and modules present in only one run. Exits 0, or 2 if an input can't be read.

### `reconcile`
```
python -m runner reconcile <testng-report dir> [--export <plan export zip>] [--strict]
```
Compares every `OpenIDConformanceTest` row in `<dir>/testng-results.xml`, and the EmailableReport filename counts, with the `(status, result)` the suite recorded in its plan export. By default the export is the single `<dir>/conformance/*/*.zip`. Exits `0` MATCH, `1` MISMATCH, or `2` if an input is missing or unreadable. `--strict` also accepts FAIL for a suite WARNING (the testrig's `conformance.strict=yes`). `--export` takes any plan export, for example one downloaded from the suite UI with **Download all Logs** after a manual run. How it works: [how-the-api-automation-works.md](how-the-api-automation-works.md#after-the-run-reconciliation-against-the-suite).

### `combined`
```
python -m runner combined --out DIR [--note TEXT] <run.jsonl>[=<benchmark.json>] …
```
Gates each run that has a benchmark, then writes `DIR/index.html`, `DIR/badge.json` and `DIR/gate.md`. Exits 1 if any gated run is red. The combined page doesn't apply `--strict`.

## Environment variables

Runner (read by `python -m runner run`, defaults in `runner/__main__.py` and the templates):

| Variable | Default | Used for |
|---|---|---|
| `CONFORMANCE_SERVER` | `https://localhost.emobix.co.uk:8443/` | Suite base URL |
| `CERTIFY_API` | `http://localhost:8091/v1/certify` | `pre-authorized-data`, credential-configuration seeding |
| `CERTIFY_PUBLIC_URL` | `https://localhost:9443` | Where the runner reads the AS metadata to observe the shim flag (the `certify-tls` host port) |
| `VERIFY_API` | `http://localhost:8080/v1/verify` | `v2/vp-request`, `vp-result/{txn}` |
| `CERTIFY_ISSUER_URL` | `https://certify-tls` | `config.vci.credential_issuer_url` in the Certify templates |
| `VERIFY_PUBLIC_URL` | `https://verify-tls` | The `redirect_uri:` client id in `verify-redirect-uri.json` |
| `VERIFY_X509_CA_PEM` | unset (key dropped) | `client.request_object_trust_anchor_pem` in `verify-x509.json`; the PEM text of `data/certs/verify-ca.pem` |
| `CONFORMANCE_VERIFY_EVIDENCE` | `vp-result-png` | `vp-result-png` uploads the rendered Verify result as the screenshot; `none` uploads nothing (use it only if someone uploads evidence by hand in the suite UI) |
| `CONFORMANCE_RETRY_TIMEOUT` | `360` | Retry budget, in seconds, of the vendored suite client |
| `CONFORMANCE_FAULT`, `CONFORMANCE_CERTIFY_RELEASE` | `none`, `1.0` | Copied into `plan.environment` (labels only; the effect comes from `env.sh`) |

Environment and entry script:

| Variable | Default | Used for |
|---|---|---|
| `CONFORMANCE_CERTIFY_AS_METADATA_SHIM` | `false` | `true` / `false` only, else exit 2. Selects the `certify-tls` template and the Certify config. |
| `CONFORMANCE_FAULT` | `none` | See [fault injection](#fault-injection-and-negative-controls). |
| `CONFORMANCE_CERTIFY_RELEASE` | `1.0` | See above. |
| `CONFORMANCE_PYTHON` | `python3` | Interpreter `run-conformance.sh` uses for the runner and the gate. |
| `CONFORMANCE_DRIVER` | `testrig` | `testrig` or `runner`, else exit 2. See [driver](#one-command-scriptsrun-conformancesh). |
| `CONFORMANCE_MVN_OFFLINE` | unset | `1` adds `mvn -o` to the testrig image build. |
| `CONFORMANCE_ROOT` | set by `env.sh` | Repository root; the overlays reach the repo's files through it. Don't set it yourself. |

## Plan templates (`plans/<component>/<config>.json`)

The config name is the file stem, and it appears in reports, test descriptions and benchmark keys.

| Field | Meaning |
|---|---|
| `component` | `certify` or `verify` |
| `description` | Free text; the runner appends `(run <run_id>)` and passes it to the suite |
| `plan_name` | Suite plan id, e.g. `oid4vci-1_0-issuer-test-plan` |
| `variant` | Suite variant selection (see the README table) |
| `module_timeout_s` | Per-module timeout, default 180 |
| `config` | The suite plan configuration (client keys, credential, issuer URL…). The runner sets `alias` and `description`. |
| `handoff.plugin` | `certify` or `verify` |
| `handoff.offer` | Certify: the body for `POST /pre-authorized-data` (`credential_configuration_id`, `claims`, `expires_in`, `tx_code`) |
| `handoff.vp_request` | Verify: the body for `POST /v2/vp-request` (`clientId`, `dcqlQuery`) |
| `handoff.evidence` | Verify: `vp-result-png` or `none` |
| `expect.certify_as_metadata_shim` | Certify: the shim state the config requires; a mismatch aborts the run |
| `setup.credential_configuration` | Certify: a file next to the template (`credential-config.json`), POSTed to `/credential-configurations` when `GET /credential-configurations/<id>` is not 200 |

**Placeholders**, in any string value:
- `${NAME}`: required. An unset variable aborts the run (exit 2) with `unresolved required placeholders`.
- `${NAME:-default}`: the default is used when the variable is unset or empty.
- A string that is *only* a placeholder and resolves to `""` removes its key (or list item). This is how `verify-x509.json` drops the trust anchor when `VERIFY_X509_CA_PEM` is unset.

The keys and certificates in the templates are the suite's public test material. To add a config, copy a template, change `variant` and `config`, run it once with `python -m runner run`, and then create its benchmark with `benchmark init`.

## Running pieces by hand

```bash
scripts/env.sh up verify
export VERIFY_X509_CA_PEM="$(cat data/certs/verify-ca.pem)"
.venv/bin/python -m runner run plans/verify/verify-x509.json --out out/x509
.venv/bin/python -m runner gate out/x509/results.jsonl plans/verify/verify-x509.benchmark.json
.venv/bin/python -m runner run plans/verify/verify-redirect-uri.json --out out/ru \
  --modules oid4vp-1final-verifier-happy-flow
scripts/env.sh down verify
```

## Testrig integration

The patches add `OpenIDConformanceTest` to each module's api-test. They apply to inji-certify `0d52155` and inji-verify `64b2790`.

**Apply and build.** Use a plain clone, not a git worktree: the api-test build's git-commit-id plugin fails inside a worktree. Leave the pinned clones under `upstream/` untouched.

```bash
git clone https://github.com/inji/inji-certify.git ~/src/inji-certify
git -C ~/src/inji-certify checkout --detach 0d52155ba5e4c624fa13d67a4f3d28cbb9151f8a
git -C ~/src/inji-certify apply "$PWD/testrig-bridge/inji-certify.patch"
source env.sh && (cd ~/src/inji-certify/api-test && mvn -q -DskipTests package)
testrig-bridge/run-unit-tests.sh certify ~/src/inji-certify/api-test/target/apitest-injicertify-*-jar-with-dependencies.jar
testrig-bridge/build-image.sh certify ~/src/inji-certify/api-test testrig-certify:conformance
```

Verify works the same way with `inji-verify`, `64b27903b5af09bf97c3d1a13563789c16995d6e`, `inji-verify.patch` and the `verify` argument. `run-unit-tests.sh` replays the fixtures in `runner/tests/fixtures/` through `testrig-bridge/tests/fake-runner.sh` and prints `ALL PASSED`. `build-image.sh` stages `target/` plus `testNgXmlFiles/` and the Dockerfile's other `COPY` sources, then runs `docker build`.

**Run in conformance mode** against a stack started with `scripts/env.sh up certify`:

```bash
docker run --rm --network host \
  -e MODULES=injicertify -e ENV_USER=local -e ENV_ENDPOINT=http://localhost:8091 -e ENV_TESTLEVEL=smokeAndRegression \
  -e conformance.enabled=yes -e conformance.runner.dir=/home/inji/conformance \
  -e conformance.plan.template=plans/certify/certify-shim-off.json \
  -e conformance.certify.as_metadata_shim=false -e injiCertifyBaseURL=http://localhost:8091 \
  -v "$PWD/runner:/home/inji/conformance/runner:ro" -v "$PWD/plans:/home/inji/conformance/plans:ro" \
  testrig-certify:conformance
```

For Verify, use `MODULES=injiverify`, `ENV_ENDPOINT=http://localhost:8080`, `injiVerifyBaseUrl=http://localhost:8080`, a `plans/verify/…` template and no shim key. For `verify-x509.json`, add `-e VERIFY_X509_CA_PEM="$(cat data/certs/verify-ca.pem)"`: the runner inherits the container's environment. The report lands in `/home/inji/testng-report/` in the container. Drop `--rm` and `docker cp` it out, or push it to MinIO:

```bash
docker compose -p minio --env-file compose/.env.pinned -f compose/minio.yml up -d
curl -fsS http://127.0.0.1:9000/minio/health/live
# add to the docker run above:
#   -e push-reports-to-s3=yes -e s3-host=http://localhost:9000 -e s3-user-key=minioadmin \
#   -e s3-user-secret=minioadmin -e s3-account=automation
curl --aws-sigv4 "aws:amz:us-east-1:s3" -u minioadmin:minioadmin "http://127.0.0.1:9000/automation?list-type=2"
docker compose -p minio --env-file compose/.env.pinned -f compose/minio.yml down
```

`S3Adapter` creates the bucket itself. MinIO's storage is tmpfs, so the objects disappear when it stops. The image has no `mc`, hence the `curl --aws-sigv4` listing.

**Keys.** These go in the `conformance.*` section of `injiCertify.properties` / `injiVerify.properties`. Like every key there, each can be overridden by an environment variable of exactly the same name, dots included.

| Key | Default | Meaning |
|---|---|---|
| `conformance.enabled` | `no` | `yes`: skip the platform setup and run only `testNgXmlFiles/*ConformanceSuite.xml`. `no`: the default run, unchanged. |
| `conformance.runner.dir` | empty | Working directory of the runner; holds `runner/` and `plans/`. Templates resolve relative to it. |
| `conformance.runner.command` | `python3 -m runner run` | Split on whitespace (no quoting); the bridge appends `<template> --out <dir>`. Use a wrapper script if you need quoting. |
| `conformance.plan.template` | Certify: empty, then chosen by the shim key (`plans/certify/certify-shim-{off,on}.json`). Verify: `plans/verify/verify-redirect-uri.json` | Plan template, relative to `conformance.runner.dir` |
| `conformance.runner.timeout` | `3600` | Seconds before the runner is killed; modules without a record become `INFRA:` failures |
| `conformance.strict` | `no` | `yes`: a `warning` outcome fails |
| `conformance.certify.as_metadata_shim` | `false` | Certify only. Passed to the runner as `CONFORMANCE_CERTIFY_AS_METADATA_SHIM`; picks the default template. It must match how `certify-tls` was started. |

The bridge also passes `CERTIFY_API=<injiCertifyBaseURL>/v1/certify` (Certify) or `VERIFY_API=<injiVerifyBaseUrl>/v1/verify` (Verify) to the runner, so it targets the same host as the module's existing tests. Existing keys used unchanged: `injiCertifyBaseURL`, `injiVerifyBaseUrl`, `push-reports-to-s3`, `s3-host`, `s3-user-key`, `s3-user-secret`, `s3-account`, `s3-region`. Known issues go in `src/main/resources/testCaseSkippedList.txt` as `<id>------OIDF_<component>_<module>`. The Certify patch adds `F-CERT-5------OIDF_certify_oid4vci-1_0-issuer-metadata-test`.

## CI

`.github/workflows/full-stack-conformance.yml` runs on manual dispatch and on tags `v*` / `release-*`. Dispatch inputs: `strict` (boolean), `parallel` (boolean), `fault` (`none`, `strip-nonce-endpoint`, `strip-credential-endpoint`), `certify_shim` (`false` / `true`). Each matrix job (`certify`, `verify`, `combined`) uploads `reports/` as the artifact `conformance-<target>` and writes the gate tables, the timing and a diff against the last successful run to the job summary.

## Unit tests

```bash
.venv/bin/python -m pytest -q runner/tests
```

They cover the template resolver, record mapping, handoff plugins, the evidence uploader, the run loop against a fake suite, and every gate verdict. They need no Docker. `runner/tests/make_fixtures.py` regenerates the JSONL fixtures from recorded suite logs.
