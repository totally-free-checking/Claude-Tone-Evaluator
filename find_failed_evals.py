#!/usr/bin/env python3
"""
Find all failed evaluations (those with errors or zero scores)
"""

import json
import glob
from collections import defaultdict

INDIVIDUAL_RESULTS_DIR = "evaluation_results/individual"


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


def main():
    """Find and report all failed evaluations"""
    json_files = glob.glob(f"{INDIVIDUAL_RESULTS_DIR}/*.json")

    if not json_files:
        print("No evaluation files found!")
        print(f"Looking in: {INDIVIDUAL_RESULTS_DIR}/")
        return

    print("Checking evaluation results...")
    print("=" * 80)

    failed_by_bot = defaultdict(list)
    total_count = 0
    failed_count = 0

    for filepath in sorted(json_files):
        total_count += 1
        is_failed, reason = check_evaluation_failed(filepath)

        if is_failed:
            failed_count += 1
            # Extract bot name and query index from filename
            filename = filepath.split('/')[-1].split('\\')[-1]
            bot_name = filename.rsplit('_query_', 1)[0]
            query_idx = filename.rsplit('_query_', 1)[1].replace('.json', '')

            failed_by_bot[bot_name].append({
                'query_idx': query_idx,
                'reason': reason,
                'filepath': filepath
            })

    # Report results
    print(f"\nTotal evaluations: {total_count}")
    print(f"Failed evaluations: {failed_count}")
    print(f"Success rate: {((total_count - failed_count) / total_count * 100):.1f}%\n")

    if failed_count == 0:
        print("No failed evaluations found!")
        return

    print("=" * 80)
    print("FAILED EVALUATIONS BY BOT")
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

    print("=" * 80)
    print("\nTO RETRY FAILED EVALUATIONS:")
    print("=" * 80)

    for bot_name in sorted(failed_by_bot.keys()):
        print(f"python evaluate_single_bot_aoai_robust.py {bot_name} --retry-failed")


if __name__ == "__main__":
    main()
