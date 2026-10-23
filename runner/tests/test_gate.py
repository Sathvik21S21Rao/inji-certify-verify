import copy
import json
import re
from pathlib import Path

import pytest

from runner import combined, gate
from runner.__main__ import main

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "runner" / "tests" / "fixtures"
LIVE = ROOT / "evidence" / "sp2" / "live"
CONFIGS = {"certify-shim-off": "certify", "certify-shim-on": "certify", "verify-redirect-uri": "verify",
           "verify-x509": "verify"}


def recs(name):
    return gate.load(FIX / f"{name}.jsonl")


def write(path, rs):
    path.write_text("".join(json.dumps(r) + "\n" for r in rs))
    return str(path)


def mod(rs, n=0):
    return [r for r in rs if r["type"] == "module"][n]


def set_out(r, outcome, fp=None):
    r["outcome"] = outcome
    r["failed_conditions"] = [{"condition": fp, "message": "m", "requirements": []}] if fp else []
    r["infra_reason"] = "boom" if outcome == "infra" else None


def bench_of(rs, **kw):
    """Benchmark whose expectation is exactly what `rs` shows (infra modules baselined as pass)."""
    base = copy.deepcopy(rs)
    for r in base:
        if r["type"] == "module" and r["outcome"] == "infra":
            set_out(r, "pass")
    for r in base:
        if r["type"] == "end":
            r["exit"] = 0
    b = gate.init_benchmark(base, "x.jsonl", "test")
    for i, e in enumerate(b["entries"]):
        e["reason"] = "r"
        if e["expected"] == "FAILED":
            e["finding"] = "F-CERT-1"
    return b


def verdicts(rs, b, **kw):
    return [r["verdict"] for r in gate.evaluate(rs, b, **kw)["rows"]]


def test_ok_and_variant_key():
    rs = recs("certify-shim-off")
    b = bench_of(rs)
    res = gate.evaluate(rs, b)
    assert not res["red"] and set(verdicts(rs, b)) == {"OK"}
    assert gate.variant_key(rs[0]).endswith("|certify_as_metadata_shim=false")
    assert gate.variant_key(recs("certify-shim-on")[0]).endswith("|certify_as_metadata_shim=true")
    assert gate.gate_markdown(res).startswith("### Gate certify-shim-off: GREEN (14 ok)")


@pytest.mark.parametrize("fixture,idx,new,fp,verdict", [
    ("certify-shim-on", 4, "pass", None, "STALE"),  # FAILED -> PASSED (index 4 is a FAILED module)
    ("certify-shim-on", 6, "pass", None, "STALE"),  # SKIPPED -> PASSED
    ("certify-shim-on", 7, "fail", "X", "REGRESSION"),  # PASSED -> FAILED
    ("certify-shim-on", 4, "fail", "Other", "NEW_FAILURE"),
])
def test_verdicts(fixture, idx, new, fp, verdict):
    rs = recs(fixture)
    b = bench_of(rs)
    rs2 = copy.deepcopy(rs)
    set_out(mod(rs2, idx), new, fp)
    res = gate.evaluate(rs2, b)
    assert res["red"] and res["rows"][idx]["verdict"] == verdict, res["rows"][idx]


def test_review_to_fail_and_unbenchmarked_and_strict():
    rs = recs("certify-shim-on")
    rs2 = copy.deepcopy(rs)
    set_out(mod(rs2, 7), "review")
    b = bench_of(rs2)
    rs3 = copy.deepcopy(rs2)
    set_out(mod(rs3, 7), "fail", "X")
    assert gate.evaluate(rs3, b)["rows"][7]["verdict"] == "REGRESSION"
    b2 = bench_of(rs)
    b2["entries"].pop(0)
    assert gate.evaluate(rs, b2)["rows"][0]["verdict"] == "UNBENCHMARKED"
    rs4 = copy.deepcopy(rs)
    set_out(mod(rs4, 7), "warning")
    b4 = bench_of(rs4)
    assert not gate.evaluate(rs4, b4)["red"]
    assert gate.evaluate(rs4, b4, True)["rows"][7]["verdict"] == "STRICT_WARNING"


def test_infra_variants():
    rs = recs("infra-interrupted-unknown")
    b = bench_of(rs)
    res = gate.evaluate(rs, b)
    assert res["red"] and "INFRA" in verdicts(rs, b)
    full = recs("certify-shim-off")
    bf = bench_of(full)
    trunc = [r for r in full if r["type"] != "end"][:5]
    v = verdicts(trunc, bf)
    assert v[:4] == ["OK"] * 4 and v[4:] == ["INFRA"] * 10
    ab = [full[0], {**full[-1], "exit": 2, "error": "suite unreachable"}]
    rows = gate.evaluate(ab, bf)["rows"]
    assert len(rows) == 15 and {r["verdict"] for r in rows} == {"INFRA"} and "suite unreachable" in rows[0]["detail"]


def test_not_run_not_red():
    rs = recs("certify-shim-off")
    b = bench_of(rs)
    sel = [r for r in rs if r["type"] != "module" or r["module"] == rs[0]["modules"][0]]
    sel[0] = {**sel[0], "modules": rs[0]["modules"][:1]}
    res = gate.evaluate(sel, b)
    assert not res["red"] and res["summary"]["not_run"] == 13


def test_variant_mismatch_and_validation(tmp_path, capsys):
    off, on = recs("certify-shim-off"), recs("certify-shim-on")
    with pytest.raises(gate.GateError, match="is for"):
        gate.evaluate(on, bench_of(off))
    good = bench_of(off)
    cases = {}
    for name, f in {
        "empty reason": lambda b: b["entries"][0].update(reason=""),
        "bad finding": lambda b: b["entries"][0].update(finding="nope"),
        "null finding": lambda b: b["entries"][0].update(finding=None),
        "no first_failure": lambda b: b["entries"][0].update(first_failure=""),
        "non-FAILED with first_failure": lambda b: b["entries"][0].update(expected="PASSED"),
        "duplicate": lambda b: b["entries"].append(dict(b["entries"][0])),
        "entry variant_key": lambda b: b["entries"][0].update(variant_key="other"),
        "v1 file": lambda b: b.update(benchmark_version=1),
        "missing expected_warnings": lambda b: b["entries"][0].pop("expected_warnings"),
        "unsorted warnings": lambda b: b["entries"][0].update(expected_warnings=["B", "A"]),
        "duplicate warnings": lambda b: b["entries"][0].update(expected_warnings=["A", "A"]),
        "non-string warnings": lambda b: b["entries"][0].update(expected_warnings=[1]),
    }.items():
        b = copy.deepcopy(good)
        f(b)
        p = tmp_path / (name.replace(" ", "_") + ".json")
        p.write_text(json.dumps(b))
        with pytest.raises(gate.GateError):
            gate.load_benchmark(p)
        assert main(["gate", str(FIX / "certify-shim-off.jsonl"), str(p)]) == 2
    capsys.readouterr()
    assert main(["gate", str(tmp_path / "missing.jsonl"), str(p)]) == 2
    empty = tmp_path / "e.jsonl"
    empty.write_text("")
    assert main(["gate", str(empty), str(p)]) == 2


def test_benchmark_init(tmp_path):
    out = tmp_path / "b.json"
    assert main(["benchmark", "init", str(FIX / "certify-shim-on.jsonl"), "--out", str(out), "--label", "L"]) == 0
    b = json.loads(out.read_text())
    e = {x["module"][19:]: x for x in b["entries"]}
    assert b["label"] == "L" and e["batch-issuance"]["expected"] == "SKIPPED" and e["batch-issuance"]["first_failure"] is None
    assert e["happy-flow"]["first_failure"] == "EnsureHttpStatusCodeIsAnyOf" and e["happy-flow"]["reason"] == ""
    assert main(["benchmark", "init", str(FIX / "certify-shim-on.jsonl"), "--out", str(out)]) == 2  # exists
    assert main(["benchmark", "init", str(FIX / "certify-shim-on.jsonl"), "--out", str(out), "--force"]) == 0
    assert main(["benchmark", "init", str(FIX / "infra-interrupted-unknown.jsonl"), "--out", str(tmp_path / "i.json")]) == 2
    assert not (tmp_path / "i.json").exists()


def test_diff():
    on, off = recs("certify-shim-on"), recs("certify-shim-off")
    d = gate.diff(off, on)
    assert "outcome FAILED→PASSED" in d and "first failure changed" in d and "variant keys differ" in d
    assert "modules changed" in d
    same = gate.diff(on, on)
    assert "no changes" in same and "|" not in same
    short = copy.deepcopy(on)
    short[0]["modules"] = short[0]["modules"][:-1]
    d2 = gate.diff(on, short)
    assert "only in A" in d2
    assert "only in B" in gate.diff(short, on)


def test_combined(tmp_path):
    rs = recs("certify-shim-off")
    rp = write(tmp_path / "r.jsonl", rs)
    bp = tmp_path / "b.json"
    bp.write_text(json.dumps(bench_of(rs)))
    out = tmp_path / "green"
    assert combined.write(out, [(rp, str(bp))], note="n") is False
    badge = json.loads((out / "badge.json").read_text())
    assert badge["color"] == "brightgreen" and badge["message"] == "benchmark green · 14 modules" and badge["schemaVersion"] == 1
    assert (out / "gate.md").read_text().startswith("### Gate")
    bad = copy.deepcopy(rs)
    set_out(mod(bad, 2), "pass")
    set_out(mod(bad, 3), "pass")
    bad[3]["message"] = "<script>alert(1)</script>"
    rp2 = write(tmp_path / "r2.jsonl", bad)
    assert combined.write(tmp_path / "red", [(rp2, str(bp))]) is True
    assert json.loads((tmp_path / "red" / "badge.json").read_text()) == {
        "schemaVersion": 1, "label": "Certify ↔ Verify OpenID 1.0", "message": "red · 2 of 14 modules off benchmark", "color": "red"}
    assert combined.write(tmp_path / "none", [(rp2, None)]) is False
    nb = json.loads((tmp_path / "none" / "badge.json").read_text())
    assert nb["color"] == "lightgrey" and nb["message"] == "not gated"
    html = (tmp_path / "none" / "index.html").read_text()
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert main(["combined", "--out", str(tmp_path / "cli"), rp2 + "=" + str(bp)]) == 1


@pytest.mark.parametrize("cfg", CONFIGS)
def test_committed_benchmarks(cfg):
    bp = ROOT / "plans" / CONFIGS[cfg] / f"{cfg}.benchmark.json"
    assert gate.load_benchmark(bp)
    for n in (1, 2, 3):
        assert main(["gate", str(LIVE / cfg / f"run{n}" / "results.jsonl"), str(bp)]) == 0, (cfg, n)


def test_committed_benchmark_wrong_variant():
    bp = ROOT / "plans" / "certify" / "certify-shim-off.benchmark.json"
    assert main(["gate", str(FIX / "certify-shim-on.jsonl"), str(bp)]) == 2
    assert main(["gate", str(LIVE / "certify-shim-on" / "run1" / "results.jsonl"), str(bp)]) == 2


def with_warnings(rs, n, conds):
    rs = copy.deepcopy(rs)
    mod(rs, n)["warnings"] = [{"condition": c, "message": "m", "requirements": []} for c in conds]
    return rs


def test_warning_set_gate():
    rs = with_warnings(recs("certify-shim-off"), 0, ["B", "A", "B"])
    b = bench_of(rs)
    assert b["entries"][0]["expected_warnings"] == ["A", "B"] and b["benchmark_version"] == 2
    assert not gate.evaluate(rs, b)["red"]
    r = gate.evaluate(with_warnings(rs, 0, ["A", "B", "C"]), b)["rows"][0]
    assert (r["verdict"], r["detail"]) == ("NEW_WARNING", "new warning(s): C")
    r = gate.evaluate(with_warnings(rs, 0, ["A"]), b)["rows"][0]
    assert (r["verdict"], r["detail"]) == ("STALE", "expected warning gone: B")
    r = gate.evaluate(with_warnings(rs, 0, ["A", "C", "D"]), b)["rows"][0]
    assert (r["verdict"], r["detail"]) == ("NEW_WARNING", "new warning(s): C, D; gone: B")
    # outcome verdicts take precedence over the warning check
    rs2 = with_warnings(rs, 0, ["Z"])
    set_out(mod(rs2, 0), "fail", "X")
    assert gate.evaluate(rs2, b)["rows"][0]["verdict"] == "NEW_FAILURE"


def test_c014_new_warning(capsys):
    bp = ROOT / "plans" / "certify" / "certify-shim-off.benchmark.json"
    run = ROOT / "evidence" / "sp4" / "SP4.8" / "c014-r2" / "certify-shim-off" / "results.jsonl"
    assert main(["gate", str(run), str(bp)]) == 1
    rows = [l for l in capsys.readouterr().out.splitlines() if "NEW_WARNING" in l]
    assert len(rows) == 1 and "oid4vci-1_0-issuer-metadata-test" in rows[0] \
        and "VCICheckForOldSdJwtFormatInCredentialConfigurations" in rows[0]


def _known_good():
    out = []
    for cfg, comp in CONFIGS.items():
        ps = sorted(LIVE.glob(f"{cfg}/run[123]/results.jsonl")) + sorted(
            (ROOT / "evidence" / "sp4" / "SP4.4").glob(f"kg-*/{cfg}/results.jsonl"))
        out += [(ROOT / "plans" / comp / f"{cfg}.benchmark.json", p) for p in ps]
    return out


@pytest.mark.parametrize("bp,run", _known_good(), ids=lambda p: "/".join(p.parts[-3:-1]))
def test_known_good_runs_green(bp, run):
    assert main(["gate", str(run), str(bp)]) == 0


def test_badge_svg(tmp_path):
    rs = recs("certify-shim-off")
    bp = tmp_path / "b.json"
    bp.write_text(json.dumps(bench_of(rs)))
    combined.write(tmp_path / "o", [(write(tmp_path / "r.jsonl", rs), str(bp))])
    svg = (tmp_path / "o" / "badge.svg").read_text()
    assert svg.startswith("<svg") and "benchmark green · 14 modules" in svg and "#4c1" in svg
    assert "<img src=badge.svg" in (tmp_path / "o" / "index.html").read_text()


def test_benchmark_update(tmp_path):
    rs = recs("certify-shim-off")
    b = bench_of(rs)
    names = [e["module"] for e in b["entries"]]
    same, md = gate.update_benchmark(rs, b, "r.jsonl")
    assert same == b and "no changes" in md

    run = copy.deepcopy(rs)
    set_out(mod(run, 0), "fail", "SomethingNew")                    # NEW_FAILURE: finding cleared
    mod(run, 1)["warnings"] = [{"condition": "W1", "message": "m"}]  # NEW_WARNING only: finding kept
    set_out(mod(run, 2), "infra")                                   # INFRA: entry kept as is
    b2 = copy.deepcopy(b)
    del b2["entries"][3]                                            # module 3 becomes UNBENCHMARKED
    b2["entries"].append(dict(b["entries"][4], module="gone-module"))  # NOT_RUN: kept
    new, md = gate.update_benchmark(run, b2, "r.jsonl")
    ent = {e["module"]: e for e in new["entries"]}
    assert ent[names[0]]["first_failure"] == "SomethingNew" and ent[names[0]]["finding"] is None
    assert ent[names[0]]["reason"] == ""
    assert ent[names[1]]["expected_warnings"] == ["W1"] and ent[names[1]]["finding"] == b["entries"][1]["finding"]
    assert ent[names[1]]["reason"] == ""
    assert ent[names[2]] == b["entries"][2] and ent["gone-module"]["reason"] == "r"
    assert ent[names[3]]["reason"] == "" and new["entries"][-1]["module"] == names[3]  # new entries go last
    assert "3 entries to review" in md and "Kept unchanged (INFRA in this run)" in md
    assert gate.validate(new)  # unreviewed: the gate refuses it

    aborted = copy.deepcopy(rs)
    next(r for r in aborted if r["type"] == "end")["exit"] = 2
    with pytest.raises(gate.GateError):
        gate.update_benchmark(aborted, b, "r.jsonl")


def test_benchmark_update_cli(tmp_path):
    rs = recs("certify-shim-off")
    bp = tmp_path / "b.json"
    bp.write_text(json.dumps(bench_of(rs)))
    run = copy.deepcopy(rs)
    set_out(mod(run, 0), "fail", "SomethingNew")
    rp = write(tmp_path / "r.jsonl", run)
    assert main(["gate", rp, str(bp)]) == 1
    prop = tmp_path / "p.json"
    assert main(["benchmark", "update", rp, str(bp), "--out", str(prop)]) == 0
    assert main(["gate", rp, str(prop)]) == 2                          # needs review first
    assert main(["benchmark", "update", rp, str(prop)]) == 0             # reruns on an unreviewed file, in place
    p = json.loads(prop.read_text())
    e = p["entries"][0]
    e["reason"], e["finding"] = "reviewed", "F-CERT-9"
    prop.write_text(json.dumps(p))
    assert main(["gate", rp, str(prop)]) == 0
