"""Plan/module loop: create plan, drive each module through its WAITING states, emit contract records."""
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import evidence as ev
from . import records
from .handoff import PLUGINS, ModuleCtx
from .setup import SetupError, prepare
from .suite import ModuleTimeout
from .templates import TemplateError


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def warn(*a):
    print("[runner]", *a, file=sys.stderr, flush=True)


async def _run_module(name, plan_id, template, flags, *, suite, http, env, out_dir, suite_url, timeout):
    started, tid, last, files = now(), None, None, []
    deadline = time.monotonic() + timeout
    left = lambda: max(deadline - time.monotonic(), 0)  # noqa: E731
    plugin = PLUGINS[template["handoff"]["plugin"]]
    try:
        tid = await suite.create_module(plan_id, name)
        ctx = ModuleCtx(name, tid)
        last = state = await suite.wait(tid, ["CONFIGURED", "WAITING", "FINISHED"], left())
        if state == "CONFIGURED":
            await suite.start(tid)
            last = state = await suite.wait(tid, ["WAITING", "FINISHED"], left())
        while state == "WAITING":
            if left() <= 0:
                raise ModuleTimeout
            ctx.exposed = (await suite.status(tid)).get("exposed") or {}
            acted = False
            if flags["verify_evidence_upload"]:
                got = await ev.fill_placeholders(suite, ctx, env, http, out_dir)
                files += [f for f in got if f not in files]
                acted = bool(got)
            acted = acted or plugin(ctx, template["handoff"], env, http)
            if not acted:
                await asyncio.sleep(min(2, left()))  # e.g. metadata tests: WAITING, nothing exposed
            # after an action this blocks until the suite is WAITING again (its handlers set RUNNING first)
            last = state = await suite.wait(tid, ["WAITING", "FINISHED"], left())
        info, log = await suite.info(tid), await suite.log(tid)
        (Path(out_dir) / f"{name}.log.json").write_text(json.dumps({"info": info, "log": log}, indent=1))
        return records.module_record(module=name, info=info, log=log, suite_url=suite_url,
                                     evidence=[f"{name}.log.json", *files])
    except Exception as e:
        reason = (f"runner timeout after {timeout}s in {last}" if isinstance(e, ModuleTimeout)
                  else f"{type(e).__name__}: {e}")
        warn(name, "infra:", reason)
        if tid:
            try:
                await suite.stop(tid)
            except Exception as e2:
                warn(name, "stop failed:", repr(e2))
        return records.module_record(module=name, info=None, log=None, suite_url=suite_url, evidence=files,
                                     infra_reason=reason, status=last, test_id=tid, started=started)


async def run_plan(template, *, suite, http, env, out_dir, run_id, modules=None, module_timeout=None,
                   emit, error=None) -> int:
    """`error`: pre-set abort reason (template failed to load); emits plan + end(exit 2)."""
    out_dir = Path(out_dir)
    comp = template["component"]
    cfg_name = Path(template.get("_path", "x")).stem
    suite_url = env.get("CONFORMANCE_SERVER", "").rstrip("/") + "/"
    alias = f"{comp}-{run_id}"
    started = now()
    flags = {"certify_as_metadata_shim": None, "verify_evidence_upload": None}
    if comp == "certify":
        flags["certify_as_metadata_shim"] = False
    else:
        flags["verify_evidence_upload"] = False

    def plan_rec(plan_id, mods):
        return records.plan_record(run_id=run_id, alias=alias, component=comp, config_name=cfg_name,
                                   plan_name=template["plan_name"], plan_id=plan_id,
                                   variant=template.get("variant", {}), shim=flags["certify_as_metadata_shim"],
                                   evidence_upload=flags["verify_evidence_upload"], suite_url=suite_url,
                                   modules=mods, started=started,
                                   environment={"fault": env.get("CONFORMANCE_FAULT") or "none",
                                                "certify_release": env.get("CONFORMANCE_CERTIFY_RELEASE") or "1.0"})

    def abort(msg, mods):
        emit(plan_rec(None, mods))
        end = records.end_record(modules=[], error=msg, export=None, finished=now())
        emit(end)
        return end["exit"]

    if error:
        return abort(error, modules or [])
    try:
        flags.update(prepare(template, env, http))
    except (SetupError, TemplateError) as e:
        flags.update({k: v for k, v in (getattr(e, "flags", None) or {}).items()})
        return abort(str(e), modules or [])
    config = dict(template["config"], alias=alias,
                  description=f"{template.get('description', '')} (run {run_id})")
    try:
        plan_id, names = await suite.create_plan(template["plan_name"], config, template.get("variant"))
    except Exception as e:
        return abort(f"plan creation failed: {type(e).__name__}: {e}", modules or [])
    if modules:
        unknown = [m for m in modules if m not in names]
        if unknown:
            return abort(f"unknown modules (not in plan {plan_id}): {', '.join(unknown)}", modules)
        names = [n for n in names if n in modules]
    (out_dir / "plan-config.json").write_text(json.dumps(config, indent=1))
    emit(plan_rec(plan_id, names))
    timeout = module_timeout or template.get("module_timeout_s", 180)
    recs = []
    for name in names:
        rec = await _run_module(name, plan_id, template, flags, suite=suite, http=http, env=env,
                                out_dir=out_dir, suite_url=suite_url, timeout=timeout)
        recs.append(rec)
        emit(rec)
    try:
        export = await suite.export_html(plan_id, out_dir)
    except Exception as e:
        warn("HTML export failed:", repr(e))
        export = None
    end = records.end_record(modules=recs, error=None, export=export, finished=now())
    emit(end)
    return end["exit"]
