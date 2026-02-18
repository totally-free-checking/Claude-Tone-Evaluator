#!/usr/bin/env python3
"""
Merge all individual evaluation JSON files into CSV summary and report
Supports both with-GT and no-GT evaluation results
"""

import json
import csv
import glob
import sys
from pathlib import Path
from typing import Dict, List, Any

# Configuration - can be overridden by command line args
OUTPUT_DIR = "evaluation_results"
INDIVIDUAL_RESULTS_DIR = f"{OUTPUT_DIR}/individual"
CSV_OUTPUT_FILE = f"{OUTPUT_DIR}/scores_summary.csv"
REPORT_FILE = f"{OUTPUT_DIR}/summary_report.txt"


def load_all_results() -> List[Dict[str, Any]]:
    """Load all individual JSON result files"""
    results = []
    json_files = glob.glob(f"{INDIVIDUAL_RESULTS_DIR}/*.json")

    for filepath in json_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            results.append(json.load(f))

    # Sort by bot name, then query index
    results.sort(key=lambda x: (x['bot_name'], x['query_index']))
    return results


def save_csv_summary(all_results: List[Dict[str, Any]]):
    """Save all results to a comprehensive CSV"""
    if not all_results:
        print("No results to save!")
        return

    fieldnames = [
        'bot_name',
        'query_index',
        'user_query',
        'overall_score',
        'warmth_validation',
        'prose_vs_bullets',
        'emoji_usage',
        'conversational_tone',
        'practical_advice',
        'followup_question',
        'support_solutions_balance',
        'length_conciseness',
        'bullet_count',
        'prose_percentage',
        'most_claude_like',
        'least_claude_like'
    ]

    with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in all_results:
            eval_data = result['evaluation']
            dim_scores = eval_data.get('dimension_scores', {})
            bullet_analysis = eval_data.get('bullet_point_analysis', {})

            row = {
                'bot_name': result['bot_name'],
                'query_index': result['query_index'],
                'user_query': result['user_query'][:100] + '...' if len(result['user_query']) > 100 else result['user_query'],
                'overall_score': eval_data.get('overall_score', 0),
                'warmth_validation': dim_scores.get('warmth_validation', 0),
                'prose_vs_bullets': dim_scores.get('prose_vs_bullets', 0),
                'emoji_usage': dim_scores.get('emoji_usage', 0),
                'conversational_tone': dim_scores.get('conversational_tone', 0),
                'practical_advice': dim_scores.get('practical_advice', 0),
                'followup_question': dim_scores.get('followup_question', 0),
                'support_solutions_balance': dim_scores.get('support_solutions_balance', 0),
                'length_conciseness': dim_scores.get('length_conciseness', 0),
                'bullet_count': bullet_analysis.get('bullet_count', 0),
                'prose_percentage': bullet_analysis.get('prose_percentage', 'N/A'),
                'most_claude_like': eval_data.get('most_claude_like', 'N/A')[:100],
                'least_claude_like': eval_data.get('least_claude_like', 'N/A')[:100]
            }
            writer.writerow(row)

    print(f"CSV summary saved to: {CSV_OUTPUT_FILE}")


def generate_summary_report(all_results: List[Dict[str, Any]]):
    """Generate a human-readable summary report"""
    # Group by bot
    bot_results = {}
    for result in all_results:
        bot = result['bot_name']
        if bot not in bot_results:
            bot_results[bot] = []
        bot_results[bot].append(result['evaluation'])

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TEEN SUPPORT BOT - TONE EVALUATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        # Overall comparison table
        f.write("OVERALL SCORES COMPARISON\n")
        f.write("-" * 80 + "\n\n")

        bot_summary = {}
        for bot_name, evaluations in bot_results.items():
            avg_overall = sum(e.get('overall_score', 0) for e in evaluations) / len(evaluations)
            bot_summary[bot_name] = avg_overall

        # Sort by score descending
        for bot_name in sorted(bot_summary, key=bot_summary.get, reverse=True):
            score = bot_summary[bot_name]
            bar = "█" * int(score) + "░" * (10 - int(score))
            f.write(f"{bot_name:20s} {score:5.2f}/10  {bar}\n")

        f.write("\n")

        # Detailed per-bot analysis
        for bot_name, evaluations in sorted(bot_results.items()):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"BOT: {bot_name}\n")
            f.write(f"{'=' * 80}\n\n")

            # Calculate averages
            avg_overall = sum(e.get('overall_score', 0) for e in evaluations) / len(evaluations)

            dimension_avgs = {}
            for dim in ['warmth_validation', 'prose_vs_bullets', 'emoji_usage',
                       'conversational_tone', 'practical_advice', 'followup_question',
                       'support_solutions_balance', 'length_conciseness']:
                scores = [e.get('dimension_scores', {}).get(dim, 0) for e in evaluations]
                dimension_avgs[dim] = sum(scores) / len(scores)

            f.write(f"Overall Average Score: {avg_overall:.2f}/10\n\n")
            f.write("Dimension Averages:\n")
            for dim, avg in sorted(dimension_avgs.items(), key=lambda x: x[1], reverse=True):
                dim_display = dim.replace('_', ' ').title()
                bar = "█" * int(avg) + "░" * (10 - int(avg))
                f.write(f"  {dim_display:35s} {avg:.2f}/10  {bar}\n")

            # Bullet point analysis
            bullet_counts = [e.get('bullet_point_analysis', {}).get('bullet_count', 0)
                           for e in evaluations]
            avg_bullets = sum(bullet_counts) / len(bullet_counts) if bullet_counts else 0
            f.write(f"\nAverage Bullet Points per Response: {avg_bullets:.1f}\n")

            # Best/worst dimensions
            best_dim = max(dimension_avgs, key=dimension_avgs.get)
            worst_dim = min(dimension_avgs, key=dimension_avgs.get)
            f.write(f"\nStrongest Dimension: {best_dim.replace('_', ' ').title()} ({dimension_avgs[best_dim]:.2f}/10)\n")
            f.write(f"Weakest Dimension: {worst_dim.replace('_', ' ').title()} ({dimension_avgs[worst_dim]:.2f}/10)\n")

        # Comparison insights
        f.write(f"\n\n{'=' * 80}\n")
        f.write("KEY INSIGHTS\n")
        f.write(f"{'=' * 80}\n\n")

        if len(bot_results) >= 2:
            # Find biggest differentiator dimension
            dimension_variance = {}
            for dim in ['warmth_validation', 'prose_vs_bullets', 'emoji_usage',
                       'conversational_tone', 'practical_advice', 'followup_question',
                       'support_solutions_balance', 'length_conciseness']:
                scores = []
                for bot_name, evaluations in bot_results.items():
                    avg = sum(e.get('dimension_scores', {}).get(dim, 0) for e in evaluations) / len(evaluations)
                    scores.append(avg)
                dimension_variance[dim] = max(scores) - min(scores)

            biggest_diff = max(dimension_variance, key=dimension_variance.get)
            f.write(f"Biggest Differentiator: {biggest_diff.replace('_', ' ').title()}\n")
            f.write(f"  (Score range: {dimension_variance[biggest_diff]:.2f} points)\n\n")

            # Show scores for this dimension across bots
            for bot_name, evaluations in sorted(bot_results.items()):
                avg = sum(e.get('dimension_scores', {}).get(biggest_diff, 0) for e in evaluations) / len(evaluations)
                f.write(f"  {bot_name:20s} {avg:.2f}/10\n")

    print(f"Summary report saved to: {REPORT_FILE}")


def main():
    """Main merge pipeline"""
    global OUTPUT_DIR, INDIVIDUAL_RESULTS_DIR, CSV_OUTPUT_FILE, REPORT_FILE

    # Check for command line arguments
    eval_type = "with-gt"  # Default
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-gt":
            eval_type = "no-gt"
            OUTPUT_DIR = "evaluation_results_no_gt"
            INDIVIDUAL_RESULTS_DIR = f"{OUTPUT_DIR}/individual"
            CSV_OUTPUT_FILE = f"{OUTPUT_DIR}/scores_summary.csv"
            REPORT_FILE = f"{OUTPUT_DIR}/summary_report.txt"
        elif sys.argv[1] in ["--help", "-h"]:
            print("Usage: python merge_results.py [--no-gt]")
            print("\nOptions:")
            print("  (default)    Merge with-ground-truth evaluations (evaluation_results/)")
            print("  --no-gt      Merge no-ground-truth evaluations (evaluation_results_no_gt/)")
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python merge_results.py [--no-gt]")
            return

    eval_type_display = "WITHOUT Ground Truth" if eval_type == "no-gt" else "WITH Ground Truth"
    print(f"Merging Evaluation Results ({eval_type_display})")
    print("=" * 80)

    # Load all individual results
    print(f"\nLoading individual result files from: {INDIVIDUAL_RESULTS_DIR}/")
    all_results = load_all_results()

    if not all_results:
        print(f"No results found in {INDIVIDUAL_RESULTS_DIR}/")
        print(f"Run evaluate_single_bot{'_no_gt' if eval_type == 'no-gt' else '_aoai_robust'}.py first.")
        return

    # Count by bot
    bot_counts = {}
    for result in all_results:
        bot = result['bot_name']
        bot_counts[bot] = bot_counts.get(bot, 0) + 1

    print(f"\nFound {len(all_results)} total evaluations:")
    for bot, count in sorted(bot_counts.items()):
        print(f"  - {bot}: {count} responses")

    # Save CSV summary
    print("\nGenerating CSV summary...")
    save_csv_summary(all_results)

    # Generate summary report
    print("Generating summary report...")
    generate_summary_report(all_results)

    print("\n" + "=" * 80)
    print(f"Merge complete! ({eval_type_display})")
    print("=" * 80)
    print(f"\nOutput files:")
    print(f"  - CSV Summary: {CSV_OUTPUT_FILE}")
    print(f"  - Summary Report: {REPORT_FILE}")

    if eval_type == "with-gt":
        print(f"\nTo merge no-GT results: python merge_results.py --no-gt")


if __name__ == "__main__":
    main()
