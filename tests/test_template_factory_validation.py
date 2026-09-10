import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / ".agents/skills/template-factory/scripts/validate_breakdown.py"
SPEC = importlib.util.spec_from_file_location("template_validation", VALIDATOR_PATH)
validation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class TemplateFactoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.breakdown = {
            "schema_version": "1.0",
            "title": "Fixture",
            "genre": "commercial",
            "visual_style": {
                "grade": "warm",
                "lighting_direction": "side key",
                "lens": "wide",
                "film_look": "clean digital",
            },
            "camera": {
                "shot_sizes": ["wide"],
                "moves": ["dolly"],
                "framing": "centered",
                "transitions": ["hard cut"],
            },
            "audio": {
                "mode": "silent",
                "music": None,
                "sfx": [],
                "dialogue": None,
            },
            "elements": [
                {
                    "type": "prop",
                    "id": "hero-shoe",
                    "tag": "@hero-shoe",
                    "descriptor": "red running shoe with a white sole",
                    "keyframe_index": [1],
                    "in_shots": [1, 2],
                }
            ],
            "shots": [self.shot(1, 0.0, 1.0), self.shot(2, 1.0, 2.0)],
        }

    def shot(self, index, start, end):
        return {
            "index": index,
            "start_s": start,
            "end_s": end,
            "duration_s": end - start,
            "composition": "centered product",
            "camera": "locked",
            "action": "shoe rotates",
            "lighting": "soft side key",
            "audio": "silent",
            "end_state": "shoe faces camera",
        }

    def motion_review(self, analysis_bytes, order=(1, 2), mode="source"):
        by_index = {shot["index"]: shot for shot in self.breakdown["shots"]}
        result = {
            "schema_version": "1.0",
            "source_breakdown_sha256": hashlib.sha256(analysis_bytes).hexdigest(),
            "mode": mode,
            "shots": [],
            "top_directing_prompt_text": ["Rotate the shoe steadily."],
        }
        for index in order:
            shot = by_index[index]
            result["shots"].append(
                {
                    "shot_index": index,
                    "start_s": shot["start_s"],
                    "end_s": shot["end_s"],
                    "visible_content": {
                        "subjects": ["shoe"],
                        "background_elements": [],
                        "effects": [],
                    },
                    "motion": {
                        "camera_motion": "locked",
                        "moving_elements": [
                            {
                                "name": "shoe",
                                "motion": "rotation",
                                "direction": "clockwise",
                                "speed": "slow",
                                "amplitude": "quarter turn",
                                "easing": "linear",
                                "loop_period": None,
                            }
                        ],
                        "light_motion": "steady",
                        "strongest_cue": "shoe rotation",
                    },
                    "confidence": "high",
                    "uncertain_estimates": [],
                    "directing_prompt_text": "Rotate the shoe clockwise.",
                }
            )
        if mode == "comparison":
            result["global_diffs"] = {
                "pace_cut_timing": "matched",
                "energy_level": "lower",
                "aesthetic": "matched",
            }
            for shot in result["shots"]:
                shot["missing_or_wrong"] = ["rotation is slow"]
                shot["concrete_fix_prompt_text"] = "Increase rotation speed."
        return result

    def rule_ids(self, findings):
        return {finding.rule_id for finding in findings}

    def test_valid_breakdown_and_reversed_motion_order_pass_without_mutation(self):
        before = copy.deepcopy(self.breakdown)
        analysis_bytes = json.dumps(self.breakdown).encode()
        motion = self.motion_review(analysis_bytes, order=(2, 1))
        self.assertEqual(
            validation.validate_breakdown(self.breakdown, source_duration_s=2.0), []
        )
        self.assertEqual(
            validation.validate_motion_review(
                motion,
                self.breakdown,
                breakdown_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
            ),
            [],
        )
        self.assertEqual(self.breakdown, before)

    def test_invalid_timeline_and_element_references_are_rejected(self):
        self.breakdown["shots"][0]["duration_s"] = 9.0
        self.breakdown["shots"][1]["start_s"] = 0.5
        self.breakdown["elements"][0]["keyframe_index"] = [9]
        rules = self.rule_ids(validation.validate_breakdown(self.breakdown))
        self.assertIn("breakdown.timeline", rules)
        self.assertIn("breakdown.element_references", rules)

    def test_nonfinite_times_duplicate_ids_and_blank_fields_are_rejected(self):
        self.breakdown["shots"][0]["start_s"] = float("nan")
        self.breakdown["shots"][1]["index"] = 1
        self.breakdown["elements"].append(copy.deepcopy(self.breakdown["elements"][0]))
        self.breakdown["shots"][0]["action"] = ""
        rules = self.rule_ids(validation.validate_breakdown(self.breakdown))
        self.assertIn("breakdown.schema", rules)
        self.assertIn("breakdown.timeline", rules)
        self.assertIn("breakdown.element_references", rules)

    def test_malformed_nested_types_return_findings_without_exceptions(self):
        motion = self.motion_review(json.dumps(self.breakdown).encode())
        self.breakdown["shots"][0]["index"] = {"bad": "value"}
        self.breakdown["elements"][0]["keyframe_index"] = [{"bad": "value"}]
        findings = validation.validate_breakdown(
            self.breakdown, source_duration_s=float("inf")
        )
        self.assertTrue(findings)

        analysis_bytes = json.dumps(self.breakdown).encode()
        motion["shots"][0]["shot_index"] = {"bad": "value"}
        self.assertTrue(
            validation.validate_motion_review(
                motion,
                self.breakdown,
                breakdown_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
            )
        )

    def test_stale_or_misaligned_motion_review_is_rejected(self):
        analysis_bytes = json.dumps(self.breakdown).encode()
        motion = self.motion_review(analysis_bytes)
        motion["source_breakdown_sha256"] = "0" * 64
        motion["shots"][0]["start_s"] = 0.4
        motion["shots"].pop()
        rules = self.rule_ids(
            validation.validate_motion_review(
                motion,
                self.breakdown,
                breakdown_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
            )
        )
        self.assertIn("motion.source_current", rules)
        self.assertIn("motion.shot_alignment", rules)

    def test_uncertain_and_comparison_evidence_is_required(self):
        analysis_bytes = json.dumps(self.breakdown).encode()
        motion = self.motion_review(analysis_bytes)
        motion["shots"][0]["confidence"] = "low"
        self.assertIn(
            "motion.schema",
            self.rule_ids(
                validation.validate_motion_review(
                    motion,
                    self.breakdown,
                    breakdown_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
                )
            ),
        )
        comparison = self.motion_review(analysis_bytes, mode="comparison")
        comparison["shots"][0].pop("concrete_fix_prompt_text")
        self.assertIn(
            "motion.schema",
            self.rule_ids(
                validation.validate_motion_review(
                    comparison,
                    self.breakdown,
                    breakdown_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
                )
            ),
        )

    def test_schemas_are_valid_and_example_template_conforms(self):
        references = VALIDATOR_PATH.parents[1] / "references"
        for name in (
            "breakdown-schema.json",
            "motion-review-schema.json",
            "template-schema.json",
        ):
            Draft202012Validator.check_schema(
                json.loads((references / name).read_text())
            )
        schema = json.loads((references / "template-schema.json").read_text())
        template = json.loads(
            (references / "templates/psychedelic-neon-cosmic/template.json").read_text()
        )
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(template)), [])

    def test_cli_returns_parseable_json_and_meaningful_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            analysis = Path(directory) / "analysis.json"
            analysis.write_text(json.dumps(self.breakdown))
            valid = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR_PATH),
                    str(analysis),
                    "--source-duration-s",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(valid.returncode, 0)
            self.assertTrue(json.loads(valid.stdout)["ok"])
            self.breakdown["shots"][0]["duration_s"] = 8.0
            analysis.write_text(json.dumps(self.breakdown))
            invalid = subprocess.run(
                [sys.executable, str(VALIDATOR_PATH), str(analysis)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertFalse(json.loads(invalid.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
