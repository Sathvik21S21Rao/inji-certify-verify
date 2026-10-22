### Gate verify-redirect-uri: GREEN (9 ok)
run `20261021190049-2599` · benchmark: Benchmark of record: Inji Verify 1.0.x, redirect_uri / url_query / direct_post · flags: verify_evidence_upload=true
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
