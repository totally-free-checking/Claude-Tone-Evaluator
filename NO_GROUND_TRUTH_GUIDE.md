# Evaluation Without Ground Truth

## Two Evaluation Approaches

### Option 1: With Ground Truth (Original)
**Files:** `evaluate_single_bot_aoai_robust.py` + `Teen Support Bot Tone Evaluator.md`

**How it works:**
- Compares each response to ActualClaude's response for the same query
- Evaluates: "How close is this to Claude's response?"
- Uses Claude's response as the reference standard

**Pros:**
- ✅ See exactly how different bots compare to Claude
- ✅ Useful for calibrating/tuning prompts to match Claude's style
- ✅ Can identify specific divergences from Claude's approach

**Cons:**
- ❌ Assumes Claude's response is always "correct"
- ❌ May penalize valid alternative responses
- ❌ Requires ActualClaude responses for all queries

---

### Option 2: Without Ground Truth (New)
**Files:** `evaluate_single_bot_no_gt.py` + `Teen Support Bot Tone Evaluator - No Ground Truth.md`

**How it works:**
- Evaluates response against the character rubric alone
- Evaluates: "Does this match the ideal teen support bot character?"
- No comparison to any specific reference response

**Pros:**
- ✅ More objective - based on rubric, not comparison
- ✅ Doesn't require ActualClaude responses
- ✅ Can evaluate any response independently
- ✅ Won't penalize creative solutions that differ from Claude

**Cons:**
- ❌ No direct comparison to see "how far from Claude"
- ❌ May score differently than with-GT version

---

## When to Use Which

### Use WITH Ground Truth when:
- You want to see how close ClaudeBot-v2 is to ActualClaude
- You're tuning a system prompt to match Claude's style
- You have ActualClaude responses to compare against
- You want to measure improvement relative to Claude baseline

### Use WITHOUT Ground Truth when:
- You want objective rubric-based evaluation
- You don't have Claude responses for your queries
- You want to evaluate responses independently
- You want to allow for creative differences from Claude

---

## Running Evaluations Without Ground Truth

### Setup (same as before)
```powershell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key'
$env:AZURE_OPENAI_DEPLOYMENT='kimi-2-5'
```

### Evaluate Bots
```bash
# Evaluate all bots without ground truth comparison
python evaluate_single_bot_no_gt.py ActualClaude
python evaluate_single_bot_no_gt.py ClaudeBot
python evaluate_single_bot_no_gt.py ClaudeBot-v2
python evaluate_single_bot_no_gt.py GPTBot

# Retry failed
python evaluate_single_bot_no_gt.py ClaudeBot-v2 --retry-failed
```

### Output Location
Results are saved to separate directory:
- **With GT**: `evaluation_results/individual/`
- **Without GT**: `evaluation_results_no_gt/individual/`

This keeps the two evaluation types separate so you can compare both approaches.

---

## Key Differences in Evaluation

### With Ground Truth Example:
```json
{
  "overall_score": 5.8,
  "weaknesses": [
    "Opens with validation but it's quite muted and clinical compared to
     Claude's warm, immediate empathy ('Oof, that's such a relatable moment! 😅')"
  ],
  "key_differences_from_ground_truth": [
    "Ground truth uses 😅 naturally in opening. Evaluated response has zero emojis"
  ]
}
```

### Without Ground Truth Example:
```json
{
  "overall_score": 6.2,
  "weaknesses": [
    "Opens with validation but it's quite muted and clinical. The ideal would be
     warmer immediate empathy like 'Ugh, I'm so sorry' or 'That's such a tough spot'"
  ],
  "specific_feedback": [
    "Add 1 emoji in opening paragraph to enhance warmth (😅 or 💙)",
    "Use more first-person language: 'I think' instead of 'The best approach would be'"
  ]
}
```

**Notice:** Without GT focuses on the rubric ideal, not comparison to a specific response.

---

## Comparing Both Approaches

You can run both and compare:

```bash
# With ground truth
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2
python merge_results.py  # generates evaluation_results/scores_summary.csv

# Without ground truth
python evaluate_single_bot_no_gt.py ClaudeBot-v2
# Note: Need to update merge_results.py path for no-GT version
```

This lets you see:
- How scores differ between approaches
- Whether GT comparison is too strict or too lenient
- Which approach gives more actionable feedback

---

## Recommendation

**For your use case (improving ClaudeBot to match Claude):**

Start with **WITH Ground Truth** for now:
- You already have ActualClaude responses
- You want to see specific improvements in matching Claude's style
- Direct comparison helps identify what to change in the system prompt

Later, switch to **WITHOUT Ground Truth** when:
- You have new queries without Claude responses
- You want to evaluate in production (no GT available)
- You want pure rubric-based scoring

---

## Next Steps

If you want to use the no-GT approach:

1. **Run evaluations:**
   ```bash
   python evaluate_single_bot_no_gt.py ClaudeBot-v2
   ```

2. **Update merge script** (or I can create a no-GT version)

3. **Compare scores** between with-GT and without-GT approaches

Want me to create a no-GT version of merge_results.py?
