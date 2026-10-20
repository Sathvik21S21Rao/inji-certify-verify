import json
import urllib.parse

import httpx
import pytest

from runner.handoff import HandoffError, ModuleCtx, certify, verify
from .helpers import ENV, OFFER_URI, Calls, certify_routes

OFFER = {"credential_configuration_id": "ConformanceSdJwt", "claims": {"given_name": "Ada"}, "expires_in": 600, "tx_code": "493817"}
CFG = {"offer": OFFER}
OK = httpx.Response(200, text="ok")


def test_certify_offer_txcode_second_offer():
    calls = Calls({**certify_routes(), ("GET", "/credential_offer"): OK, ("GET", "/tx_code"): OK})
    http, ctx = calls.http(), ModuleCtx("m", "t1")
    ctx.exposed = {"credential_offer_endpoint": "https://suite/test/a/credential_offer"}
    assert certify(ctx, CFG, ENV, http)
    post, get = calls
    assert json.loads(post.content) == OFFER and str(post.url) == ENV["CERTIFY_API"] + "/pre-authorized-data"
    assert get.url.query.decode() == "credential_offer_uri=https%3A%2F%2Fcertify-tls%2Foffers%2Fabc"
    assert get.url.path == "/test/a/credential_offer"

    calls.clear()
    ctx.exposed = {"tx_code_endpoint": "https://suite/test/a/tx_code?code=your_tx_code", "credential_offer_endpoint": "https://suite/test/a/credential_offer"}
    assert certify(ctx, CFG, ENV, http)
    (tx,) = calls
    assert tx.url.path == "/test/a/tx_code" and tx.url.params["code"] == "493817" and "your_tx_code" not in str(tx.url)

    calls.clear()  # multiple-clients: only the offer endpoint is exposed again -> second offer
    ctx.exposed = {"credential_offer_endpoint": "https://suite/test/a/credential_offer"}
    assert certify(ctx, CFG, ENV, http) and [c.method for c in calls] == ["POST", "GET"]

    calls.clear()
    ctx.exposed = {}
    assert not certify(ctx, CFG, ENV, http) and not calls


def test_certify_error():
    calls = Calls({("POST", "/pre-authorized-data"): httpx.Response(500, text="boom")})
    ctx = ModuleCtx("m", "t", {"credential_offer_endpoint": "https://s/o"})
    with pytest.raises(HandoffError, match="500"):
        certify(ctx, CFG, ENV, calls.http())


VP = {"clientId": "redirect_uri:https://v/x", "dcqlQuery": {"credentials": []}}
DETAILS = {"responseMode": "direct_post", "responseType": "vp_token", "nonce": "n1", "responseUri": "https://v/post", "dcqlQuery": {"credentials": [1]}}


def verify_calls(body):
    return Calls({("POST", "/v2/vp-request"): httpx.Response(201, json=body), ("GET", "/authorize"): httpx.Response(302)})


def test_verify_url_query_params_and_once():
    calls = verify_calls({"transactionId": "tx1", "requestId": "rq1", "authorizationDetails": DETAILS})
    ctx = ModuleCtx("m", "t", {"authorization_endpoint": "https://suite/test/a/authorize"})
    assert verify(ctx, {"vp_request": VP}, ENV, calls.http())
    q = dict(calls[1].url.params)
    assert q == {"client_id": VP["clientId"], "state": "rq1", "response_mode": "direct_post", "response_type": "vp_token",
                 "nonce": "n1", "response_uri": "https://v/post", "dcql_query": json.dumps(DETAILS["dcqlQuery"])}
    assert ctx.state == {"txn": "tx1", "handed_off": True}
    n = len(calls)
    assert not verify(ctx, {"vp_request": VP}, ENV, calls.http()) and len(calls) == n  # second WAITING: nothing


def test_verify_request_uri_and_existing_query():
    calls = verify_calls({"transactionId": "tx1", "requestId": "rq1", "requestUri": "https://v/req/1"})
    ctx = ModuleCtx("m", "t", {"authorization_endpoint": "https://suite/authorize?x=1"})
    assert verify(ctx, {"vp_request": VP}, ENV, calls.http())
    assert dict(calls[1].url.params) == {"x": "1", "client_id": VP["clientId"], "request_uri": "https://v/req/1"}


def test_verify_nothing_exposed_and_bad_status():
    calls = verify_calls({})
    assert not verify(ModuleCtx("m", "t", {}), {"vp_request": VP}, ENV, calls.http()) and not calls
    bad = Calls({("POST", "/v2/vp-request"): httpx.Response(400, text="nope")})
    with pytest.raises(HandoffError, match="400"):
        verify(ModuleCtx("m", "t", {"authorization_endpoint": "https://s/a"}), {"vp_request": VP}, ENV, bad.http())
