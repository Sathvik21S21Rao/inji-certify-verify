import json
from pathlib import Path

import httpx
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
V = Draft202012Validator(json.loads((ROOT / "runner" / "schema" / "results.schema.json").read_text()))
ENV = {"CONFORMANCE_SERVER": "https://suite.test:8443/", "CERTIFY_API": "http://certify.test/v1/certify",
       "CERTIFY_PUBLIC_URL": "https://certify.test:9443", "VERIFY_API": "http://verify.test/v1/verify"}
OFFER_URI = "openid-credential-offer://?credential_offer_uri=https%3A%2F%2Fcertify-tls%2Foffers%2Fabc"


def client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


class Calls(list):
    """MockTransport handler that records requests and answers from `routes` ((method, path-suffix) -> Response)."""

    def __init__(self, routes):
        super().__init__()
        self.routes = routes

    def __call__(self, req):
        self.append(req)
        for (m, suffix), resp in self.routes.items():
            if req.method == m and req.url.path.endswith(suffix):
                return resp if isinstance(resp, httpx.Response) else resp(req)
        return httpx.Response(404, text="no route")

    def http(self):
        return client(self)


def certify_routes(shim=False):
    meta = {"issuer": "x", **({"authorization_endpoint": "x"} if shim else {})}
    return {("GET", "/.well-known/oauth-authorization-server"): httpx.Response(200, json=meta),
            ("GET", "/credential-configurations/ConformanceSdJwt"): httpx.Response(200, json={}),
            ("POST", "/pre-authorized-data"): httpx.Response(200, json={"credential_offer_uri": OFFER_URI})}


class FakeSuite:
    """steps[module] = [(status, exposed, images), ...]; each wait() advances one step, the last repeats."""

    def __init__(self, steps, info=None, fail_create=False):
        self.steps, self.i, self.stopped, self.uploads = steps, {}, [], []
        self.infos, self.fail_create, self.cur = info or {}, fail_create, {}
        self.plans = []

    async def create_plan(self, name, config, variant):
        if self.fail_create:
            raise RuntimeError("suite down")
        self.plans.append((name, config, variant))
        return "plan-1", list(self.steps)

    async def create_module(self, plan_id, name):
        self.cur[f"id-{name}"] = name
        self.i[name] = -1
        return f"id-{name}"

    def _step(self, tid):
        n = self.cur[tid]
        return self.steps[n][min(max(self.i[n], 0), len(self.steps[n]) - 1)]

    async def start(self, tid):
        pass

    async def wait(self, tid, states, timeout_s):
        self.i[self.cur[tid]] += 1
        return self._step(tid)[0]

    async def status(self, tid):
        return {"exposed": self._step(tid)[1]}

    async def stop(self, tid):
        self.stopped.append(tid)

    async def images(self, tid):
        return self._step(tid)[2] if len(self._step(tid)) > 2 else []

    async def upload_image(self, tid, ph, data):
        self.uploads.append((tid, ph, data))

    async def info(self, tid):
        n = self.cur[tid]
        return self.infos.get(n, {"status": "FINISHED", "result": "PASSED", "testId": tid})

    async def log(self, tid):
        return self.infos.get(self.cur[tid] + ":log", [])

    async def export_html(self, plan_id, out_dir):
        return "plan.zip"

    async def close(self):
        pass
