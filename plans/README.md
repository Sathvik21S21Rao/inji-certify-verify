# Plan templates

`python -m runner run plans/<component>/<name>.json --out DIR`; `config_name` = file stem.
Fields: `component`, `description`, `plan_name`, `variant`, `module_timeout_s`, `config` (suite plan config; the runner
sets `alias` and `description`), `handoff` (`certify`: `offer`; `verify`: `vp_request`, `evidence`), certify only:
`expect.certify_as_metadata_shim` (must equal the observed AS metadata, else exit 2) and `setup.credential_configuration`.
Placeholders (every string value): `${NAME}` env var, required; `${NAME:-default}`; a string that is only a placeholder
resolving to "" drops its key.
Env: `CONFORMANCE_SERVER`, `CERTIFY_API`, `CERTIFY_PUBLIC_URL`, `VERIFY_API` (runner endpoints, defaults in `runner/__main__.py`);
`CERTIFY_ISSUER_URL` (default `https://certify-tls`), `VERIFY_PUBLIC_URL` (`https://verify-tls`),
`VERIFY_X509_CA_PEM` (unset: `client.request_object_trust_anchor_pem` is dropped), `CONFORMANCE_VERIFY_EVIDENCE`
(`vp-result-png` default, or `none`), `CONFORMANCE_RETRY_TIMEOUT` (suite client retry budget, seconds).
`credential-config.json` is POSTed to Certify when `GET /credential-configurations/<key>` is not 200.
shim-off is the benchmark of record; shim-on is the diagnostic pass.
