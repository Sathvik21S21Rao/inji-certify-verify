"""Thin async wrapper over the vendored OIDF suite client (runner/_vendor/conformance.py)."""
import json
import os
from pathlib import Path

from ._vendor.conformance import Conformance


class ModuleTimeout(Exception):
    pass


class Suite:
    def __init__(self, url):
        self.c = Conformance(url, None, False)
        self.base = self.c.api_url_base

    async def create_plan(self, name, config, variant):
        p = await self.c.create_test_plan(name, json.dumps(config), variant)
        return p["id"], [m["testModule"] for m in p["modules"]]

    async def create_module(self, plan_id, name):
        return (await self.c.create_test_from_plan(plan_id, name))["id"]

    async def start(self, tid):
        await self.c.start_test(tid)

    async def wait(self, tid, states, timeout_s):
        try:
            return await self.c.wait_for_state(tid, list(states) + ["INTERRUPTED"], timeout_s)
        except Exception as e:
            if str(e).startswith("Timed out waiting"):
                raise ModuleTimeout(str(e)) from e
            raise

    async def _get(self, path):
        r = await self.c.httpclient.get(self.base + path)
        r.raise_for_status()
        return r.json()

    async def status(self, tid):
        r = await self.c.httpclient.get(f"{self.base}api/runner/{tid}")
        if r.status_code == 404:  # test finished between wait() and this read; the next wait() sees it
            return {}
        r.raise_for_status()
        return r.json()

    async def stop(self, tid):
        await self.c.httpclient.delete(f"{self.base}api/runner/{tid}")

    async def images(self, tid):
        return await self._get(f"api/log/{tid}/images")

    async def upload_image(self, tid, placeholder, data_uri):
        r = await self.c.httpclient.post(f"{self.base}api/log/{tid}/images/{placeholder}", content=data_uri,
                                         headers={"Content-Type": "text/plain"})
        r.raise_for_status()

    async def info(self, tid):
        return await self.c.get_module_info(tid)

    async def log(self, tid):
        return await self.c.get_test_log(tid)

    async def export_html(self, plan_id, out_dir):
        return os.path.basename(await self.c.exporthtml(plan_id, str(out_dir)))

    async def close(self):
        await self.c.close_client()
