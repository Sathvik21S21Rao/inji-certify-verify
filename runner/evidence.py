"""Optional: upload Inji Verify's /vp-result rendering as the suite's screenshot evidence. Delete this file to drop the upload."""
import base64
import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

from .handoff import call


def render_png(text: str) -> bytes:
    lines = []
    for raw in text.splitlines():
        lines += textwrap.wrap(raw, 110) or [""]
    lines = lines[:80]
    img = Image.new("RGB", (900, 14 * len(lines) + 20), "white")
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((10, 10 + 14 * i), line, fill="black")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


async def fill_placeholders(suite, ctx, env, http, out_dir) -> list:
    pending = [i["upload"] for i in await suite.images(ctx.test_id) if i.get("upload") and not i.get("img")]
    if not pending:
        return []
    txn = ctx.state.get("txn")
    r = call(http, "GET", f"{env['VERIFY_API']}/vp-result/{txn}")
    text = f"Inji Verify GET /vp-result/{txn} -> HTTP {r.status_code}\n{r.text}\n"
    names = [f"{ctx.module}.verify-result.json", f"{ctx.module}.verify-result.png"]
    out = Path(out_dir)
    (out / names[0]).write_text(text, encoding="utf-8")
    png = render_png(text)
    (out / names[1]).write_bytes(png)
    data = "data:image/png;base64," + base64.b64encode(png).decode()
    for ph in pending:
        await suite.upload_image(ctx.test_id, ph, data)
    return names
