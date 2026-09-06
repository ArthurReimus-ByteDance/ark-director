#!/usr/bin/env python3
"""Generate a self-contained showcase index.html from template.html + showcase.json.

Usage:
  python3 scripts/generate_showcase.py <project_dir> [--out index.html]
  python3 scripts/generate_showcase.py <project_dir> --check
  python3 scripts/generate_showcase.py <project_dir> --serve [--port 8000]

Reads <project_dir>/showcase.json (relative asset paths are resolved against
<project_dir>) and writes the final HTML next to it. The HTML embeds the data
JSON and the renderer, so it is a single portable file.

Modes:
  (default)  generate index.html in place (read-only review page).
  --check    validate that every media ``src`` in showcase.json resolves on disk.
  --serve    generate, then run a local HTTP server so in-browser variant
             selection can persist to the project (writes selection.json, the
             element/shot manifests, and a timestamped selection.log). Opens the
             URL in the default browser.

Selection contract (see references/schema.md):
  A card is selectable when it carries ``id`` and ``manifest``. Selecting it in
  the page (server mode only) sets that asset's ``selected_variant`` (scalar)
  or, when the card also carries ``field: "selected_variants"`` and ``key``, a
  single key inside a ``selected_variants`` map in the manifest frontmatter.
"""
import argparse
import datetime
import json
import os
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "template.html")
RENDERER = os.path.join(HERE, "..", "renderer.js")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
# audit logging (append-only, timestamped, JSON Lines)
# --------------------------------------------------------------------------- #

def log_file(proj):
    return proj / "selection.log"


def append_log(proj, event, **fields):
    """Append one timestamped event record to the project audit log."""
    record = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "event": event,
    }
    record.update(fields)
    path = log_file(proj)
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass  # logging must never break the selection flow


def read_log(proj, limit=200):
    """Return the most recent `limit` log entries, newest last."""
    path = log_file(proj)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


# --------------------------------------------------------------------------- #
# selection write-back
# --------------------------------------------------------------------------- #

_FM_RE = re.compile(r"^(---\n)(.*?)(\n---)", re.DOTALL)


def _edit_frontmatter(text, apply_fn):
    m = _FM_RE.match(text)
    if not m:
        return None
    head, fm, tail = m.group(1), m.group(2), m.group(3)
    new_fm = apply_fn(fm)
    if new_fm is None:
        return None
    return head + new_fm + tail


def _set_scalar(fm, filename):
    if re.search(r"^selected_variant\s*:", fm, re.M):
        return re.sub(
            r"^selected_variant\s*:.*$",
            f"selected_variant: {filename}",
            fm, count=1, flags=re.M,
        )
    return fm + f"\nselected_variant: {filename}"


def _set_map_key(fm, key, filename):
    key_esc = re.escape(key)
    if re.search(r"^selected_variants\s*:", fm, re.M):
        if re.search(rf"^  {key_esc}\s*:", fm, re.M):
            return re.sub(
                rf"^  {key_esc}\s*:.*$",
                f"  {key}: {filename}",
                fm, count=1, flags=re.M,
            )
        return re.sub(
            r"^(selected_variants\s*:.*)$",
            rf"\1\n  {key}: {filename}",
            fm, count=1, flags=re.M,
        )
    return fm + f"\nselected_variants:\n  {key}: {filename}"


def update_manifest(meta, filename, proj):
    """Set one asset's selection in its manifest frontmatter. Returns (ok, err)."""
    path = proj / meta["manifest"]
    if not path.exists():
        return False, f"missing manifest: {meta['manifest']}"
    text = path.read_text(encoding="utf-8")
    if meta.get("field") == "selected_variants":
        new = _edit_frontmatter(text, lambda fm: _set_map_key(fm, meta["key"], filename))
    else:
        new = _edit_frontmatter(text, lambda fm: _set_scalar(fm, filename))
    if new is None:
        return False, f"no frontmatter in {meta['manifest']}"
    path.write_text(new, encoding="utf-8")
    append_log(proj, "select", manifest=meta["manifest"],
               field=meta.get("field", "selected_variant"),
               key=meta.get("key"), filename=filename)
    return True, None


def read_selection(selectable, proj):
    """Return {asset_id: filename} of currently-selected variants from manifests."""
    out = {}
    for cid, meta in selectable.items():
        path = proj / meta["manifest"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if meta.get("field") == "selected_variants":
            m = re.search(rf"^  {re.escape(meta['key'])}\s*:\s*(.*)$", text, re.M)
        else:
            m = re.search(r"^selected_variant\s*:\s*(.*)$", text, re.M)
        if m:
            val = m.group(1).strip()
            if val and val != "null":
                out[cid] = val
    return out


def collect_selectable(data):
    """Map card id -> selection metadata from showcase.json."""
    out = {}
    for section in data.get("sections", []):
        for card in section.get("cards", []):
            if card.get("id") and card.get("manifest"):
                out[card["id"]] = {
                    "manifest": card["manifest"],
                    "field": card.get("field", "selected_variant"),
                    "key": card.get("key"),
                }
    return out


def selection_file(proj):
    return proj / "selection.json"


def write_selection_json(proj, selections):
    data = {"project": proj.name, "selections": selections}
    selection_file(proj).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #

def validate(data, proj):
    missing = []
    for section in data.get("sections", []):
        if section.get("kind") == "table":
            for row in section.get("rows", []):
                m = row.get("media")
                if m and "src" in m and not (proj / m["src"]).exists():
                    missing.append(m["src"])
        elif section.get("kind") == "panel":
            m = section.get("media")
            if m and "src" in m and not (proj / m["src"]).exists():
                missing.append(m["src"])
        else:
            for card in section.get("cards", []):
                m = card.get("media")
                if m and "src" in m and not (proj / m["src"]).exists():
                    missing.append(m["src"])
    return missing


# --------------------------------------------------------------------------- #
# generation
# --------------------------------------------------------------------------- #

def generate(proj, data, out_name):
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    with open(RENDERER, "r", encoding="utf-8") as f:
        renderer = f.read()

    title = data.get("title", "Showcase")
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (
        template
        .replace("__TITLE__", title)
        .replace("__DATA__", data_json)
        .replace(
            "<script>\n/* renderer injected by generator; see scripts/generate_showcase.py */\n</script>",
            "<script>\n" + renderer + "\n</script>",
        )
    )
    out = proj / out_name
    out.write_text(html, encoding="utf-8")
    return out


# --------------------------------------------------------------------------- #
# HTTP server (--serve)
# --------------------------------------------------------------------------- #

class ShowcaseHandler(BaseHTTPRequestHandler):
    selectable = {}
    proj = None

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/selection":
            self._send_json(read_selection(self.selectable, self.proj))
            return
        if self.path == "/api/log":
            self._send_json(read_log(self.proj))
            return
        # serve a static file from the project dir
        from urllib.parse import unquote
        path = unquote(self.path.split("?", 1)[0])
        if path == "/":
            path = "/index.html"
        rel = path.lstrip("/")
        fp = (self.proj / rel).resolve()
        proj_root = self.proj.resolve()
        if not fp.is_relative_to(proj_root) or not fp.is_file():
            self.send_error(404)
            return
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
            ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
            ".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
            ".json": "application/json", ".js": "application/javascript",
        }.get(fp.suffix.lower(), "application/octet-stream")
        data = fp.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path == "/api/select":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
            except (ValueError, json.JSONDecodeError):
                self._send_json({"ok": False, "error": "bad request"}, 400)
                return
            selections = body.get("selections", {})
            write_selection_json(self.proj, selections)
            applied, errors = [], []
            for cid, filename in selections.items():
                meta = self.selectable.get(cid)
                if not meta:
                    errors.append(f"{cid}: not a selectable asset")
                    continue
                if not isinstance(filename, str) or re.search(r"[\\/\r\n]", filename):
                    errors.append(f"{cid}: invalid filename")
                    continue
                ok, err = update_manifest(meta, filename, self.proj)
                if ok:
                    applied.append(cid)
                else:
                    errors.append(err)
            append_log(self.proj, "save", applied=applied,
                       errors=errors, total=len(selections))
            self._send_json({"ok": True, "applied": applied, "errors": errors})
            return
        self._send_json({"ok": False, "error": "not found"}, 404)

    def log_message(self, *args):
        pass


def serve(proj, data, port):
    ShowcaseHandler.selectable = collect_selectable(data)
    ShowcaseHandler.proj = proj
    httpd = HTTPServer(("127.0.0.1", port), ShowcaseHandler)
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"serving {proj} at {url}  (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir")
    parser.add_argument("--out", default="index.html")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    proj = os.path.abspath(args.project_dir)
    proj_path = Path(proj)
    manifest = os.path.join(proj, "showcase.json")
    if not os.path.exists(manifest):
        sys.exit(f"missing manifest: {manifest}")

    data = load_json(manifest)

    missing = validate(data, proj_path)
    if missing:
        for m in missing:
            print(f"missing media: {m}")
        if args.strict:
            sys.exit(1)

    if args.check:
        print("OK: all media resolve" if not missing else f"{len(missing)} missing media")
        return

    if args.serve:
        generate(proj_path, data, args.out)
        serve(proj_path, data, args.port)
        return

    out = generate(proj_path, data, args.out)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
