| module | status | result | FAILURE conditions | direct_post response | Verify vp-result |
|---|---|---|---|---|---|
| oid4vp-1final-verifier-happy-flow | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 200 OK {} | SUCCESS ['SUCCESS'] |
| oid4vp-1final-verifier-invalid-credential-signature | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-invalid-kb-jwt-aud | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"Client id validation failed due t |  |
| oid4vp-1final-verifier-invalid-kb-jwt-nonce | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"Nonce validation failed due to in |  |
| oid4vp-1final-verifier-invalid-kb-jwt-signature | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-invalid-sd-hash | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-kb-jwt-iat-in-future | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"KB-JWT iat is in the future beyon |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-past | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"KB-JWT iat is too far in the past |  |
| oid4vp-1final-verifier-minimal-cnf-jwk | FINISHED | FAILED | VP1FinalValidateVpFormatsSupportedInClientMetadata | 200 OK {} | SUCCESS ['SUCCESS'] |
