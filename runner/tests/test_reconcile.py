import json
import zipfile
from pathlib import Path

import pytest

from runner import reconcile
from runner.__main__ import main

ROOT = Path(__file__).resolve().parents[2]
KI = "known issue. Hence skipping the testcase: x"


def make(tmp_path, suite, rows, counts="T-{T}_P-{P}_S-{S}_F-{F}_I-0_KI-{KI}", zip_=True):
    """suite: {module: (status, result)}; rows: {module: (TestNG status, message)}."""
    d = tmp_path / "testng-report"
    (d / "conformance" / "cfg").mkdir(parents=True)
    xml = ['<testng-results>']
    for mod, (st, msg) in rows.items():
        xml.append(f'<test-method name="setResultTestName" is-config="true" data-provider="conformance" status="PASS"/>')
        xml.append(f'<test-method name="test" data-provider="conformance" test-instance-name="WRONG" status="{st}">'
                   f'<params><param index="0"><value><![CDATA[TestCaseDTO(testCaseName=OIDF_certify_{mod}, endPoint=null)]]>'
                   f'</value></param></params><exception><message><![CDATA[{msg}]]></message></exception></test-method>')
    xml.append('</testng-results>')
    (d / "testng-results.xml").write_text("\n".join(xml))
    if zip_:
        with zipfile.ZipFile(d / "conformance" / "cfg" / "plan.zip", "w") as z:
            for i, (mod, sr) in enumerate(suite.items()):
                name = mod if isinstance(mod, str) else mod[0]
                z.writestr(f"test-log-{name}-{i}.json", json.dumps(
                    {"testInfo": {"testName": name, "testId": str(i), "status": sr[0], "result": sr[1], "planId": "PLAN1"}}))
                z.writestr(f"test-log-{name}-{i}.html", "x")
    if counts:
        (d / f"x-full-report_{counts}.html").write_text("")
    return d


def run(d, *a):
    return main(["reconcile", str(d), *a])


# (suite status/result, TestNG status, message, expected exit non-strict)
CASES = [
    (("FINISHED", "PASSED"), ("PASS", ""), 0), (("FINISHED", "PASSED"), ("FAIL", "boom"), 1),
    (("FINISHED", "WARNING"), ("PASS", ""), 0), (("FINISHED", "WARNING"), ("FAIL", "w"), 1),
    (("FINISHED", "REVIEW"), ("SKIP", "review"), 0), (("FINISHED", "REVIEW"), ("PASS", ""), 1),
    (("FINISHED", "SKIPPED"), ("SKIP", "s"), 0), (("FINISHED", "SKIPPED"), ("SKIP", KI), 1),
    (("FINISHED", "FAILED"), ("FAIL", "c: m"), 0), (("FINISHED", "FAILED"), ("SKIP", KI), 0),
    (("FINISHED", "FAILED"), ("PASS", ""), 1), (("FINISHED", "FAILED"), ("FAIL", "INFRA: x"), 1),
    (("INTERRUPTED", "UNKNOWN"), ("FAIL", "INFRA: x"), 0), (("INTERRUPTED", "UNKNOWN"), ("FAIL", "plain"), 1),
]


@pytest.mark.parametrize("sr,row,code", CASES)
def test_mapping(tmp_path, sr, row, code):
    assert run(make(tmp_path, {"m": sr}, {"m": row}, counts=None)) == code


def test_counts_match_and_mismatch(tmp_path, capsys):
    suite = {"a": ("FINISHED", "PASSED"), "b": ("FINISHED", "FAILED"), "c": ("FINISHED", "FAILED")}
    rows = {"a": ("PASS", ""), "b": ("FAIL", "x"), "c": ("SKIP", KI)}
    d = make(tmp_path, suite, rows, counts="T-3_P-1_S-0_F-1_I-0_KI-1")
    assert run(d) == 0 and "# Reconciliation: MATCH (3 modules)" in capsys.readouterr().out
    (next(d.glob("*-full-report_*"))).rename(d / "y-full-report_T-3_P-1_S-0_F-2_I-0_KI-0.html")
    (d / "x-full-report_T-3_P-1_S-0_F-1_I-0_KI-1.html").unlink(missing_ok=True)
    (d / "y-full-report_T-3_P-1_S-0_F-2_I-0_KI-0.html").rename(d / "y-full-report_T-3_P-2_S-0_F-1_I-0_KI-0.html")
    assert run(d) == 1 and "MISMATCH" in capsys.readouterr().out


def test_no_emailable_file_does_not_fail(tmp_path, capsys):
    assert run(make(tmp_path, {"a": ("FINISHED", "PASSED")}, {"a": ("PASS", "")}, counts=None)) == 0
    assert "no EmailableReport file" in capsys.readouterr().out


def test_infra_only_row_ok_but_plain_fail_not(tmp_path, capsys):
    assert run(make(tmp_path, {}, {"m": ("FAIL", "INFRA: no suite")}, counts=None)) == 0
    assert "no suite record (infra)" in capsys.readouterr().out
    (tmp_path / "b").mkdir()
    assert run(make(tmp_path / "b", {}, {"m": ("FAIL", "plain")}, counts=None)) == 1


def test_export_only_module(tmp_path, capsys):
    assert run(make(tmp_path, {"m": ("FINISHED", "PASSED"), "n": ("FINISHED", "PASSED")}, {"m": ("PASS", "")}, counts=None)) == 1
    assert "missing from TestNG" in capsys.readouterr().out


def test_duplicate(tmp_path, capsys):
    d = make(tmp_path, {"m": ("FINISHED", "PASSED")}, {"m": ("PASS", "")}, counts=None)
    x = d / "testng-results.xml"
    t = x.read_text()
    x.write_text(t.replace("</testng-results>", t.split("\n")[2] + "\n</testng-results>"))
    assert run(d) == 1 and "duplicate" in capsys.readouterr().out


def test_strict_allows_fail_for_warning(tmp_path):
    d = make(tmp_path, {"m": ("FINISHED", "WARNING")}, {"m": ("FAIL", "w")}, counts="T-1_P-0_S-0_F-1_I-0_KI-0")
    assert run(d) == 1 and run(d, "--strict") == 0


def test_cannot_evaluate(tmp_path, capsys):
    d = make(tmp_path, {"m": ("FINISHED", "PASSED")}, {"m": ("PASS", "")}, zip_=False)
    assert run(d) == 2 and "expected exactly one" in capsys.readouterr().err
    (d / "testng-results.xml").unlink()
    assert run(d, "--export", str(d / "nope.zip")) == 2


@pytest.mark.parametrize("cfg", ["certify-shim-off", "verify-redirect-uri", "verify-x509"])
def test_sp4_14_evidence(cfg):
    d = ROOT / "evidence/sp4/SP4.14/tr-kg-combined" / cfg / "testng-report"
    if not d.is_dir():
        pytest.skip("SP4.14 evidence not shipped")
    assert run(d) == 0


@pytest.mark.parametrize("row,counts", [(("PASS", ""), "T-1_P-1_S-0_F-0_I-0_KI-0"), (("FAIL", "w"), "T-1_P-0_S-0_F-1_I-0_KI-0")])
def test_strict_warning_counts_follow_row(tmp_path, row, counts):
    assert run(make(tmp_path, {"m": ("FINISHED", "WARNING")}, {"m": row}, counts=counts), "--strict") == 0
