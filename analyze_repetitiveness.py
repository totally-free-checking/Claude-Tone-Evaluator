#!/usr/bin/env python3
"""
Analyze repetitiveness and similarity across bot responses
Detects formulaic patterns, repeated openings, and lack of variety

Usage: python analyze_repetitiveness.py <bot_name>
Example: python analyze_repetitiveness.py KimiBotTuned
"""

import json
import sys
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Tuple

BOT_RESPONSES_DIR = "bot_responses"


def load_responses(bot_name: str) -> List[Dict]:
    """Load all responses for a bot"""
    filepath = f"{BOT_RESPONSES_DIR}/Output - {bot_name} Responses.jsonl"

    if not Path(filepath).exists():
        print(f"Error: Response file not found: {filepath}")
        sys.exit(1)

    responses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            responses.append(json.loads(line))

    return responses


def extract_opening(text: str, num_words: int = 5) -> str:
    """Extract the opening N words from text"""
    words = text.split()[:num_words]
    return ' '.join(words)


def extract_first_sentence(text: str) -> str:
    """Extract the first sentence"""
    # Split on sentence-ending punctuation
    match = re.match(r'^[^.!?]+[.!?]', text)
    if match:
        return match.group(0).strip()
    # If no sentence ending found, take first 50 chars
    return text[:50].strip()


def get_opening_patterns(text: str) -> Dict[str, str]:
    """Extract various opening patterns"""
    patterns = {}

    # First word
    first_word = text.split()[0] if text.split() else ""
    patterns['first_word'] = first_word

    # First two words
    patterns['first_2_words'] = extract_opening(text, 2)

    # First three words
    patterns['first_3_words'] = extract_opening(text, 3)

    # First sentence
    patterns['first_sentence'] = extract_first_sentence(text)

    # Check for common opening exclamations
    exclamations = ['Ugh', 'Oh no', 'Oof', 'Yikes', "I'm so sorry", 'That sucks', "That's rough"]
    for excl in exclamations:
        if text.startswith(excl):
            patterns['exclamation'] = excl
            break
    else:
        patterns['exclamation'] = None

    return patterns


def analyze_ngrams(responses: List[str], n: int = 3) -> Dict[str, int]:
    """Find most common n-grams across all responses"""
    ngrams = []

    for response in responses:
        words = response.lower().split()
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)

    return Counter(ngrams)


def calculate_uniqueness_score(responses: List[str]) -> float:
    """
    Calculate uniqueness score (0-10)
    10 = all responses unique
    0 = all responses identical
    """
    if len(responses) <= 1:
        return 10.0

    # Count unique first sentences
    first_sentences = [extract_first_sentence(r) for r in responses]
    unique_sentences = len(set(first_sentences))

    uniqueness_ratio = unique_sentences / len(responses)
    return uniqueness_ratio * 10


def calculate_diversity_metrics(responses: List[str]) -> Dict:
    """Calculate various diversity metrics"""
    metrics = {}

    # Unique first words
    first_words = [r.split()[0] if r.split() else "" for r in responses]
    first_word_counter = Counter(first_words)
    metrics['unique_first_words'] = len(first_word_counter)
    metrics['total_responses'] = len(responses)
    metrics['first_word_diversity'] = metrics['unique_first_words'] / metrics['total_responses']

    # Unique first 3 words
    first_3 = [extract_opening(r, 3) for r in responses]
    first_3_counter = Counter(first_3)
    metrics['unique_first_3_words'] = len(first_3_counter)
    metrics['first_3_diversity'] = metrics['unique_first_3_words'] / metrics['total_responses']

    # Unique first sentences
    first_sentences = [extract_first_sentence(r) for r in responses]
    first_sentence_counter = Counter(first_sentences)
    metrics['unique_first_sentences'] = len(first_sentence_counter)
    metrics['first_sentence_diversity'] = metrics['unique_first_sentences'] / metrics['total_responses']

    # Most common patterns
    metrics['most_common_first_word'] = first_word_counter.most_common(5)
    metrics['most_common_first_3'] = first_3_counter.most_common(10)
    metrics['most_common_sentences'] = first_sentence_counter.most_common(10)

    return metrics


def find_formulaic_patterns(responses: List[str]) -> Dict:
    """Detect formulaic patterns like 'Ugh, [problem]! [validation]'"""
    patterns = defaultdict(list)

    for i, response in enumerate(responses):
        # Check for exclamation + validation pattern
        if re.match(r'^(Ugh|Oh no|Oof|Yikes),?\s+', response):
            excl = re.match(r'^(Ugh|Oh no|Oof|Yikes)', response).group(1)
            patterns['starts_with_exclamation'].append((i, excl, response[:50]))

        # Check for "I'm so sorry" opening
        if re.match(r"^I'm so sorry", response, re.IGNORECASE):
            patterns['starts_with_apology'].append((i, response[:50]))

        # Check for "That's [adjective]" pattern
        if re.match(r"That's (so|such|really) \w+", response):
            match = re.match(r"(That's (?:so|such|really) \w+)", response)
            patterns['thats_adjective'].append((i, match.group(1), response[:50]))

        # Check for emoji in first 50 chars
        if re.search(r'[😅😊💙🫂]', response[:50]):
            emoji = re.search(r'[😅😊💙🫂]', response[:50]).group(0)
            patterns['emoji_in_opening'].append((i, emoji))

    return patterns


def calculate_repetitiveness_score(diversity_metrics: Dict, formulaic_patterns: Dict) -> Tuple[float, str]:
    """
    Calculate overall repetitiveness score (0-10)
    10 = highly varied, no repetition
    0 = extremely repetitive, formulaic
    """
    scores = []
    penalties = []

    # Diversity scores (higher is better)
    first_word_score = diversity_metrics['first_word_diversity'] * 10
    first_3_score = diversity_metrics['first_3_diversity'] * 10
    sentence_score = diversity_metrics['first_sentence_diversity'] * 10

    scores.extend([first_word_score, first_3_score, sentence_score])

    # Penalties for formulaic patterns
    total_responses = diversity_metrics['total_responses']

    # Penalty if >50% start with exclamations
    excl_count = len(formulaic_patterns.get('starts_with_exclamation', []))
    if excl_count / total_responses > 0.5:
        penalty = (excl_count / total_responses - 0.5) * 20  # Up to -10 penalty
        penalties.append(('exclamation_overuse', penalty))

    # Penalty if >30% use same first 3 words
    most_common_3_count = diversity_metrics['most_common_first_3'][0][1] if diversity_metrics['most_common_first_3'] else 0
    if most_common_3_count / total_responses > 0.3:
        penalty = (most_common_3_count / total_responses - 0.3) * 15
        penalties.append(('repeated_opening', penalty))

    # Calculate final score
    base_score = sum(scores) / len(scores)
    total_penalty = sum(p[1] for p in penalties)
    final_score = max(0, min(10, base_score - total_penalty))

    # Grade
    if final_score >= 8:
        grade = "Excellent variety"
    elif final_score >= 6:
        grade = "Good variety"
    elif final_score >= 4:
        grade = "Some repetition"
    elif final_score >= 2:
        grade = "Quite formulaic"
    else:
        grade = "Extremely repetitive"

    return final_score, grade


def generate_report(bot_name: str, responses: List[Dict]):
    """Generate comprehensive repetitiveness report"""
    response_texts = [r['response'] for r in responses]

    print("=" * 80)
    print(f"REPETITIVENESS ANALYSIS: {bot_name}")
    print("=" * 80)
    print(f"\nTotal responses: {len(response_texts)}\n")

    # Diversity metrics
    print("=" * 80)
    print("DIVERSITY METRICS")
    print("=" * 80)

    diversity = calculate_diversity_metrics(response_texts)

    print(f"\nUnique first words: {diversity['unique_first_words']}/{diversity['total_responses']} ({diversity['first_word_diversity']:.1%})")
    print(f"Unique first 3 words: {diversity['unique_first_3_words']}/{diversity['total_responses']} ({diversity['first_3_diversity']:.1%})")
    print(f"Unique first sentences: {diversity['unique_first_sentences']}/{diversity['total_responses']} ({diversity['first_sentence_diversity']:.1%})")

    # Most common patterns
    print("\n" + "-" * 80)
    print("MOST COMMON FIRST WORDS")
    print("-" * 80)
    for word, count in diversity['most_common_first_word']:
        pct = (count / diversity['total_responses']) * 100
        bar = "█" * int(pct / 2)
        print(f"{word:20s} {count:3d}x ({pct:5.1f}%)  {bar}")

    print("\n" + "-" * 80)
    print("MOST COMMON FIRST 3 WORDS")
    print("-" * 80)
    for phrase, count in diversity['most_common_first_3'][:10]:
        pct = (count / diversity['total_responses']) * 100
        bar = "█" * int(pct / 2)
        print(f"{phrase:30s} {count:3d}x ({pct:5.1f}%)  {bar}")

    print("\n" + "-" * 80)
    print("MOST REPEATED FIRST SENTENCES")
    print("-" * 80)
    for sentence, count in diversity['most_common_sentences'][:5]:
        if count > 1:  # Only show repeated sentences
            pct = (count / diversity['total_responses']) * 100
            print(f"[{count}x / {pct:.1f}%] {sentence}")

    # Formulaic patterns
    print("\n" + "=" * 80)
    print("FORMULAIC PATTERNS")
    print("=" * 80)

    patterns = find_formulaic_patterns(response_texts)

    if patterns['starts_with_exclamation']:
        count = len(patterns['starts_with_exclamation'])
        pct = (count / len(response_texts)) * 100
        print(f"\nStarts with exclamation: {count}/{len(response_texts)} ({pct:.1f}%)")

        # Count each exclamation type
        excl_types = Counter([e[1] for e in patterns['starts_with_exclamation']])
        for excl, cnt in excl_types.most_common():
            print(f"  - '{excl}': {cnt}x")

        if count > len(response_texts) * 0.5:
            print("  ⚠️  WARNING: Over 50% of responses start with exclamations")

    if patterns['starts_with_apology']:
        count = len(patterns['starts_with_apology'])
        pct = (count / len(response_texts)) * 100
        print(f"\nStarts with 'I'm so sorry': {count}/{len(response_texts)} ({pct:.1f}%)")
        if count > len(response_texts) * 0.3:
            print("  ⚠️  WARNING: Over 30% start with apology")

    if patterns['thats_adjective']:
        count = len(patterns['thats_adjective'])
        pct = (count / len(response_texts)) * 100
        print(f"\nUses 'That's [adjective]' pattern: {count}/{len(response_texts)} ({pct:.1f}%)")

    if patterns['emoji_in_opening']:
        count = len(patterns['emoji_in_opening'])
        pct = (count / len(response_texts)) * 100
        print(f"\nEmoji in opening: {count}/{len(response_texts)} ({pct:.1f}%)")
        emoji_types = Counter([e[1] for e in patterns['emoji_in_opening']])
        for emoji, cnt in emoji_types.most_common():
            print(f"  - {emoji}: {cnt}x")

    # N-gram analysis
    print("\n" + "=" * 80)
    print("MOST COMMON 3-WORD PHRASES (ACROSS ALL RESPONSES)")
    print("=" * 80)

    trigrams = analyze_ngrams(response_texts, n=3)
    common_trigrams = [t for t in trigrams.most_common(20) if t[1] > 5]  # At least 6 occurrences

    if common_trigrams:
        for trigram, count in common_trigrams[:10]:
            pct = (count / len(response_texts)) * 100
            print(f"{trigram:40s} {count:3d}x ({pct:5.1f}%)")
    else:
        print("No significantly repeated 3-word phrases found (good!)")

    # Overall score
    print("\n" + "=" * 80)
    print("REPETITIVENESS SCORE")
    print("=" * 80)

    score, grade = calculate_repetitiveness_score(diversity, patterns)

    bar = "█" * int(score) + "░" * (10 - int(score))
    print(f"\nScore: {score:.1f}/10  {bar}")
    print(f"Grade: {grade}")

    if score >= 8:
        print("\n✓ Excellent variety! Responses are diverse and not formulaic.")
    elif score >= 6:
        print("\n✓ Good variety overall, with some minor patterns.")
    elif score >= 4:
        print("\n⚠️  Moderate repetitiveness. Consider varying openings more.")
    else:
        print("\n❌ High repetitiveness! Responses are very formulaic.")
        print("   Recommendation: Revise system prompt to encourage more variety.")

    # Recommendations
    if score < 7:
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        # Check for overused exclamations
        if patterns['starts_with_exclamation'] and len(patterns['starts_with_exclamation']) / len(response_texts) > 0.5:
            print("\n1. Reduce exclamation openings:")
            print("   - Too many responses start with 'Ugh', 'Oh no', etc.")
            print("   - Vary with: direct statements, questions, 'I'm so sorry', etc.")

        # Check for repeated first 3 words
        most_common_3 = diversity['most_common_first_3'][0] if diversity['most_common_first_3'] else None
        if most_common_3 and most_common_3[1] / len(response_texts) > 0.3:
            print(f"\n2. '{most_common_3[0]}' is overused ({most_common_3[1]}x)")
            print("   - Find alternative ways to open responses")

        # Check for low sentence diversity
        if diversity['first_sentence_diversity'] < 0.5:
            print("\n3. First sentences are too similar")
            print("   - Vary sentence structure and opening phrases")
            print("   - Don't always follow the same pattern")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_repetitiveness.py <bot_name>")
        print("\nExample: python analyze_repetitiveness.py KimiBotTuned")
        print("\nAnalyzes response variety and detects formulaic patterns")
        sys.exit(1)

    bot_name = sys.argv[1]

    print(f"Loading responses for: {bot_name}")
    responses = load_responses(bot_name)

    if not responses:
        print("No responses found!")
        sys.exit(1)

    generate_report(bot_name, responses)


if __name__ == "__main__":
    main()
