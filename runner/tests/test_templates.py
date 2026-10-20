import json

import pytest

from runner.templates import TemplateError, load_template, resolve
from .helpers import ROOT

PLANS = ["certify/certify-shim-off", "certify/certify-shim-on", "verify/verify-redirect-uri", "verify/verify-x509"]


def test_required_default_multiple():
    env = {"A": "1", "B": "2"}
    assert resolve({"k": "${A}"}, env) == {"k": "1"}
    assert resolve("${NOPE:-dflt}", env) == "dflt"
    assert resolve("x-${A}-${B}-${C:-c}", env) == "x-1-2-c"
    assert resolve(["${A}", 3, None], env) == ["1", 3, None]


def test_empty_drops_key_and_list_item():
    assert resolve({"a": "${X:-}", "b": "keep", "c": ["${X:-}", "y"]}, {}) == {"b": "keep", "c": ["y"]}
    assert resolve({"a": "pre${X:-}"}, {}) == {"a": "pre"}  # only an exact placeholder drops


def test_missing_lists_all():
    with pytest.raises(TemplateError) as e:
        resolve({"a": "${ONE}", "b": ["${TWO}", "${ONE}"]}, {})
    assert "ONE" in str(e.value) and "TWO" in str(e.value)


@pytest.mark.parametrize("name", PLANS)
def test_plan_templates_load_with_empty_env(name):
    t = load_template(ROOT / "plans" / f"{name}.json", {})
    assert t["component"] == name.split("/")[0] and t["plan_name"] and t["config"]
    assert "${" not in json.dumps(t)


def test_certify_pair_differs_only_in_expectation():
    a, b = (load_template(ROOT / "plans/certify" / f"certify-shim-{s}.json", {}) for s in ("off", "on"))
    assert (a["expect"]["certify_as_metadata_shim"], b["expect"]["certify_as_metadata_shim"]) == (False, True)
    for t in (a, b):
        t.pop("description"); t.pop("expect"); t.pop("_path")
    assert a == b


def test_x509_ca_key():
    p = ROOT / "plans/verify/verify-x509.json"
    assert "request_object_trust_anchor_pem" not in load_template(p, {})["config"]["client"]
    t = load_template(p, {"VERIFY_X509_CA_PEM": "PEM"})
    assert t["config"]["client"]["request_object_trust_anchor_pem"] == "PEM"


def test_env_overrides():
    t = load_template(ROOT / "plans/verify/verify-redirect-uri.json", {"VERIFY_PUBLIC_URL": "https://v", "CONFORMANCE_VERIFY_EVIDENCE": "none"})
    assert t["handoff"]["vp_request"]["clientId"].startswith("redirect_uri:https://v/")
    assert t["handoff"]["evidence"] == "none"
