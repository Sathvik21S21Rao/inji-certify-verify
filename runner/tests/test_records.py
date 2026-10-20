import copy
import io
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from runner import records as R

HERE = Path(__file__).parent
V = Draft202012Validator(json.loads((HERE.parent / "schema" / "results.schema.json").read_text()))
NAMES = ["certify-shim-on", "certify-shim-off", "verify-redirect-uri", "verify-x509", "infra-interrupted-unknown"]


def load(name):
    return [json.loads(l) for l in (HERE / "fixtures" / f"{name}.jsonl").read_text().splitlines()]


@pytest.mark.parametrize("name", NAMES)
def test_fixture_valid_and_ordered(name):
    recs = load(name)
    for r in recs:
        V.validate(r)
    assert recs[0]["type"] == "plan" and recs[-1]["type"] == "end"
    mods = recs[1:-1]
    assert all(m["type"] == "module" for m in mods)
    assert [m["module"] for m in mods] == recs[0]["modules"]
    assert recs[-1]["exit"] == (1 if any(m["outcome"] == "infra" for m in mods) else 0)


@pytest.mark.parametrize("status,result,want", [
    ("FINISHED", "PASSED", "pass"), ("FINISHED", "WARNING", "warning"), ("FINISHED", "REVIEW", "review"),
    ("FINISHED", "SKIPPED", "skip"), ("FINISHED", "FAILED", "fail"), ("INTERRUPTED", "FAILED", "fail"),
    ("INTERRUPTED", "UNKNOWN", "infra"), ("RUNNING", None, "infra"), (None, None, "infra"),
    ("INTERRUPTED", "PASSED", "infra"),
])
def test_outcome_for(status, result, want):
    assert R.outcome_for(status, result) == want


def test_norm_ts_and_iso():
    assert R.norm_ts("2026-10-20T10:43:42.236090127Z") == "2026-10-20T10:43:42.236090Z"
    assert R.norm_ts(None) is None
    assert R.iso_from_ms(1792493022240) == "2026-10-20T10:43:42.240Z"


def counts(name):
    return load(name)[-1]["counts"]


def test_certify_shim_on_counts():
    c = counts("certify-shim-on")
    assert (c["pass"], c["skip"], c["fail"]) == (3, 2, 9)


def test_verify_redirect_uri():
    mods = load("verify-redirect-uri")[1:-1]
    assert [m["outcome"] for m in mods] == ["fail"] * 9
    assert all(m["failed_conditions"][0]["condition"] == "VP1FinalValidateVpFormatsSupportedInClientMetadata" for m in mods)


def test_certify_shim_off_first_failure():
    mods = [m for m in load("certify-shim-off")[1:-1] if m["outcome"] == "fail"]
    assert sum(m["failed_conditions"][0]["condition"] == "CheckServerConfiguration" for m in mods) == 12


def test_infra_fixture():
    m = load("infra-interrupted-unknown")[1]
    assert m["outcome"] == "infra" and m["message"].startswith("INFRA: ") and m["started"]


def test_negative_schema():
    bad = copy.deepcopy(load("infra-interrupted-unknown")[1])
    bad["infra_reason"] = None
    assert not V.is_valid(bad)
    plan = copy.deepcopy(load("certify-shim-on")[0])
    plan["flags"]["certify_as_metadata_shim"] = None
    assert not V.is_valid(plan)


def test_interrupted_unknown_reason_and_emitter(tmp_path):
    m = R.module_record(module="m", info={"started": "2026-10-20T10:00:00.1234567Z"}, log=[], suite_url="http://s/",
                        evidence=[], status="INTERRUPTED", result="UNKNOWN", test_id="t")
    assert m["infra_reason"] == "interrupted without verdict"
    V.validate(m)
    buf, p = io.StringIO(), tmp_path / "c.jsonl"
    e = R.Emitter(buf, str(p))
    e.emit(m)
    assert buf.getvalue() == p.read_text() and buf.getvalue().count("\n") == 1


def test_interrupted_null_result_reason_is_last_log_msg():
    m = load("infra-interrupted-unknown")[1]
    assert (m["status"], m["result"], m["outcome"]) == ("INTERRUPTED", None, "infra")
    assert m["infra_reason"].startswith("Test was interrupted before it could complete")
    assert R.outcome_for("INTERRUPTED", None) == "infra"
    log = [{"msg": "a", "time": 1}, {"msg": "last", "time": 2}]
    r = R.module_record(module="m", info=None, log=log, suite_url="http://s/", evidence=[], status="INTERRUPTED", result=None, test_id="t")
    assert r["infra_reason"] == "last"
