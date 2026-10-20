"""Plan template loading with ${NAME} / ${NAME:-default} substitution on parsed JSON string values."""
import json
import re
from pathlib import Path
from typing import Mapping

_PH = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
_DROP = object()


class TemplateError(Exception):
    pass


def substitute(obj, env: Mapping, missing: list):
    """Return obj with placeholders applied; record unresolved required names in `missing`."""
    if isinstance(obj, dict):
        out = {k: substitute(v, env, missing) for k, v in obj.items()}
        return {k: v for k, v in out.items() if v is not _DROP}
    if isinstance(obj, list):
        return [v for v in (substitute(v, env, missing) for v in obj) if v is not _DROP]
    if not isinstance(obj, str):
        return obj

    def one(m):
        val = env.get(m.group(1))
        if val:
            return val
        if m.group(2) is not None:
            return m.group(2)
        if val is None:
            missing.append(m.group(1))
        return val or ""

    res = _PH.sub(one, obj)
    return _DROP if res == "" and _PH.fullmatch(obj) else res


def resolve(obj, env: Mapping):
    missing: list = []
    out = substitute(obj, env, missing)
    if missing:
        raise TemplateError("unresolved required placeholders: " + ", ".join(sorted(set(missing))))
    return out


def load_template(path, env: Mapping) -> dict:
    path = Path(path)
    t = resolve(json.loads(path.read_text(encoding="utf-8")), env)
    t["_path"] = str(path)  # runner-internal: template dir for setup files, stem = config_name
    return t
