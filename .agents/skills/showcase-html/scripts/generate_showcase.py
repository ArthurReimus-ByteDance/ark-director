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
import html
import json
import os
import re
import secrets
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from selection_service import (
    SelectionConflict,
    SelectionError,
    SelectionService,
    collect_selectable,
    contained_path,
    read_selection,
)

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
    return contained_path(proj, "selection.log", must_exist=False)


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

# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #

def validate(data, proj):
    errors = []
    def inspect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ('src', 'contactSheet', 'promptFile', 'manifest'):
                    try:
                        contained_path(proj, item)
                    except SelectionError as error:
                        errors.append(str(error))
                elif isinstance(item, (dict, list)):
                    inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
    inspect(data)
    try:
        registry = collect_selectable(data)
        read_selection(registry, proj)
    except (SelectionError, TypeError, AttributeError) as error:
        errors.append(str(error))
    return errors


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
            check=False, capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            return {}
        d = json.loads(r.stdout)
        fmt = d.get("format", {})
        streams = d.get("streams", [])
        vstream: dict[str, Any] = next((s for s in streams if s.get("codec_type") == "video"), {})
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
            "audio_codecs": list(dict.fromkeys(s.get("codec_name", "unknown") for s in streams if s.get("codec_type") == "audio")),
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
        audio_str = " + " + ", ".join(info["audio_codecs"]) if info["has_audio"] else ""
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
            check=False, capture_output=True, timeout=30,
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

    # bake in current manifest selections if available
    proj_path = Path(proj) if proj else None
    selectable = collect_selectable(data)
    if proj_path and selectable:
        current_sel = read_selection(selectable, proj_path)
        data = dict(data)
        data["currentSelections"] = current_sel

    data = dict(data)
    data["selectableRegistry"] = selectable
    title = html.escape(str(data.get("title", "Showcase")))
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    rendered_html = (
        template
        .replace("__TITLE__", title)
        .replace("__DATA__", data_json)
        .replace(
            "<script>\n/* renderer injected by generator; see scripts/generate_showcase.py */\n</script>",
            "<script>\n" + renderer + "\n</script>",
        )
    )
    out = proj / out_name
    out.write_text(rendered_html, encoding="utf-8")
    return out


# --------------------------------------------------------------------------- #
# HTTP server (--serve)
# --------------------------------------------------------------------------- #

class ShowcaseHandler(BaseHTTPRequestHandler):
    service: SelectionService
    proj: Path
    server: HTTPServer
    session_token: str
    index_name = 'index.html'
    maximum_body = 65536

    def _same_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._same_host():
            self._send_json({'ok': False, 'error': 'Invalid localhost host'}, 403)
            return
        if self.path in ('/api/session', '/api/selection', '/api/log'):
            try:
                if self.path == '/api/session':
                    self._send_json({'token': self.session_token, **self.service.snapshot()})
                elif self.path == '/api/selection':
                    self._send_json(self.service.snapshot())
                else:
                    self._send_json(read_log(self.proj))
            except (SelectionError, OSError) as error:
                self._send_json({'ok': False, 'error': str(error)}, 409)
            return
        from urllib.parse import unquote
        relative = unquote(self.path.split('?', 1)[0]).lstrip('/') or self.index_name
        if any(part.startswith('.') for part in Path(relative).parts):
            self.send_error(404)
            return
        try:
            path = contained_path(self.proj, relative)
        except SelectionError:
            self.send_error(404)
            return
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        range_header = self.headers.get('Range')
        if range_header:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
            try:
                if not match or not any(match.groups()) or not size:
                    raise ValueError()
                if match[1]:
                    start = int(match[1])
                    end = min(int(match[2]), size - 1) if match[2] else size - 1
                else:
                    suffix = int(match[2])
                    if suffix <= 0:
                        raise ValueError()
                    start = max(0, size - suffix)
                if start > end or start >= size:
                    raise ValueError()
                status = 206
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
        import mimetypes
        content_type = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(max(0, end - start + 1)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if status == 206:
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        with path.open('rb') as stream:
            stream.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = stream.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_POST(self):
        origin = f'http://127.0.0.1:{self.server.server_port}'
        if not self._same_host() or self.headers.get('Origin') != origin or not secrets.compare_digest(self.headers.get('X-Showcase-Token', ''), self.session_token or ''):
            self._send_json({'ok': False, 'error': 'Same-origin session token required'}, 403)
            return
        if self.path != '/api/select':
            self._send_json({'ok': False, 'error': 'not found'}, 404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > self.maximum_body or self.headers.get('Transfer-Encoding'):
                self._send_json({'ok': False, 'error': 'Invalid or oversized request body'}, 413)
                return
            if self.headers.get_content_type() != 'application/json':
                raise SelectionError('Content-Type must be application/json')
            self.connection.settimeout(10)
            payload = self.rfile.read(length)
            if len(payload) != length:
                raise SelectionError('Incomplete request body')
            body = json.loads(payload)
            if not isinstance(body, dict) or not isinstance(body.get('expected_revision'), str) or not body['expected_revision']:
                raise SelectionError('Expected selections and expected_revision')
            result = self.service.apply(body.get('selections'), body['expected_revision'])
        except SelectionConflict as error:
            self._send_json({'ok': False, 'error': str(error)}, 409)
        except (SelectionError, ValueError, OSError) as error:
            self._send_json({'ok': False, 'error': str(error)}, 400)
        else:
            self._send_json(result)

    def log_message(self, *args):
        pass


def serve(proj, data, port, index_name='index.html'):
    handler = type('ProjectShowcaseHandler', (ShowcaseHandler,), {
        'service': SelectionService(proj, data), 'proj': proj,
        'session_token': secrets.token_urlsafe(32), 'index_name': index_name,
    })
    httpd = HTTPServer(('127.0.0.1', port), handler)
    url = f'http://127.0.0.1:{httpd.server_port}/{index_name}'
    print(f'serving {proj} at {url}  (Ctrl+C to stop)')
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped')
    finally:
        httpd.server_close()


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

    # group by type
    videos_by_dir: dict[str, list[Path]] = {}
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

    sections: list[dict[str, Any]] = []

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

    data: dict[str, Any] = {
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
    rendered_html = (
        template
        .replace("__TITLE__", data["title"])
        .replace("__DATA__", data_json)
        .replace(
            "<script>\n/* renderer injected by generator; see scripts/generate_showcase.py */\n</script>",
            "<script>\n" + renderer + "\n</script>",
        )
    )
    out.write_text(rendered_html, encoding="utf-8")
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
    parser.add_argument("--apply", metavar="JSON_OR_FILE",
                        help="Apply selections from a JSON string or file path, updating manifests and selection.json.")
    parser.add_argument("--open", action="store_true",
                        help="Open the generated HTML in the default browser.")
    parser.add_argument("--expected-revision", help="Reject --apply when current manifest hashes differ")
    args = parser.parse_args()
    if args.check and (args.apply or args.serve or args.quick):
        parser.error("--check cannot be combined with --apply, --serve, or --quick")

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

    missing = validate(data, proj_path)
    if missing:
        for item in missing:
            print(f"invalid showcase: {item}")
        if args.check or args.strict or args.apply or args.serve:
            sys.exit(1)
    if args.check:
        print("OK: all media, prompts, and manifests resolve")
        return

    if args.apply:
        raw_val = args.apply.strip()
        if os.path.isfile(raw_val):
            apply_dict = load_json(raw_val)
        else:
            try:
                apply_dict = json.loads(raw_val)
            except json.JSONDecodeError as e:
                sys.exit(f"invalid JSON for --apply: {e}")

        if isinstance(apply_dict, dict) and "selections" in apply_dict:
            apply_dict = apply_dict["selections"]

        if not isinstance(apply_dict, dict):
            sys.exit("expected a dict of {asset_id: filename} for --apply")

        try:
            result = SelectionService(proj_path, data).apply(apply_dict, args.expected_revision)
        except (SelectionError, OSError) as error:
            sys.exit(f"selection failed: {error}")
        print(json.dumps(result))
        return

    enrich_takes(data, proj_path, generate_sheets=args.contact_sheets)
    if args.contact_sheets:
        from selection_service import atomic_write
        atomic_write(proj_path / 'showcase.json', (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))

    if args.serve:
        generate(proj_path, data, out_name)
        serve(proj_path, data, args.port, out_name)
        return

    out = generate(proj_path, data, out_name)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    if args.open:
        webbrowser.open(f"file://{out.resolve()}")


if __name__ == "__main__":
    main()
