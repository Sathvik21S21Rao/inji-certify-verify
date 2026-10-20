"""Environment preparation before a plan is created."""
import json
import sys
from pathlib import Path

from .templates import resolve


class SetupError(Exception):
    def __init__(self, msg, flags=None):
        super().__init__(msg)
        self.flags = flags  # flags known at the time of failure, if any


def seed_certify_credential_config(template_dir, setup, env, http):
    # Fallback seeding; scripts/seed-certify.sh does the same from compose.
    body = resolve(json.loads((Path(template_dir) / setup["credential_configuration"]).read_text()), env)
    base = f"{env['CERTIFY_API']}/credential-configurations"
    r = http.get(f"{base}/{body['credentialConfigKeyId']}")
    if r.status_code == 200:
        print(f"[setup] credential config {body['credentialConfigKeyId']} present", file=sys.stderr)
        return
    r = http.post(base, json=body)
    if r.status_code != 201:
        raise SetupError(f"seeding credential config failed: HTTP {r.status_code} {r.text[:300]}")
    print(f"[setup] credential config {body['credentialConfigKeyId']} created", file=sys.stderr)


def prepare(template, env, http) -> dict:
    flags = {"certify_as_metadata_shim": None, "verify_evidence_upload": None}
    if template["component"] == "verify":
        ev = template["handoff"].get("evidence")
        if ev not in ("vp-result-png", "none"):
            raise SetupError(f"unknown verify evidence mode {ev!r} (want vp-result-png or none)",
                             {**flags, "verify_evidence_upload": False})
        return {**flags, "verify_evidence_upload": ev == "vp-result-png"}
    want = template["expect"]["certify_as_metadata_shim"]
    name = Path(template["_path"]).stem
    try:
        r = http.get(f"{env['CERTIFY_PUBLIC_URL']}/.well-known/oauth-authorization-server")
        shim = "authorization_endpoint" in r.json()
    except Exception as e:
        raise SetupError(f"cannot read AS metadata: {type(e).__name__}: {e}", {**flags, "certify_as_metadata_shim": want})
    flags["certify_as_metadata_shim"] = shim
    if shim != want:
        raise SetupError(f"environment has shim={shim}, config {name} expects {want}", flags)
    seed_certify_credential_config(Path(template["_path"]).parent, template["setup"], env, http)
    return flags
