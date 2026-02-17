#!/usr/bin/env python3
"""
Evaluate a single bot using Azure OpenAI WITHOUT ground truth comparison
Evaluates based on character rubric alone
Usage: python evaluate_single_bot_no_gt.py <bot_name>
Example: python evaluate_single_bot_no_gt.py ClaudeBot-v2
Available bots: ActualClaude, ClaudeBot, ClaudeBot-v2, GPTBot
"""

import json
import csv
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI

# Configuration
EVALUATION_PROMPT_FILE = "Teen Support Bot Tone Evaluator - No Ground Truth.md"
INPUT_PROMPTS_FILE = "input-prompts.csv"
ACTUAL_CLAUDE_FILE = "Output - ActualClaude Responses.jsonl"
CLAUDE_BOT_FILE = "Output - ClaudeBot Responses.jsonl"
CLAUDE_BOT_V2_FILE = "Output - ClaudeBot-v2 Responses.jsonl"
GPT_BOT_FILE = "Output - GPTBot Responses.jsonl"

OUTPUT_DIR = "evaluation_results_no_gt"
INDIVIDUAL_RESULTS_DIR = f"{OUTPUT_DIR}/individual"

BOT_FILES = {
    "ActualClaude": ACTUAL_CLAUDE_FILE,
    "ClaudeBot": CLAUDE_BOT_FILE,
    "ClaudeBot-v2": CLAUDE_BOT_V2_FILE,
    "GPTBot": GPT_BOT_FILE
}


def load_evaluation_prompt() -> str:
    """Load the evaluation prompt from markdown file"""
    with open(EVALUATION_PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def load_prompts() -> List[str]:
    """Load user prompts from CSV"""
    prompts = []
    with open(INPUT_PROMPTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row['userQuery'])
    return prompts


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load responses from JSONL file"""
    responses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            responses.append(json.loads(line))
    return responses


def create_evaluation_request(
    user_query: str,
    response_to_evaluate: str
) -> str:
    """Create the full evaluation request text (no ground truth)"""
    return f"""**User Query:**
{user_query}

**Response to Evaluate:**
{response_to_evaluate}

---

Please evaluate the "Response to Evaluate" against the ideal teen support bot character as defined in your instructions. Return your evaluation ONLY as valid JSON in the exact format specified. Do not include any text before or after the JSON."""


def clean_json_string(json_str: str) -> str:
    """Clean and repair common JSON string issues"""
    if not json_str:
        return "{}"

    # Remove any text before first { and after last }
    start = json_str.find('{')
    end = json_str.rfind('}')

    if start == -1 or end == -1:
        return "{}"

    json_str = json_str[start:end+1]

    # Fix common issues with unescaped quotes in strings
    json_str = json_str.replace('\n', '\\n')
    json_str = json_str.replace('\r', '\\r')
    json_str = json_str.replace('\t', '\\t')

    return json_str


def extract_json_from_response(response_text: str) -> Optional[str]:
    """Extract JSON from response with multiple fallback strategies"""
    if not response_text:
        return None

    # Strategy 1: Look for ```json code blocks
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        if json_end != -1:
            return response_text[json_start:json_end].strip()

    # Strategy 2: Look for any ``` code blocks
    if "```" in response_text:
        json_start = response_text.find("```") + 3
        newline = response_text.find('\n', json_start)
        if newline != -1:
            json_start = newline + 1
        json_end = response_text.find("```", json_start)
        if json_end != -1:
            return response_text[json_start:json_end].strip()

    # Strategy 3: Find first { to last }
    start = response_text.find('{')
    end = response_text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return response_text[start:end+1].strip()

    # Strategy 4: Use the whole response
    return response_text.strip()


def parse_json_robust(json_str: str) -> Dict[str, Any]:
    """Try multiple strategies to parse JSON"""
    # Try 1: Direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Try 2: Clean and parse
    try:
        cleaned = clean_json_string(json_str)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try 3: Extract numbers with regex as fallback
    try:
        overall_match = re.search(r'"overall_score"\s*:\s*([0-9.]+)', json_str)
        overall_score = float(overall_match.group(1)) if overall_match else 0.0

        dimensions = [
            'warmth_validation', 'prose_vs_bullets', 'emoji_usage',
            'conversational_tone', 'practical_advice', 'followup_question',
            'support_solutions_balance', 'length_conciseness'
        ]

        dimension_scores = {}
        for dim in dimensions:
            match = re.search(rf'"{dim}"\s*:\s*([0-9.]+)', json_str)
            if match:
                dimension_scores[dim] = float(match.group(1))
            else:
                dimension_scores[dim] = 0

        return {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "strengths": ["(Partial parse - JSON was malformed)"],
            "weaknesses": ["(Partial parse - JSON was malformed)"],
            "most_ideal_aspect": "N/A (parsing error)",
            "least_ideal_aspect": "N/A (parsing error)",
            "bullet_point_analysis": {
                "bullet_count": 0,
                "prose_percentage": "N/A",
                "notes": "N/A (parsing error)"
            },
            "specific_feedback": ["(Partial parse - JSON was malformed)"],
            "parse_warning": "JSON was malformed, scores extracted via regex"
        }
    except Exception as e:
        return {
            "overall_score": 0.0,
            "dimension_scores": {},
            "error": f"JSON parse failed completely: {str(e)[:200]}"
        }


def evaluate_response(
    client: AzureOpenAI,
    evaluation_prompt: str,
    user_query: str,
    response_to_evaluate: str,
    deployment_name: str
) -> Dict[str, Any]:
    """Call Azure OpenAI API to evaluate a single response (no ground truth)"""
    evaluation_request = create_evaluation_request(
        user_query,
        response_to_evaluate
    )

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": evaluation_request}
            ],
            temperature=0.0,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content

        if not response_text:
            return {
                "overall_score": 0.0,
                "dimension_scores": {},
                "error": "Empty response from API"
            }

        json_str = extract_json_from_response(response_text)

        if not json_str:
            return {
                "overall_score": 0.0,
                "dimension_scores": {},
                "error": "Could not extract JSON from response"
            }

        evaluation = parse_json_robust(json_str)
        return evaluation

    except Exception as e:
        print(f"Error evaluating response: {e}")
        return {
            "overall_score": 0.0,
            "dimension_scores": {},
            "error": str(e)
        }


def save_individual_result(
    bot_name: str,
    query_index: int,
    user_query: str,
    evaluation: Dict[str, Any]
):
    """Save individual evaluation result as JSON"""
    result = {
        "bot_name": bot_name,
        "query_index": query_index,
        "user_query": user_query,
        "evaluation": evaluation
    }

    filename = f"{INDIVIDUAL_RESULTS_DIR}/{bot_name}_query_{query_index:03d}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def check_already_evaluated(bot_name: str, query_index: int) -> bool:
    """Check if this bot/query combo has already been evaluated"""
    filename = f"{INDIVIDUAL_RESULTS_DIR}/{bot_name}_query_{query_index:03d}.json"
    return os.path.exists(filename)


def check_evaluation_failed(bot_name: str, query_index: int) -> bool:
    """Check if an evaluation exists but failed"""
    filename = f"{INDIVIDUAL_RESULTS_DIR}/{bot_name}_query_{query_index:03d}.json"
    if not os.path.exists(filename):
        return False

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            result = json.load(f)
            evaluation = result.get('evaluation', {})
            has_error = 'error' in evaluation
            has_zero_score = evaluation.get('overall_score', 0) == 0.0
            return has_error or has_zero_score
    except:
        return True


def main():
    """Main evaluation pipeline"""
    if len(sys.argv) < 2:
        print("Usage: python evaluate_single_bot_no_gt.py <bot_name> [--retry-failed]")
        print("Available bots: ActualClaude, ClaudeBot, ClaudeBot-v2, GPTBot")
        print("\nOptions:")
        print("  --retry-failed    Only re-evaluate queries that failed previously")
        sys.exit(1)

    bot_name = sys.argv[1]
    retry_failed_only = "--retry-failed" in sys.argv

    if bot_name not in BOT_FILES:
        print(f"Error: Unknown bot '{bot_name}'")
        print("Available bots: ActualClaude, ClaudeBot, ClaudeBot-v2, GPTBot")
        sys.exit(1)

    mode = "RETRY FAILED" if retry_failed_only else "FULL"
    print(f"Evaluating: {bot_name} (Mode: {mode}, NO GROUND TRUTH)")
    print("=" * 80)

    # Setup Azure OpenAI
    azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    deployment_name = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'kimi-2-5')

    if not azure_endpoint or not api_key:
        print("Error: Azure OpenAI credentials not set")
        sys.exit(1)

    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version="2024-08-01-preview"
    )

    print(f"Using Azure OpenAI deployment: {deployment_name}")

    # Create output directories
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(INDIVIDUAL_RESULTS_DIR).mkdir(exist_ok=True)

    # Load data
    print("\nLoading data...")
    evaluation_prompt = load_evaluation_prompt()
    prompts = load_prompts()

    if not os.path.exists(BOT_FILES[bot_name]):
        print(f"\nError: Response file not found: {BOT_FILES[bot_name]}")
        sys.exit(1)

    bot_responses = load_jsonl(BOT_FILES[bot_name])

    print(f"   - {len(prompts)} prompts loaded")
    print(f"   - {len(bot_responses)} {bot_name} responses")

    # Check status
    if retry_failed_only:
        failed_count = sum(1 for i in range(1, len(prompts) + 1)
                          if check_evaluation_failed(bot_name, i))
        print(f"\n   Found {failed_count} failed evaluations to retry")
    else:
        already_done = sum(1 for i in range(1, len(prompts) + 1)
                          if check_already_evaluated(bot_name, i))
        if already_done > 0:
            print(f"\n   Found {already_done} already evaluated responses (will skip)")

    # Evaluate
    print(f"\nStarting evaluation...")
    evaluated_count = 0
    skipped_count = 0

    for i, (prompt, bot_resp) in enumerate(zip(prompts, bot_responses)):
        query_idx = i + 1

        # Check skip conditions
        if retry_failed_only:
            if not check_evaluation_failed(bot_name, query_idx):
                skipped_count += 1
                continue
        else:
            if check_already_evaluated(bot_name, query_idx) and not check_evaluation_failed(bot_name, query_idx):
                skipped_count += 1
                continue

        evaluated_count += 1
        print(f"   [{evaluated_count}] Query {query_idx}: {prompt[:60]}...")

        response_to_eval = bot_resp['response']

        # Evaluate (no ground truth)
        evaluation = evaluate_response(
            client,
            evaluation_prompt,
            prompt,
            response_to_eval,
            deployment_name
        )

        # Save individual result
        save_individual_result(bot_name, query_idx, prompt, evaluation)

    print("\n" + "=" * 80)
    print(f"Evaluation complete for {bot_name}!")
    print("=" * 80)
    print(f"  Evaluated: {evaluated_count} responses")
    print(f"  Skipped: {skipped_count}")
    print(f"\nResults saved to: {INDIVIDUAL_RESULTS_DIR}/{bot_name}_query_*.json")
    print("\nRun 'python merge_results.py' (with updated path) to generate reports")


if __name__ == "__main__":
    main()
