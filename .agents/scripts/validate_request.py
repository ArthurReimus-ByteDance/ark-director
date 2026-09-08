from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "contracts/schemas"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    message: str
    path: str = ""
    severity: str = "error"
    line: int = 0


@dataclass(frozen=True)
class RecoveryDecision:
    action: str
    task_id: str | None = None
    reason: str = ""


def contained_path(root: Path, value: str) -> Path:
    if (
        not isinstance(value, str)
        or not value
        or Path(value).is_absolute()
        or ".." in Path(value).parts
    ):
        raise ValueError("Expected a project-relative path without traversal")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Path must resolve to an existing file within the project")
    return path


def schema_findings(value: Any, name: str) -> list[Finding]:
    schema = json.loads((SCHEMA_ROOT / name).read_text())
    return [
        Finding("schema.valid", error.message, ".".join(map(str, error.path)))
        for error in Draft202012Validator(schema).iter_errors(value)
    ]


def compute_request_hash(
    prompt_bytes: bytes,
    references: list[dict[str, Any]],
    model: str,
    operation: str,
    params: dict[str, Any],
) -> str:
    body = {
        "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "model": model,
        "operation": operation,
        "params": params,
        "references": [
            {key: ref.get(key) for key in ("sha256", "role", "binding")}
            for ref in references
        ],
    }
    return hashlib.sha256(
        json.dumps(
            body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def approval_matches(root: Path, ref: dict[str, Any], target: Path) -> bool:
    evidence = ref.get("approval_evidence", {})
    try:
        manifest = contained_path(root, evidence.get("manifest", ""))
        text = manifest.read_text()
        match = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
        if not match:
            return False
        metadata = YAML(typ="safe").load(match.group(1))
        field = evidence.get("field")
        if field not in ("selected_variant", "selected_variants") or not isinstance(
            metadata, dict
        ):
            return False
        selected = metadata.get(field)
        if field == "selected_variants":
            selected = (
                selected.get(evidence.get("key"))
                if isinstance(selected, dict)
                else None
            )
        if (
            not isinstance(selected, str)
            or selected == "auto"
            or Path(selected).is_absolute()
            or ".." in Path(selected).parts
        ):
            return False
        return any(
            candidate.resolve() == target
            for candidate in (root / selected, manifest.parent / selected)
        )
    except (OSError, ValueError, TypeError, AttributeError, YAMLError):
        return False


def reference_findings(
    root: Path, references: list[dict[str, Any]], prompt: str
) -> list[Finding]:
    findings: list[Finding] = []
    counters = {"Image": 0, "Video": 0, "Audio": 0}
    expected_bindings: list[str] = []
    for ref in references:
        path = ref["path"]
        if ref.get("control_only"):
            findings.append(
                Finding(
                    "references.control_only",
                    "Control-only assets are not eligible generation inputs",
                    path,
                )
            )
        try:
            target = contained_path(root, path)
        except ValueError as error:
            findings.append(Finding("path.containment", str(error), path))
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != ref["sha256"]:
            findings.append(
                Finding("references.current_hashes", "Reference content changed", path)
            )
        if not approval_matches(root, ref, target):
            findings.append(
                Finding(
                    "approval.explicit_choice",
                    "Reference must match an explicit manifest selection",
                    path,
                )
            )
        media = (
            "Audio"
            if "audio" in ref["role"]
            else "Video"
            if "video" in ref["role"]
            else "Image"
        )
        counters[media] += 1
        expected = f"@{media} {counters[media]}"
        expected_bindings.append(ref["binding"])
        if ref["binding"] != expected or expected not in prompt:
            findings.append(
                Finding(
                    "references.ordered_bindings",
                    f"Expected bound input {expected}",
                    path,
                )
            )
    actual = set(re.findall(r"@(?:Image|Video|Audio) \d+\b", prompt))
    if actual != set(expected_bindings):
        findings.append(
            Finding(
                "references.ordered_bindings",
                "Prompt bindings and ordered inputs differ",
            )
        )
    return findings


def external_schema_references(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            (key in ("$ref", "$dynamicRef") and not str(child).startswith("#"))
            or external_schema_references(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(external_schema_references(child) for child in value)
    return False


def capability_findings(request: dict[str, Any], evidence: Any) -> list[Finding]:
    malformed = schema_findings(evidence, "capability-evidence.schema.json")
    if malformed:
        return [
            Finding("model.supported_mode", finding.message) for finding in malformed
        ]
    if external_schema_references(evidence["parameters"]):
        return [
            Finding(
                "model.supported_mode",
                "Capability schemas must be self-contained; remote references are not loaded",
            )
        ]
    findings: list[Finding] = []
    if evidence.get("model") != request["model"] or request[
        "operation"
    ] not in evidence.get("operations", []):
        findings.append(
            Finding(
                "model.supported_mode",
                "Model or operation is absent from capability evidence",
            )
        )
    properties = evidence.get("parameters", {})
    if not isinstance(properties, dict):
        return [
            Finding(
                "model.supported_mode", "Parameter evidence must be a schema mapping"
            )
        ]
    schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "required": evidence.get("required_parameters", []),
    }
    try:
        Draft202012Validator.check_schema(schema)
        for error in Draft202012Validator(schema).iter_errors(request["params"]):
            findings.append(Finding("model.supported_mode", error.message))
    except (SchemaError, TypeError, ValueError) as error:
        findings.append(
            Finding("model.supported_mode", f"Invalid capability schema: {error}")
        )
    roles = [ref["role"] for ref in request["references"]]
    if any(role not in evidence.get("reference_roles", []) for role in roles):
        findings.append(
            Finding("model.supported_mode", "Reference role is unsupported")
        )
    maximum = evidence.get("max_references", 0)
    if not isinstance(maximum, int) or len(roles) > maximum:
        findings.append(
            Finding(
                "model.supported_mode", "Reference count exceeds verified allowance"
            )
        )
    if (
        "reference_image" in roles
        and any(role in roles for role in ("first_frame", "last_frame"))
        and not evidence.get("supports_first_frame_with_reference_images", False)
    ):
        findings.append(
            Finding(
                "model.supported_mode",
                "Mixed frame and reference-image roles are not verified",
            )
        )
    return findings


def validate_request(
    project_root: Path, request: Any, capability_evidence: Any
) -> list[Finding]:
    findings = schema_findings(request, "generation-request.schema.json")
    if findings:
        return findings
    root = Path(project_root).resolve()
    try:
        prompt_path = contained_path(root, request["prompt_file"])
        prompt_bytes = prompt_path.read_bytes()
        prompt_text = prompt_bytes.decode("utf-8")
    except (ValueError, OSError, UnicodeError) as error:
        return [Finding("path.containment", str(error), request["prompt_file"])]
    if hashlib.sha256(prompt_bytes).hexdigest() != request["prompt_sha256"]:
        findings.append(
            Finding(
                "prompt.current_hash",
                "Prompt snapshot content changed",
                request["prompt_file"],
            )
        )
    try:
        digest = compute_request_hash(
            prompt_bytes,
            request["references"],
            request["model"],
            request["operation"],
            request["params"],
        )
        if digest != request["request_sha256"]:
            findings.append(
                Finding(
                    "request.current_hash",
                    "Request content differs from the reviewed request",
                )
            )
    except (ValueError, TypeError) as error:
        findings.append(Finding("request.current_hash", str(error)))
    findings.extend(reference_findings(root, request["references"], prompt_text))
    findings.extend(capability_findings(request, capability_evidence))
    if (
        request["submission_status"] != "prepared"
        or request["provider_task_id"] is not None
    ):
        findings.append(
            Finding(
                "submission.reconcile_unknown",
                "Existing or uncertain operations must reconcile rather than submit",
            )
        )
    return findings


def validate_review(
    review: Any, request_hash: str, required_rule_ids: list[str]
) -> list[Finding]:
    findings = schema_findings(review, "review-result.schema.json")
    if findings:
        return findings
    if (
        review["request_sha256"] != request_hash
        or review["reviewer_status"] != "complete"
    ):
        findings.append(
            Finding(
                "review.complete_evidence",
                "Review is incomplete or belongs to another request",
            )
        )
    seen: set[str] = set()
    for check in review["checks"]:
        if check["rule_id"] in seen:
            findings.append(
                Finding("review.complete_evidence", "Duplicate rule result")
            )
        seen.add(check["rule_id"])
        if check["status"] == "fail" or not check["evidence"].strip():
            findings.append(
                Finding(check["rule_id"], "Failed check or missing evidence")
            )
        if (
            check["status"] == "not_applicable"
            and check["rule_id"] in required_rule_ids
        ):
            findings.append(
                Finding(
                    check["rule_id"], "Required applicable checks cannot be skipped"
                )
            )
    for missing in set(required_rule_ids) - seen:
        findings.append(
            Finding("review.complete_evidence", f"Missing required rule: {missing}")
        )
    return findings


def reconcile_operation(
    operation: dict[str, Any], provider_observation: dict[str, Any]
) -> RecoveryDecision:
    task_id = operation.get("provider_task_id") or provider_observation.get(
        "provider_task_id"
    )
    status = provider_observation.get("provider_status")
    if status == "succeeded":
        return RecoveryDecision(
            "download", task_id, "Recover the existing output; do not regenerate"
        )
    if status in ("failed", "cancelled", "expired", "moderation_rejected"):
        return RecoveryDecision(
            "review_failure",
            task_id,
            "Review failure evidence before authorizing a new operation",
        )
    if task_id:
        return RecoveryDecision("poll", task_id, "Resume the existing provider task")
    return RecoveryDecision(
        "hold",
        None,
        "Acceptance is unknown; reconcile or obtain an explicit retry decision",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only generation preflight; never calls a provider"
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--capabilities", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--required-rule", action="append", default=[])
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text())
        findings = validate_request(
            args.project, request, json.loads(args.capabilities.read_text())
        )
        if args.review:
            findings.extend(
                validate_review(
                    json.loads(args.review.read_text()),
                    request.get("request_sha256", ""),
                    args.required_rule,
                )
            )
        else:
            findings.append(
                Finding(
                    "review.complete_evidence",
                    "A completed review is required before submission",
                )
            )
    except (OSError, ValueError) as error:
        findings = [Finding("input.readable", str(error))]
    print(
        json.dumps(
            {"ok": not findings, "findings": [asdict(f) for f in findings]}, indent=2
        )
    )
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
