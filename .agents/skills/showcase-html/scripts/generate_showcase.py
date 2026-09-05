#!/usr/bin/env python3
"""Generate a self-contained showcase index.html from template.html + showcase.json.

Usage:
  python3 scripts/generate_showcase.py <project_dir> [--out index.html]

Reads <project_dir>/showcase.json (relative asset paths are resolved against
<project_dir>) and writes the final HTML next to it. The HTML embeds the data
JSON and the renderer, so it is a single portable file.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "template.html")
RENDERER = os.path.join(HERE, "..", "renderer.js")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir")
    parser.add_argument("--out", default="index.html")
    args = parser.parse_args()

    proj = os.path.abspath(args.project_dir)
    manifest = os.path.join(proj, "showcase.json")
    if not os.path.exists(manifest):
        sys.exit(f"missing manifest: {manifest}")

    data = load_json(manifest)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    with open(RENDERER, "r", encoding="utf-8") as f:
        renderer = f.read()

    title = data.get("title", "Showcase")
    # Escape "</" so a verbatim prompt cannot terminate the inline script/JSON tag.
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

    out = os.path.join(proj, args.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
