# Handoff: how each component is driven while the suite waits

In a conformance plan, the suite plays one side of the protocol: the wallet. The component under test is the other side. Neither Certify nor Verify starts a flow on its own. A person normally creates the credential offer or the presentation request in an app. The harness does that step through each component's own API, from a **handoff plugin**.

Plugins live in `runner/handoff.py` (`PLUGINS = {"certify": …, "verify": …}`). The template picks one with `handoff.plugin`. The module loop calls the plugin every time the module is WAITING ([how-the-api-automation-works.md](how-the-api-automation-works.md), "Module loop").

The contract is small:
- The plugin receives `ModuleCtx` (`module`, `test_id`, the suite's `exposed` values, and a per-module `state` dict), its template `handoff` block, the environment, and an HTTP client.
- It returns `True` if it acted and `False` if there was nothing to do.
- It raises `HandoffError` if the component refused. That becomes an `infra` record, never a conformance verdict.

Every call is logged to stderr as `[handoff] METHOD url -> status body…`. In the testrig, that is `testng-report/conformance/<cfg>/runner.stderr.log`.

## Inji Certify (issuer, OpenID4VCI 1.0)

**What the suite exposes.** In issuer-initiated mode, the suite waits for a credential offer at `credential_offer_endpoint`. If the offer carries a transaction code, it then waits for that code at `tx_code_endpoint` (`vci10issuer/AbstractVCIIssuerTestModule.java:375,445`; suite paths are relative to `upstream/conformance-suite/src/main/java/net/openid/conformance/`).

**What the plugin does** (`handoff.py`, `certify`):
1. When `credential_offer_endpoint` is exposed, it calls `POST $CERTIFY_API/pre-authorized-data` with the template's `handoff.offer`: `credential_configuration_id`, `claims`, `expires_in` and `tx_code`. This is Certify's own endpoint for creating a pre-authorized offer (`certify-service/.../controller/PreAuthorizedCodeController.java:22`).
2. Certify returns `credential_offer_uri`, an `openid-credential-offer://?credential_offer_uri=…` link. The plugin passes that link's query to the suite with a GET on `<credential_offer_endpoint>?<query>`. That is what a wallet does when it scans the offer QR code.
3. When `tx_code_endpoint` is exposed, it sends the code with a GET on `<tx_code_endpoint>?code=<tx_code>`.

From there the suite talks to Certify directly over TLS (`https://certify-tls`): metadata, token, nonce, credential.

Observed:
```
[handoff] POST http://localhost:8091/v1/certify/pre-authorized-data -> 200 '{"credential_offer_uri":"openid-credential-offer://?credential_offer_uri=https%3A%2F%2Fcertify-tls%2Fv1%2Fcertify%2Fcredential-offer-data%2F…
[handoff] GET https://localhost.emobix.co.uk:8443/test/a/certify-…/credential_offer?credential_offer_uri=… -> 200
```
(`evidence/sp4/SP4.4/kg-certify-shim-on/certify-shim-on/stderr.log`, diagnostic pass.)

**Before the first module.** `runner/setup.py` seeds the SD-JWT credential configuration the offer refers to (`POST /credential-configurations`, skipped if it already exists). It also checks that the AS-metadata shim state matches the template.

**When the plugin isn't reached.** In the benchmark of record (shim off), 12 of 14 modules stop at `CheckServerConfiguration` before they expose an offer endpoint (F-CERT-1). The two metadata modules need no handoff. So in that pass the Certify plugin never runs, and only the diagnostic shim-on pass exercises it ([known-limitations.md](known-limitations.md)).

## Inji Verify (verifier, OpenID4VP 1.0)

**What the suite exposes.** Each verifier module waits as a wallet with an `authorization_endpoint` (`vp1finalverifier/AbstractVP1FinalVerifierTest.java:209`).

**What the plugin does** (`handoff.py`, `verify` and `wallet_params`):
1. It calls `POST $VERIFY_API/v2/vp-request` with the template's `handoff.vp_request`: `clientId`, plus a `dcqlQuery` that asks for the suite's SD-JWT credential. It expects 201 and keeps `transactionId` in `ctx.state`.
2. It builds the wallet request **exactly as Verify's own SDK does** (`inji-verify-sdk/src/components/openid4vp-verification/OpenID4VPVerification.tsx:58-69`):
   - If Verify returned a `requestUri` (signed request, `x509_san_dns`), it sends `client_id` and `request_uri`.
   - Otherwise (`redirect_uri` with `url_query`), it sends `client_id`, `state` = `requestId`, and `response_mode`, `response_type`, `nonce`, `response_uri` and `dcql_query`, all taken from `authorizationDetails`.
3. It calls `GET <authorization_endpoint>?<params>` on the suite without following redirects, then marks the module `handed_off`, so later WAITINGs of the same module don't create a second request.

The suite's wallet then fetches the request object if there is one, validates it, and posts the presentation to Verify's `response_uri` (`direct_post`).

Using the SDK's mapping matters for the findings. When the suite reports that a `url_query` request has no `client_metadata` (F-VER-1), a real wallet driven by Verify's UI would see the same request. It isn't a harness artefact.

**Screenshot evidence** (`runner/evidence.py`, on unless `CONFORMANCE_VERIFY_EVIDENCE=none`):
1. After a successful `direct_post`, positive verifier modules create a screenshot placeholder and wait (`vp1finalverifier/AbstractVP1FinalVerifierTest.java:623-632`). The module loop runs the evidence uploader before the plugin.
2. The uploader reads Verify's own verdict with `GET $VERIFY_API/vp-result/{transactionId}`.
3. It renders the verdict to a PNG and posts it to every open placeholder (`POST /api/log/{id}/images/{placeholder}`). It also saves `<module>.verify-result.json` and `.png` next to the log.

The suite then marks the module REVIEW, by design (`logging/ImageAPI.java:162`). That is why verifier happy paths are "skip, needs human review" in TestNG ([design-decisions.md](design-decisions.md)).

Observed (`evidence/sp5/SP5.2/live/verify-redirect-uri/testng-report/conformance/verify-redirect-uri/runner.stderr.log`):
```
[handoff] POST http://localhost:8080/v1/verify/v2/vp-request -> 201 '{"transactionId":"txn_…","requestId":"req_…","authorizationDetails":{"clientId":"…
[handoff] GET https://localhost.emobix.co.uk:8443/test/a/verify-…/authorize?client_id=redirect_uri%3Ahttps%3A%2F%2Fverify-tls%2Fv1%2Fverify%2Fv2%2Fvp-submission%2Fdirect-post&state=req_… -> 20…
[handoff] GET http://localhost:8080/v1/verify/vp-result/txn_… -> 200 '{"transactionId":"txn_…","vpResultStatus":"SUCCESS",…
```

## Adding a plugin
Write a function `(ctx, cfg, env, http) -> bool` in `runner/handoff.py`, add it to `PLUGINS`, and name it in the template's `handoff.plugin`. Unit tests with a fake HTTP client are in `runner/tests/test_handoff.py`.
