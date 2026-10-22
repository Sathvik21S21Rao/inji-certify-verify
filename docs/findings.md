# Findings

This page lists every non-passing module in the four plan configs, grouped by root cause, with the evidence and a suggested owner. Each finding id is also the `finding` (and usually the `ki`) value in the benchmark files, so a gate table row leads straight here.

Targets: Inji Certify image built from `bbd913e` (source pin `0d52155`, `release-1.0.x`); Inji Verify image built from `5f44a36` (source pin `64b2790`). Suite `release-v5.3.3`. Outcomes were stable across three repeated runs of each config (`evidence/sp2/live/stability.md`).

Evidence files used below:
- `evidence/sp0/baseline-v0-certify/reasons.md`: Certify with the AS-metadata shim on. Per module: the first failing condition and Certify's HTTP response.
- `evidence/sp0/baseline-v0-verify/reasons.md` and `evidence/sp0/baseline-v0-verify-x509/reasons.md`: per module, the failing conditions, Verify's `direct_post` response and its `/vp-result` verdict.
- `evidence/sp2/live/stability.md`: all four configs × 3 runs, with outcome and first failing condition.
- Testrig reports, one per config: `evidence/sp3/SP3.4/<config>/testng-report/*.html`.

Status values: **confirmed** (the spec text and the observed behaviour agree), **triage** (the behaviour is observed, but who must change, the component or the suite, is still open).

## Summary

| ID | Owner | Status | Modules affected (config) |
|---|---|---|---|
| F-CERT-1 | Certify | confirmed | 12 of 14 (certify-shim-off) |
| F-CERT-2 | Certify | confirmed | happy-flow, fail-unknown-credential-identifier (certify-shim-on) |
| F-CERT-3 | Certify (or harness config) | triage | happy-flow-additional-requests, happy-flow-multiple-clients, happy-flow-skip-notification, fail-on-access-token-in-query (certify-shim-on) |
| F-CERT-4 | Certify | confirmed | fail-unknown-credential-configuration (certify-shim-on) |
| F-CERT-5 | Certify (signed part: triage) | confirmed / triage | metadata-test, metadata-test-signed (both Certify configs) |
| F-VER-1 | Verify | confirmed | all 9 (verify-redirect-uri) |
| F-VER-2 | Verify | confirmed | x509_san_dns presentations |
| F-VER-3 | Verify | confirmed | happy paths (verify-redirect-uri) |
| F-VER-4 | — (informational) | permitted behaviour | invalid-credential-signature, invalid-kb-jwt-signature, invalid-sd-hash |
| F-VER-5 | Verify and/or OIDF suite | triage | 10 of 11 (verify-x509) |

## Inji Certify

### F-CERT-1: AS metadata has no `authorization_endpoint`
- **Observed.** Certify's `/.well-known/oauth-authorization-server` advertises the `authorization_code` grant but has no `authorization_endpoint`; Certify uses an interactive authorization endpoint instead. Every non-metadata issuer module runs `CheckServerConfiguration` first and stops there: 12 of 14 modules are `INTERRUPTED/FAILED` at `CheckServerConfiguration` in the record pass.
- **Spec.** RFC 8414 §2: `authorization_endpoint` is REQUIRED unless no grant type that uses it is supported.
- **Evidence.** `evidence/sp2/live/stability.md` (certify-shim-off table); `evidence/sp0/s04-noshim-fullplan/summary.json`; `evidence/sp0/s04-v1-preauth-pkjwt-dpop/summary.json` (the first unshimmed attempt); testrig report `evidence/sp3/SP3.4/certify-shim-off/testng-report/…T-14_P-0_S-0_F-13_I-0_KI-1.html`.
- **Suggested fix.** Publish `authorization_endpoint`, or stop advertising `authorization_code` in deployments that don't serve it.
- **Impact on this harness.** While F-CERT-1 stands, the record pass exercises only the two metadata modules ([known-limitations.md](known-limitations.md)).

### F-CERT-2: credential endpoint rejects unknown request fields
- **Observed.** `POST /issuance/credential` with an extra member returns `400 {"error":"invalid_request","error_description":"Unrecognized field '<name>' in request"}`. `happy-flow` sends a random extra field. `fail-unknown-credential-identifier` sends `credential_identifier`, which Certify rejects as unrecognised instead of answering with the specified error.
- **Spec.** OpenID4VCI 1.0: unknown parameters in requests must be ignored.
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (rows `oid4vci-1_0-issuer-happy-flow`, `oid4vci-1_0-issuer-fail-unknown-credential-identifier`, with the response bodies); `evidence/sp2/live/stability.md` (certify-shim-on: `EnsureHttpStatusCodeIsAnyOf`, `VCIValidateCredentialErrorResponse`).
- **Suggested fix.** Configure the request DTO's JSON deserialisation to ignore unknown properties.

### F-CERT-3: proof JWT `iss` rejected in the pre-authorized flow
- **Observed.** The credential endpoint returns `400 {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."}`. Certify's log gives the cause: `BadJWTException: JWT iss claim has value 52480754053, must be` followed by an empty value. Certify expects no `iss`, because its pre-authorized token carries no client. The suite sends the client id (`52480754053`, from the template) as `iss`, having authenticated with `private_key_jwt` at the token endpoint.
- **Spec.** OpenID4VCI 1.0 Appendix F.1: `iss` must be omitted only when the pre-authorized flow is used anonymously.
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (rows `happy-flow-additional-requests`, `happy-flow-multiple-clients`, `happy-flow-skip-notification`, `fail-on-access-token-in-query`); `evidence/sp2/live/stability.md` (certify-shim-on). The container-log line is quoted above; the log itself is not in the curated evidence.
- **Triage.** Is a client that authenticates at the token endpoint "anonymous" for Certify? If Certify should bind the client to the pre-authorized token, this is a Certify bug. If not, the harness should configure the suite for anonymous access. Owner to confirm before reporting it upstream.

### F-CERT-4: wrong error code for an unknown credential configuration
- **Observed.** A credential request for an unknown `credential_configuration_id` returns `400 {"error":"invalid_credential_request","error_description":"No credential configuration found for credential_configuration_id"}`.
- **Spec.** OpenID4VCI 1.0 defines the credential error code `unknown_credential_configuration` for this case; the suite checks for it (`VCIValidateCredentialErrorResponse`).
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (row `fail-unknown-credential-configuration`).
- **Suggested fix.** Return `unknown_credential_configuration`.

### F-CERT-5: issuer metadata schema errors; signed metadata not served
- **Observed.** (a) `metadata-test` fails `VCICredentialIssuerMetadataValidation` ("Found invalid entries in OID4VCI Credential Issuer metadata input"; suite requirement `OID4VCI-1FINAL-12.2.3`), because Certify emits `null` for unset optional display fields such as `logo` and `background_color`. (b) `metadata-test-signed` fails `EnsureContentTypeApplicationJwt`: a request with `Accept: application/jwt` gets `200` with no `Content-Type` header at all ("Couldn't find content-type header in endpoint_response"), and no JWT.
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (rows `metadata-test`, `metadata-test-signed`, including the start of the metadata body); `evidence/sp2/live/stability.md` (both Certify configs); `runner/tests/fixtures/certify-shim-off.jsonl` (full condition list). It is the one Certify known issue in the testrig patch (`F-CERT-5------OIDF_certify_oid4vci-1_0-issuer-metadata-test`), hence `KI-1` in both Certify report names (`evidence/sp3/SP3.4/counts-check.md`).
- **Suggested fix.** (a) Omit unset optional fields instead of emitting `null`. (b) Triage: signed metadata is optional in OpenID4VCI. Decide whether the suite should skip the module when the issuer doesn't sign its metadata, or whether Certify should support it.

## Inji Verify

### F-VER-1: `url_query` requests carry no `client_metadata`
- **Observed.** With the `redirect_uri` client id and `url_query`, Verify's authorization request has no `client_metadata` and so no `vp_formats_supported`. All 9 modules fail `VP1FinalValidateVpFormatsSupportedInClientMetadata`. The harness passes exactly the parameters Verify's own SDK passes (`inji-verify-sdk/src/components/openid4vp-verification/OpenID4VPVerification.tsx`), so a real wallet sees the same request.
- **Spec.** OpenID4VP 1.0 client metadata (`vp_formats_supported`), checked by the suite's `VP1FinalValidateVpFormatsSupportedInClientMetadata`.
- **Evidence.** `evidence/sp0/baseline-v0-verify/reasons.md`; `evidence/sp2/live/stability.md` (verify-redirect-uri); testrig report `evidence/sp3/SP3.4/verify-redirect-uri/testng-report/…T-9_P-0_S-0_F-9_I-0_KI-0.html`.
- **Suggested fix.** Include `client_metadata` (with `vp_formats_supported`) in `url_query` requests, or return it from `vp-request` so the SDK can forward it.

### F-VER-2: KB-JWT `aud` with an `x509_san_dns:` client id is rejected
- **Observed.** With `client_id = x509_san_dns:test.example.com`, Verify rejects the key-binding JWT whose `aud` equals that client id, logging "must be a valid URI when containing ':'". The presentation's `/vp-result` is `INVALID` although `direct_post` returned 200.
- **Spec.** OpenID4VP 1.0 sets the KB-JWT `aud` to the client id, including its prefix.
- **Evidence.** `evidence/sp0/baseline-v0-verify-x509/reasons.md` (`happy-flow` and `minimal-cnf-jwk`: `200 OK`, `/vp-result` `INVALID`). The log message is from Verify's container log, which is not in the curated evidence. In the current x509 config, F-VER-5 fails every module earlier, so F-VER-2 doesn't appear as a first failing condition in the benchmark.
- **Suggested fix.** Accept prefixed client ids as `aud` without URI parsing.

### F-VER-3: no trust anchor enforced for credentials
- **Observed.** Verify returns `SUCCESS` for the suite's SD-JWT credential, whose `x5c` chains to the suite's own test root (`CN=OIDF Test CA`, visible in the templates' `credential.signing_jwk.x5c`). The compose stack configures no trust in that root. A credential with a bad signature is still rejected (`INVALID`).
- **Evidence.** `evidence/sp0/baseline-v0-verify/reasons.md` (`happy-flow`, `minimal-cnf-jwk`: `/vp-result` `SUCCESS`; `invalid-credential-signature`: `INVALID`).
- **Suggested fix.** Validate the issuer chain against configured trust anchors, or document the trust model if issuer trust is left to the relying application. This is also a HAIP prerequisite.

### F-VER-4: some rejections appear only in `/vp-result` (informational)
- **Observed.** For `invalid-credential-signature`, `invalid-kb-jwt-signature` and `invalid-sd-hash`, `direct_post` returns `200 {}`, and the rejection appears only later in `/vp-result` as `INVALID`. Other negative cases (`invalid-kb-jwt-nonce`, `invalid-kb-jwt-aud`, `kb-jwt-iat-in-past`, `kb-jwt-iat-in-future`) are rejected immediately with 400.
- **Spec.** Deferred verification is permitted. This is not a conformance failure; it is listed so maintainers know where each check happens.
- **Evidence.** `evidence/sp0/baseline-v0-verify/reasons.md`.

### F-VER-5: `x509_san_dns` request objects are signed with EdDSA only
- **Observed.** Verify signs request objects with a hard-coded `JWSAlgorithm.EdDSA` and an `Ed25519Signer`, and its keystore loader accepts only an Ed25519 key entry. A P-256 leaf certificate makes `verify-service` exit at startup. The suite's `ValidateRequestObjectSignatureAgainstX5cHeader` cannot verify EdDSA ("Unsupported JWS algorithm: EdDSA"), so 10 of the 11 x509 modules fail there. The eleventh, `request-uri-method-post`, is skipped as not applicable. The certificate chain itself validates against the test CA.
- **Source.** inji-verify `64b2790`: `verify-core/src/main/java/io/inji/verify/services/impl/VerifiablePresentationRequestServiceImpl.java` (header algorithm and signer) and `verify-core/src/main/java/io/inji/verify/key/impl/P12KeyExtractor.java` (key type check). The harness's test leaf is Ed25519 for this reason (`scripts/gen-certs.sh`).
- **Evidence.** `evidence/sp2/live/stability.md` (verify-x509); testrig report `evidence/sp3/SP3.4/verify-x509/testng-report/…T-11_P-0_S-1_F-10_I-0_KI-0.html`.
- **Triage.** OpenID4VP doesn't forbid EdDSA, so the suite's plain-OID4VP x5c check is arguably too narrow, and an OIDF issue may be warranted. HAIP requires ES256 for verifiers, so Verify needs ES256/P-256 request-object signing for HAIP regardless. Suggested owner: Verify, with an issue to OIDF as well.

## Skipped modules

These are not findings, but they are listed so no module is unaccounted for:
- `oid4vci-1_0-issuer-batch-issuance` (shim on): Certify's metadata has no `batch_credential_issuance`, so the suite skips.
- `oid4vci-1_0-issuer-fail-invalid-key-attestation-signature` (shim on): the credential configuration uses `jwt` proofs without key attestations; not applicable.
- `oid4vp-1final-verifier-request-uri-method-post` (x509): Verify's request has no `request_uri_method=post`; not applicable.

Passing (shim on): `fail-invalid-nonce`, `fail-invalid-jwt-proof-signature`, `fail-missing-proof`. Certify rejects each bad request as required.
