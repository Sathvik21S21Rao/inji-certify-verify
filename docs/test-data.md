# Test data

Everything a run needs is either checked in (below) or generated on the first run. None of it is a real identity or a production secret. All keys and passwords are local test values.

## Plan configurations (`plans/`)

| File | What it holds |
|---|---|
| `plans/certify/certify-shim-off.json` | OID4VCI issuer plan, variant, suite client settings, and the credential offer the handoff plugin sends to Certify. Benchmark of record. |
| `plans/certify/certify-shim-on.json` | Same, with the AS-metadata shim on (diagnostic pass only). |
| `plans/verify/verify-redirect-uri.json` | OID4VP verifier plan, `redirect_uri` client-ID mode, and the VP request sent to Verify. |
| `plans/verify/verify-x509.json` | Same plan, `x509_san_dns` client-ID mode with signed request objects. |
| `plans/*/*.benchmark.json` | Expected outcome, first failing condition and expected warnings per module. The gate compares each run against these. |

Field reference: [`plans/README.md`](../plans/README.md) and [usage.md](usage.md).

## Credential issued by Certify

| Item | Value | Source |
|---|---|---|
| Credential configuration | `ConformanceSdJwt`, format `dc+sd-jwt`, vct `urn:mosip:conformance:sdjwt`, signed ES256 | `plans/certify/credential-config.json`, seeded by `scripts/seed-certify.sh` (`compose/seed/certify-sdjwt-config.json`) |
| Claims in the offer | `given_name` = Ada, `family_name` = Lovelace, `birthdate` = 1815-12-10 | `handoff.offer.claims` in the Certify plan configs |
| Transaction code | `493817` | `handoff.offer.tx_code` |
| Offer lifetime | 600 s | `handoff.offer.expires_in` |

## Suite clients (the wallet side)

| Plan | Client | Keys |
|---|---|---|
| Certify | `client_id` 52480754053 (EC P-256, ES256), `client2` 61732691006 (RSA, PS256), scope `accounts` | Test JWKS inline in the plan config. They are the OIDF suite's own example keys. |
| Verify, `redirect_uri` | `redirect_uri:https://verify-tls/v1/verify/v2/vp-submission/direct-post` | none |
| Verify, `x509_san_dns` | `x509_san_dns:test.example.com` | Verify signs with the generated leaf certificate below; the suite trusts the generated test CA (`VERIFY_X509_CA_PEM`). |

The VP request asks for a `dc+sd-jwt` credential with vct `urn:eudi:pid:1` and the claims `given_name` and `family_name` (DCQL, in `handoff.vp_request`).

## Certificates and keys generated on the first run

`scripts/gen-certs.sh` writes these under `data/certs/` (git-ignored). Rerun with `--force` to regenerate.

| File | Purpose |
|---|---|
| `tls/tls.crt`, `tls/tls.key` | Self-signed RSA certificate for the `certify-tls` and `verify-tls` TLS fronts (SANs `certify-tls`, `verify-tls`, `localhost`) |
| `ca/ca.pem`, `ca/ca.key` | "Conformance Harness Test CA" (EC P-256) |
| `verify/leaf.pem`, `verify/leaf.key` | Ed25519 leaf `CN=test.example.com`, issued by the test CA |
| `verify/verify-signing.p12` | The leaf as PKCS#12 for Verify's signing key; password `mosip` |

## Service credentials

| Service | Credential | Where |
|---|---|---|
| MinIO (report storage) | `minioadmin` / `minioadmin`, bucket `automation` | `compose/minio.yml`, `scripts/run-conformance.sh` |
| OIDF suite | no login (local dev mode) | `compose/suite.yml` |
| Certify and Verify databases | upstream compose defaults | upstream `docker-compose` files, unchanged |

## Fault-injection inputs

| Input | Effect |
|---|---|
| `CONFORMANCE_FAULT=strip-credential-endpoint` | The TLS proxy removes `credential_endpoint` from Certify's issuer metadata |
| `CONFORMANCE_FAULT=strip-nonce-endpoint` | Removes `nonce_endpoint` |
| `CONFORMANCE_CERTIFY_RELEASE=0.14` | Runs Certify v0.14.0 (draft-13 OpenID4VCI) against the 1.0 benchmark, seeded with `compose/seed/certify-sdjwt-config-0.14.json` |

All inputs are listed in [usage.md](usage.md).

Expected results for each are in [test-cases-and-results.md](test-cases-and-results.md#negative-controls).
