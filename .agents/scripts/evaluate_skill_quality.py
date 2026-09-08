from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any


def digest(document: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def indexed_cases(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = document.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('A nonempty cases list is required')
    indexed = {}
    for case in cases:
        if not isinstance(case, dict) or not nonempty(case.get('id')):
            raise ValueError('Each case needs a nonempty string ID')
        if case['id'] in indexed:
            raise ValueError('Case IDs must be unique')
        indexed[case['id']] = case
    return indexed


def blind_pairs(
    scenarios: dict[str, Any], before: dict[str, Any], after: dict[str, Any], seed: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    cases = indexed_cases(scenarios)
    for outputs in (before.get('outputs'), after.get('outputs')):
        if not isinstance(outputs, dict) or set(outputs) != set(cases):
            raise ValueError('Both versions must contain exactly the scenario IDs')
        if not all(nonempty(value) for value in outputs.values()):
            raise ValueError('Candidate outputs must be nonempty text')
    randomizer = random.Random(seed)
    blinded = []
    mapping = {}
    for identifier, case in cases.items():
        criteria = case.get('criteria')
        if not nonempty(case.get('prompt')) or not isinstance(criteria, dict) or not criteria:
            raise ValueError('Each case needs a prompt and named semantic criteria')
        if not all(nonempty(key) and nonempty(value) for key, value in criteria.items()):
            raise ValueError('Criteria need nonempty IDs and descriptions')
        versions = ['before', 'after']
        randomizer.shuffle(versions)
        labels = dict(zip(('A', 'B'), versions, strict=True))
        mapping[identifier] = labels
        sources = {'before': before['outputs'][identifier], 'after': after['outputs'][identifier]}
        blinded.append({'id': identifier, 'prompt': case['prompt'], 'criteria': criteria,
                        'candidates': {label: sources[version] for label, version in labels.items()}})
    pack = {'schema_version': 1, 'cases': blinded}
    key = {'schema_version': 1, 'seed': seed, 'pack_sha256': digest(pack), 'cases': mapping}
    return pack, key


def validate_rating(rating: Any, criteria: dict[str, str]) -> int:
    if not isinstance(rating, dict) or set(rating) != {'criteria', 'hard_failures'}:
        raise ValueError('Each candidate needs criteria and hard_failures')
    scored = rating['criteria']
    failures = rating['hard_failures']
    if not isinstance(scored, dict) or set(scored) != set(criteria):
        raise ValueError('Every requested criterion must be judged exactly once')
    if not isinstance(failures, list) or not all(nonempty(item) for item in failures):
        raise ValueError('Hard failures must be a list of concrete evidence strings')
    total = 0
    for entry in scored.values():
        if not isinstance(entry, dict) or set(entry) != {'score', 'evidence'}:
            raise ValueError('Each criterion needs a score and evidence')
        score = entry['score']
        if type(score) is not int or not 0 <= score <= 3 or not nonempty(entry['evidence']):
            raise ValueError('Scores must be integers 0-3 with nonempty evidence')
        total += score
    return total


def summarize(pack: dict[str, Any], key: dict[str, Any], judgments: dict[str, Any]) -> dict[str, Any]:
    if key.get('pack_sha256') != digest(pack):
        raise ValueError('Blind pack differs from the version-bound key')
    if judgments.get('pack_sha256') != digest(pack):
        raise ValueError('Judgments must identify the exact blind pack they assessed')
    cases = indexed_cases(pack)
    judged = indexed_cases(judgments)
    keys = key.get('cases')
    if not isinstance(keys, dict) or set(cases) != set(judged) or set(cases) != set(keys):
        raise ValueError('Judgment, key and pack IDs must match exactly')
    results = []
    counts = {'before': 0, 'after': 0, 'tie': 0, 'neither': 0}
    for identifier, case in cases.items():
        mapping = keys[identifier]
        if not isinstance(mapping, dict) or set(mapping) != {'A', 'B'} or set(mapping.values()) != {'before', 'after'}:
            raise ValueError('Each key must map A/B uniquely to before/after')
        ratings = judged[identifier].get('ratings')
        if not isinstance(ratings, dict) or set(ratings) != {'A', 'B'}:
            raise ValueError('Each case must judge both anonymous candidates')
        totals = {label: validate_rating(ratings[label], case['criteria']) for label in ('A', 'B')}
        eligible = [label for label in ('A', 'B') if not ratings[label]['hard_failures']]
        if not eligible:
            winner = 'neither'
        elif len(eligible) == 1:
            winner = mapping[eligible[0]]
        elif totals['A'] == totals['B']:
            winner = 'tie'
        else:
            winner = mapping[max(totals, key=lambda label: totals[label])]
        counts[winner] += 1
        results.append({'id': identifier, 'winner': winner,
                        'scores': {mapping[label]: totals[label] for label in ('A', 'B')},
                        'hard_failures': {mapping[label]: ratings[label]['hard_failures'] for label in ('A', 'B')}})
    return {'schema_version': 1, 'counts': counts, 'cases': results,
            'scope': 'Offline prompt judgments; no generated-media or statistical quality claim'}


def read_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text())
    if not isinstance(document, dict):
        raise TypeError('Expected a JSON object')
    return document


def write_json(path: Path, document: dict[str, Any]) -> None:
    with path.open('x') as handle:
        json.dump(document, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write('\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Blind paired prompt outputs and aggregate evidence-backed judgments; never generate or auto-judge')
    commands = parser.add_subparsers(dest='command', required=True)
    pack = commands.add_parser('pack')
    pack.add_argument('--cases', type=Path, required=True)
    pack.add_argument('--before', type=Path, required=True)
    pack.add_argument('--after', type=Path, required=True)
    pack.add_argument('--seed', type=int, default=0)
    pack.add_argument('--out', type=Path, required=True)
    report = commands.add_parser('summarize')
    report.add_argument('--pack', type=Path, required=True)
    report.add_argument('--key', type=Path, required=True)
    report.add_argument('--judgments', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'pack':
            blinded, key = blind_pairs(read_json(args.cases), read_json(args.before), read_json(args.after), args.seed)
            args.out.mkdir(parents=True, exist_ok=False)
            write_json(args.out / 'blind.json', blinded)
            write_json(args.out / 'key.json', key)
            print(json.dumps({'cases': len(blinded['cases']), 'out': str(args.out)}))
        else:
            print(json.dumps(summarize(read_json(args.pack), read_json(args.key), read_json(args.judgments)), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
