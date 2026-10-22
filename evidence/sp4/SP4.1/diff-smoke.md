### Diff certify-shim-off `20261020205530-7d9d` → certify-shim-on `20261020205702-4d84`: 12 of 14 modules changed
note: variant keys differ
| module | A | B | change |
|---|---|---|---|
| oid4vci-1_0-issuer-happy-flow | FAILED CheckServerConfiguration | FAILED EnsureHttpStatusCodeIsAnyOf | first failure changed |
| oid4vci-1_0-issuer-happy-flow-additional-requests | FAILED CheckServerConfiguration | FAILED EnsureHttpStatusCodeIsAnyOf | first failure changed |
| oid4vci-1_0-issuer-happy-flow-multiple-clients | FAILED CheckServerConfiguration | FAILED EnsureHttpStatusCodeIsAnyOf | first failure changed |
| oid4vci-1_0-issuer-happy-flow-skip-notification | FAILED CheckServerConfiguration | FAILED EnsureHttpStatusCodeIsAnyOf | first failure changed |
| oid4vci-1_0-issuer-batch-issuance | FAILED CheckServerConfiguration | SKIPPED | outcome FAILED→SKIPPED |
| oid4vci-1_0-issuer-fail-invalid-nonce | FAILED CheckServerConfiguration | PASSED | outcome FAILED→PASSED |
| oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | FAILED CheckServerConfiguration | PASSED | outcome FAILED→PASSED |
| oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | FAILED CheckServerConfiguration | SKIPPED | outcome FAILED→SKIPPED |
| oid4vci-1_0-issuer-fail-missing-proof | FAILED CheckServerConfiguration | PASSED | outcome FAILED→PASSED |
| oid4vci-1_0-issuer-fail-unknown-credential-configuration | FAILED CheckServerConfiguration | FAILED VCIValidateCredentialErrorResponse | first failure changed |
| oid4vci-1_0-issuer-fail-unknown-credential-identifier | FAILED CheckServerConfiguration | FAILED VCIValidateCredentialErrorResponse | first failure changed |
| oid4vci-1_0-issuer-fail-on-access-token-in-query | FAILED CheckServerConfiguration | FAILED EnsureHttpStatusCodeIsAnyOf | first failure changed |
