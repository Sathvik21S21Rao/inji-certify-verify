"""Handoff plugins: when the suite is WAITING, drive the component under test (Certify / Verify)."""
import json
import sys
import urllib.parse
from dataclasses import dataclass, field


class HandoffError(Exception):
    pass


@dataclass
class ModuleCtx:
    module: str
    test_id: str
    exposed: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)  # persists across WAITINGs of one module


def call(http, method, url, **kw):
    r = http.request(method, url, **kw)
    print(f"[handoff] {method} {url[:200]} -> {r.status_code} {r.text[:300]!r}", file=sys.stderr, flush=True)
    return r


def _join(ep, query):
    return ep + ("&" if "?" in ep else "?") + query


def certify(ctx, cfg, env, http) -> bool:
    offer, ex = cfg["offer"], ctx.exposed
    if ex.get("tx_code_endpoint"):
        call(http, "GET", ex["tx_code_endpoint"].split("?")[0], params={"code": offer.get("tx_code", "")})
    elif ex.get("credential_offer_endpoint"):
        r = call(http, "POST", f"{env['CERTIFY_API']}/pre-authorized-data", json=offer)
        if r.status_code != 200:
            raise HandoffError(f"pre-authorized-data HTTP {r.status_code}: {r.text[:300]}")
        try:
            query = urllib.parse.urlsplit(r.json()["credential_offer_uri"]).query
        except (ValueError, KeyError) as e:
            raise HandoffError(f"pre-authorized-data response has no credential_offer_uri: {r.text[:300]}") from e
        call(http, "GET", _join(ex["credential_offer_endpoint"], query))
    else:
        return False
    return True


def wallet_params(body, client_id):
    # Same mapping as Verify's SDK: inji-verify-sdk/.../OpenID4VPVerification.tsx:58-69
    p = {"client_id": client_id}
    if body.get("requestUri"):
        p["request_uri"] = body["requestUri"]
        return p
    a = body["authorizationDetails"]
    p.update(state=body["requestId"], response_mode=a["responseMode"], response_type=a["responseType"],
             nonce=a["nonce"], response_uri=a["responseUri"])
    if a.get("dcqlQuery"):
        p["dcql_query"] = json.dumps(a["dcqlQuery"])
    return p


def verify(ctx, cfg, env, http) -> bool:
    ep = ctx.exposed.get("authorization_endpoint")
    if ctx.state.get("handed_off") or not ep:
        return False
    vp = cfg["vp_request"]
    r = call(http, "POST", f"{env['VERIFY_API']}/v2/vp-request", json=vp)
    if r.status_code != 201:
        raise HandoffError(f"vp-request HTTP {r.status_code}: {r.text[:300]}")
    body = r.json()
    ctx.state["txn"] = body.get("transactionId")
    ctx.state["handed_off"] = True
    call(http, "GET", _join(ep, urllib.parse.urlencode(wallet_params(body, vp["clientId"]))), follow_redirects=False)
    return True


PLUGINS = {"certify": certify, "verify": verify}
