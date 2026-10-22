"""Benchmark gate, benchmark skeleton, run diff. Stdlib only. ADR-004 option 3."""
import json
import re
from collections import Counter
from pathlib import Path

OUT2EXP = {"pass": "PASSED", "warning": "WARNING", "review": "REVIEW", "skip": "SKIPPED", "fail": "FAILED"}
SEV = {"PASSED": 0, "WARNING": 1, "REVIEW": 2, "SKIPPED": 3, "FAILED": 4}  # SKIPPED placement: lead decision [inferred]
FINDING = re.compile(r"^F-(CERT|VER)-\d+$")
OK_VERDICTS = ("OK", "NOT_RUN")


class GateError(Exception):
    """Input cannot be evaluated (CLI exit 2)."""


def load(path):
    try:
        recs = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    except (OSError, ValueError) as e:
        raise GateError(f"cannot read {path}: {e}")
    if not any(r.get("type") == "plan" for r in recs):
        raise GateError(f"{path}: no plan record")
    return recs


def _plan(recs):
    return next(r for r in recs if r["type"] == "plan")


def _end(recs):
    return next((r for r in recs if r["type"] == "end"), None)


def variant_key(plan):
    flags = ",".join(f"{k}={json.dumps(v)}" for k, v in sorted((plan.get("flags") or {}).items()) if v is not None)
    return plan["plan_name"] + "|" + ",".join(f"{k}={v}" for k, v in sorted(plan["variant"].items())) + "|" + flags


def flags_text(plan):
    return ", ".join(f"{k}={json.dumps(v)}" for k, v in sorted((plan.get("flags") or {}).items()) if v is not None)


def env_text(plan):
    e = plan.get("environment")
    return f" · environment: fault={e['fault']}, certify_release={e['certify_release']}" if e else ""


def observe(rec):
    """(suite-style outcome, fingerprint) of a module record; a missing record is INFRA."""
    if rec is None or rec["outcome"] == "infra":
        return "INFRA", None
    fp = rec["failed_conditions"][0]["condition"] if rec["outcome"] == "fail" and rec.get("failed_conditions") else None
    return OUT2EXP[rec["outcome"]], fp


def _txt(o, fp):
    return f"{o} {fp}" if fp else o


def _warnings(rec):
    return sorted({w["condition"] for w in rec.get("warnings") or []})


def _by_module(recs):
    return {r["module"]: r for r in recs if r["type"] == "module"}


def init_benchmark(recs, src, label=""):
    plan, end, mods = _plan(recs), _end(recs), _by_module(recs)
    if end is None or end["exit"] != 0 or any(mods.get(m) is None or mods[m]["outcome"] == "infra" for m in plan["modules"]):
        raise GateError("cannot baseline an infra/aborted run")
    vk = variant_key(plan)
    entries = []
    for m in plan["modules"]:
        o, fp = observe(mods[m])
        entries.append({"module": m, "variant_key": vk, "expected": o, "first_failure": fp,
                        "expected_warnings": _warnings(mods[m]), "finding": None, "reason": "", "ki": None})
    return {"benchmark_version": 2, "label": label, "component": plan["component"], "config_name": plan["config_name"],
            "variant_key": vk, "source_run": f"{src} (run_id {plan['run_id']})", "entries": entries}


def validate(bench):
    bad = [] if bench.get("benchmark_version") == 2 else ["benchmark_version must be 2"]
    seen = set()
    for e in bench.get("entries", []):
        m, p = e.get("module"), []
        if not str(e.get("reason") or "").strip():
            p.append("empty reason")
        if e.get("expected") == "FAILED":
            if not FINDING.match(str(e.get("finding") or "")):
                p.append("FAILED needs finding F-CERT-n/F-VER-n")
            if not e.get("first_failure"):
                p.append("FAILED needs first_failure")
        elif e.get("first_failure") is not None:
            p.append("non-FAILED must have null first_failure")
        w = e.get("expected_warnings")
        if not isinstance(w, list) or not all(isinstance(x, str) for x in w) or w != sorted(set(w)):
            p.append("expected_warnings must be a sorted unique list of strings")
        if e.get("expected") not in SEV:
            p.append("bad expected")
        if m in seen:
            p.append("duplicate module")
        seen.add(m)
        if e.get("variant_key") != bench.get("variant_key"):
            p.append("entry variant_key differs from file")
        bad += [f"{m}: {x}" for x in p]
    return bad


def load_benchmark(path):
    try:
        b = json.loads(Path(path).read_text())
        b["entries"], b["variant_key"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise GateError(f"invalid benchmark {path}: {e}")
    bad = validate(b)
    if bad:
        raise GateError(f"invalid benchmark {path}: " + "; ".join(bad))
    return b


def evaluate(recs, bench, strict=False):
    plan, end, mods = _plan(recs), _end(recs), _by_module(recs)
    rk = variant_key(plan)
    if rk != bench["variant_key"]:
        raise GateError(f"benchmark {bench.get('label')} is for {bench['variant_key']}, run is {rk}")
    ent = {e["module"]: e for e in bench["entries"]}
    rows = []

    def row(m, exp, obs, verdict, finding="", detail=""):
        rows.append({"module": m, "expected": exp, "observed": obs, "verdict": verdict, "finding": finding or "",
                     "detail": detail[:120]})

    def exp_of(m):
        e = ent.get(m)
        return _txt(e["expected"], e["first_failure"]) if e else ""

    if end is not None and end["exit"] == 2:
        row("(run)", "", "INFRA", "INFRA", "", f"run aborted: {end.get('error')}")
        for m in ent:
            row(m, exp_of(m), "INFRA", "INFRA", ent[m]["finding"], "not run (aborted)")
    else:
        for m in plan["modules"]:
            e, rec = ent.get(m), mods.get(m)
            o, fp = observe(rec)
            obs = _txt(o, fp)
            if rec is None:
                row(m, exp_of(m), obs, "INFRA", "", "no record (runner died?)")
            elif o == "INFRA":
                row(m, exp_of(m), obs, "INFRA", "", rec.get("infra_reason") or "")
            elif e is None:
                row(m, "", obs, "UNBENCHMARKED")
            elif o == e["expected"]:
                if o == "FAILED" and fp != e["first_failure"]:
                    row(m, exp_of(m), obs, "NEW_FAILURE", e["finding"], f"expected {e['first_failure']}, got {fp}")
                elif strict and o == "WARNING":
                    row(m, exp_of(m), obs, "STRICT_WARNING", e["finding"], "warning under --strict")
                else:
                    seen = _warnings(rec)
                    extra, gone = sorted(set(seen) - set(e["expected_warnings"])), sorted(set(e["expected_warnings"]) - set(seen))
                    if extra:
                        row(m, exp_of(m), obs, "NEW_WARNING", e["finding"],
                            f"new warning(s): {', '.join(extra)}" + (f"; gone: {', '.join(gone)}" if gone else ""))
                    elif gone:
                        row(m, exp_of(m), obs, "STALE", e["finding"], f"expected warning gone: {', '.join(gone)}")
                    else:
                        row(m, exp_of(m), obs, "OK", e["finding"])
            elif SEV[o] < SEV[e["expected"]]:
                row(m, exp_of(m), obs, "STALE", e["finding"], "benchmark stale: update entry")
            else:
                row(m, exp_of(m), obs, "REGRESSION", e["finding"])
        for m in ent:
            if m not in plan["modules"]:
                row(m, exp_of(m), "", "NOT_RUN", ent[m]["finding"], "not in this run's module list")
    summary = Counter(r["verdict"].lower() for r in rows)
    red = any(r["verdict"] not in OK_VERDICTS for r in rows)
    return {"rows": rows, "red": red, "summary": dict(summary), "plan": plan, "bench": bench}


def _c(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def gate_markdown(res):
    plan, bench, s = res["plan"], res["bench"], res["summary"]
    if res["red"]:
        verdict = "RED (" + ", ".join(f"{k} {v}" for k, v in s.items() if k not in ("ok", "not_run")) + ")"
    else:
        verdict = f"GREEN ({s.get('ok', 0)} ok)"
    out = [f"### Gate {plan['config_name']}: {verdict}",
           f"run `{plan['run_id']}` · benchmark: {bench.get('label')} · flags: {flags_text(plan)}{env_text(plan)}",
           "| module | expected | observed | verdict | finding | detail |", "|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(_c(r[k]) for k in ("module", "expected", "observed", "verdict", "finding", "detail")) + " |"
            for r in res["rows"]]
    return "\n".join(out) + "\n"


def diff(a, b):
    pa, pb, ma, mb = _plan(a), _plan(b), _by_module(a), _by_module(b)
    order = list(pa["modules"]) + [m for m in pb["modules"] if m not in pa["modules"]]
    rows = []
    for m in order:
        inA, inB = m in pa["modules"], m in pb["modules"]
        va, vb = _txt(*observe(ma.get(m))), _txt(*observe(mb.get(m)))
        if not inB:
            ch = "only in A"
        elif not inA:
            ch = "only in B"
        elif va == vb:
            continue
        else:
            oa, ob = va.split(" ")[0], vb.split(" ")[0]
            ch = f"outcome {oa}→{ob}" if oa != ob else "first failure changed"
        rows.append((m, va if inA else "", vb if inB else "", ch))
    total = len(order)
    head = f"### Diff {pa['config_name']} `{pa['run_id']}` → {pb['config_name']} `{pb['run_id']}`: " + \
           (f"{len(rows)} of {total} modules changed" if rows else "no changes")
    out = [head]
    if env_text(pa) or env_text(pb):
        out.append(f"environment A:{env_text(pa)[2:].removeprefix(' environment:') or ' none'} · B:{env_text(pb)[2:].removeprefix(' environment:') or ' none'}")
    if variant_key(pa) != variant_key(pb):
        out.append("note: variant keys differ")
    if rows:
        out += ["| module | A | B | change |", "|---|---|---|---|"]
        out += ["| " + " | ".join(_c(x) for x in r) + " |" for r in rows]
    return "\n".join(out) + "\n"
