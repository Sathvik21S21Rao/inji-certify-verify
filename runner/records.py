"""Builders for the runner JSONL contract v1.1 (runner/schema/CONTRACT.md). Stdlib only."""
import json
import re
from datetime import datetime, timezone

SCHEMA_VERSION = "1.1"
OUTCOMES = ("pass", "warning", "review", "skip", "fail", "infra")
_MAP = {"PASSED": "pass", "WARNING": "warning", "REVIEW": "review", "SKIPPED": "skip"}  # with FINISHED


def iso_from_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def norm_ts(s):
    """Trim suite nanosecond fractions to 6 digits (schema allows any, consumers parse micros)."""
    return None if s is None else re.sub(r"(\.\d{6})\d+", r"\1", s)


def outcome_for(status, result) -> str:
    if result == "FAILED":
        return "fail"
    if status == "FINISHED" and result in _MAP:
        return _MAP[result]
    return "infra"


def plan_record(*, run_id, alias, component, config_name, plan_name, plan_id, variant,
                shim, evidence_upload, suite_url, modules, started, environment=None) -> dict:
    rec = {"type": "plan", "schema_version": SCHEMA_VERSION, "run_id": run_id, "alias": alias,
            "component": component, "config_name": config_name, "plan_name": plan_name,
            "plan_id": plan_id, "variant": variant,
            "flags": {"certify_as_metadata_shim": shim, "verify_evidence_upload": evidence_upload},
            "suite_url": suite_url, "modules": list(modules), "started": norm_ts(started)}
    if environment is not None:
        rec["environment"] = dict(environment)
    return rec


def _conds(log, kind):
    return [{"condition": e.get("src") or "unknown", "message": str(e.get("msg", "")),
             "requirements": list(e.get("requirements") or [])}
            for e in log if e.get("result") == kind]


def module_record(*, module, info, log, suite_url, evidence, infra_reason=None,
                  status=None, result=None, test_id=None, started=None) -> dict:
    # `started` is an addition to the spec'd interface: lets an info-less record keep the real start time.
    info, log = info or {}, log or []
    status = status if status is not None else info.get("status")
    result = result if result is not None else info.get("result")
    test_id = test_id or info.get("testId") or info.get("_id")
    failed, warns = _conds(log, "FAILURE"), _conds(log, "WARNING")
    outcome = "infra" if infra_reason else outcome_for(status, result)
    if outcome == "infra" and not infra_reason:
        if status == "INTERRUPTED" and result in ("UNKNOWN", None):
            infra_reason = (str(log[-1].get("msg")) if log and log[-1].get("msg") else None) or "interrupted without verdict"
        else:
            infra_reason = f"unexpected suite state status={status} result={result}"
    if outcome == "infra":
        msg = f"INFRA: {infra_reason}"
    elif outcome == "pass":
        msg = ""
    elif outcome == "warning":
        msg = "warnings: " + ", ".join(w["condition"] for w in warns)
    elif outcome == "review":
        msg = "needs human review: evidence image uploaded by harness"
    elif outcome == "skip":
        msg = next((str(e.get("msg", "")) for e in log if e.get("result") == "SKIPPED"), "skipped")
    else:
        msg = f"{failed[0]['condition']}: {failed[0]['message']}" if failed else "failed (no failure condition logged)"
    times = [e["time"] for e in log if "time" in e]
    return {"type": "module", "module": module, "test_id": test_id, "status": status, "result": result,
            "outcome": outcome, "message": msg[:500], "failed_conditions": failed, "warnings": warns,
            "log_url": f"{suite_url}log-detail.html?log={test_id}" if test_id else None,
            "started": norm_ts(started or info.get("started")),
            "finished": iso_from_ms(max(times)) if times else None,
            "evidence": list(evidence), "infra_reason": infra_reason if outcome == "infra" else None}


def end_record(*, modules, error, export, finished) -> dict:
    counts = {o: sum(m["outcome"] == o for m in modules) for o in OUTCOMES}
    return {"type": "end", "exit": 2 if error else 1 if counts["infra"] else 0, "counts": counts,
            "error": error, "export": export, "finished": norm_ts(finished)}


class Emitter:
    def __init__(self, stream, copy_path=None):
        self.stream, self.copy_path = stream, copy_path

    def emit(self, record: dict) -> None:
        line = json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n"
        self.stream.write(line)
        self.stream.flush()
        if self.copy_path:
            with open(self.copy_path, "a", encoding="utf-8") as f:
                f.write(line)
