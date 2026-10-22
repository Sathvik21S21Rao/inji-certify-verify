# Triage of F-CERT-3, F-CERT-5 (signed part) and F-VER-5

Date 2026-10-22. Sources:
- Spec texts were downloaded from openid.net into `evidence/sp5/specs/` (`*.html` as fetched, `*.txt` text renderings, `sha256.txt`). Line numbers below refer to the `.txt` files. The versions are:
  - OpenID4VCI 1.0, Final, 16 Sep 2025.
  - OpenID4VP 1.0, Final.
  - HAIP 1.0, Final, 24 Dec 2025.
- Suite source is `upstream/conformance-suite` at `7d420f716` (release-v5.3.3). Paths are relative to `src/main/java/net/openid/conformance/`.
- Certify source is `upstream/inji-certify` at `0d52155`. The running image is `bbd913e`, and no `.java` file differs between the two (ADR-006). Verify source is `upstream/inji-verify` at `64b2790`.

| ID | Class | Suggested owner | Change to the benchmark reason |
|---|---|---|---|
| F-CERT-3 | **Component defect** (Certify) | Inji Certify | yes: "triage" is dropped |
| F-CERT-5 (b) signed metadata | **Component defect** (Certify) | Inji Certify | yes |
| F-VER-5 | **Suite limitation** (it causes the observed failures), plus a Verify interoperability gap for HAIP | OIDF conformance suite for the failure; Inji Verify for ES256 | yes |

None of the three is a harness configuration issue. For each, the suite offers no variant or config field that would change the outcome. The reasons are given below.

## F-CERT-3: proof `iss` rejected after an authenticated pre-authorized token request

**What happens.**
1. The suite authenticates at Certify's token endpoint with `private_key_jwt`. The token request carries `client_assertion` next to `pre-authorized_code` and `tx_code` [observed: `evidence/sp2/live/certify-shim-on/run1/oid4vci-1_0-issuer-happy-flow-additional-requests.log.json`, `CallTokenEndpointAllowingDpopNonceErrorAndReturnFullResponse` request body]. Certify answers 200.
2. The access token Certify issues has `"client_id": ""` [observed: the decoded `access_token` in the same log].
3. The suite's proof JWT sets `iss` to `client.client_id` (`52480754053`) [verified: `vci10issuer/condition/VCIGenerateJwtProof.java:48,104`]. Certify rejects it: `BadJWTException: JWT iss claim has value 52480754053, must be` followed by an empty value [observed: `evidence/sp0/s04-certify-container.log:1382`].

**Why, in Certify's source.**
- On the pre-authorized grant, the token endpoint reads only `grant_type`, `pre-authorized_code` and `tx_code`. Any client authentication is ignored [verified: `certify-service/.../controller/OAuthController.java:115-120`].
- The token is minted with an empty client id [verified: `services/PreAuthorizedCodeService.java` `generateAccessToken`, which passes `""` as `clientId` to `AccessTokenJwtUtil.generateSignedJwt`].
- Proof validation then requires `iss` to equal the token's `client_id` whenever `iss` is present [verified: `proof/JwtProofValidator.java:101-102`; `services/CertifyIssuanceServiceImpl.java:153,176`].

So Certify treats every pre-authorized token as anonymous.

**Spec.**
- OID4VCI 1.0 App. F.1 says `iss` "MUST be the client_id of the Client making the Credential request. This claim MUST be omitted if the access token … was obtained from a Pre-Authorized Code Flow through anonymous access to the token endpoint" [verified: `specs/openid-4-verifiable-credential-issuance-1_0.txt:3376`]. The suite's token request was not anonymous: it carried client authentication. So sending `iss` = client_id is required, not just allowed.
- §6.1: client authentication is OPTIONAL for the pre-authorized grant [verified: same file:993]. Certify may therefore support anonymous access. But it must then accept, or bind, a client that does authenticate.
- §12.3 `pre-authorized_grant_anonymous_access_supported` defaults to false [verified: same file:1845]. Certify's AS metadata has no such field [verified: `certify-core/.../OAuthAuthorizationServerMetadataDTO.java`]. So by its own metadata Certify does *not* offer anonymous access, yet that is the only mode it actually implements.

**Not a harness configuration issue.** The suite cannot run the VCI issuer modules without client authentication: `ClientAuthType` `none` is `@VariantNotApplicable` on the FAPI2 base class that every non-metadata issuer module extends [verified: `fapi2spfinal/AbstractFAPI2SPFinalServerTestModule.java:197-199`; `vci10issuer/AbstractVCIIssuerTestModule.java:162`]. The proof builder has no branch that omits `iss` [verified: `VCIGenerateJwtProof.java`]. A suite-side corollary: an anonymous-only issuer cannot be exercised by this plan. That is a coverage note, not the cause here.

**Conclusion.** This is a Certify defect, and the owner is Inji Certify. Suggested fix: on the pre-authorized grant, authenticate the client when client authentication is presented and put its `client_id` in the access token. That makes `JwtProofValidator` accept `iss` = client_id. If anonymous access is intended, also advertise `pre-authorized_grant_anonymous_access_supported: true`.

## F-CERT-5 (b): `Accept: application/jwt` answered with 200, an empty body and no Content-Type

**What happens.** `oid4vci-1_0-issuer-metadata-test-signed` sends `Accept: application/jwt`. Certify answers `200 OK`, `content-length: 0`, with no `Content-Type` header [observed: `evidence/sp4/SP4.14/tr-kg-combined/certify-shim-off/testng-report/conformance/certify-shim-off/oid4vci-1_0-issuer-metadata-test-signed.log.json`, `VCIGetDynamicCredentialIssuerMetadata` response]. The module then fails `EnsureContentTypeApplicationJwt` and `VCIDecodeSignedCredentialIssuerMetadata` (JsonNull body).

**The suite does not fail unsigned issuers.** If the response is `application/json`, the module calls `fireTestSkipped(...)` [verified: `vci10issuer/VCIIssuerMetadataSignedTest.java:46-50`]. It fails here only because Certify sent no media type at all.

**Why, in Certify's source.**
- The endpoint is `@GetMapping(..., produces = "application/json")` [verified: `certify-service/.../controller/WellKnownController.java:30`]. An `Accept: application/jwt` request therefore raises `HttpMediaTypeNotAcceptableException`.
- The advice turns that exception into `ResponseEntity(..., HttpStatus.OK)` with an error wrapper [verified: `advice/ExceptionHandlerAdvice.java:79-81,143-146`].
- That the wrapper can't be written for an `application/jwt`-only client, leaving the body empty and no Content-Type, is [inferred] from Spring's message-converter selection. It fits the observed response. Confirm with `curl -H 'Accept: application/jwt' -i https://<certify>/.well-known/openid-credential-issuer`.

**Spec.** OID4VCI 1.0 §12.2.2 says:
- "The Credential Issuer MUST respond with HTTP Status Code 200 and return the Credential Issuer Metadata … as either an unsigned JSON document using the media type application/json, or a signed JSON Web Token …".
- "MUST support returning metadata in an unsigned form … and MAY support … signed".
- "In all cases the Credential Issuer MUST indicate the media type of the returned Metadata using the HTTP Content-Type header."

[verified: `specs/openid-4-verifiable-credential-issuance-1_0.txt:1587-1600`]

**Conclusion.** This is a Certify defect, and the owner is Inji Certify. Signed metadata is optional, but answering a JWT-preferring wallet with an empty 200 is not allowed. Suggested fix: on an `Accept` that Certify cannot satisfy, fall back to the JSON metadata with `Content-Type: application/json`. For example, drop `produces` or add a fallback handler. The suite would then *skip* the module, which is correct for an issuer that doesn't sign its metadata. Signing support is optional and can follow later. Part (a), the `null` display fields, stays confirmed as before.

## F-VER-5: `x509_san_dns` request objects signed with EdDSA; the suite's x5c check can't verify EdDSA

**What happens.**
- Verify signs request objects with a hard-coded `JWSAlgorithm.EdDSA` and an `Ed25519Signer`, and it accepts only an Ed25519 key entry [verified: `verify-core/.../VerifiablePresentationRequestServiceImpl.java:463,496`; `key/impl/P12KeyExtractor.java:92-106`]. A P-256 leaf stops `verify-service` at startup [observed: `evidence/sp1/fver5/`].
- The suite fails 10 of 11 modules at `ValidateRequestObjectSignatureAgainstX5cHeader` with "Unsupported JWS algorithm: EdDSA" [observed: `evidence/sp4/SP4.14/tr-kg-combined/verify-x509/`]. The chain itself validates [observed: `evidence/sp1/SP1.3/r2-B3-x5c-check.log`].

**Suite source.**
- The x5c path verifies with `new DefaultJWSVerifierFactory().createJWSVerifier(header, leafCert.getPublicKey())` [verified: `condition/AbstractValidateX5cCertificateChain.java:102-110`]. That factory has no EdDSA verifier for a `java.security.PublicKey`; the "Unsupported JWS algorithm" message comes from there [inferred from Nimbus behaviour, and it matches the observed message].
- The suite's JWKS-based check for the same request object handles Ed25519 explicitly with `Ed25519Verifier` [verified: `condition/as/ValidateRequestObjectSignature.java:88-92`].
- So the suite supports EdDSA request objects on one path and not on the other.

**Spec.**
- OID4VP 1.0 §5.9.3 (`x509_san_dns`): "The request MUST be signed with the private key corresponding to the public key in the leaf X.509 certificate …". No algorithm is restricted [verified: `specs/openid-4-verifiable-presentations-1_0.txt:905`].
- HAIP 1.0 §7 requires Wallets to support ES256 at a minimum "for the purpose of validating … signed presentation requests" [verified: `specs/openid4vc-high-assurance-interoperability-profile-1_0.txt:472-490`]. It requires `x509_hash` for signed requests [verified: same file:359].
- HAIP therefore does not literally forbid an EdDSA-signed request. But a HAIP wallet is only guaranteed to verify ES256, so an EdDSA-only verifier is not interoperable under HAIP. (Earlier docs said "HAIP requires ES256 for verifiers". That wording is corrected here.)

**Conclusion.**
- **Suite limitation.** This causes the observed failures in the plain OID4VP 1.0 plan. Owner: the OIDF conformance suite. Raise an issue asking the x5c path to verify Ed25519 leaf keys the same way `ValidateRequestObjectSignature` does.
- **Verify gap.** Verify should support ES256 (P-256) request-object signing, with a configurable algorithm, for HAIP interoperability and self-certification. Owner: Inji Verify. This is a feature gap, not a violation of OID4VP 1.0.
- No harness configuration helps. Verify only accepts an Ed25519 key, and the suite's x5c path only accepts the algorithms its default factory supports.

## Benchmark impact
Only the `reason` texts change. Expectations and fingerprints stay as they are, because nothing observed changed:
- `plans/certify/certify-shim-off.benchmark.json` and `certify-shim-on.benchmark.json`: metadata-test-signed (F-CERT-5).
- `certify-shim-on.benchmark.json`: the four F-CERT-3 rows.
- `plans/verify/verify-x509.benchmark.json`: the F-VER-5 rows.
