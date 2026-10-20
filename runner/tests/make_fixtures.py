"""Regenerate runner/tests/fixtures/*.jsonl deterministically from evidence/sp0/ (run from worktree root)."""
import json
import os
from pathlib import Path

from runner import records as R

ROOT = Path(__file__).resolve().parents[2]
SP0 = ROOT / "evidence" / "sp0"
OUT = Path(__file__).parent / "fixtures"
SUITE_URL = "https://localhost.emobix.co.uk:8443/"
PLANS = {"certify": "oid4vci-1_0-issuer-test-plan", "verify": "oid4vp-1final-verifier-test-plan"}

# (fixture, source dir, component, config_name, shim, evidence_upload)
FIXTURES = [
    ("certify-shim-on", "baseline-v0-certify", "certify", "certify-shim-on", True, None),
    ("certify-shim-off", "s04-noshim-fullplan", "certify", "certify-shim-off", False, None),
    ("verify-redirect-uri", "baseline-v0-verify", "verify", "verify-redirect-uri", None, True),
    ("verify-x509", "baseline-v0-verify-x509", "verify", "verify-x509", None, True),
]


def _load(d, mod):
    return json.loads((d / f"{mod}.log.json").read_text())


def build(src, component, config_name, shim, upload):
    d = SP0 / src
    summary = json.loads((d / "summary.json").read_text())
    rows = summary["results"]
    first = _load(d, rows[0][0])["info"]
    zips = sorted(p.name for p in d.glob("*.zip"))
    run_id = f"sp0-{src}"
    out = [R.plan_record(run_id=run_id, alias=first["alias"], component=component, config_name=config_name,
                         plan_name=PLANS[component], plan_id=summary["plan_id"], variant=summary["variant"],
                         shim=shim, evidence_upload=upload, suite_url=SUITE_URL,
                         modules=[r[0] for r in rows], started=first["started"])]
    mods = []
    for name, test_id, status, result in rows:
        ev = [f"{name}.log.json"] + [f"{name}.verify-result.{x}" for x in ("json", "png") if (d / f"{name}.verify-result.{x}").exists()]
        blob = _load(d, name)
        mods.append(R.module_record(module=name, info=blob["info"], log=blob["log"], suite_url=SUITE_URL,
                                    evidence=ev, status=status, result=result, test_id=test_id))
    out += mods
    out.append(R.end_record(modules=mods, error=None, export=zips[0] if zips else None,
                            finished=max((m["finished"] for m in mods if m["finished"]), default=first["started"])))
    return out


def build_live_infra():
    """Live capture (suite test stopped via DELETE /api/runner/{id}): INTERRUPTED, result null."""
    name = "oid4vp-1final-verifier-happy-flow"
    blob = json.loads((ROOT / "evidence/sp2/live/infra-capture" / f"{name}.log.json").read_text())
    info = blob["info"]
    plan = R.plan_record(run_id="sp2-live-infra-capture", alias=info["alias"], component="verify",
                         config_name="verify-redirect-uri", plan_name=PLANS["verify"], plan_id=info["planId"],
                         variant=info["variant"], shim=None, evidence_upload=True, suite_url=SUITE_URL,
                         modules=[name], started=info["started"])
    m = R.module_record(module=name, info=info, log=blob["log"], suite_url=SUITE_URL, evidence=[f"{name}.log.json"])
    return [plan, m, R.end_record(modules=[m], error=None, export=None, finished=m["finished"])]


def main():
    OUT.mkdir(exist_ok=True)
    jobs = [(n, *a) for n, *a in FIXTURES]
    for name, src, comp, cfg, shim, up in jobs:
        write(name, build(src, comp, cfg, shim, up))
    write("infra-interrupted-unknown", build_live_infra())


def write(name, recs):
    p = OUT / f"{name}.jsonl"
    p.write_text("".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    print(p.relative_to(ROOT), len(recs))


if __name__ == "__main__":
    main()
