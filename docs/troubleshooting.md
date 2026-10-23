# Troubleshooting

Each entry is a failure seen while building or running the harness, its cause, and the fix. Start with the stderr log of the step that failed: `reports/<config>/stderr.log` for the runner, `scripts/env.sh compose <project> logs <service>` for containers, and `docker logs` for the testrig.

## Bringing the stack up

**`fetch-upstream: upstream/<repo> is at <sha>, pin is <sha> (not touching it)`**
An existing clone under `upstream/` is at a different commit. The script never moves a clone. Check it out at the pin from `compose/.env.pinned` yourself, or delete it so it is re-cloned.

**`wait-ready: TIMEOUT after 300s; failing: <check>`**
The failing check names the hop:
- `suite-api`: the suite isn't serving `https://localhost.emobix.co.uk:8443`. See [Suite hostname](#suite-hostname-doesnt-resolve).
- `certify-host`: Certify is still starting (its health check has a 120 s start period) or has crashed. Run `scripts/env.sh compose certify logs certify`.
- `certify-from-suite`: the suite can't reach `https://certify-tls`, or `credential_issuer` isn't `https://certify-tls`. With `CONFORMANCE_FAULT=rewrite-credential-issuer`, this check times out on purpose.
- `certify-as-from-suite`: the AS metadata isn't routed. This was seen with Certify v0.14.0, whose compose nginx doesn't proxy `/.well-known/oauth-authorization-server`; `CONFORMANCE_CERTIFY_RELEASE=0.14` adds the route.
- `verify-host` / `verify-from-suite`: `verify-service` isn't healthy, or isn't on `mosip_network`.

**Port 5432 already in use**
Verify's upstream compose publishes Postgres on host port 5432, which clashes with a local Postgres. The overlay removes that mapping (`ports: !reset []`), so this happens only if you run the upstream compose file without `compose/verify.yml`.

**`network mosip_network declared as external, but could not be found`**
You ran `docker compose` directly. `scripts/env.sh up` creates the network; otherwise run `docker network create mosip_network`.

**`mimoto-service` fails on `certs/oidckeystore.p12`**
That service needs eSignet onboarding and isn't used by the harness. The overlay moves it to the `inji-wallet` profile; don't enable that profile.

**Images fail to pull**
Every image is pinned by digest. If a registry has dropped a digest, `docker pull` fails for that reference; update it in `compose/.env.pinned` deliberately and re-baseline. Anonymous pulls of `minio/minio` (Docker Hub) and `quay.io/minio/minio` are refused, which is why MinIO comes from `cgr.dev/chainguard/minio`.

**`env.sh down --purge` leaves `data/`**
Some files under `data/` are created by containers as another user. `env.sh` removes them through a throwaway nginx container; if that fails, remove `data/` with `sudo`.

**`needs bash 4+, this is 3.2…`**
macOS ships bash 3.2. Run `brew install bash` and make sure Homebrew's bin directory comes first on `PATH`; the scripts start with `#!/usr/bin/env bash`.

**Testrig container can't reach Certify, Verify or MinIO (Docker Desktop)**
Docker Desktop has no host networking by default, so the script uses `CONFORMANCE_DOCKER_NETWORK=bridge` there. Check `reports/run-info.txt` for `docker_network=bridge`. If you enabled host networking in Docker Desktop yourself, either value works. On Linux, a firewall that drops traffic from Docker bridges to the host (some `ufw` setups) breaks `bridge`; use the default `host`.

### Suite hostname doesn't resolve
`localhost.emobix.co.uk` is a public DNS name for 127.0.0.1. Without DNS, or behind a resolver that filters private answers, add `127.0.0.1 localhost.emobix.co.uk` to `/etc/hosts`. The CI workflow does this automatically if `getent hosts` fails.

## Runner aborts (exit 2) and INFRA results

**`environment has shim=<x>, config <name> expects <y>`**
The AS metadata the runner observed doesn't match the template's `expect.certify_as_metadata_shim`. Bring Certify up again with the matching setting (`CONFORMANCE_CERTIFY_AS_METADATA_SHIM=true scripts/env.sh up certify` for `certify-shim-on`), or pick the other template. In the testrig, `conformance.certify.as_metadata_shim` must match how the stack was started.

**`cannot read AS metadata: …`**
The runner reads `https://localhost:9443/.well-known/oauth-authorization-server` (`CERTIFY_PUBLIC_URL`). `certify-tls` isn't up or isn't published on 9443.

**`unresolved required placeholders: NAME`**
A template uses `${NAME}` without a default, and the variable is unset. Export it or add `:-default`.

**`seeding credential config failed: HTTP …`**
Certify rejected `plans/certify/credential-config.json`. With Certify v0.14.0, the 1.0 configuration fails with `Unrecognized field "cryptographicBindingMethodsSupported"`; v0.14.0 also rejects `dc+sd-jwt`. `CONFORMANCE_CERTIFY_RELEASE=0.14` makes `seed-certify.sh` use `compose/seed/certify-sdjwt-config-0.14.json` instead.

**`unknown modules (not in plan …)`**
A `--modules` name isn't in the plan. The module lists are in the benchmark files.

**`INFRA: runner timeout after 180s in WAITING`**
The module waited for something nobody did. Typical causes: the handoff plugin didn't find the endpoint it expected in the suite's exposed values (see `stderr.log`, lines starting `[handoff]`), or `CONFORMANCE_VERIFY_EVIDENCE=none` on a positive verifier module. Raise the limit with `--module-timeout` only if the component is just slow.

**`INFRA:` with an interruption reason, or a module stopped unexpectedly**
A second test with the same suite alias stops the running one. The runner's alias is `<component>-<run_id>`, so this happens only if two runs share a `--run-id`.

**`direct_post` returns HTTP 500 from Verify**
Verify's compose `db-init/init.sql` is stale: it lacks `vp_submission.response_code*` and has `vp_token` NOT NULL. The overlay initialises the database from the upstream DDL instead (`compose/verify-db/10-verify-ddl.sh`). If you still see 500s, the database may predate the overlay: run `scripts/env.sh down verify --purge`, then `up` again.

## Expected failures that look like bugs in the harness

**Every `verify-x509` module fails `ValidateRequestObjectSignatureAgainstX5cHeader` ("Unsupported JWS algorithm: EdDSA")**
That is finding F-VER-5, not a setup error. Verify signs only with Ed25519, and the suite's x5c check can't verify EdDSA, although its JWKS check can (a suite limitation, `evidence/sp5/triage.md`). Don't swap in a P-256 leaf: `verify-service` exits at startup with one.

**x5c validation fails because the chain contains the trust anchor**
The suite rejects an `x5c` that includes the root. `scripts/gen-certs.sh` therefore puts only the leaf into `verify-signing.p12`. Regenerate with `scripts/gen-certs.sh --force` if you replaced it.

**12 of 14 Certify modules fail `CheckServerConfiguration`**
That is F-CERT-1, the expected state of the benchmark of record. Use the shim diagnostic pass to see the rest of the flow.

**Verifier happy paths are "skipped" in TestNG**
They ended `REVIEW` after the harness uploaded Verify's result as screenshot evidence. That is the suite's verdict for a conformant verifier ([ADR-003](design-decisions.md#adr-003-mapping-suite-outcomes-to-testng-results)).

## Gate

**Gate exits 2: `benchmark … is for <key>, run is <key>`**
The run's plan, variant or observed flags differ from the benchmark's `variant_key`. The usual cause is gating a shim-on run against the shim-off benchmark.

**Gate exits 2: `invalid benchmark … empty reason` (or other validation errors)**
Every entry needs a `reason`. FAILED entries also need `first_failure` and a `finding` id of the form `F-CERT-n` / `F-VER-n`, and `expected_warnings` must be a sorted list.

**`STALE`**
The module did better than the benchmark, or an expected warning disappeared. Confirm the improvement is real, then update the entry by a reviewed edit. Don't regenerate the whole file to silence it.

**`NEW_FAILURE` / `REGRESSION` / `NEW_WARNING`**
Compare the run with the last good one: `python -m runner diff <old>/results.jsonl <new>/results.jsonl`, then open the module's `<module>.log.json` or its suite log URL.

## Testrig and Maven

**`mvn package` fails with git-commit-id-plugin "Missing unknown <sha>"**
The plugin can't read a `git worktree` checkout. Build from a plain clone.

**No conformance tests run; the default suite runs instead**
`conformance.enabled` isn't `yes`. Pass it as `-e conformance.enabled=yes`: environment variables override properties by exact name, dots included.

**`No files found in directory: …/testNgXmlFiles`**
The image doesn't contain the suite XML files. The api-test `Dockerfile` copies only `api-test/target`; build with `testrig-bridge/build-image.sh`, which stages `testNgXmlFiles/` into `target/`.

**`OIDF_<component>_runner` fails with `runner produced no plan record`**
The runner didn't start. Check `testng-report/conformance/<config>/runner.stderr.log` in the container. Typical causes: `conformance.runner.dir` doesn't contain `runner/` and `plans/` (mount them), or `python3` / `httpx` / `PIL` is missing in the image (the patched Dockerfile installs them).

**Default (non-conformance) Certify run exits 1 before any test**
Expected without a full MOSIP platform: `InjiTestRunner` first sets up Keycloak users and eSignet, and the compose stack has neither. Conformance mode skips that setup.

**ERROR lines about a Slack URL, `mountPathForReport` or `healthCheckEndpoint.properties`**
These come from apitest-commons code paths, appear in every run, and don't affect the report.

**The patched Certify image is much larger than expected**
A previous build left `original-…-jar-with-dependencies.jar` in `target/`, and the Dockerfile's `chown -R` layer copies it again. Build from a clean `target/`. The real cost of the patch is the +20.2 MB for Python.

**`known-issue entry present but outcome=pass` in the test log**
A module listed in `testCaseSkippedList.txt` no longer fails. Remove the entry, along with the matching benchmark change.

## MinIO

**`compose/minio.yml` has no health check.** The image ships no `mc`. Poll `curl -fsS http://127.0.0.1:9000/minio/health/live` from the host, and list buckets with `curl --aws-sigv4 "aws:amz:us-east-1:s3" -u minioadmin:minioadmin "http://127.0.0.1:9000/automation?list-type=2"`.

**Uploaded reports are gone.** MinIO's `/data` is tmpfs, so objects last only as long as the container.
