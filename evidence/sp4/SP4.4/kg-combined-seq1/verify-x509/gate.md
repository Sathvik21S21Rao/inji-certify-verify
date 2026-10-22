### Gate verify-x509: GREEN (11 ok)
run `20261021184500-9450` · benchmark: Benchmark of record: Inji Verify 1.0.x, x509_san_dns / request_uri_signed / direct_post · flags: verify_evidence_upload=true
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
