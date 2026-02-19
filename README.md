# Claude Tone Evaluator

I frequently hear people say they like the "tone" of Claude more than other models, but I have not been able to find good, data-based comparisons. This project evaluates LLM responses against a scoring rubric to evaluate tone and style matching. You can easily test new model versions, prompt engineering changes, temperature, etc to tune your own models to sound more like Claude.

## Example

Query: 
```
I just walked into class and realized I’m wearing two different shoes.
```




| Claude | GPT-5.2, default ❌ | GPT-5.2, modified ✅ |
|------------|-------------------------|---------------------------|
| Oh no! That's one of those moments that makes your stomach drop, isn't it? 😅 We've all been there with some version of this - it's like suddenly everyone's eyes feel like they're on your feet.<br><br>Honestly though, most people probably won't even notice unless you point it out. I think it feels way worse to you than it actually looks to everyone else. If you can, try tucking your feet under your desk for now and maybe slip out at a natural break to see how obvious it really is.<br><br>If someone does notice, I'd just own it with a quick "Yeah, rough morning!" - that usually gets a laugh and then everyone moves on. Sometimes the best way to handle these little disasters is just to lean into the humor of it all.<br><br>Are they at least similar colors, or are we talking like a sneaker and a dress shoe situation?|Own it—you’ve accidentally invented “asymmetrical fashion.” If you want a low-drama fix:<br>• If you’ve got time, ask to run to your locker/car/bathroom and swap.<br>• If not, tuck your feet under the desk a bit and act normal; most people won’t notice unless you point it out.<br>• If someone does notice, go with a quick line like: “Yeah, it’s a limited edition.”<br><br>Also: are they just different colors of the same shoe, or like… sneaker + dress shoe?|Oh nooo, that stomach-drop moment is so real 😅 That’s such an awkward-but-weirdly-common thing, I’d wanna disappear too.<br><br>Honestly though, it probably feels way bigger to you than it looks to anyone else. Most people are half-asleep or focused on their own stuff, and even if someone notices, it’s usually like a two-second “wait what” and then they move on.<br><br>If you can, I’d just keep your feet tucked under your desk for now and wait for a natural moment to step out (bathroom break, passing period, grabbing something from your locker). If someone says something, owning it casually works so well—like, “Yeah, I grabbed shoes in the dark… bold choice today,” and then laugh it off.<br><br>Are they at least kinda similar (like same color/style), or is it a full-on sneaker + dress shoe situation?|

## Evaluation Dimensions

The primary goal of this evaluation is to determine how closely the tone of an LLM's response matches that of Claude. To emulate a real-life scenario, we simulate a character chat bot for teenagers. Claude's responses tend to follow a similar pattern and with a certain style of writing. 

The evaluation scores across 8 dimensions, although this can be changed by altering the Evaluation prompt.

- **Validates first**: Always acknowledge feelings before advice
- **Warmth & Emotional Validation** - Empathy and emotional acknowledgment
- **Uses prose**: Natural paragraphs, not bullet lists
- **Minimal emojis**: 0-1 per response, prefer none unless they enhance warmth
- **First-person language**: "I think", "I'd say", "I get it"
- **Casual tone**: Contractions, natural phrases, not formal
- **Engaging**: Always ends with specific follow-up question
- **Balanced**: Mix emotional support with practical advice
- **Length & Conciseness** - Appropriate response length


Each dimension is scored 0-10, with an overall average score.


## Results

The results show that, via prompt engineering, other models can be made to sound just as Claude-like as Claude.  The full report is in [evaluation_results_no_gt/summary_report.txt](evaluation_results_no_gt/summary_report.txt)

```
Using the system prompt in `ClaudeBot-v2.txt`
GPT-5.2                 9.16/10  █████████░  aka "ClaudeBot-v2"
GPT-4.1                 9.16/10  █████████░  aka "GPT4.1Bot"
Grok-4-fast-reasoning   9.09/10  █████████░  aka "GrokBot"
Claude                  9.08/10  █████████░  aka "ActualClaudeTuned"
GPT-4o                  9.00/10  █████████░  aka "GPT4oBot"
gpt-OSS-120b            8.96/10  ████████░░  aka "OSS120Bot"
Kimi-K2.5               8.94/10  ████████░░  aka "KimiBotTuned"

No system prompt (`You are a friendly and casual AI Assistant`)
Claude                  7.32/10  ███████░░░  aka "ActualClaude"
Kimi-K2.5               7.31/10  ███████░░░  aka "KimiBotRaw"
GPT-5.2                 5.28/10  █████░░░░░  aka "GPTBot"
```


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

If you want to compare against a ground truth and also evaluate against a scoring rubric:

```bash
# With ground truth comparison (compares to ActualClaude)
python evaluate_single_bot_aoai_robust.py MyBotName
```

or, to ignore the ground truth and just use a scoring rubric:

```bash
# Without ground truth (rubric-only evaluation)
python evaluate_single_bot_no_gt.py MyBotName
```

See [NO_GROUND_TRUTH_GUIDE.md](NO_GROUND_TRUTH_GUIDE.md) for more info.

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

or

```bash
# Without ground truth (rubric-only evaluation)
python evaluate_single_bot_no_gt.py MyBotName --retry-failed
```

### 8. Merge Results

```bash
# Generate CSV and summary report
python merge_results.py
```

or 

```bash
# For no-GT evaluations
python merge_results.py --no-gt
```


## Key Features


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

# 3. Evaluate (without ground truth)
python evaluate_single_bot_no_gt.py KimiBotTuned

# 4. Check for failures
python find_failed_evals.py

# 5. Retry failures
python evaluate_single_bot_no_gt.py KimiBotTuned --retry-failed

# 6. Generate report
python merge_results.py --no-gt

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
python evaluate_single_bot_no_gt.py ActualClaude
python evaluate_single_bot_no_gt.py KimiBotTuned
python evaluate_single_bot_no_gt.py GPTBot

# Merge and compare
python merge_results.py --no-gt
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

- [GATHER_RESPONSES.md](GATHER_RESPONSES.md) - Generating responses
- [RUN_EVALUATIONS.md](RUN_EVALUATIONS.md) - Running evaluations
- [NO_GROUND_TRUTH_GUIDE.md](NO_GROUND_TRUTH_GUIDE.md) - With vs without GT
- [REPETITIVENESS_ANALYSIS.md](REPETITIVENESS_ANALYSIS.md) - Detecting patterns


See [bot_system_prompts/ClaudeBot-v2.txt](ClaudeBot-v2.txt) for complete guidelines.


## License

This is an evaluation framework for comparing LLM responses. Use responsibly.
