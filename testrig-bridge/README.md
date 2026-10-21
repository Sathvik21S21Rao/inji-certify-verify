# testrig-bridge

Patches that let the Inji api-test jars run the OpenID conformance runner (ADR-005). Off by default.

- `inji-certify.patch` / `.diffstat.txt`: patch against inji-certify `0d52155` (6 files under `api-test/`).
- `inji-verify.patch` / `.diffstat.txt`: same bridge for inji-verify `64b2790`; keys are the same minus the shim key, template `plans/verify/verify-redirect-uri.json`, runner env `VERIFY_API=<injiVerifyBaseUrl>/v1/verify`.
- `tests/OpenIDConformanceBridgeTest.java`: module-agnostic unit test (fixtures in `runner/tests/fixtures`).
- `tests/fake-runner.sh`: replays a JSONL fixture in place of the runner.
- `run-unit-tests.sh <certify|verify> <jar-with-dependencies>`: compiles and runs the unit test.
- `build-image.sh <certify|verify> <api-test dir> <tag>`: stages a context and `docker build`s the testrig image.

## Apply and build
    git -C <inji-certify checkout at 0d52155> apply $PWD/testrig-bridge/inji-certify.patch
    source env.sh && cd <checkout>/api-test && mvn -o -q -DskipTests package

## Test
    testrig-bridge/run-unit-tests.sh certify <checkout>/api-test/target/apitest-injicertify-*-jar-with-dependencies.jar

## Keys (`injiCertify.properties`; any key can be overridden by an env var of the same name)
- `conformance.enabled` (`no`): `yes` runs only `injicertifyConformanceSuite.xml`.
- `conformance.runner.dir`: working dir of the runner; templates resolve relative to it.
- `conformance.runner.command` (`python3 -m runner run`): split on whitespace, no quoting.
- `conformance.plan.template`: blank selects `plans/certify/certify-shim-{on,off}.json` by the shim key.
- `conformance.runner.timeout` (`3600`): seconds before the runner is killed.
- `conformance.strict` (`no`): `yes` makes a `warning` outcome fail.
- `conformance.certify.as_metadata_shim` (`false`): passed to the runner as `CONFORMANCE_CERTIFY_AS_METADATA_SHIM`.

The runner also gets `CERTIFY_API=<injiCertifyBaseURL>/v1/certify`. Known issue F-CERT-5 is in `testCaseSkippedList.txt`.
