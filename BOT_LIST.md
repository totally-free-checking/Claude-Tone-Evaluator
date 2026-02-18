# Bot List - All Available Models

## Overview

This evaluation system supports 7 different bots across 4 model families:

| Bot Name | Model | System Prompt | Purpose |
|----------|-------|---------------|---------|
| **ActualClaude** | Claude Sonnet 4.5 | Default | Baseline - Claude's natural behavior |
| **ActualClaudeTuned** | Claude Sonnet 4.5 | Custom tuned | Claude with teen support system prompt |
| **ClaudeBot** | GPT-5.2 | Old version | GPT trying to mimic Claude (v1) |
| **ClaudeBot-v2** | GPT-5.2 | Updated prompt | GPT with improved system prompt |
| **GPTBot** | GPT-5.2 | Default | GPT-5.2 baseline |
| **KimiBotRaw** | Kimi-2.5 | No system prompt | Kimi's natural behavior |
| **KimiBotTuned** | Kimi-2.5 | Custom tuned | Kimi with teen support system prompt |

## Expected File Names

Response files should be in JSONL format in the `bot_responses/` directory:
```
bot_responses/Output - [BotName] Responses.jsonl
```

**Required files:**
- `bot_responses/Output - ActualClaude Responses.jsonl`
- `bot_responses/Output - ActualClaudeTuned Responses.jsonl`
- `bot_responses/Output - ClaudeBot Responses.jsonl`
- `bot_responses/Output - ClaudeBot-v2 Responses.jsonl`
- `bot_responses/Output - GPTBot Responses.jsonl`
- `bot_responses/Output - KimiBotRaw Responses.jsonl`
- `bot_responses/Output - KimiBotTuned Responses.jsonl`

**Note:** The evaluation scripts now accept ANY bot name - not just the ones listed above. As long as the response file exists in `bot_responses/`, you can evaluate it.

## Bot Purposes

### Baseline Bots (Natural Behavior)
1. **ActualClaude** - The gold standard. Claude's natural response style.
2. **GPTBot** - GPT-5.2's natural style for comparison.
3. **KimiBotRaw** - Kimi's natural style without tuning.

### Tuned Bots (With System Prompts)
4. **ActualClaudeTuned** - Claude with explicit teen support instructions.
5. **ClaudeBot** - GPT-5.2's first attempt at matching Claude.
6. **ClaudeBot-v2** - GPT-5.2 with improved prompt incorporating evaluation feedback.
7. **KimiBotTuned** - Kimi with teen support system prompt.

## Comparison Strategy

### Primary Comparisons:
1. **Baseline vs Tuned (Same Model)**
   - ActualClaude vs ActualClaudeTuned
   - KimiBotRaw vs KimiBotTuned
   - Shows impact of system prompt

2. **Cross-Model Comparison**
   - ActualClaude vs ClaudeBot-v2 vs KimiBotTuned
   - All tuned to match Claude's style
   - Shows which model mimics Claude best

3. **Version Comparison (Prompt Iteration)**
   - ClaudeBot vs ClaudeBot-v2
   - Shows improvement from prompt refinement

## Running Evaluations

### Evaluate All Bots:
```bash
python evaluate_single_bot_aoai_robust.py ActualClaude
python evaluate_single_bot_aoai_robust.py ActualClaudeTuned
python evaluate_single_bot_aoai_robust.py ClaudeBot
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2
python evaluate_single_bot_aoai_robust.py GPTBot
python evaluate_single_bot_aoai_robust.py KimiBotRaw
python evaluate_single_bot_aoai_robust.py KimiBotTuned

python merge_results.py
```

### Evaluate Specific Subset:
```bash
# Just the tuned versions
python evaluate_single_bot_aoai_robust.py ActualClaudeTuned
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2
python evaluate_single_bot_aoai_robust.py KimiBotTuned

python merge_results.py
```

## Expected Results Ranking

Based on design goals (from best to worst expected scores):

1. **ActualClaude** / **ActualClaudeTuned** - 8.0-8.5 (baseline)
2. **ClaudeBot-v2** / **KimiBotTuned** - 7.0-7.5 (if prompts work well)
3. **ClaudeBot** - 5.5-6.0 (old prompt, known issues)
4. **KimiBotRaw** - 4.0-5.0 (no tuning)
5. **GPTBot** - 3.5-4.0 (GPT-4, not tuned for this task)

## Key Questions to Answer

1. **Does system prompting help Claude?**
   - Compare ActualClaude vs ActualClaudeTuned
   - Expected: Small difference (Claude is already good)

2. **Can GPT match Claude's style?**
   - Compare ActualClaude vs ClaudeBot-v2
   - Gap analysis: Which dimensions are hardest to match?

3. **How does Kimi compare?**
   - Compare KimiBotTuned vs ClaudeBot-v2
   - Which model mimics Claude better with same prompt?

4. **Does prompt iteration help?**
   - Compare ClaudeBot vs ClaudeBot-v2
   - Quantify improvement from prompt refinement

5. **What's the gap from raw to tuned?**
   - Compare KimiBotRaw vs KimiBotTuned
   - Shows maximum impact of system prompt on Kimi
