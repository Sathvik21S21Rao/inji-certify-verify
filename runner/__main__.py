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


def _report(a) -> int:
    from . import combined, gate, reconcile
    try:
        if a.cmd == "gate":
            res = gate.evaluate(gate.load(a.results), gate.load_benchmark(a.benchmark), a.strict)
            print(gate.gate_markdown(res), end="")
            return 1 if res["red"] else 0
        if a.cmd == "benchmark":
            if Path(a.out).exists() and not a.force:
                raise gate.GateError(f"{a.out} exists (use --force)")
            bench = gate.init_benchmark(gate.load(a.results), a.results, a.label)
            Path(a.out).write_text(json.dumps(bench, indent=1, ensure_ascii=False) + "\n")
            return 0
        if a.cmd == "reconcile":
            res = reconcile.evaluate(a.report_dir, a.export, a.strict)
            print(reconcile.markdown(res), end="")
            return 1 if res["mismatch"] else 0
        if a.cmd == "diff":
            print(gate.diff(gate.load(a.a), gate.load(a.b)), end="")
            return 0
        return 1 if combined.write(a.out, [tuple(r.partition("=")[::2]) if "=" in r else (r, None) for r in a.runs],
                                   a.note) else 0
    except (gate.GateError, reconcile.ReconcileError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def main(argv=None) -> int:
    real_stdout = sys.stdout
    ap = argparse.ArgumentParser(prog="python -m runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("template")
    p.add_argument("--out", required=True)
    p.add_argument("--run-id")
    p.add_argument("--modules")
    p.add_argument("--module-timeout", type=int)
    g = sub.add_parser("gate")
    g.add_argument("results")
    g.add_argument("benchmark")
    g.add_argument("--strict", action="store_true")
    b = sub.add_parser("benchmark").add_subparsers(dest="bcmd", required=True).add_parser("init")
    b.add_argument("results")
    b.add_argument("--out", required=True)
    b.add_argument("--label", default="")
    b.add_argument("--force", action="store_true")
    r = sub.add_parser("reconcile")
    r.add_argument("report_dir")
    r.add_argument("--export")
    r.add_argument("--strict", action="store_true")
    d = sub.add_parser("diff")
    d.add_argument("a")
    d.add_argument("b")
    c = sub.add_parser("combined")
    c.add_argument("--out", required=True)
    c.add_argument("--note")
    c.add_argument("runs", nargs="+", help="run.jsonl[=benchmark.json]")
    a = ap.parse_args(argv)
    if a.cmd != "run":
        return _report(a)
    sys.stdout = sys.stderr  # the vendored suite client prints; stdout is JSONL only

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
