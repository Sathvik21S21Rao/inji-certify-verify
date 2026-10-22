# Findings

This page lists every non-passing module in the four plan configs, grouped by root cause, with the evidence and a suggested owner. Each finding id is also the `finding` (and usually the `ki`) value in the benchmark files, so a gate table row leads straight here.

Targets: Inji Certify image built from `bbd913e` (source pin `0d52155`, `release-1.0.x`); Inji Verify image built from `5f44a36` (source pin `64b2790`). Suite `release-v5.3.3`. Outcomes were stable across three repeated runs of each config (`evidence/sp2/live/stability.md`).

Evidence files used below:
- `evidence/sp0/baseline-v0-certify/reasons.md`: Certify with the AS-metadata shim on. Per module: the first failing condition and Certify's HTTP response.
- `evidence/sp0/baseline-v0-verify/reasons.md` and `evidence/sp0/baseline-v0-verify-x509/reasons.md`: per module, the failing conditions, Verify's `direct_post` response and its `/vp-result` verdict.
- `evidence/sp2/live/stability.md`: all four configs × 3 runs, with outcome and first failing condition.
- Testrig reports, one per config: `evidence/sp3/SP3.4/<config>/testng-report/*.html`.

Status values: **confirmed** (the spec text and the observed behaviour agree), **suite limitation** (the component's behaviour is allowed by the spec, and the suite can't check it). The triage of F-CERT-3, F-CERT-5 (b) and F-VER-5, with spec quotes and source references, is in `evidence/sp5/triage.md`. The spec texts used (OpenID4VCI 1.0, OpenID4VP 1.0 and HAIP 1.0, all Final) are saved in `evidence/sp5/specs/`.

## Summary

| ID | Owner | Status | Modules affected (config) |
|---|---|---|---|
| F-CERT-1 | Certify | confirmed | 12 of 14 (certify-shim-off) |
| F-CERT-2 | Certify | confirmed | happy-flow, fail-unknown-credential-identifier (certify-shim-on) |
| F-CERT-3 | Certify | confirmed | happy-flow-additional-requests, happy-flow-multiple-clients, happy-flow-skip-notification, fail-on-access-token-in-query (certify-shim-on) |
| F-CERT-4 | Certify | confirmed | fail-unknown-credential-configuration (certify-shim-on) |
| F-CERT-5 | Certify | confirmed | metadata-test, metadata-test-signed (both Certify configs) |
| F-VER-1 | Verify | confirmed | all 9 (verify-redirect-uri) |
| F-VER-2 | Verify | confirmed | x509_san_dns presentations |
| F-VER-3 | Verify | confirmed | happy paths (verify-redirect-uri) |
| F-VER-4 | — (informational) | permitted behaviour | invalid-credential-signature, invalid-kb-jwt-signature, invalid-sd-hash |
| F-VER-5 | OIDF suite (failure); Verify (ES256 for HAIP) | suite limitation | 10 of 11 (verify-x509) |

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

### F-CERT-3: proof JWT `iss` rejected after an authenticated pre-authorized token request
- **Observed.** The suite authenticates at Certify's token endpoint with `private_key_jwt`: the pre-authorized token request carries `client_assertion`, and Certify answers 200. The access token Certify issues has `"client_id": ""`. The suite's proof JWT then carries `iss` = the client id (`52480754053`, from the template), and the credential endpoint answers `400 {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."}`. Certify's log gives the cause: `BadJWTException: JWT iss claim has value 52480754053, must be` followed by an empty value.
- **Cause in Certify's source** (`0d52155`):
  - On the pre-authorized grant, the token endpoint reads only `grant_type`, `pre-authorized_code` and `tx_code`. Client authentication is ignored (`certify-service/.../controller/OAuthController.java:115-120`).
  - The token is minted with an empty client id (`services/PreAuthorizedCodeService.java`, `generateAccessToken`).
  - When `iss` is present, proof validation requires it to equal the token's `client_id` (`proof/JwtProofValidator.java:101-102`).
- **Spec.**
  - OpenID4VCI 1.0 Appendix F.1: `iss` "MUST be the client_id of the Client making the Credential request. This claim MUST be omitted if the access token … was obtained from a Pre-Authorized Code Flow through anonymous access to the token endpoint." The suite's request was not anonymous.
  - §6.1 makes client authentication optional for this grant.
  - §12.3: `pre-authorized_grant_anonymous_access_supported` defaults to false, and Certify doesn't advertise it.
- **Not a harness setting.** The suite's issuer modules can't run with client auth `none`: it is marked not applicable on the FAPI2 base class they extend (`fapi2spfinal/AbstractFAPI2SPFinalServerTestModule.java:197-199`). The proof builder always sets `iss` to the client id (`vci10issuer/condition/VCIGenerateJwtProof.java:48,104`).
- **Evidence.**
  - `evidence/sp0/baseline-v0-certify/reasons.md` (rows `happy-flow-additional-requests`, `happy-flow-multiple-clients`, `happy-flow-skip-notification`, `fail-on-access-token-in-query`).
  - `evidence/sp2/live/stability.md` (certify-shim-on).
  - `evidence/sp5/triage.md` (token request and decoded token).
- **Suggested fix.** When the client authenticates on the pre-authorized grant, authenticate it and put its `client_id` in the access token. If anonymous access is intended as well, advertise `pre-authorized_grant_anonymous_access_supported: true`.

### F-CERT-4: wrong error code for an unknown credential configuration
- **Observed.** A credential request for an unknown `credential_configuration_id` returns `400 {"error":"invalid_credential_request","error_description":"No credential configuration found for credential_configuration_id"}`.
- **Spec.** OpenID4VCI 1.0 defines the credential error code `unknown_credential_configuration` for this case; the suite checks for it (`VCIValidateCredentialErrorResponse`).
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (row `fail-unknown-credential-configuration`).
- **Suggested fix.** Return `unknown_credential_configuration`.

### F-CERT-5: issuer metadata schema errors; signed metadata not served
- **Observed.** (a) `metadata-test` fails `VCICredentialIssuerMetadataValidation` ("Found invalid entries in OID4VCI Credential Issuer metadata input"; suite requirement `OID4VCI-1FINAL-12.2.3`), because Certify emits `null` for unset optional display fields such as `logo` and `background_color`. (b) `metadata-test-signed` fails `EnsureContentTypeApplicationJwt`. A request with `Accept: application/jwt` gets `200` with an empty body and no `Content-Type` header ("Couldn't find content-type header in endpoint_response"). The suite would *skip* this module if Certify answered with `application/json` (`vci10issuer/VCIIssuerMetadataSignedTest.java:46-50`), so the failure comes from the missing media type, not from the missing signature. Certify's endpoint `produces` only `application/json` (`certify-service/.../controller/WellKnownController.java:30`), and its exception advice turns the resulting `HttpMediaTypeNotAcceptableException` into HTTP 200 (`advice/ExceptionHandlerAdvice.java:79-81,143-146`).
- **Evidence.** `evidence/sp0/baseline-v0-certify/reasons.md` (rows `metadata-test`, `metadata-test-signed`, including the start of the metadata body); `evidence/sp2/live/stability.md` (both Certify configs); `runner/tests/fixtures/certify-shim-off.jsonl` (full condition list). It is the one Certify known issue in the testrig patch (`F-CERT-5------OIDF_certify_oid4vci-1_0-issuer-metadata-test`), hence `KI-1` in both Certify report names (`evidence/sp3/SP3.4/counts-check.md`).
- **Spec.** OpenID4VCI 1.0 §12.2.2: "The Credential Issuer MUST respond with HTTP Status Code 200 and return the Credential Issuer Metadata … as either an unsigned JSON document using the media type application/json, or a signed JSON Web Token …" and "In all cases the Credential Issuer MUST indicate the media type of the returned Metadata using the HTTP Content-Type header." Signed metadata itself is optional (MAY).
- **Suggested fix.** (a) Omit unset optional fields instead of emitting `null`. (b) When the `Accept` header can't be met, fall back to the JSON metadata with `Content-Type: application/json`. Signing support is optional and can come later.

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
- **Suite source.**
  - The x5c path verifies with Nimbus `DefaultJWSVerifierFactory` and the leaf's `java.security.PublicKey` (`condition/AbstractValidateX5cCertificateChain.java:102-110`). That fails for EdDSA with "Unsupported JWS algorithm".
  - The suite's JWKS path for the same request object verifies Ed25519 explicitly with `Ed25519Verifier` (`condition/as/ValidateRequestObjectSignature.java:88-92`).
- **Spec.**
  - OpenID4VP 1.0 §5.9.3 (`x509_san_dns`) only requires the request to be signed with the key of the leaf in `x5c`. No algorithm is restricted.
  - HAIP 1.0 §7 requires Wallets to support at least ES256 for validating signed presentation requests, and §5 requires the `x509_hash` client id prefix for signed requests.
- **Conclusion.** The observed failures are a **suite limitation**: its x5c check should accept Ed25519 leaves as its JWKS check does. That is an issue for the OIDF suite. Separately, Verify needs ES256 (P-256) request-object signing, with a configurable algorithm, to interoperate with HAIP wallets and to self-certify. That is a Verify feature gap, not an OpenID4VP 1.0 violation. Triage: `evidence/sp5/triage.md`.

## Skipped modules

These are not findings, but they are listed so no module is unaccounted for:
- `oid4vci-1_0-issuer-batch-issuance` (shim on): Certify's metadata has no `batch_credential_issuance`, so the suite skips.
- `oid4vci-1_0-issuer-fail-invalid-key-attestation-signature` (shim on): the credential configuration uses `jwt` proofs without key attestations; not applicable.
- `oid4vp-1final-verifier-request-uri-method-post` (x509): Verify's request has no `request_uri_method=post`; not applicable.

Passing (shim on): `fail-invalid-nonce`, `fail-invalid-jwt-proof-signature`, `fail-missing-proof`. Certify rejects each bad request as required.
