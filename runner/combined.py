"""Aggregate several gated runs into index.html + badge.json + gate.md. Stdlib only."""
import json
from collections import Counter
from html import escape as e
from pathlib import Path

from . import gate

CSS = ("body{font:14px system-ui,sans-serif;margin:16px;max-width:1200px}table{border-collapse:collapse;margin:8px 0 24px}"
       "td,th{border:1px solid #bbb;padding:3px 8px;text-align:left;vertical-align:top}th{background:#eee}"
       ".red{color:#b00020;font-weight:bold}.green{color:#176f2c;font-weight:bold}")


def write(out_dir, runs, note=None):
    """runs: [(jsonl_path, benchmark_path_or_None)]. Returns True if any gated run is red."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for rp, bp in runs:
        recs = gate.load(rp)
        res = gate.evaluate(recs, gate.load_benchmark(bp)) if bp else None
        items.append((recs, res))
    gated = [r for _, r in items if r]
    red = any(r["red"] for r in gated)
    n = sum(len(r["plan"]["modules"]) for r in gated)
    k = sum(1 for r in gated for x in r["rows"] if x["verdict"] not in gate.OK_VERDICTS)
    if not gated:
        badge = ("not gated", "lightgrey")
    elif red:
        badge = (f"red · {k} of {n} modules off benchmark", "red")
    else:
        badge = (f"benchmark green · {n} modules", "brightgreen")
    (out / "badge.json").write_text(json.dumps({"schemaVersion": 1, "label": "Certify ↔ Verify OpenID 1.0",
                                                "message": badge[0], "color": badge[1]}, ensure_ascii=False))
    (out / "gate.md").write_text("\n".join(gate.gate_markdown(r) for r in gated))

    summ, detail = [], []
    for recs, res in items:
        p, end = gate._plan(recs), gate._end(recs)
        counts = Counter(m["outcome"] for m in recs if m["type"] == "module")
        v = "not gated" if not res else ("<span class=red>RED</span>" if res["red"] else "<span class=green>GREEN</span>")
        summ.append(f"<tr><td>{e(p['config_name'])}</td><td>{e(p['component'])}</td><td>{e(p['run_id'])}</td>"
                    f"<td>{e(gate.flags_text(p))}</td><td>{e(', '.join(f'{k} {c}' for k, c in sorted(counts.items())))}</td>"
                    f"<td>{v}</td></tr>")
        grows = {r["module"]: r for r in res["rows"]} if res else {}
        body = []
        for m in p["modules"]:
            rec, g = gate._by_module(recs).get(m), grows.get(m, {})
            o, fp = gate.observe(rec)
            msg = fp or (rec or {}).get("message") or (rec or {}).get("infra_reason") or ""
            url = (rec or {}).get("log_url")
            link = f"<a href=\"{e(url)}\">log</a>" if url and url.startswith(("http://", "https://")) else ""
            body.append("<tr>" + "".join(f"<td>{x}</td>" for x in (
                e(m), e(o), e(msg), e(g.get("expected", "")), e(g.get("verdict", "")), e(g.get("finding", "")), link)) + "</tr>")
        detail.append(f"<h2>{e(p['config_name'])} <small>{e(p['run_id'])}</small></h2>"
                      + (f"<p>exit {e(str(end['exit']))}{': ' + e(str(end.get('error'))) if end and end.get('error') else ''}</p>" if end else "<p>no end record</p>")
                      + "<table><tr><th>module<th>outcome<th>fingerprint / message<th>expected<th>verdict<th>finding<th>suite log</tr>"
                      + "".join(body) + "</table>")
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Certify ↔ Verify OpenID 1.0 conformance</title>"
        f"<style>{CSS}</style><h1>Certify ↔ Verify OpenID 1.0 conformance</h1>"
        + (f"<p>{e(note)}</p>" if note else "")
        + "<table><tr><th>config<th>component<th>run id<th>flags<th>counts<th>gate</tr>" + "".join(summ) + "</table>"
        + "".join(detail))
    return red
