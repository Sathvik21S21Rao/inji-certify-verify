# Oracle 2: manual suite-UI run vs harness (procedure for the human)

Goal: run one plan per component **by hand** in the suite web UI, then compare it module by module with a harness run of the same config. The result goes in `evidence/manual-vs-harness.md`. About 40 minutes.

UI labels below were checked in the suite source at `release-v5.3.3`:
- "Create Test Plan": `upstream/conformance-suite/src/main/resources/static/schedule-test.html:894`
- "Run Test" and "Download Logs": `static/components/cts-plan-modules.js:555,574`
- "Download all Logs": `static/components/cts-plan-actions.js:424`. It opens `/api/plan/exporthtml/{planId}`, the same export the harness saves (`plan-detail.html:646-648`).

Anything else about the UI layout is [unknown]. Note what you actually see.

## 0. Harness run first (gives the resolved configs)
```bash
cd <repo>; source env.sh; export CONFORMANCE_PYTHON=<python with runner deps>
flock /tmp/inji-conformance.docker.lock scripts/run-conformance.sh --combined --keep --out evidence/sp5/oracle2/harness
```
`--keep` leaves Certify, Verify and the suite running, so the manual run uses the same stack. The resolved plan configs are written to:
- `evidence/sp5/oracle2/harness/certify-shim-off/testng-report/conformance/certify-shim-off/plan-config.json`
- `evidence/sp5/oracle2/harness/verify-redirect-uri/testng-report/conformance/verify-redirect-uri/plan-config.json`

Make a copy of each and change `"alias"` to `manual-certify` or `manual-verify`, so the manual plan never shares an alias with a harness plan. A shared alias stops the running test (`runner/TestRunner.java:505-521`).

## 1. Certify: `oid4vci-1_0-issuer-test-plan`, config certify-shim-off
1. Open <https://localhost.emobix.co.uk:8443> and accept the self-signed certificate.
2. Choose create a test plan, then pick **OpenID for Verifiable Credential Issuance 1.0 Final: Test an issuer** (`oid4vci-1_0-issuer-test-plan`).
3. Variant, exactly as in `plans/certify/certify-shim-off.json` `variant`:
   - `fapi_profile=vci`
   - `credential_format=sd_jwt_vc`
   - `authorization_request_type=simple`
   - `client_auth_type=private_key_jwt`
   - `fapi_request_method=unsigned`
   - `sender_constrain=dpop`
   - `vci_authorization_code_flow_variant=issuer_initiated`
   - `vci_credential_encryption=plain`
   - `vci_grant_type=pre_authorization_code`

   Write down any key whose UI label differs.
4. Paste the edited `plan-config.json` into the JSON configuration editor, then click **Create Test Plan**.
5. For each of the 14 modules, in order, click **Run Test**.
   - With the shim off, 12 modules stop at `CheckServerConfiguration` right away, and the two metadata modules need no action. No offer handoff is needed.
   - If a module shows WAITING for a credential offer (it shouldn't with the shim off), write that down: it is a difference.
6. On the plan page, click **Download all Logs**. Save the zip as `evidence/sp5/oracle2/manual/certify-plan.zip`.

## 2. Verify: `oid4vp-1final-verifier-test-plan`, config verify-redirect-uri
1. Create a test plan, then pick `oid4vp-1final-verifier-test-plan`. Variant: `vp_profile=plain_vp`, `credential_format=sd_jwt_vc`, `client_id_prefix=redirect_uri`, `request_method=url_query`, `response_mode=direct_post`.
2. Paste the edited `plan-config.json`, then click **Create Test Plan**.
3. For each of the 9 modules, click **Run Test**. When the module shows WAITING with an authorization endpoint (shown in the module's exposed values), play Verify's front end by hand:
   ```bash
   # 1) ask Verify for an authorization request (same body as plans/verify/verify-redirect-uri.json handoff.vp_request)
   curl -s -X POST http://localhost:8080/v1/verify/v2/vp-request -H 'Content-Type: application/json' -d '{
     "clientId":"redirect_uri:https://verify-tls/v1/verify/v2/vp-submission/direct-post",
     "dcqlQuery":{"credentials":[{"id":"pid","format":"dc+sd-jwt","meta":{"vct_values":["urn:eudi:pid:1"]},
                  "claims":[{"path":["given_name"]},{"path":["family_name"]}]}]}}' | tee /tmp/vp.json
   ```
   2. Build the wallet URL from the response, the way Verify's SDK does (`inji-verify-sdk/.../OpenID4VPVerification.tsx:58-69`). Send `client_id`, `state=requestId`, `response_mode`, `response_type`, `nonce`, `response_uri`, and `dcql_query` (JSON), all taken from `authorizationDetails`. Open `<authorization_endpoint>?<those params>` in the browser.
   3. If the module then asks for a screenshot: upload any screenshot of `curl http://localhost:8080/v1/verify/vp-result/<transactionId>` through the UI. That is what the harness does automatically (ADR-003 H2).

   With F-VER-1, every module is expected to fail on the first request, before any screenshot.
4. Click **Download all Logs** and save the zip as `evidence/sp5/oracle2/manual/verify-plan.zip`.

## 3. Compare (no new code)
The reconcile check compares a TestNG report with *any* plan export, so point it at the manual export:
```bash
$CONFORMANCE_PYTHON -m runner reconcile evidence/sp5/oracle2/harness/certify-shim-off/testng-report --export evidence/sp5/oracle2/manual/certify-plan.zip | tee evidence/sp5/oracle2/certify-compare.md
$CONFORMANCE_PYTHON -m runner reconcile evidence/sp5/oracle2/harness/verify-redirect-uri/testng-report --export evidence/sp5/oracle2/manual/verify-plan.zip | tee evidence/sp5/oracle2/verify-compare.md
```
MATCH means harness and manual agree on every module's verdict. The counts line compares the harness's EmailableReport with the manual run.

First failing condition per module, from each zip:
```bash
python3 - evidence/sp5/oracle2/manual/certify-plan.zip <<'EOF'
import json, sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
for n in sorted(z.namelist()):
    if n.startswith("test-log-") and n.endswith(".json"):
        d = json.loads(z.read(n)); ti = d["testInfo"]
        ff = next((r.get("src") for r in d["results"] if r.get("result") == "FAILURE"), "-")
        print(f'| {ti["testName"]} | {ti["status"]}/{ti["result"]} | {ff} |')
EOF
```
Run the same on the harness zip (`…/conformance/<cfg>/*.zip`), then fill the table below.

Finally, tear down: `flock /tmp/inji-conformance.docker.lock scripts/env.sh down all` and `docker compose -p minio --env-file compose/.env.pinned -f compose/minio.yml down -v`.

## 4. Template for `evidence/manual-vs-harness.md`
```markdown
# Manual vs harness (oracle 2)
Date, person, suite tag, git sha, time taken (manual / harness).

| component | module | manual status/result | manual first failure | harness status/result | harness first failure | same? |
|---|---|---|---|---|---|---|
| certify | oid4vci-1_0-issuer-metadata-test | | | | | |
| … 14 certify rows, 9 verify rows … |

reconcile (harness TestNG vs manual export): certify MATCH/MISMATCH, verify MATCH/MISMATCH (files: oracle2/*-compare.md)
Differences and their explanation:
UI steps that differed from the procedure:
```
