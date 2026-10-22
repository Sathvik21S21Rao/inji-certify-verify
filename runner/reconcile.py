"""Oracle 1: compare MOSIP's TestNG outcome per module with the suite's own plan export. Stdlib only."""
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from .records import outcome_for

KI_PREFIX = "known issue. Hence skipping the testcase"
_NAME = re.compile(r"testCaseName=OIDF_[^_,]+_([^,]+),")
_COUNTS = re.compile(r"-full-report_T-(\d+)_P-(\d+)_S-(\d+)_F-(\d+)_I-(\d+)_KI-(\d+)\.html$")
_ALLOWED = {"pass": {"PASS"}, "warning": {"PASS"}, "review": {"SKIP"}, "skip": {"SKIP"},
            "fail": {"FAIL", "SKIP-KI"}, "infra": {"FAIL-INFRA"}}


class ReconcileError(Exception):
    pass


def testng_rows(xml_path) -> dict:
    """module -> [row kind]; kinds PASS, FAIL, FAIL-INFRA, SKIP, SKIP-KI. test-instance-name is ignored (same on every row)."""
    try:
        root = ET.parse(xml_path).getroot()
    except (OSError, ET.ParseError) as e:
        raise ReconcileError(f"cannot read {xml_path}: {e}")
    rows = defaultdict(list)
    for m in root.iter("test-method"):
        if m.get("data-provider") != "conformance" or m.get("is-config") == "true":
            continue
        val = m.find("params/param[@index='0']/value")
        hit = _NAME.search(val.text or "") if val is not None else None
        if not hit:
            raise ReconcileError(f"{xml_path}: conformance row without a testCaseName")
        msg = (m.findtext("exception/message") or "").strip()
        st = m.get("status")
        if st == "FAIL":
            kind = "FAIL-INFRA" if msg.startswith("INFRA:") else "FAIL"
        elif st == "SKIP":
            kind = "SKIP-KI" if msg.startswith(KI_PREFIX) else "SKIP"
        else:
            kind = st
        rows[hit.group(1)].append(kind)
    return rows


def suite_modules(zip_path):
    """-> (plan_id, module -> [(status, result)]) from test-log-*.json testInfo."""
    mods, plan = defaultdict(list), None
    try:
        with zipfile.ZipFile(zip_path) as z:
            for n in z.namelist():
                if n.startswith("test-log-") and n.endswith(".json"):
                    ti = json.loads(z.read(n))["testInfo"]
                    plan = plan or ti.get("planId")
                    mods[ti["testName"]].append((ti.get("status"), ti.get("result")))
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as e:
        raise ReconcileError(f"cannot read {zip_path}: {e}")
    return plan, mods


def find_export(report_dir):
    zips = sorted(Path(report_dir).glob("conformance/*/*.zip"))
    if len(zips) != 1:
        raise ReconcileError(f"expected exactly one {report_dir}/conformance/*/*.zip, found {len(zips)} (use --export)")
    return zips[0]


def evaluate(report_dir, export=None, strict=False) -> dict:
    report_dir = Path(report_dir)
    rows = testng_rows(report_dir / "testng-results.xml")
    plan, suite = suite_modules(export or find_export(report_dir))
    table, tally = [], defaultdict(int)
    # ponytail: a duplicated name on either side is a flat mismatch; no pairing of the copies
    for mod in sorted(set(rows) | set(suite)):
        r, s = rows.get(mod, []), suite.get(mod, [])
        if len(r) > 1 or len(s) > 1:
            table.append((mod, f"x{len(s)}", "-", f"x{len(r)}", "MISMATCH: duplicate"))
        elif not s:
            ok = r[0] == "FAIL-INFRA"
            tally["infra"] += 1
            table.append((mod, "-", "FAIL INFRA", r[0], "no suite record (infra)" if ok else "MISMATCH: no suite record"))
        elif not r:
            tally[outcome_for(*s[0])] += 1
            table.append((mod, "/".join(map(str, s[0])), "-", "-", "MISMATCH: missing from TestNG"))
        else:
            out = outcome_for(*s[0])
            allowed = set(_ALLOWED[out]) | ({"FAIL"} if strict and out == "warning" else set())
            ok = r[0] in allowed
            tally["fail" if out == "warning" and r[0] == "FAIL" else out] += 1
            table.append((mod, "/".join(map(str, s[0])), " or ".join(sorted(allowed)), r[0],
                          "ok" if ok else "MISMATCH"))
    n = len(table)
    exp = {"T": n, "P": tally["pass"] + tally["warning"], "S": tally["review"] + tally["skip"],
           "F+KI": tally["fail"] + tally["infra"], "I": 0}
    counts = None
    for f in sorted(report_dir.glob("*-full-report_T-*")):
        if (m := _COUNTS.search(f.name)):
            t, p, s_, fl, i, ki = map(int, m.groups())
            counts = {"file": f.name, "actual": {"T": t, "P": p, "S": s_, "F+KI": fl + ki, "I": i}}
    bad = any(v.startswith("MISMATCH") for *_, v in table)
    if counts and counts["actual"] != exp:
        bad = True
    return {"plan_id": plan, "table": table, "expected": exp, "counts": counts, "mismatch": bad}


def markdown(res) -> str:
    t = res["table"]
    out = [f"# Reconciliation: {'MISMATCH' if res['mismatch'] else 'MATCH'} ({len(t)} modules)", "",
           f"Suite plan: {res['plan_id']}", "",
           "| module | suite status/result | expected TestNG | TestNG | verdict |", "|---|---|---|---|---|"]
    out += ["| " + " | ".join(row) + " |" for row in t]
    c, e = res["counts"], res["expected"]
    out.append("")
    if c is None:
        out.append("Counts: no EmailableReport file")
    else:
        out.append(f"Counts ({c['file']}): EmailableReport {c['actual']} vs suite-derived {e}: "
                   + ("match" if c["actual"] == e else "MISMATCH"))
    return "\n".join(out) + "\n"
