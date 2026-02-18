# Evaluation Without Ground Truth

You can evaluate responses with or without ground truth. For example, to compare a Kimi response to a Claude response, you can provide the Claude response as ground truth. This uses the evaluation rubric specified in the Evaluator prompt (`Teen Support Bot Tone Evaluator.md`), and also compares to ground truth.

Alternatively, you can rely on the evaluation rubric specified in the Evaluator prompt(`Teen Support Bot Tone Evaluator - No Ground Truth.md`)

Because we are evaluating _tone_, I am more interested in the evaluation rubric, rather than similarity to a single answer. For this reason, I prefer Without Ground Truth (Option 2). Because my focus was on GPT-5.x and Claude, I selected a third and slightly cheaper model (Kimi-K2.5) to prevent bias and reduce cost.

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

### Option 2: Without Ground Truth
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