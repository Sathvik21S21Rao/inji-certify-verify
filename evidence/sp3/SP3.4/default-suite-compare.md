## injicertify (`certify`)

| field | before | after | same |
|---|---|---|---|
| exit code | 1 | 1 | yes |
| testng-report produced | False | False | yes |
| full-report filename | None | None | yes |
| test-method count (non-config) | 0 | 0 | yes |
| distinct test-method names | 0 | 0 | yes |
| test classes | 0 | 0 | yes |

- first test line index: before=None, after=None
- log lines before the first test identical (timestamps stripped): NO (1170 vs 1170 lines)
```diff
--- before
+++ after
@@ -3,0 +4,16 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/valueMapping.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/valueMapping.properties to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_landregistry.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_landregistry.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/internalAuthRequest.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/internalAuthRequest.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/landRegistryDataDeleteQueries.txt
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/landRegistryDataDeleteQueries.txt to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/healthCheckEndpoint.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/healthCheckEndpoint.properties to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/injiCertify.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/injiCertify.properties to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/idRepoToken.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/idRepoToken.properties to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_mdl.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_mdl.json to external resource successfully..!
@@ -6,14 +22,6 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/internalAuthRequest.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/internalAuthRequest.json to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_preauthcode.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_preauthcode.json to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_landregistry.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_landregistry.json to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/masterDataCertDataDeleteQueries.txt
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/masterDataCertDataDeleteQueries.txt to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/valueMapping.properties
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/valueMapping.properties to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/landRegistryDataDeleteQueries.txt
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/landRegistryDataDeleteQueries.txt to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/idaCertDataDeleteQueries.txt
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/idaCertDataDeleteQueries.txt to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/request.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/request.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/esignetPayload.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/esignetPayload.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/application.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/application.properties to external resource successfully..!
@@ -24,4 +32,6 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/request.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/request.json to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_mdl.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_mdl.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/keyManagerCertDataDeleteQueries.txt
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/keyManagerCertDataDeleteQueries.txt to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/OtpGeneration/request.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/OtpGeneration/request.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_mosipid.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_mosipid.json to external resource successfully..!
@@ -30,4 +40,8 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/idRepoToken.properties
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/idRepoToken.properties to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_mosipid.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_mosipid.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/idaCertDataDeleteQueries.txt
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/idaCertDataDeleteQueries.txt to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injicertify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency_mock.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency_mock.json to external resource successfully..!
```
- whole docker log: same line multiset NO; same order NO (1170 vs 1170 lines)
```diff
--- before
+++ after
@@ -5,3 +5,3 @@
-	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.main(InjiTestRunner.java:101)
-	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.main(InjiTestRunner.java:82)
-	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.suiteSetup(InjiTestRunner.java:192)
+	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.main(InjiTestRunner.java:105)
+	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.main(InjiTestRunner.java:86)
+	at io.inji.testrig.apirig.injicertify.testrunner.InjiTestRunner.suiteSetup(InjiTestRunner.java:196)
```

## injiverify (`verify`)

| field | before | after | same |
|---|---|---|---|
| exit code | 0 | 0 | yes |
| testng-report produced | True | True | yes |
| full-report filename | mosip-local-injiverify-2026-10-21_12-51-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html | mosip-local-injiverify-2026-10-21_13-02-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html | NO |
| test-method count (non-config) | 279 | 279 | yes |
| distinct test-method names | 1 | 1 | yes |
| test classes | 7 | 7 | yes |
| test-method name multiset identical | | | yes |
| class set identical | | | yes |

- first test line index: before=521, after=521
- log lines before the first test identical (timestamps stripped): NO (521 vs 521 lines)
```diff
--- before
+++ after
@@ -6,0 +7,4 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/request.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/request.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/DB_delete_script.txt
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/DB_delete_script.txt to external resource successfully..!
@@ -11,8 +14,0 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/injiVerify.properties
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/injiVerify.properties to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/Authorization/request.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/Authorization/request.json to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/DB_delete_script.txt
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/DB_delete_script.txt to external resource successfully..!
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency.json
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency.json to external resource successfully..!
@@ -22,0 +19,4 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/testCaseInterDependency.json
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/testCaseInterDependency.json to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/config/injiVerify.properties
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: config/injiVerify.properties to external resource successfully..!
@@ -34,0 +35,2 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/dbFiles/dbConfig.xml
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: dbFiles/dbConfig.xml to external resource successfully..!
@@ -37,2 +38,0 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/dbFiles/dbConfig.xml
-INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: dbFiles/dbConfig.xml to external resource successfully..!
@@ -55,0 +56,22 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/CreateVpRequestWithSDJWT/CreateVpRequestWithSDJWT.yml
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/CreateVpRequestWithSDJWT/CreateVpRequestWithSDJWT.yml to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/CreateNewVerificationRequestWithProof/CreateVpRequestWithDCQLWithoutVC.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/CreateNewVerificationRequestWithProof/CreateVpRequestWithDCQLWithoutVC.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/VpSubmission/VpSubmissionSdJwtKbJwtNeg.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/VpSubmission/VpSubmissionSdJwtKbJwtNeg.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/VcVerificationV2/VcVerificationResultV2.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/VcVerificationV2/VcVerificationResultV2.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/VpInvalidSignatureEdge/1_5_ldp_vp_invalid_signature_require_cryptographic_holder_binding_fals_submit.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/VpInvalidSignatureEdge/1_5_ldp_vp_invalid_signature_require_cryptographic_holder_binding_fals_submit.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/VcVerificationV2Edge/ldp_vc_vc_verify_ldp_vc_status_check_error.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/VcVerificationV2Edge/ldp_vc_vc_verify_ldp_vc_status_check_error.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/VpRequestUriEdge/VpRequestUriEdge_GetWithParam.yml
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/VpRequestUriEdge/VpRequestUriEdge_GetWithParam.yml to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/VpRequestUriEdge/1_3_ldp_vp_valid_signature_request_uri_results_v2_vp_results_v2.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/VpRequestUriEdge/1_3_ldp_vp_valid_signature_request_uri_results_v2_vp_results_v2.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/DcqlQueryMatchingEdge/6_8_vp_submission_dcql_query_matching_no_satisfiable_claim_sets_option_create.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/DcqlQueryMatchingEdge/6_8_vp_submission_dcql_query_matching_no_satisfiable_claim_sets_option_create.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/DcqlQueryMatchingEdge/6_9_vp_submission_dcql_query_matching_multiple_credentials_not_allowed_create.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/EdgeTestCases/DcqlQueryMatchingEdge/6_9_vp_submission_dcql_query_matching_multiple_credentials_not_allowed_create.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/VcRevocationStatus/VcRevocationStatusResult.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/VcRevocationStatus/VcRevocationStatusResult.hbs to external resource successfully..!
@@ -57,0 +80,16 @@
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/CreateNewVerificationRequestWithX509SanDns/CreateNewVerificationRequestWithX509SanDns.yml
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/CreateNewVerificationRequestWithX509SanDns/CreateNewVerificationRequestWithX509SanDns.yml to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/GetVpRequestStatus/GetVpRequestStatus.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/GetVpRequestStatus/GetVpRequestStatus.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/VcVerification/VcVerification.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/VcVerification/VcVerification.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/VcVerificationV2/VcVerificationSdJwt.hbs
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - Copied the file: injiverify/VcVerificationV2/VcVerificationSdJwt.hbs to external resource successfully..!
+INFO    <ts> [main] io.mosip.testrig.apirig.testrunner.ExtractResource  - resourceFile : /home/inji/apitest-injiverify-1.0.0-rc.1-SNAPSHOT-jar-with-dependencies.jardestinationFile : /home/inji/MosipTestResource/MosipTemporaryTestResource/injiverify/EdgeTestCases/VpMultipleSubmissionEdge/VpMultipleSubmissionEdge_PostWithBodyAndPathParams.yml
```
- whole docker log: same line multiset NO; same order NO (6763 vs 6763 lines)
```diff
--- before
+++ after
@@ -333,4 +333,4 @@
-	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.main(InjiTestRunner.java:103)
-	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.main(InjiTestRunner.java:103)
-	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.startTestRunner(InjiTestRunner.java:177)
-	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.startTestRunner(InjiTestRunner.java:177)
+	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.main(InjiTestRunner.java:107)
+	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.main(InjiTestRunner.java:107)
+	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.startTestRunner(InjiTestRunner.java:181)
+	at io.inji.testrig.apirig.injiverify.testrunner.InjiTestRunner.startTestRunner(InjiTestRunner.java:181)
@@ -3758,2 +3758,2 @@
-ERROR   <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Error occurred while copying file to mount path: /home/mosip/testrig/report/mosip-local-injiverify-2026-10-21_12-51-error-report_T-279_S-112_F-167_I-0_KI-0.html
-ERROR   <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Error occurred while copying file to mount path: /home/mosip/testrig/report/mosip-local-injiverify-2026-10-21_12-51-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html
+ERROR   <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Error occurred while copying file to mount path: /home/mosip/testrig/report/mosip-local-injiverify-2026-10-21_13-02-error-report_T-279_S-112_F-167_I-0_KI-0.html
+ERROR   <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Error occurred while copying file to mount path: /home/mosip/testrig/report/mosip-local-injiverify-2026-10-21_13-02-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html
@@ -4670,2 +4670,2 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - New reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-error-report_T-279_S-112_F-167_I-0_KI-0.html
-INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - New reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html
+INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - New reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-error-report_T-279_S-112_F-167_I-0_KI-0.html
+INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - New reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-full-report_T-279_P-0_S-112_F-167_I-0_KI-0.html
@@ -4674,2 +4674,2 @@
-INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-report.html
-INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-report.html
+INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-report.html
+INFO    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - reportFile is::/home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-report.html
@@ -6457,2 +6457,2 @@
-WARN    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Failed to delete original report file: /home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-report.html
-WARN    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Failed to delete original report file: /home/inji/testng-report/mosip-local-injiverify-2026-10-21_12-51-report.html
+WARN    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Failed to delete original report file: /home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-report.html
+WARN    <ts> [main] io.mosip.testrig.apirig.report.EmailableReport  - Failed to delete original report file: /home/inji/testng-report/mosip-local-injiverify-2026-10-21_13-02-report.html
```

