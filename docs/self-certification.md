# Self-certification

**Short version.** The results this harness produces are useful conformance signal, but they cannot be submitted for OpenID certification today. The certification plans for issuers and verifiers are the HAIP plans, and Inji Certify 1.0.x and Inji Verify 1.0.x lack features those plans require. This page explains why, what a vendor would need in order to self-certify, and what closes each gap.

## Why the harness runs the non-HAIP plans

At the pinned suite tag (`release-v5.3.3`), the plans the harness runs are labelled by the suite itself as not part of certification:

- `oid4vci-1_0-issuer-test-plan`: "OpenID for Verifiable Credential Issuance 1.0 Final: Test an issuer – alpha tests (not part of certification program – use the HAIP issuer plan to certify)"
- `oid4vp-1final-verifier-test-plan`: "OpenID for Verifiable Presentations 1.0 Final: Test a verifier – alpha tests (not part of certification program – use the HAIP verifier plan to certify)"

The certification plans are `oid4vci-1_0-issuer-haip-test-plan` and `oid4vp-1final-verifier-haip-test-plan` (`vci10issuer/VCIIssuerTestPlanHaip.java` and `vp1finalverifier/VP1FinalVerifierTestPlanHaip.java` in the suite source). They fix variants the components cannot meet:

| HAIP plan | Fixed variants (from the suite source) | Inji 1.0.x today |
|---|---|---|
| Issuer | profile `vci_haip`; client authentication `client_attestation`; grant `authorization_code`; DPoP; plus the FAPI 2.0 Security Profile modules, and an encrypted-credential pass | Certify has no client-attestation client authentication. The compose stack has no authorization server the suite can drive for `authorization_code`, and Certify publishes no `authorization_endpoint` (F-CERT-1). |
| Verifier | profile `haip`; client id prefix `x509_hash`; request method `request_uri_signed` | Verify supports `decentralized_identifier`, `x509_san_dns` and `redirect_uri` client ids, not `x509_hash`. It signs request objects with EdDSA only (F-VER-5), while HAIP wallets are only required to verify ES256 (HAIP 1.0 §7). HAIP also requires `direct_post.jwt`; Verify supports `direct_post` and `dc_api`. |

So both HAIP plans would fail at setup, before testing anything. Running them would add no information beyond this table, which is why the harness targets the 1.0 plans that do run end to end and reports the HAIP gaps as findings ([findings.md](findings.md)).

## What a vendor needs in order to self-certify

OpenID certification is self-certification: the implementer runs the certification test plan, and the OpenID Foundation publishes the declared results. For an Inji deployment:

1. **A deployment that passes the HAIP plan** for its role (issuer or verifier), with every module PASSED. For verifiers, the happy paths end in REVIEW (screenshot evidence) and must be reviewable.
2. **A run on the suite instance the OpenID Foundation hosts for certification**, against a deployment that instance can reach. A locally run suite, like the one in this harness, is for development. The harness's own setup also departs from a certifiable run in ways that must go: test certificates, the self-signed TLS front, the AS-metadata shim, and the automated verifier screenshot.
3. **The exported test logs** for the plan, plus a signed declaration of conformance and the certification fee, as set out on the OpenID Foundation's certification pages. Check those pages for the current process and fees before planning a submission; this harness doesn't automate it.

The harness helps with step 1: once the gaps below are closed, the same runner can drive the HAIP plans. That needs a template with the HAIP plan name and variant, and a handoff for the `authorization_code` login. Steps 2 and 3 are deliberately manual.

## Gap list

| # | Component | Gap | Required by | What closes it | Evidence today |
|---|---|---|---|---|---|
| G1 | Certify | Client authentication with wallet/client attestation | HAIP issuer plan (`client_attestation`) | Implement attestation-based client authentication at the token endpoint | Not found in Certify 1.0.x |
| G2 | Certify | `authorization_code` flow the suite can drive, with `authorization_endpoint` in AS metadata | HAIP issuer plan; RFC 8414 (F-CERT-1) | Publish `authorization_endpoint` and support a browser-drivable authorization flow (or an AS such as eSignet that does) | `evidence/sp2/live/stability.md` (12 of 14 stop at `CheckServerConfiguration`) |
| G3 | Certify | Ignore unknown request fields; correct error codes; metadata without `null`s | OID4VCI 1.0 (F-CERT-2, F-CERT-4, F-CERT-5) | Fixes listed in [findings.md](findings.md) | `evidence/sp0/baseline-v0-certify/reasons.md` |
| G4 | Certify | Proof `iss` handling when a client authenticated (F-CERT-3) | OID4VCI 1.0 App. F.1 | Authenticate the client on the pre-authorized grant and put its `client_id` in the access token | `evidence/sp0/baseline-v0-certify/reasons.md` |
| G5 | Verify | `x509_hash` client id prefix | HAIP verifier plan | Implement `x509_hash` | Not found in Verify 1.0.x |
| G6 | Verify | ES256 (P-256) request-object signing | HAIP 1.0 §7 | Accept an EC key and sign with ES256 (F-VER-5) | `evidence/sp2/live/stability.md` (verify-x509) |
| G7 | Verify | `direct_post.jwt` (encrypted responses) | HAIP | Implement `direct_post.jwt` | Not found in Verify 1.0.x |
| G8 | Verify | Trust-anchor validation of credential issuers | HAIP trust model (F-VER-3) | Validate issuer chains against configured anchors | `evidence/sp0/baseline-v0-verify/reasons.md` |
| G9 | Verify | `client_metadata` in requests; prefixed `aud` accepted | OID4VP 1.0 (F-VER-1, F-VER-2) | Fixes listed in [findings.md](findings.md) | `evidence/sp0/baseline-v0-verify/reasons.md`, `…-x509/reasons.md` |
| G10 | Harness | HAIP plan templates and an `authorization_code` handoff | — | Add HAIP templates under `plans/<component>/`, benchmark them, and extend `runner/handoff.py` to complete the login | — |

When G1–G2 (issuer) or G5–G7 (verifier) are closed, add the HAIP template, run it with `python -m runner run`, and baseline it with `benchmark init`. The gate then tracks progress towards certification module by module, exactly as it does for the 1.0 plans.
