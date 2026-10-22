### Gate certify-shim-off: GREEN (14 ok)
run `20261021185541-366d` · benchmark: Benchmark of record: Inji Certify 1.0.x, AS-metadata shim OFF · flags: certify_as_metadata_shim=false
| module | expected | observed | verdict | finding | detail |
|---|---|---|---|---|---|
| oid4vci-1_0-issuer-metadata-test | FAILED VCICredentialIssuerMetadataValidation | FAILED VCICredentialIssuerMetadataValidation | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-metadata-test-signed | FAILED EnsureContentTypeApplicationJwt | FAILED EnsureContentTypeApplicationJwt | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-happy-flow | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-happy-flow-additional-requests | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-happy-flow-multiple-clients | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-happy-flow-skip-notification | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-batch-issuance | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-invalid-nonce | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-missing-proof | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-unknown-credential-configuration | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-unknown-credential-identifier | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
| oid4vci-1_0-issuer-fail-on-access-token-in-query | FAILED CheckServerConfiguration | FAILED CheckServerConfiguration | OK | F-CERT-1 |  |
