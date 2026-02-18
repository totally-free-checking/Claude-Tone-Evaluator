# Claude Tone Evaluator

Evaluates LLM responses against Claude's teen support bot character for tone and style matching. Supports flexible bot names, multiple evaluation modes, and robust error handling.

## Overview

This system helps you:
1. **Generate responses** from any LLM (Claude, GPT, Kimi, etc.)
2. **Analyze repetitiveness** to detect formulaic patterns
3. **Evaluate tone/style** against Claude's character with or without ground truth
4. **Track failures** and retry them automatically
5. **Compare results** across multiple bots and system prompts

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Keys

**For Azure OpenAI (Kimi, GPT-5.2):**
```powershell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key'
$env:AZURE_OPENAI_DEPLOYMENT='Kimi-K2.5'  # Default deployment name, used for evaluating responses
```

**For Anthropic (Claude):**
```powershell
$env:ANTHROPIC_API_KEY='your-api-key'
```

**For OpenAI:**
```powershell
$env:OPENAI_API_KEY='your-api-key'
```

### 3. Generate Responses

```bash
# Generate responses from any bot
python gather_responses.py MyBotName \
  --provider azure-openai \
  --model kimi-2-5 \ # The model to generate responses
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"
```

This creates: `bot_responses/Output - MyBotName Responses.jsonl`

### 4. Analyze Repetitiveness (Optional)

```bash
# Check for formulaic patterns
python analyze_repetitiveness.py MyBotName
```

### 5. Evaluate Responses

```bash
# With ground truth comparison (compares to ActualClaude)
python evaluate_single_bot_aoai_robust.py MyBotName

# Without ground truth (rubric-only evaluation)
python evaluate_single_bot_no_gt.py MyBotName
```

### 6. Check for Failures

```bash
# See which evaluations failed
python find_failed_evals.py
```

### 7. Retry Failed Evaluations

```bash
# Retry only the failed ones
python evaluate_single_bot_aoai_robust.py MyBotName --retry-failed
```

### 8. Merge Results

```bash
# Generate CSV and summary report
python merge_results.py

# For no-GT evaluations
python merge_results.py --no-gt
```

## Supported Bots

The system supports **ANY bot name** - just create response files with this format:
```
bot_responses/Output - [BotName] Responses.jsonl
```

**Example bots (7 currently tracked):**
- **ActualClaude** - Claude Sonnet 4.5 baseline
- **ActualClaudeTuned** - Claude with teen support prompt
- **ClaudeBot** - GPT-5.2 old version
- **ClaudeBot-v2** - GPT-5.2 improved version
- **GPTBot** - GPT-5.2 baseline
- **KimiBotRaw** - Kimi-2.5 baseline
- **KimiBotTuned** - Kimi-2.5 with teen support prompt

See [BOT_LIST.md](BOT_LIST.md) for details.

## Key Features

### 🔄 Flexible Bot Names
- No hardcoded bot lists - use any name you want
- Automatically finds response files in `bot_responses/` directory
- See [FLEXIBLE_BOT_NAMES.md](FLEXIBLE_BOT_NAMES.md)

### 🎯 Dual Evaluation Modes
- **With Ground Truth**: Compare responses to ActualClaude
- **Without Ground Truth**: Evaluate against character rubric alone
- See [NO_GROUND_TRUTH_GUIDE.md](NO_GROUND_TRUTH_GUIDE.md)

### 🛡️ Robust Error Handling
- Multiple JSON parsing strategies
- Automatic retry of failed evaluations
- Incremental evaluation (skips already-done)
- See [RETRY_FAILED.md](RETRY_FAILED.md)

### 🔍 Repetitiveness Detection
- Measures response diversity
- Detects formulaic patterns
- Scores 0-10 with recommendations
- See [REPETITIVENESS_ANALYSIS.md](REPETITIVENESS_ANALYSIS.md)

### 🤖 Multi-Provider Support
- Anthropic (Claude)
- Azure OpenAI (Kimi, GPT-5.2)
- OpenAI (GPT-4, etc.)
- See [GATHER_RESPONSES.md](GATHER_RESPONSES.md)

## Evaluation Dimensions

Responses are scored across 8 dimensions:

1. **Warmth & Emotional Validation** - Empathy and emotional acknowledgment
2. **Prose vs. Bullets** - Natural prose flow vs. over-structured lists
3. **Emoji Usage** - Appropriate emoji use (0-1 per response, prefer none)
4. **Conversational Tone** - Casual, natural language with first-person ("I think", "I'd say")
5. **Practical Advice** - Concrete, actionable suggestions
6. **Follow-up Question** - Engaging questions to continue conversation
7. **Support/Solutions Balance** - Mix of emotional support and practical help
8. **Length & Conciseness** - Appropriate response length

Each dimension is scored 0-10, with an overall average score.

## File Structure

```
claude-tone-evaluator/
├── bot_responses/                          # Response files (JSONL)
│   ├── Output - ActualClaude Responses.jsonl
│   ├── Output - KimiBotTuned Responses.jsonl
│   └── ...
├── evaluation_results/                     # With-GT evaluations
│   ├── individual/                         # Individual JSON results
│   ├── scores_summary.csv                 # Tabular scores
│   └── summary_report.txt                 # Human-readable report
├── evaluation_results_no_gt/              # No-GT evaluations
│   └── individual/
├── input-prompts.csv                      # 100 test queries
├── gather_responses.py                    # Generate responses
├── analyze_repetitiveness.py              # Check for patterns
├── evaluate_single_bot_aoai_robust.py     # Evaluate with GT
├── evaluate_single_bot_no_gt.py           # Evaluate without GT
├── find_failed_evals.py                   # Find failures
├── merge_results.py                       # Generate reports
└── README.md                              # This file
```

## Scripts Overview

### Core Scripts

**gather_responses.py** - Generate response files
- Supports Anthropic, Azure OpenAI, OpenAI providers
- Optional system prompts
- Incremental saving with resume support
- See [GATHER_RESPONSES.md](GATHER_RESPONSES.md)

**evaluate_single_bot_aoai_robust.py** - Evaluate with ground truth
- Compares each response to ActualClaude
- Robust JSON parsing with multiple fallbacks
- Incremental evaluation (skip already-done)
- `--retry-failed` flag to retry failures only
- Uses Kimi-2.5 (or specified Azure OpenAI deployment)
- See [RUN_EVALUATIONS.md](RUN_EVALUATIONS.md)

**evaluate_single_bot_no_gt.py** - Evaluate without ground truth
- Evaluates against character rubric alone
- No comparison to reference response
- Same robust parsing and retry features
- See [NO_GROUND_TRUTH_GUIDE.md](NO_GROUND_TRUTH_GUIDE.md)

**analyze_repetitiveness.py** - Detect formulaic patterns
- Measures response diversity
- Finds repeated phrases
- Scores 0-10 with recommendations
- Free (no API calls)
- See [REPETITIVENESS_ANALYSIS.md](REPETITIVENESS_ANALYSIS.md)

**find_failed_evals.py** - Find failed evaluations
- Checks both with-GT and no-GT results
- Groups failures by bot and reason
- Detects missing evaluation files
- Provides retry commands

**merge_results.py** - Generate summary reports
- Combines individual JSONs into CSV
- Creates human-readable summary report
- Use `--no-gt` flag for no-GT results

## Complete Workflow Example

```bash
# 1. Generate responses
python gather_responses.py KimiBotTuned \
  --provider azure-openai \
  --model kimi-2-5 \
  --system-prompt "bot_system_prompts/ClaudeBot-v2.txt"

# 2. Check repetitiveness
python analyze_repetitiveness.py KimiBotTuned

# 3. Evaluate (with ground truth)
python evaluate_single_bot_aoai_robust.py KimiBotTuned

# 4. Check for failures
python find_failed_evals.py

# 5. Retry failures
python evaluate_single_bot_aoai_robust.py KimiBotTuned --retry-failed

# 6. Generate report
python merge_results.py

# 7. Review results
# - evaluation_results/scores_summary.csv
# - evaluation_results/summary_report.txt
```

## Comparing Multiple Bots

```bash
# Generate responses for all bots
python gather_responses.py ActualClaude --provider anthropic --model claude-sonnet-4-5-20250929
python gather_responses.py KimiBotTuned --provider azure-openai --model kimi-2-5 -s "bot_system_prompts/ClaudeBot-v2.txt"
python gather_responses.py GPTBot --provider azure-openai --model gpt-5-2

# Analyze repetitiveness for all
python analyze_repetitiveness.py ActualClaude
python analyze_repetitiveness.py KimiBotTuned
python analyze_repetitiveness.py GPTBot

# Evaluate all
python evaluate_single_bot_aoai_robust.py ActualClaude
python evaluate_single_bot_aoai_robust.py KimiBotTuned
python evaluate_single_bot_aoai_robust.py GPTBot

# Merge and compare
python merge_results.py
```

## Cost Estimation

**Per bot (100 queries):**
- Response generation: ~40K tokens (~$0.10-$1.00 depending on model)
- Evaluation: ~200K tokens (~$0.20-$2.00 depending on evaluator)
- Repetitiveness analysis: Free (no API calls)

**For 7 bots:**
- Total: ~1.7M tokens
- Estimated cost: $2-20 depending on models used

## Troubleshooting

### "Response file not found"
- Make sure file exists: `bot_responses/Output - [BotName] Responses.jsonl`
- Generate with: `python gather_responses.py [BotName] ...`

### JSON parsing errors
- The robust evaluator handles most errors automatically
- Use `--retry-failed` to retry
- See [RETRY_FAILED.md](RETRY_FAILED.md) for details

### High repetitiveness score
- Review analyze_repetitiveness.py output
- Update system prompt to encourage variety
- See [REPETITIVENESS_ANALYSIS.md](REPETITIVENESS_ANALYSIS.md)

### Missing evaluations
- Run `python find_failed_evals.py` to detect
- Use `--retry-failed` flag to retry

## Documentation

- [BOT_LIST.md](BOT_LIST.md) - All supported bots
- [FLEXIBLE_BOT_NAMES.md](FLEXIBLE_BOT_NAMES.md) - Using any bot name
- [GATHER_RESPONSES.md](GATHER_RESPONSES.md) - Generating responses
- [RUN_EVALUATIONS.md](RUN_EVALUATIONS.md) - Running evaluations
- [NO_GROUND_TRUTH_GUIDE.md](NO_GROUND_TRUTH_GUIDE.md) - With vs without GT
- [RETRY_FAILED.md](RETRY_FAILED.md) - Handling failures
- [REPETITIVENESS_ANALYSIS.md](REPETITIVENESS_ANALYSIS.md) - Detecting patterns
- [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) - Improving bot performance

## Character Guidelines

The teen support bot character:
- **Validates first**: Always acknowledge feelings before advice
- **Uses prose**: Natural paragraphs, not bullet lists
- **Minimal emojis**: 0-1 per response, prefer none unless they enhance warmth
- **First-person language**: "I think", "I'd say", "I get it"
- **Casual tone**: Contractions, natural phrases, not formal
- **Engaging**: Always ends with specific follow-up question
- **Balanced**: Mix emotional support with practical advice

See [bot_system_prompts/ClaudeBot-v2.txt](ClaudeBot-v2.txt) for complete guidelines.

## Contributing

When adding new bots:
1. Generate responses with `gather_responses.py`
2. Check repetitiveness with `analyze_repetitiveness.py`
3. Evaluate with appropriate script
4. Document in [BOT_LIST.md](BOT_LIST.md) if it's a standard bot

## License

This is an evaluation framework for comparing LLM responses. Use responsibly.
