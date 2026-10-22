### Gate certify-shim-on: RED (regression 1)
run `20261021192417-7521` · benchmark: DIAGNOSTIC ONLY (not the benchmark of record): Inji Certify 1.0.x with AS-metadata shim ON (F-CERT-1 masked) · flags: certify_as_metadata_shim=true
| module | expected | observed | verdict | finding | detail |
|---|---|---|---|---|---|
| oid4vci-1_0-issuer-metadata-test | FAILED VCICredentialIssuerMetadataValidation | FAILED VCICredentialIssuerMetadataValidation | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-metadata-test-signed | FAILED EnsureContentTypeApplicationJwt | FAILED EnsureContentTypeApplicationJwt | OK | F-CERT-5 |  |
| oid4vci-1_0-issuer-happy-flow | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-2 |  |
| oid4vci-1_0-issuer-happy-flow-additional-requests | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-happy-flow-multiple-clients | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-happy-flow-skip-notification | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |
| oid4vci-1_0-issuer-batch-issuance | SKIPPED | SKIPPED | OK |  |  |
| oid4vci-1_0-issuer-fail-invalid-nonce | PASSED | FAILED VCIValidateCredentialErrorResponse | REGRESSION |  |  |
| oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | PASSED | PASSED | OK |  |  |
| oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | SKIPPED | SKIPPED | OK |  |  |
| oid4vci-1_0-issuer-fail-missing-proof | PASSED | PASSED | OK |  |  |
| oid4vci-1_0-issuer-fail-unknown-credential-configuration | FAILED VCIValidateCredentialErrorResponse | FAILED VCIValidateCredentialErrorResponse | OK | F-CERT-4 |  |
| oid4vci-1_0-issuer-fail-unknown-credential-identifier | FAILED VCIValidateCredentialErrorResponse | FAILED VCIValidateCredentialErrorResponse | OK | F-CERT-2 |  |
| oid4vci-1_0-issuer-fail-on-access-token-in-query | FAILED EnsureHttpStatusCodeIsAnyOf | FAILED EnsureHttpStatusCodeIsAnyOf | OK | F-CERT-3 |  |

### Gate verify-redirect-uri: GREEN (9 ok)
run `20261021192433-c4fd` · benchmark: Benchmark of record: Inji Verify 1.0.x, redirect_uri / url_query / direct_post · flags: verify_evidence_upload=true
| module | expected | observed | verdict | finding | detail |
|---|---|---|---|---|---|
| oid4vp-1final-verifier-happy-flow | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-minimal-cnf-jwk | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-signature | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-invalid-credential-signature | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-invalid-sd-hash | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-nonce | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-aud | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-past | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-future | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | FAILED VP1FinalValidateVpFormatsSupportedInClientMetadata | OK | F-VER-1 |  |

### Gate verify-x509: GREEN (11 ok)
run `20261021192439-2714` · benchmark: Benchmark of record: Inji Verify 1.0.x, x509_san_dns / request_uri_signed / direct_post · flags: verify_evidence_upload=true
| module | expected | observed | verdict | finding | detail |
|---|---|---|---|---|---|
| oid4vp-1final-verifier-happy-flow | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-minimal-cnf-jwk | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-request-uri-method-post | SKIPPED | SKIPPED | OK |  |  |
| oid4vp-1final-verifier-request-uri-fetched-twice | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-signature | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-invalid-credential-signature | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-invalid-sd-hash | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-nonce | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-invalid-kb-jwt-aud | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-past | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-future | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | FAILED ValidateRequestObjectSignatureAgainstX5cHeader | OK | F-VER-5 |  |
