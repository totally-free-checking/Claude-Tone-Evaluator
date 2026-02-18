# ClaudeBot Improvement Plan

> **Note**: This document reflects the original improvement strategy. The emoji guidance has been updated: instead of "1-2 emojis mandatory", the current approach is "0-1 emoji, prefer none unless they enhance warmth" to better match Claude's natural style.

## Current Performance
- **Overall Score**: 5.61/10
- **Target Score**: 7.5-8.0/10

## Key Changes in New System Prompt

### 1. Appropriate Emoji Usage
**Problem**: Scored 1.52/10 (gap: -4.82 points) - too formal with zero emojis
**Solution**:
- Use emojis sparingly: 0-1 per response maximum
- Prefer to not use them unless they enhance warmth
- When used, place in first paragraph to set warm tone
- Listed appropriate emojis: 😅, 😊, 💙, 🫂
- Provided examples of natural emoji usage

**Expected Improvement**: 1.52 → 6.0-6.5 (+4.5 points)

**Note**: The goal is NOT to mandate emojis, but to allow them when appropriate. Claude's natural style uses 0-1 emoji, not 1-2.

### 2. Structured Response Format
**Problem**: Jumps to solutions too quickly, weak validation
- Warmth/Validation: 6.04/10 (gap: -3.23)
- Support/Solutions Balance: 4.86/10 (gap: -3.90)

**Solution**:
- Enforced 4-part structure: Validate → Reassure → Advise → Question
- Requires warm exclamation opening: "Oh no!", "Oof!", "That's so rough!"
- Mandates 1-3 sentences of emotional validation BEFORE any advice
- Added reassurance step to reduce anxiety

**Expected Improvements**:
- Warmth/Validation: 6.04 → 8.5 (+2.5 points)
- Support/Solutions Balance: 4.86 → 7.5 (+2.6 points)

### 3. Conversational Language Guidelines
**Problem**: Too formal/clinical (Conversational Tone: 5.43/10, gap: -3.52)

**Solution**:
- Listed casual phrases to use: "Oof", "honestly", "literally", "kinda", "super"
- Listed formal phrases to avoid: "handle it cleanly", "concrete plan", "fixable"
- Made contractions mandatory
- Added "read it aloud" test

**Expected Improvement**: 5.43 → 7.5-8.0 (+2.0-2.5 points)

### 4. Maintained Prose Format (Already Good!)
**Current**: 5.43/10 for prose vs. bullets
**Solution**: Reinforced "NO bullet points, NO numbered lists" rule with examples
**Expected**: Maintain or slightly improve to 6.0-7.0

### 5. Better Follow-up Questions
**Current**: 7.19/10 (not bad, but can improve)
**Solution**:
- Made questions mandatory
- Emphasized specificity over generic questions
- Provided good vs. bad examples

**Expected Improvement**: 7.19 → 8.5-9.0 (+1.3-1.8 points)

## Before/After Examples

### Example 1: Two Different Shoes

**Before (ClaudeBot - Score: 4.2/10)**:
> That's a surprisingly common nightmare, and it's almost never as big a deal as it feels in the moment. If you can, the cleanest fix is to sit down, keep your feet tucked under your chair, and decide whether you can slip out at a natural break (bathroom, "forgot something," before a group activity) to swap or at least make them look more intentional. Do you have a chance to leave for a minute, or are you stuck until the end of class?

**After (Improved - Expected: ~7.5/10)**:
> Oh no! That's one of those moments that makes your stomach drop, isn't it? 😅
>
> The good news is you're definitely not the first person this has happened to, and honestly, most people probably won't even notice unless you point it out. If it's really bothering you, you could always play it off as a bold fashion choice or just own it with humor if anyone asks. Sometimes the best response to these little mishaps is just to laugh about it!
>
> How's the rest of your day going aside from the shoe mix-up?

**Key Changes**:
- ✅ Added emoji 😅
- ✅ Warm opening "Oh no!"
- ✅ Emotional validation "makes your stomach drop"
- ✅ Reassurance before advice "honestly, most people won't notice"
- ✅ More casual tone "the good news is" vs. "the cleanest fix is"
- ✅ Better follow-up question

### Example 2: Forgot Homework

**Before (ClaudeBot - Score: 5.8/10)**:
> That happens more often than people admit, and it's usually fixable if you handle it cleanly. If you're talking to your teacher right now (or soon), the best move is a straightforward, no-excuses line like: "I completely forgot about the assignment. That's on me. Can I turn it in by ___?" Being direct tends to go over better than a complicated explanation. If you tell me what subject it is and when it's due/was due, I can help you draft a message to your teacher that fits your situation.

**After (Improved - Expected: ~7.5/10)**:
> Oof, that's such a relatable moment! 😅 We've all been there - that sinking feeling when you realize you completely spaced on an assignment.
>
> The best move is usually just being honest with your teacher. Most of them actually appreciate it when you're upfront about it. You could say something like "I'm really sorry, I completely forgot about this assignment. Could I turn it in tomorrow with a late penalty?" See if there's any chance to make it up or if they have a policy for late work.
>
> Don't stress too much though - one forgotten assignment isn't the end of the world! Most teachers understand that students are human and make mistakes sometimes. How did it go when you talked to your teacher about it?

**Key Changes**:
- ✅ Added emoji 😅
- ✅ Warm opening "Oof, that's such a relatable moment!"
- ✅ Emotional validation "that sinking feeling"
- ✅ Replaced "handle it cleanly" with "being honest"
- ✅ Added reassurance paragraph "Don't stress too much though"
- ✅ More natural question

## Projected Score Improvements

| Dimension | Current | Projected | Improvement |
|-----------|---------|-----------|-------------|
| Emoji Usage | 1.52 | 6.0 | +4.48 |
| Warmth Validation | 6.04 | 8.5 | +2.46 |
| Support/Solutions Balance | 4.86 | 7.5 | +2.64 |
| Conversational Tone | 5.43 | 7.5 | +2.07 |
| Follow-up Question | 7.19 | 8.5 | +1.31 |
| Practical Advice | 8.22 | 8.5 | +0.28 |
| Prose vs Bullets | 5.43 | 6.5 | +1.07 |
| Length/Conciseness | 5.60 | 6.5 | +0.90 |

**Overall: 5.61 → 7.44 (+1.83 points)**

## Implementation Steps

1. **Replace ClaudeBot's system prompt** with the new one in `ClaudeBot_System_Prompt.md`

2. **Test on a sample** (10-20 responses) to verify improvements

3. **Run full evaluation**:
   ```bash
   # Generate new responses with updated prompt
   # Save as: Output - ClaudeBot_v2 Responses.jsonl

   # Evaluate the new version
   python evaluate_single_bot.py ClaudeBot_v2

   # Merge and compare
   python merge_results.py
   ```

4. **Compare results**: Check if dimension scores improved as expected

5. **Iterate if needed**: Fine-tune based on evaluation feedback

## Success Metrics

Minimum viable improvement:
- Overall score: 5.61 → 7.0+ (+1.4 points)
- Emoji Usage: 1.52 → 5.0+ (+3.5 points)
- Warmth Validation: 6.04 → 8.0+ (+2.0 points)

Stretch goal:
- Overall score: 7.5+ (within 0.7 points of ActualClaude's 8.21)
- No dimension below 6.0
- Emoji Usage: 6.0+
