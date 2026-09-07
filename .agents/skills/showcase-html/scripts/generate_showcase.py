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
import subprocess
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

_FM_RE = re.compile(r"^(---\n)(.*?)(\n---)(.*)$", re.DOTALL)


def _edit_frontmatter(text, apply_fn):
    m = _FM_RE.match(text)
    if not m:
        return None
    head, fm, tail, rest = m.group(1), m.group(2), m.group(3), m.group(4)
    new_fm = apply_fn(fm)
    if new_fm is None:
        return None
    return head + new_fm + tail + rest


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
        existing = re.search(rf"^(?P<ind>[ \t]+){key_esc}\s*:.*$", fm, re.M)
        if existing:
            indent = existing.group("ind")
            return re.sub(
                rf"^[ \t]+{key_esc}\s*:.*$",
                f"{indent}{key}: {filename}",
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
    if meta.get("field") == "selected_variants" and not meta.get("key"):
        return False, "selected_variants requires a key"
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
            key = meta.get("key")
            if not key:
                continue
            m = re.search(rf"^[ \t]+{re.escape(key)}\s*:\s*(.*)$", text, re.M)
        else:
            m = re.search(r"^selected_variant\s*:\s*(.*)$", text, re.M)
        if m:
            val = m.group(1).strip()
            if val and val != "null":
                out[cid] = val
    return out


def collect_selectable(data):
    """Map card id -> selection metadata from showcase.json.

    Covers both grid sections (cards with id+manifest) and takes sections
    (groups[].takes[] with id+manifest+filename).
    """
    out = {}
    for section in data.get("sections", []):
        if section.get("kind") == "takes":
            for grp in section.get("groups", []):
                for tk in grp.get("takes", []):
                    if tk.get("id") and tk.get("manifest"):
                        out[tk["id"]] = {
                            "manifest": tk["manifest"],
                            "field": "selected_variant",
                            "key": None,
                        }
        else:
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
        elif section.get("kind") == "takes":
            for grp in section.get("groups", []):
                for tk in grp.get("takes", []):
                    m = tk.get("media")
                    if m and "src" in m and not (proj / m["src"]).exists():
                        missing.append(m["src"])
                    cs = tk.get("contactSheet")
                    if cs and not (proj / cs).exists():
                        missing.append(cs)
        else:
            for card in section.get("cards", []):
                m = card.get("media")
                if m and "src" in m and not (proj / m["src"]).exists():
                    missing.append(m["src"])
    return missing


# --------------------------------------------------------------------------- #
# ffprobe + contact sheet helpers
# --------------------------------------------------------------------------- #

def _run_ffprobe(path):
    """Return dict with duration, width, height, fps, codec, size_mb or {} on failure."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate",
                "-of", "json", str(path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            return {}
        d = json.loads(r.stdout)
        fmt = d.get("format", {})
        streams = d.get("streams", [])
        vstream = next((s for s in streams if s.get("codec_type") == "video"), {})
        duration = float(fmt.get("duration", 0))
        size_bytes = int(fmt.get("size", 0))
        width = vstream.get("width", 0)
        height = vstream.get("height", 0)
        fps_raw = vstream.get("r_frame_rate", "0/1")
        fps_num, fps_den = fps_raw.split("/")
        fps = round(int(fps_num) / int(fps_den), 1) if int(fps_den) else 0
        codec = vstream.get("codec_name", "")
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        return {
            "duration": duration,
            "size_bytes": size_bytes,
            "width": width,
            "height": height,
            "fps": fps,
            "codec": codec,
            "has_audio": has_audio,
        }
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, KeyError):
        return {}


def _fmt_duration(seconds):
    if seconds < 10:
        return f"{seconds:.2f}s"
    return f"{seconds:.1f}s"


def _fmt_size(bytes_val):
    mb = bytes_val / (1024 * 1024)
    if mb < 10:
        return f"{mb:.1f} MB"
    return f"{mb:.0f} MB"


def _ffprobe_chips(path):
    """Return a chips list for a take card from ffprobe."""
    info = _run_ffprobe(path)
    if not info:
        return []
    chips = []
    if info["size_bytes"]:
        chips.append(_fmt_size(info["size_bytes"]))
    if info["duration"]:
        chips.append(_fmt_duration(info["duration"]))
    if info["fps"]:
        chips.append(f"{info['fps']}fps")
    if info["width"] and info["height"]:
        chips.append(f"{info['width']}x{info['height']}")
    if info["codec"]:
        audio_str = " + AAC" if info["has_audio"] else ""
        chips.append(f"{info['codec']}{audio_str}")
    return chips


def generate_contact_sheet(video_path, output_path, frames=4):
    """Generate a 4-frame contact sheet (opening, 1/3, 2/3, ending) as a JPEG."""
    info = _run_ffprobe(video_path)
    if not info or not info["duration"]:
        return False
    duration = info["duration"]
    w = info["width"] or 1280
    h = info["height"] or 720
    timestamps = [
        min(0.1, duration / 2),
        duration / 3,
        2 * duration / 3,
        max(duration - 0.1, 3 * duration / 4),
    ]
    clip_dur = 0.2
    thumb_w = w // 2
    thumb_h = h // 2
    filter_parts = []
    for i, ts in enumerate(timestamps):
        end_ts = ts + clip_dur
        filter_parts.append(
            f"[0:v]trim={ts:.3f}:{end_ts:.3f},setpts=PTS-STARTPTS,"
            f"scale={thumb_w}:{thumb_h}[t{i}]"
        )
    inputs = "".join(f"[t{i}]" for i in range(len(timestamps)))
    filter_complex = ";".join(filter_parts) + f";{inputs}hstack=inputs={len(timestamps)}[out]"
    try:
        r = subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(video_path),
                "-filter_complex", filter_complex,
                "-map", "[out]", "-frames:v", "1",
                "-q:v", "3", str(output_path),
            ],
            capture_output=True, timeout=30,
        )
        return r.returncode == 0 and output_path.exists()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def enrich_takes(data, proj, generate_sheets=False):
    """Auto-populate chips and contact sheets for takes sections."""
    for section in data.get("sections", []):
        if section.get("kind") != "takes":
            continue
        for grp in section.get("groups", []):
            # also enrich group meta from first take if empty
            first_info = None
            for tk in grp.get("takes", []):
                src = tk.get("media", {}).get("src", "")
                if not src:
                    continue
                video_path = proj / src
                if not video_path.exists():
                    continue
                info = _run_ffprobe(video_path)
                if not first_info and info:
                    first_info = info
                # auto-populate chips if missing or if we're regenerating
                if (not tk.get("chips") or generate_sheets) and info:
                    tk["chips"] = _ffprobe_chips(video_path)
                # generate contact sheet if requested
                if generate_sheets and not tk.get("contactSheet"):
                    cs_path = video_path.with_name(
                        video_path.stem + "_contacts.jpg"
                    )
                    if generate_contact_sheet(video_path, cs_path):
                        tk["contactSheet"] = str(cs_path.relative_to(proj))
            # auto-populate group meta if empty or regenerating
            if (not grp.get("meta") or generate_sheets) and first_info:
                meta = []
                if first_info["width"] and first_info["height"]:
                    ratio = "16:9" if first_info["width"] > first_info["height"] else "9:16"
                    meta.append(f"{first_info['height']}p")
                    meta.append(ratio)
                if first_info["duration"]:
                    meta.append(f"{_fmt_duration(first_info['duration'])}")
                if meta:
                    grp["meta"] = meta


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
                if not isinstance(filename, str) or not filename.strip() or re.search(r"[\\/\r\n]", filename):
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

_VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
_AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".flac", ".aac"}


def _detect_media_type(path):
    ext = path.suffix.lower()
    if ext in _VIDEO_EXTS:
        return "video"
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _AUDIO_EXTS:
        return "audio"
    return None


def quick_review(paths, out_path=None, do_contact_sheets=False, open_browser=False):
    """Build a minimal showcase page from a list of media file paths — no showcase.json needed.

    Videos from the same directory are grouped into takes groups.
    Images are placed in a grid section.
    Audio files are placed in an audio section.
    """
    # resolve to absolute paths and validate
    resolved = []
    for p in paths:
        fp = Path(p).resolve()
        if not fp.exists():
            print(f"warning: file not found: {p}")
            continue
        resolved.append(fp)
    if not resolved:
        sys.exit("no valid media files found")

    # determine the common root (for relative paths)
    common_root = Path(os.path.commonpath([str(p.parent) for p in resolved]))

    # group by type
    videos_by_dir = {}
    images = []
    audios = []
    for fp in resolved:
        mtype = _detect_media_type(fp)
        if mtype == "video":
            d = str(fp.parent)
            videos_by_dir.setdefault(d, []).append(fp)
        elif mtype == "image":
            images.append(fp)
        elif mtype == "audio":
            audios.append(fp)
        else:
            print(f"warning: unrecognized file type: {fp}")

    sections = []

    # build takes groups for videos
    if videos_by_dir:
        groups = []
        for d, vids in sorted(videos_by_dir.items()):
            dpath = Path(d)
            group_title = dpath.name or "Videos"
            takes = []
            first_info = None
            for v in sorted(vids):
                info = _run_ffprobe(v)
                if not first_info and info:
                    first_info = info
                chips = _ffprobe_chips(v) if info else []
                take = {
                    "label": v.stem,
                    "media": {"type": "video", "src": str(v)},
                    "chips": chips,
                }
                # contact sheet
                if do_contact_sheets:
                    cs_path = v.with_name(v.stem + "_contacts.jpg")
                    if generate_contact_sheet(v, cs_path):
                        take["contactSheet"] = str(cs_path)
                takes.append(take)
            meta = []
            if first_info:
                if first_info.get("height"):
                    ratio = "16:9" if first_info.get("width", 0) > first_info.get("height", 0) else "9:16"
                    meta.append(f"{first_info['height']}p")
                    meta.append(ratio)
                if first_info.get("duration"):
                    meta.append(_fmt_duration(first_info["duration"]))
            groups.append({
                "title": group_title,
                "uc": "",
                "meta": meta,
                "takes": takes,
            })
        sections.append({
            "id": "video-review",
            "title": "Video Review",
            "icon": "🎥",
            "iconBg": "var(--accent-soft)",
            "count": f"{sum(len(g['takes']) for g in groups)} videos · {len(groups)} group(s)",
            "desc": "Quick review — auto-generated from file paths. Videos from the same folder are grouped.",
            "kind": "takes",
            "groups": groups,
        })

    # build grid for images
    if images:
        cards = []
        for img in sorted(images):
            cards.append({
                "type": "elem",
                "kindPill": "Image",
                "media": {"type": "image", "src": str(img), "alt": img.name},
                "tag": "",
                "title": img.stem,
                "sub": img.name,
                "chips": [],
                "prompt": "",
            })
        sections.append({
            "id": "images",
            "title": "Images",
            "icon": "🖼️",
            "iconBg": "var(--accent-2-soft)",
            "count": f"{len(images)} image(s)",
            "desc": "Quick review — auto-generated from file paths.",
            "kind": "grid",
            "mediaOnly": True,
            "cards": cards,
        })

    # build grid for audio
    if audios:
        cards = []
        for aud in sorted(audios):
            cards.append({
                "type": "audio",
                "kindPill": "Audio",
                "media": {"type": "audio", "src": str(aud)},
                "tag": "AUDIO",
                "title": aud.stem,
                "sub": aud.name,
                "chips": [],
                "prompt": "",
            })
        sections.append({
            "id": "audio",
            "title": "Audio",
            "icon": "🔊",
            "iconBg": "var(--accent-3-soft)",
            "count": f"{len(audios)} track(s)",
            "desc": "Quick review — auto-generated from file paths.",
            "kind": "grid",
            "mediaOnly": False,
            "cards": cards,
        })

    data = {
        "title": "Quick Review",
        "kicker": "Ad-hoc Media Review",
        "lede": f"Auto-generated from {len(resolved)} file(s). No showcase.json required.",
        "badges": [],
        "sections": sections,
        "footer": "Generated with showcase-html --quick.",
    }

    # use absolute paths for media src (since there's no project dir)
    # convert to file:// URIs for browser access
    for section in data["sections"]:
        if section.get("kind") == "takes":
            for grp in section.get("groups", []):
                for tk in grp.get("takes", []):
                    src = tk.get("media", {}).get("src", "")
                    if src and not src.startswith("http"):
                        tk["media"]["src"] = "file://" + src
                    cs = tk.get("contactSheet", "")
                    if cs and not cs.startswith("http"):
                        tk["contactSheet"] = "file://" + cs
        else:
            for card in section.get("cards", []):
                src = card.get("media", {}).get("src", "")
                if src and not src.startswith("http") and not src.startswith("file://"):
                    card["media"]["src"] = "file://" + src

    # determine output path
    if out_path:
        out = Path(out_path)
    else:
        out = Path.cwd() / "_quick_review.html"
    # write to a temp dir, use common_root for relative paths if possible
    # but since we're using file:// URIs, the output location doesn't matter
    # generate using the template directly
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    with open(RENDERER, "r", encoding="utf-8") as f:
        renderer = f.read()

    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (
        template
        .replace("__TITLE__", data["title"])
        .replace("__DATA__", data_json)
        .replace(
            "<script>\n/* renderer injected by generator; see scripts/generate_showcase.py */\n</script>",
            "<script>\n" + renderer + "\n</script>",
        )
    )
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    if open_browser:
        webbrowser.open(f"file://{out.resolve()}")
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Generate a self-contained showcase index.html from showcase.json, or a quick review page from file paths."
    )
    parser.add_argument("project_dir", nargs="?", default=None,
                        help="Project directory containing showcase.json. Required unless --quick is used.")
    parser.add_argument("--quick", nargs="+", metavar="PATH",
                        help="Quick mode: build a review page from file paths (no showcase.json needed).")
    parser.add_argument("--out", default=None,
                        help="Output HTML filename (default: index.html, or _quick_review.html in --quick mode).")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--contact-sheets", action="store_true",
                        help="Generate contact sheet images for video takes via FFmpeg.")
    parser.add_argument("--open", action="store_true",
                        help="Open the generated HTML in the default browser.")
    args = parser.parse_args()

    # ---- quick mode ----
    if args.quick:
        out_path = args.out or "_quick_review.html"
        quick_review(
            args.quick,
            out_path=out_path,
            do_contact_sheets=args.contact_sheets,
            open_browser=True,  # always open in quick mode
        )
        return

    # ---- normal mode (requires project_dir + showcase.json) ----
    if not args.project_dir:
        parser.error("project_dir is required (or use --quick with file paths)")
    if not os.path.isdir(args.project_dir):
        sys.exit(f"not a directory: {args.project_dir}")

    proj = os.path.abspath(args.project_dir)
    proj_path = Path(proj)
    out_name = args.out or "index.html"
    manifest = os.path.join(proj, "showcase.json")
    if not os.path.exists(manifest):
        sys.exit(f"missing manifest: {manifest}")

    data = load_json(manifest)

    # auto-populate take chips from ffprobe + optionally generate contact sheets
    enrich_takes(data, proj_path, generate_sheets=args.contact_sheets)
    # write back enriched data so the manifest stays in sync
    if args.contact_sheets:
        with open(manifest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("updated showcase.json with ffprobe chips + contact sheet paths")

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
        generate(proj_path, data, out_name)
        serve(proj_path, data, args.port)
        return

    out = generate(proj_path, data, out_name)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    if args.open:
        webbrowser.open(f"file://{out.resolve()}")


if __name__ == "__main__":
    main()
