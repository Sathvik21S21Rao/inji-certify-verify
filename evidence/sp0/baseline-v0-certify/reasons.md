| module | status | result | first FAILURE (condition: message) | Certify response (if any) |
|---|---|---|---|---|
| oid4vci-1_0-issuer-batch-issuance | FINISHED | SKIPPED | (skipped) Client JWKS already present in configuration, skipping generation |  |
| oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | FINISHED | PASSED |  |  |
| oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | FINISHED | SKIPPED | (skipped) Client JWKS already present in configuration, skipping generation |  |
| oid4vci-1_0-issuer-fail-invalid-nonce | FINISHED | PASSED |  |  |
| oid4vci-1_0-issuer-fail-missing-proof | FINISHED | PASSED |  |  |
| oid4vci-1_0-issuer-fail-on-access-token-in-query | INTERRUPTED | FAILED | EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status | 400 BAD_REQUEST {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."} |
| oid4vci-1_0-issuer-fail-unknown-credential-configuration | INTERRUPTED | FAILED | VCIValidateCredentialErrorResponse: Expected error code not found in credential error response: unknown_credential_configuration | 400 BAD_REQUEST {"error":"invalid_credential_request","error_description":"No credential configuration found for credential_configuration_id"} |
| oid4vci-1_0-issuer-fail-unknown-credential-identifier | INTERRUPTED | FAILED | VCIValidateCredentialErrorResponse: Non-standard credential error response error code found: invalid_request | 400 BAD_REQUEST {"error":"invalid_request","error_description":"Unrecognized field 'credential_identifier' in request"} |
| oid4vci-1_0-issuer-happy-flow-additional-requests | INTERRUPTED | FAILED | EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status | 400 BAD_REQUEST {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."} |
| oid4vci-1_0-issuer-happy-flow-multiple-clients | INTERRUPTED | FAILED | EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status | 400 BAD_REQUEST {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."} |
| oid4vci-1_0-issuer-happy-flow-skip-notification | INTERRUPTED | FAILED | EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status | 400 BAD_REQUEST {"error":"invalid_proof","error_description":"None of the submitted proofs passed validation."} |
| oid4vci-1_0-issuer-happy-flow | INTERRUPTED | FAILED | EnsureHttpStatusCodeIsAnyOf: resource endpoint returned an unexpected http status | 400 BAD_REQUEST {"error":"invalid_request","error_description":"Unrecognized field 'qpZbsrPJIXDtDlJw' in request"} |
| oid4vci-1_0-issuer-metadata-test-signed | INTERRUPTED | FAILED | EnsureContentTypeApplicationJwt: Couldn't find content-type header in endpoint_response | 200 OK  |
| oid4vci-1_0-issuer-metadata-test | FINISHED | FAILED | VCICredentialIssuerMetadataValidation: Found invalid entries in OID4VCI Credential Issuer metadata input | 200 OK {"display":[{"name":"Farmer Issuer","locale":"en"}],"credential_issuer":"https://certify-tls","authorization_servers":["https://certify-tls" |
