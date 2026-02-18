# Flexible Bot Names - No More Hardcoded Lists!

## What Changed

### Before (Hardcoded)
- Bot names were hardcoded in a `BOT_FILES` dictionary
- Only predefined bots could be evaluated
- Had to edit code to add new bots

### After (Flexible)
- ✅ **Any bot name works** - no code changes needed
- ✅ **Files in dedicated folder** - `bot_responses/` directory
- ✅ **Dynamic file path construction** - based on bot name
- ✅ **Automatic directory creation** - `gather_responses.py` creates folder

## New File Structure

```
claude-tone-evaluator/
├── bot_responses/                          # NEW: All response files here
│   ├── Output - ActualClaude Responses.jsonl
│   ├── Output - KimiBotTuned Responses.jsonl
│   ├── Output - YourCustomBot Responses.jsonl  # Any name works!
│   └── ...
├── evaluation_results/                     # Evaluation outputs (with GT)
├── evaluation_results_no_gt/              # Evaluation outputs (no GT)
└── ...
```

## Using Any Bot Name

### 1. Generate Responses
```bash
# Works with ANY bot name
python gather_responses.py MyCustomBot \
  --provider azure-openai \
  --model my-model \
  --system-prompt my_prompt.md
```

**Output:** `bot_responses/Output - MyCustomBot Responses.jsonl`

### 2. Evaluate
```bash
# Evaluate ANY bot (as long as file exists)
python evaluate_single_bot_aoai_robust.py MyCustomBot

# Or without ground truth
python evaluate_single_bot_no_gt.py MyCustomBot
```

### 3. Merge Results
```bash
python merge_results.py
```

## Examples

### Custom Model Testing
```bash
# Test GPT-4o-mini
python gather_responses.py GPT4oMini \
  --provider openai \
  --model gpt-4o-mini

python evaluate_single_bot_aoai_robust.py GPT4oMini
```

### Different System Prompts
```bash
# Version 1
python gather_responses.py ClaudeBot-v1 \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt version1.md

# Version 2
python gather_responses.py ClaudeBot-v2 \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt version2.md

# Version 3
python gather_responses.py ClaudeBot-v3 \
  --provider azure-openai \
  --model gpt-5-2 \
  --system-prompt version3.md

# Evaluate all versions
python evaluate_single_bot_aoai_robust.py ClaudeBot-v1
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2
python evaluate_single_bot_aoai_robust.py ClaudeBot-v3

python merge_results.py
```

### Temperature Experiments
```bash
# Low temperature
python gather_responses.py KimiTemp0 \
  --provider azure-openai \
  --model kimi-2-5
  # (Edit script to set temperature=0)

# High temperature
python gather_responses.py KimiTemp1 \
  --provider azure-openai \
  --model kimi-2-5
  # (Edit script to set temperature=1)

# Compare
python merge_results.py
```

## File Naming Convention

**Format:** `bot_responses/Output - [BotName] Responses.jsonl`

**Bot Name Rules:**
- ✅ Use any alphanumeric characters
- ✅ Hyphens and underscores are fine
- ✅ Spaces in bot name work (but not recommended)
- ✅ CamelCase recommended for readability

**Examples:**
- `ActualClaude` → `bot_responses/Output - ActualClaude Responses.jsonl`
- `GPT-4-Turbo` → `bot_responses/Output - GPT-4-Turbo Responses.jsonl`
- `Kimi_Custom_v2` → `bot_responses/Output - Kimi_Custom_v2 Responses.jsonl`

## Migration from Old Structure

If you have old files in the root directory:

```bash
# Create bot_responses folder
mkdir bot_responses

# Move all response files
mv "Output - "*.jsonl bot_responses/

# Or on Windows PowerShell:
New-Item -ItemType Directory -Path bot_responses -Force
Move-Item -Path "Output - *.jsonl" -Destination bot_responses/
```

## Benefits

1. **Experimentation-Friendly**
   - Test multiple prompt variations
   - Try different models easily
   - A/B test different approaches

2. **No Code Changes**
   - Add new bots without editing scripts
   - No need to update hardcoded lists
   - Less maintenance

3. **Organization**
   - All response files in one place
   - Easy to clean up old experiments
   - Clear separation from evaluation results

4. **Scalability**
   - Evaluate 7 bots or 70 bots
   - No performance impact
   - Same workflow regardless of number

## Error Handling

**If you get "Response file not found":**
```
Error: Response file not found: bot_responses/Output - MyBot Responses.jsonl

Make sure the file exists in the bot_responses/ directory
Expected file: bot_responses/Output - MyBot Responses.jsonl
```

**Solution:**
1. Check file exists: `ls bot_responses/`
2. Check exact name matches (case-sensitive)
3. Generate if missing: `python gather_responses.py MyBot ...`

## Updated Scripts

All scripts now support flexible bot names:
- ✅ `gather_responses.py` - saves to `bot_responses/`
- ✅ `evaluate_single_bot_aoai_robust.py` - reads from `bot_responses/`
- ✅ `evaluate_single_bot_no_gt.py` - reads from `bot_responses/`
- ✅ `merge_results.py` - works with any bots evaluated

## Backward Compatibility

The hardcoded bot list is removed, but common bot names still work:
- ActualClaude
- ActualClaudeTuned
- ClaudeBot
- ClaudeBot-v2
- GPTBot
- KimiBotRaw
- KimiBotTuned

These are just conventions - you can use any name you want!
