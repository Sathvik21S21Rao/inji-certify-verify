### Gate certify-shim-off: GREEN (14 ok)
run `20261021190410-ebe3` · benchmark: Benchmark of record: Inji Certify 1.0.x, AS-metadata shim OFF · flags: certify_as_metadata_shim=false
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

### Gate verify-redirect-uri: GREEN (9 ok)
run `20261021190410-8188` · benchmark: Benchmark of record: Inji Verify 1.0.x, redirect_uri / url_query / direct_post · flags: verify_evidence_upload=true
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
run `20261021190418-1a87` · benchmark: Benchmark of record: Inji Verify 1.0.x, x509_san_dns / request_uri_signed / direct_post · flags: verify_evidence_upload=true
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
