# Gathering LLM Responses

## Overview

Use `gather_responses.py` to generate response files for evaluation. This script:
- Reads queries from `input-prompts.csv`
- Sends them to your chosen LLM
- Saves responses in the correct JSONL format
- Supports multiple providers (Anthropic, Azure OpenAI, OpenAI)
- Can use custom system prompts

## Setup

### Install Dependencies
```bash
pip install anthropic openai
```

### Set API Keys

**For Anthropic:**
```powershell
$env:ANTHROPIC_API_KEY='your-api-key'
```

**For Azure OpenAI:**
```powershell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key'
```

**For OpenAI:**
```powershell
$env:OPENAI_API_KEY='your-api-key'
```

## Usage

### Basic Syntax
```bash
python gather_responses.py <bot_name> --provider <provider> --model <model> [--system-prompt <file>]
```

### Examples

#### 1. ActualClaude (Anthropic Direct, No System Prompt)
```bash
python gather_responses.py ActualClaude --provider anthropic --model claude-sonnet-4-5-20250929
```

#### 2. ActualClaudeTuned (Anthropic with System Prompt)
```bash
python gather_responses.py ActualClaudeTuned \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"
```

#### 3. KimiBotRaw (Azure OpenAI, No System Prompt)
```bash
python gather_responses.py KimiBotRaw \
  --provider azure-openai \
  --model kimi-2-5
```

#### 4. KimiBotTuned (Azure OpenAI with System Prompt)
```bash
python gather_responses.py KimiBotTuned \
  --provider azure-openai \
  --model kimi-2-5 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"
```

#### 5. GPTBot (OpenAI Direct)
```bash
python gather_responses.py GPTBot \
  --provider openai \
  --model gpt-4
```

#### 6. ClaudeBot-v2 (GPT-5.2 via Azure with System Prompt)
```bash
python gather_responses.py ClaudeBot-v2 \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"
```

## Resume Mode

If the script is interrupted, use `--resume` to continue:

```bash
python gather_responses.py KimiBotTuned \
  --provider azure-openai \
  --model kimi-2-5 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt" \
  --resume
```

This will:
- Load existing responses from the output file
- Skip already generated responses
- Continue from where it left off

## Output Format

Responses are saved to: `bot_responses/Output - [BotName] Responses.jsonl`

The script automatically creates the `bot_responses/` directory if it doesn't exist.

Each line contains:
```json
{
  "query": "User's question here",
  "response": "LLM's response here"
}
```

## Generating All 7 Bots

### Baseline Bots (No System Prompt)
```bash
# ActualClaude - Claude Sonnet baseline
python gather_responses.py ActualClaude \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929

# GPTBot - GPT-5.2 baseline
python gather_responses.py GPTBot \
  --provider azure-openai \
  --model gpt-5-2

# KimiBotRaw - Kimi-2.5 baseline
python gather_responses.py KimiBotRaw \
  --provider azure-openai \
  --model kimi-2-5
```

### Tuned Bots (With System Prompt)
```bash
# ActualClaudeTuned - Claude with teen support prompt
python gather_responses.py ActualClaudeTuned \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"

# ClaudeBot - GPT-5.2 old version (if you have old prompt)
python gather_responses.py ClaudeBot \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt "bot_system_prompts/ClaudeBot.txt"

# ClaudeBot-v2 - GPT-5.2 new version
python gather_responses.py ClaudeBot-v2 \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"

# KimiBotTuned - Kimi with teen support prompt
python gather_responses.py KimiBotTuned \
  --provider azure-openai \
  --model kimi-2-5 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"
```

## Features

### Incremental Saving
- Saves every 10 responses to prevent data loss
- Safe to interrupt and resume

### Error Handling
- API errors are caught and logged
- Failed responses are marked with `[ERROR: ...]`
- Script continues to next query

### Progress Display
```
[1/100] I just walked into class and realized I'm wearing two differ...
[2/100] My teacher asked for my homework and I fully forgot it exist...
...
✓ Saved 100 responses to: Output - KimiBotTuned Responses.jsonl
```

## Workflow

### Complete End-to-End Workflow

1. **Generate responses:**
   ```bash
   python gather_responses.py KimiBotTuned --provider azure-openai --model kimi-2-5 -s bot_system_prompts/ClaudeBot-v2.txt
   ```

2. **Evaluate:**
   ```bash
   python evaluate_single_bot_aoai_robust.py KimiBotTuned
   ```

3. **Check for failures:**
   ```bash
   python find_failed_evals.py
   ```

4. **Retry failed:**
   ```bash
   python evaluate_single_bot_aoai_robust.py KimiBotTuned --retry-failed
   ```

5. **Merge results:**
   ```bash
   python merge_results.py
   ```

6. **Review:**
   - Open `evaluation_results/scores_summary.csv`
   - Read `evaluation_results/summary_report.txt`

## Tips

### Testing with Small Subset
To test with just a few queries first, temporarily edit `input-prompts.csv` to only include 5-10 rows, then restore it for the full run.

### Cost Estimation
- 100 queries × ~100 tokens per query = ~10K input tokens
- 100 queries × ~300 tokens per response = ~30K output tokens
- Total: ~40K tokens per bot

Check your provider's pricing for cost estimates.

### System Prompt Tips
- Keep system prompts focused and clear
- Test on a few queries before running all 100
- The same system prompt can be used across different models
- Store different prompt versions if iterating

## Troubleshooting

### "Module not found: anthropic"
```bash
pip install anthropic
```

### "Module not found: openai"
```bash
pip install openai
```

### "API key not set"
Check your environment variables are set correctly for your chosen provider.

### "Rate limit exceeded"
Add a delay between requests if needed (modify the script to add `time.sleep(1)` in the loop).

### Output file already exists
- Delete the old file to regenerate from scratch
- Or use `--resume` to continue from where you left off
