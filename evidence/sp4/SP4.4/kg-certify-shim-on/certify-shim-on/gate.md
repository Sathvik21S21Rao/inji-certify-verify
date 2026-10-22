### Gate certify-shim-on: GREEN (14 ok)
run `20261021184933-551b` · benchmark: DIAGNOSTIC ONLY (not the benchmark of record): Inji Certify 1.0.x with AS-metadata shim ON (F-CERT-1 masked) · flags: certify_as_metadata_shim=true
| module | expected | observed | verdict | finding | detail |
|---|---|---|---|---|---|
| oid4vci-1_0-issuer-metadata-test | FAILED VCICredentialIssuerMetadataValidation | FAILED VCICredentialIssuerMetadataValidation | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-metadata-test-signed | FAILED EnsureContentTypeApplicationJwt | FAILED EnsureContentTypeApplicationJwt | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-happy-flow | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-2 |  |
| oid4vci-1_0-issuer-happy-flow-additional-requests | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-happy-flow-multiple-clients | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-happy-flow-skip-notification | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-batch-issuance | SKIPPED | SKIPPED | OK |  |  |
| oid4vci-1_0-issuer-fail-invalid-nonce | PASSED | PASSED | OK |  |  |
| oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | PASSED | PASSED | OK |  |  |
| oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | SKIPPED | SKIPPED | OK |  |  |
| oid4vci-1_0-issuer-fail-missing-proof | PASSED | PASSED | OK |  |  |
| oid4vci-1_0-issuer-fail-unknown-credential-configuration | FAILED VCIValidateCredentialErrorResponse | FAILED VCIValidateCredentialErrorResponse | OK | F-CERT-4 |  |
| oid4vci-1_0-issuer-fail-unknown-credential-identifier | FAILED VCIValidateCredentialErrorResponse | FAILED VCIValidateCredentialErrorResponse | OK | F-CERT-2 |  |
| oid4vci-1_0-issuer-fail-on-access-token-in-query | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
