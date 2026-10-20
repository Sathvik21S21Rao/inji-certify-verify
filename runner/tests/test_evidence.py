import asyncio

import httpx

from runner.evidence import fill_placeholders
from runner.handoff import ModuleCtx
from .helpers import ENV, Calls, FakeSuite


def run(suite, ctx, http, out):
    return asyncio.run(fill_placeholders(suite, ctx, ENV, http, out))


def test_pending_placeholder_uploads_png(tmp_path):
    calls = Calls({("GET", "/vp-result/tx1"): httpx.Response(200, json={"vpResultStatus": "SUCCESS"})})
    suite = FakeSuite({"m": [("WAITING", {}, [{"upload": "ph1"}, {"upload": "ph2", "img": "x"}, {"img": "y"}])]})
    suite.cur["t"], suite.i["m"] = "m", 0
    ctx = ModuleCtx("m", "t", state={"txn": "tx1"})
    names = run(suite, ctx, calls.http(), tmp_path)
    assert names == ["m.verify-result.json", "m.verify-result.png"]
    assert (tmp_path / names[1]).read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / names[0]).read_text().startswith("Inji Verify GET /vp-result/tx1 -> HTTP 200\n")
    assert len(suite.uploads) == 1 and suite.uploads[0][:2] == ("t", "ph1")
    assert suite.uploads[0][2].startswith("data:image/png;base64,")


def test_no_pending_no_verify_call(tmp_path):
    calls = Calls({})
    suite = FakeSuite({"m": [("WAITING", {}, [{"img": "y"}])]})
    suite.cur["t"], suite.i["m"] = "m", 0
    assert run(suite, ModuleCtx("m", "t"), calls.http(), tmp_path) == [] and not calls and not suite.uploads
