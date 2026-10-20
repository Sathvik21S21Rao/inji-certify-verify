import argparse
import asyncio
import json
import os
import secrets
import sys
import time
from pathlib import Path

DEFAULT_ENV = {"CONFORMANCE_SERVER": "https://localhost.emobix.co.uk:8443/",
               "CERTIFY_API": "http://localhost:8091/v1/certify",
               "CERTIFY_PUBLIC_URL": "https://localhost:9443",
               "VERIFY_API": "http://localhost:8080/v1/verify"}


def main(argv=None) -> int:
    real_stdout, sys.stdout = sys.stdout, sys.stderr  # the vendored suite client prints; stdout is JSONL only
    ap = argparse.ArgumentParser(prog="python -m runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("template")
    p.add_argument("--out", required=True)
    p.add_argument("--run-id")
    p.add_argument("--modules")
    p.add_argument("--module-timeout", type=int)
    a = ap.parse_args(argv)

    import httpx

    from . import records
    from .run import run_plan
    from .suite import Suite
    from .templates import TemplateError, load_template

    env = {**DEFAULT_ENV, **os.environ}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.jsonl").unlink(missing_ok=True)
    emit = records.Emitter(real_stdout, out / "results.jsonl").emit
    run_id = a.run_id or time.strftime("%Y%m%d%H%M%S") + "-" + secrets.token_hex(2)
    error = None
    try:
        template = load_template(a.template, env)
    except TemplateError as e:  # still emit plan + end(2); read the raw file for the plan fields
        template, error = json.loads(Path(a.template).read_text()), str(e)
        template["_path"] = a.template
    http = httpx.Client(verify=False, timeout=60)
    suite = Suite(env["CONFORMANCE_SERVER"])

    async def go():
        try:
            return await run_plan(template, suite=suite, http=http, env=env, out_dir=out, run_id=run_id,
                                  modules=a.modules.split(",") if a.modules else None,
                                  module_timeout=a.module_timeout, emit=emit, error=error)
        finally:
            await suite.close()
            http.close()

    return asyncio.run(go())


if __name__ == "__main__":
    sys.exit(main())
