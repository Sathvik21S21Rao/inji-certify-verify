# Design decisions

Six decisions shape the harness. Comments in the code refer to them by id. Each one records the context, the options weighed, the decision with its deciding reason, and the consequences. Suite source paths are relative to `src/main/java/net/openid/conformance/` in the conformance suite at `release-v5.3.3`.

| ID | Decision | Status |
|---|---|---|
| ADR-001 | Non-HAIP plans; issuer pre-authorized code; two verifier variants; AS-metadata shim behind a reported flag, off in the benchmark of record | accepted |
| ADR-002 | The runner is a Python subprocess; `python3` is added to the testrig image | proposed (deployment model to confirm with MOSIP QA) |
| ADR-003 | Map suite (status, result) pairs to outcomes; verifier happy paths end in REVIEW | proposed; the screenshot-evidence part is accepted |
| ADR-004 | Benchmark gate: expected outcome, first failing condition and expected warnings per module | proposed |
| ADR-005 | Module-local bridge in each api-test, selected by `conformance.enabled` | accepted |
| ADR-006 | Pin every image by digest; accept the image-to-commit gap | proposed |

---

## ADR-001: Target plans and variants

**Context.**
- Both 1.0 plans exist at the pinned suite tag: `oid4vci-1_0-issuer-test-plan` (`vci10issuer/VCIIssuerTestPlan.java`) and `oid4vp-1final-verifier-test-plan` (`vp1finalverifier/VP1FinalVerifierTestPlan.java`). The suite labels both "alpha tests (not part of certification program – use the HAIP … plan to certify)".
- The issuer plan tests only `sd_jwt_vc` and `mdoc`, and the verifier plan only `sd_jwt_vc` and `iso_mdl`, both queried with DCQL. Neither tests `ldp_vc`, the format of Certify's default compose credential. Certify 1.0.x can issue `dc+sd-jwt` through `POST /credential-configurations`, and Verify 1.0.x accepts DCQL queries for `dc+sd-jwt`.
- The compose stack has no separate authorization server. Certify publishes no `authorization_endpoint`, because it uses an interactive authorization endpoint instead (`OAuthAuthorizationServerMetadataDTO.java`).
- HAIP requires features the components don't have: client attestation for issuers; `x509_hash` client ids and `direct_post.jwt` for verifiers.

**Options.**
- Issuer: (1) pre-authorized code with `private_key_jwt` and DPoP, with Certify as its own AS, set entirely through property overrides and needing no image change; (2) authorization code with wallet-initiated flow, which needs a browser login on an AS the stack doesn't have; (3) mTLS or client attestation, which Certify doesn't implement; (4) `mdoc`, available only in a different Certify plugin mode.
- Verifier: (1) `redirect_uri` + `url_query` + `direct_post`, which needs no keys; (2) `x509_san_dns` + `request_uri_signed` + `direct_post`, Verify's signed-request path; (3) `direct_post.jwt`, `x509_hash`, `iso_mdl` and HAIP, none of which Verify 1.0.x supports.

**Decision.**
- **Issuer: option 1.** Pre-authorized code is the only grant the compose stack can complete unattended. The plan config seeds an SD-JWT credential configuration (`plans/certify/credential-config.json`).
- **The AS-metadata shim.** The suite requires `authorization_endpoint` even for pre-authorized-only flows (`CheckServerConfiguration`), so without it 12 of the 14 issuer modules stop at setup (`evidence/sp0/s04-noshim-fullplan/summary.json`, `evidence/sp2/live/stability.md`). The project owner chose to ship a shim behind an explicit flag: `conformance.certify.as_metadata_shim` in the testrig, `CONFORMANCE_CERTIFY_AS_METADATA_SHIM` in the environment, default `false`. **The benchmark of record runs with the flag off.** A separately labelled diagnostic pass runs with it on, so the rest of the issuance flow still gives signal. Every report states the observed flag value, and F-CERT-1 is reported in both passes.
- **Verifier: both option 1 and option 2,** as two configs. They surface different Verify findings (F-VER-1 and F-VER-5), and each config takes seconds to run once the stack is up.
- HAIP plans are out of scope ([self-certification.md](self-certification.md)).

**Consequences.** Both components need TLS fronts, because the suite requires `https://` for the offer URI and the issuer metadata. The Certify config must seed its credential configuration on every bring-up. The findings F-CERT-1…5 and F-VER-1…5 come from these baselines ([findings.md](findings.md)). Revisit if Certify adds `authorization_endpoint`, if the suite adds an `ldp_vc` plan, or if either component gains the HAIP features.

---

## ADR-002: How the runner subprocess runs inside the testrig

**Context.** The Java bridge launches a Python runner built on the suite's own client. The suite is MIT-licensed (`LICENSE.txt` in the suite repo), so `conformance.py` can be vendored with its notice; it lives unmodified in `runner/_vendor/`. Both testrig images build `FROM mosipid/openjdk-21-jre:21.0.4`: Ubuntu 24.04 with `apt-get` and no `python3`. The testrig normally runs as a Kubernetes job, and its Dockerfile already installs `kubectl`.

**Options.**
- **(a) `python3` in the testrig image.** One Dockerfile line in each module: `apt-get install -y python3 python3-httpx python3-pil`. Measured on the base image: 228,329,533 B → 248,553,533 B, i.e. **+20.2 MB (+8.9 %)**, of which Pillow is 2.6 MB (`evidence/sp3/SP3.1/image-size.log`). Installed versions: python3 3.12.3, httpx 0.26.0, Pillow 10.2.0. `runner/requirements.txt` pins the same versions.
- **(b) A separate runner image started with `docker run`.** The testrig image stays untouched, but the testrig pod then needs a Docker socket or Docker-in-Docker, which is a security exception or a privileged pod in a cluster.

**Decision. (a).** A 20 MB, one-line image change costs far less than asking a cluster to give a test pod Docker access. The command is kept as a single config value, `conformance.runner.command` (default `python3 -m runner run`), so (b) stays possible without a code change.

**Consequences.** The runner depends only on the standard library, `httpx` (tested against 0.26) and Pillow (for the evidence PNG). The image change is the one change to MOSIP's image, and it is disclosed in the README. The runner code and templates are mounted into the container at `conformance.runner.dir`; baking them into the image instead is an open deployment choice. Revisit if MOSIP QA confirms the testrig already has a Docker socket, or rejects any image change.

---

## ADR-003: Mapping suite outcomes to TestNG results

**Context.** Each suite module ends with a `status` and a `result` (`testmodule/TestModule.java`). What the suite source shows:
- `FAILED` is set by any failed condition with `onFail=FAILURE`, and is never overwritten.
- `WARNING` is set only if the result is not already FAILED or REVIEW, and becomes a verdict only when the module completes.
- `REVIEW` is set when a screenshot placeholder is filled (`logging/ImageAPI.java`). Every positive OID4VP verifier module creates such a placeholder after a successful `direct_post` (`vp1finalverifier/AbstractVP1FinalVerifierTest.java`). So **a fully conformant verifier ends REVIEW, never PASSED**.
- `INTERRUPTED` usually means a `callAndStopOnFailure` condition failed, and the result is then `FAILED`: real non-conformance. Only an API stop, an alias collision or the idle timeout gives `UNKNOWN`. A test stopped through the API reports a `null` result.

**Options.** (1) Treat INTERRUPTED as an infrastructure failure. That is wrong: it would label Certify bugs as "infra". (2) Map on the (status, result) pair and keep harness-side errors apart. (3) Map on the result only, which loses "stopped early" versus "completed".

**Decision. Option 2.** The suite already encodes the verdict in `result`; `INTERRUPTED` only means "stopped early". The full table is in [results-contract.md](results-contract.md#outcome-mapping). In short: PASSED → pass; WARNING → pass with warnings, or fail under strict mode; REVIEW → skip ("needs human review"); SKIPPED → skip; FAILED (finished or interrupted) → fail with the first failed condition; INTERRUPTED with UNKNOWN or null, or any runner timeout, HTTP or handoff error → fail labelled `INFRA:`.

**Accepted: verifier screenshot evidence.** The project owner accepted that the harness fills the verifier's screenshot placeholder with a PNG rendering of Verify's own `GET /v1/verify/vp-result/{txn}` response. This is an automated stand-in, like the suite's own CI evidence capture. Positive verifier modules therefore end in REVIEW. The rendering is in `runner/evidence.py`, switched by `CONFORMANCE_VERIFY_EVIDENCE` (`vp-result-png` or `none`).

**Consequences.** Certify failures appear as failures with the violated condition named, and infrastructure problems carry their own label. Verifier happy paths can never show green: the benchmark records REVIEW as their expected outcome, and a drop to FAILED turns the gate red. The meaning of `--strict` for WARNING is the harness's choice, not the suite's. Revisit if the suite adds a non-screenshot completion path for verifier tests, or changes its result precedence.

---

## ADR-004: Conformance benchmark gate

**Context.** The brief gates on a "conformance benchmark", but neither apitest-commons nor either api-test has benchmark code. The closest existing mechanism is the known-issue skip: a test listed in `testCaseSkippedList.txt` as `<id>------<testCaseName>` is skipped with the known-issue message, and `EmailableReport` counts it in the KI column. Almost every module fails at the current baseline, so "all must pass" would be red forever. A FAILED verdict can also hide a new bug behind an old one, because a module stops at its first failing condition.

**Options.** (1) Pass/fail only, which is always red and gives no signal. (2) An expected outcome per module, which misses "still failing, but somewhere new". (3) Option 2 plus a failure fingerprint, the first failing condition, read straight from the suite log.

**Decision. Option 3.** With nearly every module FAILED, only the failing condition tells a known bug from a new one. `plans/<component>/<config>.benchmark.json` holds, per module: `expected`, `first_failure`, `expected_warnings` (sorted warning condition names), `finding`, `ki`, and a human-written `reason`. A `variant_key` ties the file to one plan, variant and set of observed flags.

| Observed vs expected | Verdict | Gate |
|---|---|---|
| Same outcome, same first failure, same warnings | `OK` | green |
| In the benchmark, not selected in this run | `NOT_RUN` | green |
| Better (e.g. FAILED → PASSED), or an expected warning disappeared | `STALE` | red: update the entry |
| Worse (e.g. PASSED/REVIEW → FAILED) | `REGRESSION` | red |
| Still FAILED, different first failure | `NEW_FAILURE` | red |
| A warning not in the expected set | `NEW_WARNING` | red |
| WARNING outcome under `--strict` | `STRICT_WARNING` | red |
| Module not in the benchmark | `UNBENCHMARKED` | red |
| `infra` outcome or missing record | `INFRA` | red |

**Amendment: expected warnings.** Running Certify v0.14.0 (draft 13) against the 1.0 record benchmark produced the same 14 outcomes and first failures as 1.0. The only difference was one extra warning, `VCICheckForOldSdJwtFormatInCredentialConfigurations`, on `oid4vci-1_0-issuer-metadata-test`. Warning sets were stable across every known-good run, so the benchmark now also records them, and that control turns red.

**Consequences.** Known failures stay visible in the report, through the existing KI mechanism (`ki` ids match `testCaseSkippedList.txt` entries), without a new reporter. The negative controls are testable. A suite upgrade that renames conditions makes entries stale; that is intended, since the suite tag is pinned. `benchmark init` writes the skeleton from a clean run; a person writes each `reason`. Revisit if MOSIP QA wants the benchmark kept in `testCaseSkippedList.txt` itself. That file holds only names, so it would lose the stale and new-failure checks.

---

## ADR-005: Module-local bridge, selected by `conformance.enabled`

**Context.**
- The Inji testrigs live in `inji-certify/api-test` and `inji-verify/api-test`; `mosip-functional-tests` supplies only `apitest-commons`.
- The two modules use different commons versions: 1.6.0 for Certify, 1.5.0 for Verify. Every class the bridge reuses (`EmailableReport` and its inner classes, `SkipTestCaseHandler`, `S3Adapter`, `ConfigManager`) is byte-identical in the two jars (`evidence/sp3/commons-diff/jar-bytecode-compare.txt`).
- `env.endpoint` is the platform's API gateway. The module's own Certify and Verify tests call `injiCertifyBaseURL` / `injiVerifyBaseUrl` instead.
- Any property can be overridden by an environment variable of exactly the same name.
- `InjiTestRunner` runs only suite files whose name contains `mastertestsuite`, after platform setup (Keycloak users, eSignet CSRF, OTP listener, master-data checks) that the compose stack doesn't have.

**Options.**
- Location: (1) a module-local class in each api-test, built against that module's own commons, with no pom change; (2) a shared class in apitest-commons, which needs a commons release and a Verify version bump first.
- Base URL: (1) `injiCertifyBaseURL` / `injiVerifyBaseUrl`; (2) `env.endpoint`, which is a different host than the existing tests use.
- Selection: (1) a new `conformance.enabled` key in both modules; (2) Certify's `useCaseToExecute`, which Verify lacks; (3) adding the test to the master suite, which would change the default run.

**Decision. Option 1 in all three groups.** It reaches exactly the host the module's own tests reach, and leaves the default run's code path and suite selection untouched. The new keys are in one `conformance.*` section per properties file (table in [usage.md](usage.md#testrig-integration)). MinIO upload needs no code: the existing `s3-*` and `push-reports-to-s3` keys point `S3Adapter` at it.

**Consequences.** MOSIP QA reviews a small per-module diff: Certify 6 files (+384/−3), Verify 5 files (+377/−2) (`testrig-bridge/*.diffstat.txt`). Results use the report, KI column and MinIO upload QA already read. The two bridge classes must be kept in step by hand. A conformance run is a separate jar invocation from the default run. Revisit if Verify moves to commons ≥ 1.6 and MOSIP wants the bridge in commons.

---

## ADR-006: Pin every image by digest

**Context.** The upstream compose files use moving tags (`injistackqa/inji-certify-with-plugins:1.0.x`, `injistackqa/inji-verify-service:1.0.x`, `nginx:stable`, `postgres:13`, `postgres:15`), so a run next week could test a different build. The images carry a `commit_hash` label. The Certify image was built from `bbd913e`, 4 commits behind the source pin `0d52155`. The Verify service image was built from `5f44a36`, 11 commits behind `64b2790`. Both are ancestors of the pins, and **neither gap changes any `.java` file**: the gaps touch versions, Helm charts, scripts, docs, UI and CI only. The Certify image also bundles plugin jars from other repos, whose versions differ from those declared at the source pin.

**Options.** (a) Pin the published images by digest. (b) Build images from the pinned source, which means a full Maven build per run and is effectively a fork of the upstream build. (c) Use the floating tags, which makes runs unreproducible and leaves a gate unable to tell a code change from a repushed tag.

**Decision. (a).** Every image is referenced as `repo:tag@sha256:…` from `compose/.env.pinned`; the tag is there for readability only. Runs are reproducible, and they test what MOSIP actually publishes. MinIO uses `cgr.dev/chainguard/minio:latest@sha256:…`, chosen by the project owner, because Docker Hub's and Quay's MinIO images refuse anonymous pulls. Chainguard's free tier publishes only `latest`, so the digest is the only pin. MinIO is only the local report store, not a component under test.

**Consequences.** Every machine runs identical bits. Picking up a new upstream build means bumping a digest explicitly. Findings cite both the source pin and the image commit. Revisit if a gap ever includes `.java` changes in code the suite exercises, if a finding depends on plugin code, or if MOSIP publishes images tagged per commit.
