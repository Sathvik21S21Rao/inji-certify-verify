| module | status | result | FAILURE conditions | direct_post response | Verify vp-result |
|---|---|---|---|---|---|
| oid4vp-1final-verifier-happy-flow | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-invalid-credential-signature | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-invalid-kb-jwt-aud | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"Client id validation failed due t |  |
| oid4vp-1final-verifier-invalid-kb-jwt-nonce | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"Nonce validation failed due to in |  |
| oid4vp-1final-verifier-invalid-kb-jwt-signature | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-invalid-sd-hash | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-kb-jwt-iat-in-future | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"KB-JWT iat is in the future beyon |  |
| oid4vp-1final-verifier-kb-jwt-iat-in-past | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 400 BAD_REQUEST {"errorCode":"invalid_request","errorMessage":"KB-JWT iat is too far in the past |  |
| oid4vp-1final-verifier-minimal-cnf-jwk | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-request-uri-fetched-twice | FINISHED | FAILED | ValidateRequestObjectSignatureAgainstX5cHeader | 200 OK {} | FAILED ['INVALID'] |
| oid4vp-1final-verifier-request-uri-method-post | FINISHED | SKIPPED |  |  |  |
