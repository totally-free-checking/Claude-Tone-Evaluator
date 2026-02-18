# Retry Failed Evaluations - Kimi JSON Error Fix

## Problem
Kimi-2.5 sometimes produces malformed JSON with:
- Unterminated strings
- Missing delimiters
- Null responses
- Invalid JSON syntax

## Solution

### New Script: `evaluate_single_bot_aoai_robust.py`

**Improvements over original:**
1. ✅ **Robust JSON parsing** with multiple fallback strategies
2. ✅ **JSON cleaning** - fixes common formatting issues
3. ✅ **Regex extraction** - extracts scores even from malformed JSON
4. ✅ **Null response handling** - prevents "NoneType" errors
5. ✅ **JSON mode enforcement** - forces API to return valid JSON
6. ✅ **Retry failed mode** - `--retry-failed` flag to only re-run failures

### Helper Script: `find_failed_evals.py`

Shows which evaluations failed and why:
- Lists failed evaluations by bot
- Groups failures by error type
- Shows query indices that failed
- Provides retry commands

## Usage

### Step 1: Find Failed Evaluations

```bash
python find_failed_evals.py
```

**Output example:**
```
Total evaluations: 100
Failed evaluations: 18
Success rate: 82.0%

FAILED EVALUATIONS BY BOT
================================================================================

ClaudeBot-v2: 18 failures
--------------------------------------------------------------------------------
  Unterminated string starting at: line 21 column 5 (char 1214)
  Queries: 007, 021, 031, 054, 073

  argument of type 'NoneType' is not iterable
  Queries: 004, 008, 013, 020, 030, 039, 043, 056, 068, 077

  Expecting ',' delimiter: line 8 column 27 (char 186)
  Queries: 057, 072, 090

TO RETRY FAILED EVALUATIONS:
================================================================================
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2 --retry-failed
```

### Step 2: Retry Failed Evaluations

```bash
# Retry only the failed ones for specific bot
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2 --retry-failed

# Or retry all bots that have failures
python evaluate_single_bot_aoai_robust.py ActualClaude --retry-failed
python evaluate_single_bot_aoai_robust.py ClaudeBot --retry-failed
python evaluate_single_bot_aoai_robust.py ClaudeBot-v2 --retry-failed
python evaluate_single_bot_aoai_robust.py GPTBot --retry-failed
```

### Step 3: Merge Results

```bash
python merge_results.py
```

This will include all successful evaluations (original + retried).

## How the Robust Parser Works

### 1. Multiple Extraction Strategies
```
1. Try: ```json code blocks
2. Try: Any ``` code blocks
3. Try: First { to last }
4. Fallback: Whole response
```

### 2. JSON Cleaning
- Removes text before/after JSON
- Escapes newlines, tabs, carriage returns
- Handles common formatting issues

### 3. Multiple Parse Attempts
```
1. Direct parse (normal JSON)
2. Clean then parse
3. Regex extraction (fallback)
   - Extracts overall_score
   - Extracts each dimension score
   - Returns partial result with warning
```

### 4. Null Response Handling
- Checks if response is None before processing
- Returns error dict if API returns empty response

## JSON Mode

The robust script uses `response_format={"type": "json_object"}` which:
- Forces the model to return valid JSON
- Should reduce malformed JSON issues
- Works with most Azure OpenAI deployments

**Note:** If your deployment doesn't support JSON mode, remove this line:
```python
response_format={"type": "json_object"}  # Remove if not supported
```

## Expected Results

After retrying failed evaluations:
- ✅ Most failures should succeed on retry
- ✅ Some may still fail (persistent API issues)
- ✅ Regex fallback will extract scores from malformed JSON

**Success rate improvement:**
- Before: ~82% success rate
- After retry: ~95%+ success rate
- With regex fallback: ~100% have scores (may have warnings)

## Checking Results After Retry

Run the find script again to see if any still failed:

```bash
python find_failed_evals.py
```

If some evaluations still show "parse_warning", they were partially parsed via regex. The scores should still be usable, but detailed feedback (strengths/weaknesses) may be incomplete.

## Manual Cleanup (if needed)

If an evaluation persistently fails even after retry, you can manually edit the JSON file:

1. Find the file: `evaluation_results/individual/ClaudeBot-v2_query_007.json`
2. Check the `error` field to see the raw response
3. Fix the JSON manually if needed
4. Re-run merge: `python merge_results.py`
