from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from functools import partial
from pathlib import Path

from validate_workspace import bundle_hashes, validate_skill


def replacement_text(text: str, match: re.Match[str]) -> str:
    return text


def desired_outputs(root: Path, refresh_integrity: bool) -> dict[Path, str]:
    lock_path = root / "skills-lock.json"
    catalog_path = root / ".agents/catalog/skills.json"
    lock = json.loads(lock_path.read_text())
    catalog = json.loads(catalog_path.read_text())
    readme = (root / "README.md").read_text()
    skills = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    if {p.parent.name for p in skills} != set(catalog["skills"]) or set(
        catalog["skills"]
    ) != set(lock["skills"]):
        raise ValueError(
            "Review new/removed skill classification and source metadata before synchronization"
        )
    for skill in skills:
        metadata, errors = validate_skill(skill)
        if errors:
            raise ValueError("; ".join(error.message for error in errors))
        name = skill.parent.name
        catalog["skills"][name]["description"] = metadata["description"].strip()
        summary = catalog["skills"][name]["readme_summary"].replace("\n", " ")
        row = f"| **{name}** | {summary} |"
        pattern = r"^\| \*\*" + re.escape(name) + r"\*\* \| .*? \|$"
        readme, count = re.subn(pattern, partial(replacement_text, row), readme, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(
                f"{name}: expected exactly one README row; review table placement"
            )
        if refresh_integrity and lock["skills"][name]["sourceType"] == "local":
            lock["skills"][name]["computedHash"] = hashlib.sha256(
                skill.read_bytes()
            ).hexdigest()
    outputs = {
        catalog_path: json.dumps(catalog, indent=2) + "\n",
        root / "README.md": readme,
    }
    if refresh_integrity:
        outputs[lock_path] = json.dumps(lock, indent=2) + "\n"
        outputs[root / ".agents/catalog/integrity.json"] = (
            json.dumps(
                {
                    "schema_version": 1,
                    "algorithm": "sha256",
                    "files": bundle_hashes(root),
                },
                indent=2,
            )
            + "\n"
        )
    return outputs


def write_atomic(path: Path, content: str) -> None:
    descriptor, filename = tempfile.mkstemp(prefix=".catalog-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(filename, path)
    finally:
        Path(filename).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview catalog/README changes; refresh hashes only after reviewing source changes"
    )
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-integrity", action="store_true")
    args = parser.parse_args()
    try:
        outputs = desired_outputs(args.root.resolve(), args.refresh_integrity)
        changed = [
            path
            for path, text in outputs.items()
            if not path.exists() or path.read_text() != text
        ]
        if args.write:
            for path in changed:
                write_atomic(path, outputs[path])
        print(
            json.dumps(
                {
                    "mode": "write" if args.write else "check",
                    "changed": [str(p) for p in changed],
                },
                indent=2,
            )
        )
        return int(bool(changed) and not args.write)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
