import asyncio
import json
import os
import subprocess
import sys

import httpx

from runner import records
from runner.run import run_plan
from runner.templates import load_template
from .helpers import ENV, ROOT, V, Calls, FakeSuite, certify_routes

CERT = ROOT / "plans/certify/certify-shim-off.json"
VER = ROOT / "plans/verify/verify-redirect-uri.json"
OFFER_EP = {"credential_offer_endpoint": "https://suite/o"}
GET_OK = {("GET", "/o"): httpx.Response(200)}
INFO_FAIL = {"m1": {"status": "FINISHED", "result": "FAILED", "testId": "id-m1"},
             "m1:log": [{"src": "SomeCondition", "result": "FAILURE", "msg": "bad", "requirements": [], "time": 1792493022240}]}


def go(tpl_path, suite, calls, tmp_path, **kw):
    out = []
    template = load_template(tpl_path, {})
    code = asyncio.run(run_plan(template, suite=suite, http=calls.http(), env=ENV, out_dir=tmp_path, run_id="r1",
                                emit=out.append, **kw))
    for r in out:
        V.validate(r)
    assert out[0]["type"] == "plan" and out[-1]["type"] == "end" and out[-1]["exit"] == code
    return code, out


def test_pass_and_fail_and_files(tmp_path):
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("FINISHED", {})],
                       "m1": [("CONFIGURED", {}), ("WAITING", OFFER_EP), ("FINISHED", {})]}, info=INFO_FAIL)
    calls = Calls({**certify_routes(), **GET_OK})
    code, out = go(CERT, suite, calls, tmp_path)
    assert code == 0 and [m["outcome"] for m in out[1:-1]] == ["pass", "fail"]
    assert out[0]["alias"] == "certify-r1" and out[0]["flags"]["certify_as_metadata_shim"] is False
    assert out[1]["evidence"] == ["m0.log.json"] and out[2]["message"] == "SomeCondition: bad"
    _, cfg, _ = suite.plans[0]
    assert cfg["alias"] == "certify-r1" and cfg["description"].endswith("(run r1)")
    assert json.loads((tmp_path / "m1.log.json").read_text())["info"]["result"] == "FAILED"
    assert (tmp_path / "plan-config.json").exists() and out[-1]["export"] == "plan.zip"
    assert [r.method for r in calls if r.url.path.endswith(("pre-authorized-data", "/o"))] == ["POST", "GET"]


def test_modules_filter_and_unknown(tmp_path):
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("FINISHED", {})], "m1": [("FINISHED", {})]})
    _, out = go(CERT, suite, Calls(certify_routes()), tmp_path, modules=["m1"])
    assert out[0]["modules"] == ["m1"] and len(out) == 3
    code, out = go(CERT, FakeSuite({"m0": [("FINISHED", {})]}), Calls(certify_routes()), tmp_path, modules=["zz"])
    assert code == 2 and out[0]["plan_id"] is None and "zz" in out[-1]["error"]


def test_timeout_is_infra_and_stops(tmp_path):
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("WAITING", {})]})
    code, out = go(CERT, suite, Calls(certify_routes()), tmp_path, module_timeout=1)
    m = out[1]
    assert code == 1 and suite.stopped == ["id-m0"] and m["outcome"] == "infra"
    assert m["infra_reason"] == "runner timeout after 1s in WAITING" and m["test_id"] == "id-m0"


def test_plugin_error_is_infra_and_next_module_runs(tmp_path):
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("WAITING", OFFER_EP)], "m1": [("FINISHED", {})]})
    routes = {**certify_routes(), ("POST", "/pre-authorized-data"): httpx.Response(500, text="boom")}
    code, out = go(CERT, suite, Calls(routes), tmp_path)
    assert code == 1 and [m["outcome"] for m in out[1:-1]] == ["infra", "pass"]
    assert out[1]["infra_reason"].startswith("HandoffError:") and suite.stopped == ["id-m0"]


def test_plan_creation_fails(tmp_path):
    code, out = go(CERT, FakeSuite({"m0": []}, fail_create=True), Calls(certify_routes()), tmp_path)
    assert code == 2 and out[0]["plan_id"] is None and "suite down" in out[-1]["error"] and len(out) == 2


def test_shim_mismatch_creates_no_plan(tmp_path):
    suite = FakeSuite({"m0": [("FINISHED", {})]})
    code, out = go(CERT, suite, Calls(certify_routes(shim=True)), tmp_path)
    assert code == 2 and not suite.plans and out[0]["flags"]["certify_as_metadata_shim"] is True
    assert "environment has shim=True, config certify-shim-off expects False" in out[-1]["error"]


def test_certify_seeds_missing_credential_config(tmp_path):
    routes = {**certify_routes(), ("GET", "/credential-configurations/ConformanceSdJwt"): httpx.Response(404),
              ("POST", "/credential-configurations"): httpx.Response(201)}
    calls = Calls(routes)
    code, _ = go(CERT, FakeSuite({"m0": [("FINISHED", {})]}), calls, tmp_path)
    post = [r for r in calls if r.method == "POST"][0]
    assert code == 0 and json.loads(post.content)["credentialConfigKeyId"] == "ConformanceSdJwt"
    routes[("POST", "/credential-configurations")] = httpx.Response(400, text="bad")
    code, out = go(CERT, FakeSuite({"m0": [("FINISHED", {})]}), Calls(routes), tmp_path)
    assert code == 2 and "HTTP 400" in out[-1]["error"]


def test_verify_handoff_then_evidence(tmp_path):
    body = {"transactionId": "tx1", "requestId": "rq", "requestUri": "https://v/r"}
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("WAITING", {"authorization_endpoint": "https://suite/a"}),
                              ("WAITING", {}, [{"upload": "ph"}]), ("FINISHED", {})]})
    calls = Calls({("POST", "/v2/vp-request"): httpx.Response(201, json=body), ("GET", "/a"): httpx.Response(200),
                   ("GET", "/vp-result/tx1"): httpx.Response(200, json={"ok": 1})})
    code, out = go(VER, suite, calls, tmp_path)
    assert code == 0 and out[0]["flags"] == {"certify_as_metadata_shim": None, "verify_evidence_upload": True}
    assert out[1]["evidence"] == ["m0.log.json", "m0.verify-result.json", "m0.verify-result.png"]
    assert len(suite.uploads) == 1


def test_cli_stdout_purity_unreachable(tmp_path):
    env = {**os.environ, "CONFORMANCE_SERVER": "https://127.0.0.1:9/", "CONFORMANCE_RETRY_TIMEOUT": "1",
           "CERTIFY_PUBLIC_URL": "https://127.0.0.1:9", "CERTIFY_API": "http://127.0.0.1:9/v1/certify"}
    p = subprocess.run([sys.executable, "-m", "runner", "run", str(CERT), "--out", str(tmp_path)], cwd=ROOT,
                       env=env, capture_output=True, text=True, timeout=60)
    lines = p.stdout.splitlines()
    recs = [json.loads(l) for l in lines]
    for r in recs:
        V.validate(r)
    assert p.returncode == 2 and recs[0]["type"] == "plan" and recs[-1]["type"] == "end" and recs[-1]["exit"] == 2
    assert (tmp_path / "results.jsonl").read_text().splitlines() == lines


def test_cli_stdout_purity_unreachable_suite(tmp_path):
    """verify has no shim check, so this reaches the vendored client (which prints) and must still keep stdout clean."""
    env = {**os.environ, "CONFORMANCE_SERVER": "https://127.0.0.1:9/", "CONFORMANCE_RETRY_TIMEOUT": "1"}
    p = subprocess.run([sys.executable, "-m", "runner", "run", str(VER), "--out", str(tmp_path)], cwd=ROOT,
                       env=env, capture_output=True, text=True, timeout=60)
    recs = [json.loads(l) for l in p.stdout.splitlines()]
    for r in recs:
        V.validate(r)
    assert p.returncode == 2 and recs[-1]["exit"] == 2 and recs[0]["plan_id"] is None


def test_status_404_race_is_not_infra(tmp_path):
    class Racy(FakeSuite):
        async def status(self, tid):  # Suite.status maps a 404 (test already finished) to {}
            return {}

    suite = Racy({"m0": [("CONFIGURED", {}), ("WAITING", {}), ("FINISHED", {})]})
    code, out = go(CERT, suite, Calls(certify_routes()), tmp_path)
    assert code == 0 and out[1]["outcome"] == "pass" and not suite.stopped


def test_plan_carries_environment(tmp_path, monkeypatch):
    suite = FakeSuite({"m0": [("CONFIGURED", {}), ("FINISHED", {})]})
    calls = Calls({**certify_routes(), **GET_OK})
    _, out = go(CERT, suite, calls, tmp_path, modules=["m0"])
    assert out[0]["schema_version"] == "1.1" and out[0]["environment"] == {"fault": "none", "certify_release": "1.0"}
    monkeypatch.setitem(ENV, "CONFORMANCE_FAULT", "strip-nonce-endpoint")
    _, out = go(CERT, FakeSuite({"m0": [("CONFIGURED", {}), ("FINISHED", {})]}), Calls({**certify_routes(), **GET_OK}),
                tmp_path, modules=["m0"])
    assert out[0]["environment"]["fault"] == "strip-nonce-endpoint"
