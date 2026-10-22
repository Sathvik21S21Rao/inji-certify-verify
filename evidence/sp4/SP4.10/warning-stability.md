| config | module | runs | distinct warning sets | stable | warning set(s) |
|---|---|---|---|---|---|
| certify-shim-off | oid4vci-1_0-issuer-metadata-test | 9/9 | 1 | yes | CheckForUnexpectedParametersInCredentialIssuerMetadata,CheckForUnexpectedParametersInServerMetadata,VCIValidateFormatOfCredentialConfigurationsInMetadata |
| certify-shim-off | oid4vci-1_0-issuer-metadata-test-signed | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-happy-flow | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-happy-flow-additional-requests | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-happy-flow-multiple-clients | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-happy-flow-skip-notification | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-batch-issuance | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-invalid-nonce | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-missing-proof | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-unknown-credential-configuration | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-unknown-credential-identifier | 9/9 | 1 | yes | (none) |
| certify-shim-off | oid4vci-1_0-issuer-fail-on-access-token-in-query | 9/9 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-metadata-test | 4/4 | 1 | yes | CheckForUnexpectedParametersInCredentialIssuerMetadata,CheckForUnexpectedParametersInServerMetadata,VCIValidateFormatOfCredentialConfigurationsInMetadata |
| certify-shim-on | oid4vci-1_0-issuer-metadata-test-signed | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-happy-flow | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-happy-flow-additional-requests | 4/4 | 1 | yes | RequireOnlyBCP195RecommendedCiphersForTLS12 |
| certify-shim-on | oid4vci-1_0-issuer-happy-flow-multiple-clients | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-happy-flow-skip-notification | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-batch-issuance | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-invalid-nonce | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-invalid-jwt-proof-signature | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-invalid-key-attestation-signature | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-missing-proof | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-unknown-credential-configuration | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-unknown-credential-identifier | 4/4 | 1 | yes | (none) |
| certify-shim-on | oid4vci-1_0-issuer-fail-on-access-token-in-query | 4/4 | 1 | yes | (none) |
| verify-redirect-uri | oid4vp-1final-verifier-happy-flow | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-minimal-cnf-jwk | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-invalid-kb-jwt-signature | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-invalid-credential-signature | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-invalid-sd-hash | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-invalid-kb-jwt-nonce | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-invalid-kb-jwt-aud | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-kb-jwt-iat-in-past | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-redirect-uri | oid4vp-1final-verifier-kb-jwt-iat-in-future | 9/9 | 1 | yes | VP1FinalCheckForUnexpectedParametersInVpClientMetadata |
| verify-x509 | oid4vp-1final-verifier-happy-flow | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-minimal-cnf-jwk | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-request-uri-method-post | 9/9 | 1 | yes | (none) |
| verify-x509 | oid4vp-1final-verifier-request-uri-fetched-twice | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-invalid-kb-jwt-signature | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-invalid-credential-signature | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-invalid-sd-hash | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-invalid-kb-jwt-nonce | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-invalid-kb-jwt-aud | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-kb-jwt-iat-in-past | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |
| verify-x509 | oid4vp-1final-verifier-kb-jwt-iat-in-future | 9/9 | 1 | yes | ValidateRequestObjectIssIfPresent |

unstable modules: 0
certify-shim-off: evidence/sp2/live/certify-shim-off/run1/results.jsonl, evidence/sp2/live/certify-shim-off/run2/results.jsonl, evidence/sp2/live/certify-shim-off/run3/results.jsonl, evidence/sp4/SP4.4/kg-combined-par1/certify-shim-off/results.jsonl, evidence/sp4/SP4.4/kg-combined-par2/certify-shim-off/results.jsonl, evidence/sp4/SP4.4/kg-combined-par3/certify-shim-off/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq1/certify-shim-off/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq2/certify-shim-off/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq3/certify-shim-off/results.jsonl
certify-shim-on: evidence/sp2/live/certify-shim-on/run1/results.jsonl, evidence/sp2/live/certify-shim-on/run2/results.jsonl, evidence/sp2/live/certify-shim-on/run3/results.jsonl, evidence/sp4/SP4.4/kg-certify-shim-on/certify-shim-on/results.jsonl
verify-redirect-uri: evidence/sp2/live/verify-redirect-uri/run1/results.jsonl, evidence/sp2/live/verify-redirect-uri/run2/results.jsonl, evidence/sp2/live/verify-redirect-uri/run3/results.jsonl, evidence/sp4/SP4.4/kg-combined-par1/verify-redirect-uri/results.jsonl, evidence/sp4/SP4.4/kg-combined-par2/verify-redirect-uri/results.jsonl, evidence/sp4/SP4.4/kg-combined-par3/verify-redirect-uri/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq1/verify-redirect-uri/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq2/verify-redirect-uri/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq3/verify-redirect-uri/results.jsonl
verify-x509: evidence/sp2/live/verify-x509/run1/results.jsonl, evidence/sp2/live/verify-x509/run2/results.jsonl, evidence/sp2/live/verify-x509/run3/results.jsonl, evidence/sp4/SP4.4/kg-combined-par1/verify-x509/results.jsonl, evidence/sp4/SP4.4/kg-combined-par2/verify-x509/results.jsonl, evidence/sp4/SP4.4/kg-combined-par3/verify-x509/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq1/verify-x509/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq2/verify-x509/results.jsonl, evidence/sp4/SP4.4/kg-combined-seq3/verify-x509/results.jsonl
