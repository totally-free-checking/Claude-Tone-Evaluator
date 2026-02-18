# Running Evaluations

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Azure OpenAI Environment Variables
```powershell
# PowerShell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key-here'
$env:AZURE_OPENAI_DEPLOYMENT='kimi-2-5'  # Your deployment name
```

## Required Response Files

Make sure you have these JSONL files in the `bot_responses/` directory:
- ✅ `bot_responses/Output - ClaudeBot Responses.jsonl` (GPT-5.2 old version)
- ✅  `bot_responses/Output - ClaudeBot-v2 Responses.jsonl` (GPT-5.2 new version - needs updated system prompt)
- ✅  `bot_responses/Output - KimiBotRaw Responses.jsonl` (Kimi-2.5 without system prompt)
- ✅  `bot_responses/Output - KimiBotTuned Responses.jsonl` (Kimi-2.5 with tuned system prompt)
etc...


**Flexibility**: You can evaluate ANY bot - just make sure the response file exists in `bot_responses/Output - [YourBotName] Responses.jsonl`. Each item must have a `query` and `response` field.

## Running Evaluations

### Evaluate Multiple Bots

```bash
# Evaluate multiple bots sequentially
python evaluate_single_bot_no_gt.py Bot1
python evaluate_single_bot_no_gt.py Bot2
python evaluate_single_bot_no_gt.py Bot3

# Merge results
python merge_results.py --no-gt
```


###  Re-evaluate Everything (Clean Slate)

If you want to test new responses (e.g., you changed the system prompt), then start with a clean slate:

```bash
# Delete existing evaluations
rm -rf evaluation_results_no_gt/individual/*

# Evaluate all bots
python evaluate_single_bot_no_gt.py Bot1
python evaluate_single_bot_no_gt.py Bot2
python evaluate_single_bot_no_gt.py Bot3

# Generate reports
python merge_results.py --no-gt
```

## Script Features

- **Incremental evaluation**: Skips already-evaluated responses
- **Error handling**: Continues on API errors, saves error in result
- **Progress tracking**: Shows which query is being evaluated
- **Safe**: Won't re-evaluate unless you delete the individual JSON files

## Output

After running evaluations and merge:
- `evaluation_results_no_gt/individual/` - 700 individual JSON files (100 per bot × 7 bots)
- `evaluation_results_no_gt/scores_summary.csv` - All scores in tabular format
- `evaluation_results_no_gt/summary_report.txt` - Human-readable comparison report

## Expected Results

After running all evaluations, the summary report will show:

```
OVERALL SCORES COMPARISON
--------------------------------------------------------------------------------

ActualClaude          8.XX/10  ████████░░  (Claude Sonnet baseline)
ActualClaudeTuned     8.XX/10  ████████░░  (Claude Sonnet tuned)
ClaudeBot-v2          7.XX/10  ███████░░░  (GPT-5.2 improved)
KimiBotTuned          7.XX/10  ███████░░░  (Kimi-2.5 tuned)
ClaudeBot             5.61/10  █████░░░░░  (GPT-5.2 old)
KimiBotRaw            X.XX/10  ████░░░░░░  (Kimi-2.5 raw)
GPTBot                3.74/10  ███░░░░░░░  (GPT-4)
```

## Troubleshooting

### Error: Response file not found
- Make sure the bot response files exist in `bot_responses/` directory (e.g., `Output - [BotName] Responses.jsonl`)
- File format: `bot_responses/Output - [BotName] Responses.jsonl`
- Generate missing files using `gather_responses.py`

### Error: Azure OpenAI credentials not set
- Verify environment variables are set correctly
- Check your Azure OpenAI endpoint URL format
- Ensure deployment name matches your Azure resource

### API Errors (500, rate limits)
- The script will log errors and continue
- Failed evaluations will have `overall_score: 0` and an `error` field
- You can re-run to retry failed ones (they'll be skipped if already completed)

## Cost Estimation

Using Kimi-2.5 on Azure OpenAI:
- ~700 evaluations (100 per bot × 7 bots)
- ~2000 tokens per evaluation (input + output)
- Total: ~1.4M tokens

Check Azure OpenAI pricing for Kimi-2.5 in your region.
