#!/usr/bin/env python3
"""
Find all failed evaluations (those with errors or zero scores)
Checks both with-GT and no-GT evaluation results
"""

import json
import glob
import sys
import csv
from pathlib import Path
from collections import defaultdict

RESULTS_DIR_GT = "evaluation_results/individual"
RESULTS_DIR_NO_GT = "evaluation_results_no_gt/individual"
INPUT_PROMPTS_FILE = "input-prompts.csv"


def check_evaluation_failed(filepath: str) -> tuple[bool, str]:
    """
    Check if an evaluation failed
    Returns: (is_failed, reason)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            result = json.load(f)
            evaluation = result.get('evaluation', {})

            if 'error' in evaluation:
                return True, f"Error: {evaluation['error'][:100]}"

            if evaluation.get('overall_score', 0) == 0.0:
                # Check if all dimension scores are also 0
                dim_scores = evaluation.get('dimension_scores', {})
                if all(score == 0 for score in dim_scores.values()):
                    return True, "All scores are 0"

            if 'parse_warning' in evaluation:
                return True, "JSON parsing issue (partial parse)"

            return False, ""

    except Exception as e:
        return True, f"Could not read file: {str(e)}"


_PROMPT_COUNT_CACHE: int | None = None


def load_total_prompt_count() -> int:
    """Return total queries in input-prompts.csv (cached)."""
    global _PROMPT_COUNT_CACHE
    if _PROMPT_COUNT_CACHE is not None:
        return _PROMPT_COUNT_CACHE

    try:
        with open(INPUT_PROMPTS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            _PROMPT_COUNT_CACHE = sum(1 for _ in reader)
    except FileNotFoundError:
        print(f"Warning: {INPUT_PROMPTS_FILE} not found; missing-file check limited.")
        _PROMPT_COUNT_CACHE = 0

    return _PROMPT_COUNT_CACHE


def get_expected_query_count(bot_name: str) -> int:
    """Determine expected query count for a bot via response files or prompt list."""
    candidate_files = [
        Path("bot_responses") / f"Output - {bot_name} Responses.jsonl",
        Path(f"Output - {bot_name} Responses.jsonl"),
    ]

    for candidate in candidate_files:
        if candidate.exists():
            with open(candidate, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)

    return load_total_prompt_count()


def check_directory(results_dir: str, eval_type: str):
    """Check a specific evaluation directory"""
    json_files = glob.glob(f"{results_dir}/*.json")

    if not json_files:
        print(f"\nNo {eval_type} evaluation files found in: {results_dir}/")
        return None

    print(f"\n{'=' * 80}")
    print(f"Checking {eval_type} evaluation results...")
    print(f"{'=' * 80}")

    failed_by_bot = defaultdict(list)
    indices_by_bot: dict[str, set[int]] = defaultdict(set)
    total_count = 0
    failed_count = 0
    missing_total = 0

    for filepath in sorted(json_files):
        total_count += 1
        is_failed, reason = check_evaluation_failed(filepath)

        # Extract bot name and query index from filename
        filename = filepath.split('/')[-1].split('\\')[-1]
        bot_name = filename.rsplit('_query_', 1)[0]
        query_idx = filename.rsplit('_query_', 1)[1].replace('.json', '')            
        
        if is_failed:
            failed_count += 1        

            failed_by_bot[bot_name].append({
                'query_idx': query_idx,
                'reason': reason,
                'filepath': filepath
            })

        try:
            query_idx_int = int(query_idx)
            indices_by_bot[bot_name].add(query_idx_int)
        except ValueError:
            pass

    # Detect missing evaluations per bot
    for bot_name, existing_indices in indices_by_bot.items():
        expected_count = get_expected_query_count(bot_name)
        if expected_count <= 0:
            continue

        missing_indices = [i for i in range(1, expected_count + 1) if i not in existing_indices]
        if missing_indices:
            for idx in missing_indices:
                failed_count += 1
                missing_total += 1
                failed_by_bot[bot_name].append({
                    'query_idx': f"{idx:03d}",
                    'reason': "Missing evaluation file",
                    'filepath': str(Path(results_dir) / f"{bot_name}_query_{idx:03d}.json")
                })

    total_count += missing_total

    # Report results
    print(f"\nTotal evaluations: {total_count}")
    print(f"Failed evaluations: {failed_count}")
    if total_count > 0:
        print(f"Success rate: {((total_count - failed_count) / total_count * 100):.1f}%\n")

    if failed_count == 0:
        print(f"✓ No failed {eval_type} evaluations found!")
        return None

    print("=" * 80)
    print(f"FAILED {eval_type.upper()} EVALUATIONS BY BOT")
    print("=" * 80)

    for bot_name, failures in sorted(failed_by_bot.items()):
        print(f"\n{bot_name}: {len(failures)} failures")
        print("-" * 80)

        # Group by reason
        reasons = defaultdict(list)
        for failure in failures:
            reasons[failure['reason']].append(failure['query_idx'])

        for reason, queries in sorted(reasons.items()):
            print(f"  {reason}")
            print(f"  Queries: {', '.join(queries)}")
            print()

    return failed_by_bot


def main():
    """Find and report all failed evaluations"""

    # Check both directories
    print("=" * 80)
    print("CHECKING ALL EVALUATION RESULTS")
    print("=" * 80)

    failed_gt = check_directory(RESULTS_DIR_GT, "WITH Ground Truth")
    failed_no_gt = check_directory(RESULTS_DIR_NO_GT, "WITHOUT Ground Truth")

    # Print retry commands
    has_failures = (failed_gt and len(failed_gt) > 0) or (failed_no_gt and len(failed_no_gt) > 0)

    if not has_failures:
        print("\n" + "=" * 80)
        print("✓ ALL EVALUATIONS SUCCESSFUL!")
        print("=" * 80)
        return

    print("\n" + "=" * 80)
    print("TO RETRY FAILED EVALUATIONS:")
    print("=" * 80)

    if failed_gt and len(failed_gt) > 0:
        print("\n# With Ground Truth:")
        for bot_name in sorted(failed_gt.keys()):
            print(f"python evaluate_single_bot_aoai_robust.py {bot_name} --retry-failed")

    if failed_no_gt and len(failed_no_gt) > 0:
        print("\n# Without Ground Truth:")
        for bot_name in sorted(failed_no_gt.keys()):
            print(f"python evaluate_single_bot_no_gt.py {bot_name} --retry-failed")


if __name__ == "__main__":
    main()
