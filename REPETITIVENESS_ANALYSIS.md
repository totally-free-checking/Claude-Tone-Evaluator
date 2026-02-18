# Repetitiveness Analysis

## Problem

Some models become too predictable and formulaic:
- "Ugh, that sucks!" (repeated 30x)
- "Oh no! That's so rough!" (repeated 25x)
- Always starting with the same exclamation
- Using identical sentence structures

While consistency is good, **repetitiveness is bad**. We need variety!

## Solution: analyze_repetitiveness.py

Analyzes response diversity and detects formulaic patterns.

## Usage

```bash
python analyze_repetitiveness.py <bot_name>
```

**Example:**
```bash
python analyze_repetitiveness.py KimiBotTuned
```

## What It Analyzes

### 1. Diversity Metrics
- **Unique first words**: How many different words start responses?
- **Unique first 3 words**: How varied are the openings?
- **Unique first sentences**: Are first sentences diverse?

### 2. Most Common Patterns
- Which words/phrases are overused?
- Which sentence openings repeat?
- Percentage and frequency of each pattern

### 3. Formulaic Patterns
- Starts with exclamation ("Ugh", "Oh no", "Oof")
- Starts with apology ("I'm so sorry")
- "That's [adjective]" pattern
- Emoji placement patterns

### 4. N-gram Analysis
- Finds repeated 3-word phrases across all responses
- Identifies overused expressions

### 5. Repetitiveness Score (0-10)
- **10**: Excellent variety, not formulaic
- **8-9**: Good variety, minor patterns
- **6-7**: Some repetition
- **4-5**: Quite formulaic
- **0-3**: Extremely repetitive

## Example Output

```
================================================================================
REPETITIVENESS ANALYSIS: KimiBotTuned
================================================================================

Total responses: 100

================================================================================
DIVERSITY METRICS
================================================================================

Unique first words: 12/100 (12.0%)
Unique first 3 words: 35/100 (35.0%)
Unique first sentences: 58/100 (58.0%)

--------------------------------------------------------------------------------
MOST COMMON FIRST WORDS
--------------------------------------------------------------------------------
Ugh                   45x (45.0%)  ██████████████████████
I'm                   18x (18.0%)  █████████
Oh                    12x (12.0%)  ██████
That's                 8x ( 8.0%)  ████
Oof                    7x ( 7.0%)  ███

--------------------------------------------------------------------------------
MOST COMMON FIRST 3 WORDS
--------------------------------------------------------------------------------
Ugh, that sucks                    15x (15.0%)  ███████
Ugh, that's so                     12x (12.0%)  ██████
I'm so sorry                       11x (11.0%)  █████
Oh no! That's                       8x ( 8.0%)  ████

================================================================================
FORMULAIC PATTERNS
================================================================================

Starts with exclamation: 67/100 (67.0%)
  - 'Ugh': 45x
  - 'Oh no': 12x
  - 'Oof': 10x
  ⚠️  WARNING: Over 50% of responses start with exclamations

Starts with 'I'm so sorry': 11/100 (11.0%)

Emoji in opening: 78/100 (78.0%)
  - 😅: 65x
  - 💙: 8x
  - 😊: 5x

================================================================================
REPETITIVENESS SCORE
================================================================================

Score: 4.2/10  ████░░░░░░
Grade: Some repetition

⚠️  Moderate repetitiveness. Consider varying openings more.

================================================================================
RECOMMENDATIONS
================================================================================

1. Reduce exclamation openings:
   - Too many responses start with 'Ugh', 'Oh no', etc.
   - Vary with: direct statements, questions, 'I'm so sorry', etc.

2. 'Ugh, that sucks' is overused (15x)
   - Find alternative ways to open responses

3. First sentences are too similar
   - Vary sentence structure and opening phrases
   - Don't always follow the same pattern
```

## Interpreting Results

### Good Signs (High Score)
- ✅ High diversity percentages (>70%)
- ✅ No phrase used more than 20% of the time
- ✅ Wide variety of opening patterns
- ✅ No "WARNING" messages

### Red Flags (Low Score)
- ❌ Low diversity (<40%)
- ❌ One phrase dominates (>30% usage)
- ❌ Warnings about overuse
- ❌ Same exclamation repeated many times

## Fixing Repetitiveness

### System Prompt Adjustments

**Bad (encourages repetition):**
```
Always start with a warm exclamation like "Ugh" or "Oh no"
followed by validation.
```

**Better:**
```
Vary your opening based on the situation:
- Sometimes start with direct acknowledgment: "I'm so sorry you're dealing with this"
- Sometimes with a question: "Has this been going on for a while?"
- Sometimes with empathy: "That sounds really tough"
- Sometimes with validation: "Your feelings are completely valid"
- Use "Ugh" or "Oh no" occasionally, not every time
```

**Examples to include in prompt:**
```
Opening variety examples:
1. "I'm so sorry - that's one of those moments..."
2. "That sounds really difficult to navigate."
3. "Have you been able to talk to anyone about this?"
4. "Your frustration makes complete sense here."
5. "Breakups are brutal, especially when..."
```

### Temperature Settings

Lower temperature (0.0-0.3) → More repetitive
Higher temperature (0.7-1.0) → More varied

If repetitiveness is high, try increasing temperature.

## Comparing Bots

```bash
# Analyze multiple bots
python analyze_repetitiveness.py ActualClaude
python analyze_repetitiveness.py KimiBotTuned
python analyze_repetitiveness.py ClaudeBot-v2

# Compare scores
```

**Example comparison:**
- ActualClaude: 8.5/10 (Excellent variety)
- ClaudeBot-v2: 6.8/10 (Good variety)
- KimiBotTuned: 4.2/10 (Some repetition)

## Integration with Main Evaluation

This analysis is **separate** from the main tone evaluation but complements it:

1. **Main evaluation** (tone match, warmth, advice quality)
2. **Repetitiveness analysis** (variety, uniqueness, formulaic patterns)

Both are important for quality assessment!

## When to Run This

Run repetitiveness analysis:
- ✅ After generating new bot responses
- ✅ After modifying system prompts
- ✅ Before final evaluation
- ✅ When comparing different models
- ✅ When tuning temperature/parameters

## Cost

This analysis is **free** - it only reads local files, no API calls!

## Recommendations by Score Range

### 8-10 (Excellent)
- Keep current prompt
- Good variety maintained

### 6-7.9 (Good)
- Minor improvements possible
- Review most common patterns
- Consider slight prompt adjustments

### 4-5.9 (Moderate)
- Significant improvement needed
- Add explicit variety instructions
- Include diverse examples in prompt

### 0-3.9 (Poor)
- Major prompt revision needed
- Add "vary your openings" instruction
- Remove formulaic templates
- Increase temperature if applicable
- Provide 10+ diverse opening examples

## Advanced: Custom Thresholds

You can modify the script to adjust what counts as "too repetitive":

```python
# In calculate_repetitiveness_score()

# Stricter (penalize earlier)
if excl_count / total_responses > 0.3:  # Was 0.5

# More lenient
if excl_count / total_responses > 0.7:  # Was 0.5
```

## Future Enhancements

Potential additions:
- [ ] Semantic similarity (not just exact matches)
- [ ] Middle/ending pattern analysis
- [ ] Phrase template detection
- [ ] Comparison mode (compare 2+ bots)
- [ ] Automated prompt suggestions
- [ ] Integration with main evaluation scoring
