# Known limitations

## What the benchmark of record can see

**While F-CERT-1 stands, the Certify benchmark of record really exercises only 2 of its 14 issuer modules.** With the AS-metadata shim off, 12 of the 14 modules stop at `CheckServerConfiguration` because Certify's AS metadata has no `authorization_endpoint` (`evidence/sp2/live/stability.md`, certify-shim-off table). Only `oid4vci-1_0-issuer-metadata-test` and `oid4vci-1_0-issuer-metadata-test-signed` test anything else, and both only read the issuer metadata. So the record gate catches faults in Certify's issuer metadata, and **nothing in the token, nonce, proof or credential flow**. Faults there show up only in the shim-on diagnostic pass. For example, removing `nonce_endpoint` from the metadata leaves the record gate green and turns the diagnostic gate red, while removing `credential_endpoint` turns the record gate red. Until Certify publishes `authorization_endpoint`, run the diagnostic pass alongside the record pass whenever issuance code changes, and read its result as diagnostic.

Similar masking applies on the verifier side:
- **No verifier module reaches its real verdict.** Every `verify-redirect-uri` module stops at F-VER-1, and every `verify-x509` module at F-VER-5. A regression in Verify's presentation checks would change only conditions after the first failure. The record gate sees that only if it adds or removes a warning or changes the first failure.
- Consequently, the REVIEW path (the automated screenshot evidence) is exercised in the code and unit tests, but no module in today's benchmarks ends in REVIEW.

The fingerprint is the first failing condition plus the module's set of warning conditions. Later failed conditions in a module that is already FAILED are not compared, by design ([ADR-004](design-decisions.md#adr-004-conformance-benchmark-gate)).

## Scope

- **Not certifiable.** Only the non-HAIP 1.0 plans run; the HAIP certification plans would fail at setup for both components ([self-certification.md](self-certification.md)).
- **One credential format.** Only `sd_jwt_vc` (`dc+sd-jwt`) is tested. Neither suite plan tests `ldp_vc`, Certify's default compose credential, and `mdoc` / `iso_mdl` are not configured.
- **One issuer grant.** Only `pre_authorization_code`, issuer-initiated, with `private_key_jwt` and DPoP. `authorization_code` needs a browser login on an authorization server the compose stack doesn't include.
- **Verifier response mode.** Only `direct_post`. Verify doesn't implement `direct_post.jwt`, and its `dc_api` mode is not tested.
- **Published images, not source builds.** The images are a few commits behind the source pins (Certify `bbd913e` vs `0d52155`, Verify `5f44a36` vs `64b2790`). Neither gap contains a `.java` change. The Certify image bundles plugin jars whose versions differ from those declared at the source pin; no finding depends on plugin code ([ADR-006](design-decisions.md#adr-006-pin-every-image-by-digest)).

## Harness behaviour

- **The testrig driver builds images on the run host.** The first run of `scripts/run-conformance.sh` clones both modules and runs a Maven build per module (about two minutes each). MOSIP CI would use its own published testrig images instead. `CONFORMANCE_DRIVER=runner` skips the testrig entirely.
- **`runner combined` ignores `--strict`.** Per-config gates honour it; the combined page and badge gate non-strictly. This only matters if a WARNING outcome ever appears (none does today).
- **No locking.** Two harness runs on one Docker host recreate each other's containers. Ports are fixed: 8443, 8091, 9443 and 8080, plus 9000/9001 for MinIO. Use `flock` around whole runs.
- **Docker Desktop is untested end to end.** Bridge networking (`CONFORMANCE_DOCKER_NETWORK=bridge`, the default on Docker Desktop) was checked on Linux for reachability (published host port, the suite hostname, MinIO by name), but every recorded full run used Linux with host networking.
- **Certify's credential configuration doesn't persist.** Certify's database uses an anonymous volume, so the configuration is lost on `down`. `env.sh up` and the runner both re-seed it, idempotently.
- **Suite upgrades need a re-baseline.** Benchmarks key on suite condition names, so a new suite tag that renames conditions makes entries `STALE` or `NEW_FAILURE` until they are reviewed.
- **The verifier screenshot is automated.** It is a rendering of Verify's own `/vp-result` response, not a wallet or UI capture. That is acceptable for regression gating, but it isn't evidence a certification reviewer would accept.
- **The MinIO store is ephemeral** (tmpfs) and exists only for local and CI report uploads.

## Deployment assumptions to confirm with MOSIP QA

- The testrig runs as a Kubernetes job without a Docker socket. That is why Python goes into the image instead of a separate runner container ([ADR-002](design-decisions.md#adr-002-how-the-runner-subprocess-runs-inside-the-testrig)).
- How the runner code reaches the testrig container in a cluster. Today `runner/` and `plans/` are mounted at `conformance.runner.dir`; baking them into the image or using a volume are both open.
- The report bucket used in MOSIP environments. The commons default is `automation`; the brief's `automationtests` appears nowhere in code. Either works through `s3-account`.
- How MOSIP CI stages `testNgXmlFiles/` into the image. The api-test `Dockerfile` copies only `api-test/target`, so `testrig-bridge/build-image.sh` copies the XML files into `target/testNgXmlFiles` itself.
- The GitHub Actions workflow has run green on GitHub (known-good and the credential-endpoint negative control). It assumes `localhost.emobix.co.uk` resolves to 127.0.0.1 on the runner, and adds an `/etc/hosts` entry if it doesn't.

## Triage outcome

- F-CERT-3 and the signed-metadata half of F-CERT-5 are Certify defects.
- F-VER-5's failures come from a suite limitation: the suite's x5c check can't verify EdDSA. Verify still needs ES256 for HAIP.

Spec quotes and source references are in `evidence/sp5/triage.md`, and the summary is in [findings.md](findings.md). Until the suite accepts Ed25519 x5c leaves, the `verify-x509` record pass can't see past the request-object check.
