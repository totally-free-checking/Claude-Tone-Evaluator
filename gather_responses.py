#!/usr/bin/env python3
"""
Gather LLM responses for evaluation
Generates Output - [BotName] Responses.jsonl files

Usage:
  python gather_responses.py <bot_name> --provider <provider> --model <model> [--system-prompt <file>]

Examples:
  # Anthropic direct
  python gather_responses.py ActualClaude --provider anthropic --model claude-sonnet-4-5-20250929

  # Azure OpenAI
  python gather_responses.py KimiBotTuned --provider azure-openai --model kimi-2-5 --system-prompt "ClaudeBot_System_Prompt.md"

  # Anthropic with custom prompt
  python gather_responses.py ActualClaudeTuned --provider anthropic --model claude-sonnet-4-5-20250929 --system-prompt "ClaudeBot_System_Prompt.md"
"""

import json
import csv
import os
import sys
import argparse
from typing import List, Optional
from pathlib import Path

# Import SDKs
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAIClient = None

# Configuration
INPUT_PROMPTS_FILE = "input-prompts.csv"
BOT_RESPONSES_DIR = "bot_responses"


def load_prompts() -> List[str]:
    """Load user prompts from CSV"""
    prompts = []
    with open(INPUT_PROMPTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append(row['userQuery'])
    return prompts


def load_system_prompt(filepath: Optional[str]) -> Optional[str]:
    """Load system prompt from file if provided"""
    if not filepath:
        return None

    if not os.path.exists(filepath):
        print(f"Warning: System prompt file not found: {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def get_response_anthropic(
    client: Anthropic,
    model: str,
    query: str,
    system_prompt: Optional[str]
) -> str:
    """Get response from Anthropic API"""
    try:
        kwargs = {
            "model": model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": query}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        message = client.messages.create(**kwargs)
        return message.content[0].text

    except Exception as e:
        print(f"Error getting Anthropic response: {e}")
        return f"[ERROR: {str(e)}]"


def get_response_azure_openai(
    client: OpenAIClient,
    deployment: str,
    query: str,
    system_prompt: Optional[str]
) -> str:
    """Get response from Azure OpenAI"""
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=2000,
            temperature=1.0
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error getting Azure OpenAI response: {e}")
        return f"[ERROR: {str(e)}]"


def save_responses(bot_name: str, responses: List[dict]):
    """Save responses to JSONL file"""
    # Create bot_responses directory if it doesn't exist
    Path(BOT_RESPONSES_DIR).mkdir(exist_ok=True)

    output_file = f"{BOT_RESPONSES_DIR}/Output - {bot_name} Responses.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        for response_data in responses:
            f.write(json.dumps(response_data, ensure_ascii=False) + '\n')

    print(f"\n✓ Saved {len(responses)} responses to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Gather LLM responses for evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Anthropic direct
  python gather_responses.py ActualClaude --provider anthropic --model claude-sonnet-4-5-20250929

  # Azure OpenAI with system prompt
  python gather_responses.py KimiBotTuned --provider azure-openai --model kimi-2-5 --system-prompt ClaudeBot_System_Prompt.md

  # OpenAI direct
  python gather_responses.py GPTBot --provider openai --model gpt-4 --system-prompt ClaudeBot_System_Prompt.md
        """
    )

    parser.add_argument('bot_name', help='Name of the bot (e.g., ActualClaude, KimiBotTuned)')
    parser.add_argument('--provider', required=True, choices=['anthropic', 'azure-openai', 'openai'],
                       help='LLM provider')
    parser.add_argument('--model', required=True,
                       help='Model name or deployment name')
    parser.add_argument('--system-prompt', '--system', '-s',
                       help='Path to system prompt file (optional)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing file (skip already generated responses)')

    args = parser.parse_args()

    # Validate provider availability
    if args.provider == 'anthropic' and not ANTHROPIC_AVAILABLE:
        print("Error: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    if args.provider in ['azure-openai', 'openai'] and not OPENAI_AVAILABLE:
        print("Error: openai package not installed. Run: pip install openai")
        sys.exit(1)

    # Setup provider clients
    client = None
    if args.provider == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set")
            sys.exit(1)
        client = Anthropic(api_key=api_key)

    elif args.provider == 'azure-openai':
        endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
        api_key = os.environ.get('AZURE_OPENAI_API_KEY')
        if not endpoint or not api_key:
            print("Error: AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set")
            sys.exit(1)
        client = OpenAIClient(
            base_url=endpoint,
            api_key=api_key,
        )

    elif args.provider == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            sys.exit(1)
        client = OpenAIClient(api_key=api_key)

    # Load system prompt if provided
    system_prompt = load_system_prompt(args.system_prompt)
    if args.system_prompt:
        if system_prompt:
            print(f"✓ Loaded system prompt from: {args.system_prompt}")
            print(f"  ({len(system_prompt)} characters)")
        else:
            print(f"⚠ Could not load system prompt, continuing without it")

    # Load prompts
    print(f"\nLoading queries from: {INPUT_PROMPTS_FILE}")
    prompts = load_prompts()
    print(f"✓ Loaded {len(prompts)} queries")

    # Check for existing responses to resume
    output_file = f"{BOT_RESPONSES_DIR}/Output - {args.bot_name} Responses.jsonl"
    existing_responses = []
    start_index = 0

    if args.resume and os.path.exists(output_file):
        print(f"\n⚠ Resume mode: Loading existing responses from {output_file}")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                existing_responses.append(json.loads(line))
        start_index = len(existing_responses)
        print(f"✓ Found {start_index} existing responses, will resume from query {start_index + 1}")

    # Generate responses
    print(f"\n{'=' * 80}")
    print(f"Generating responses for: {args.bot_name}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"{'=' * 80}\n")

    all_responses = existing_responses.copy()

    for i in range(start_index, len(prompts)):
        query = prompts[i]
        print(f"[{i+1}/{len(prompts)}] {query[:60]}...")

        # Get response based on provider
        if args.provider == 'anthropic':
            response_text = get_response_anthropic(client, args.model, query, system_prompt)
        elif args.provider == 'azure-openai':
            response_text = get_response_azure_openai(client, args.model, query, system_prompt)
        elif args.provider == 'openai':
            response_text = get_response_azure_openai(client, args.model, query, system_prompt)  # Same API

        # Create response entry
        response_entry = {
            "query": query,
            "response": response_text
        }

        all_responses.append(response_entry)

        # Save incrementally (in case of interruption)
        if (i + 1) % 10 == 0 or (i + 1) == len(prompts):
            save_responses(args.bot_name, all_responses)

    print("\n" + "=" * 80)
    print(f"✓ Complete! Generated {len(all_responses)} total responses")
    print("=" * 80)
    print(f"\nOutput file: {output_file}")
    print(f"\nNext steps:")
    print(f"  1. Review the responses")
    print(f"  2. Run evaluation: python evaluate_single_bot_aoai_robust.py {args.bot_name}")
    print(f"  3. Merge results: python merge_results.py")


if __name__ == "__main__":
    main()
