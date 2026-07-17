#!/usr/bin/env python3
"""Garden-path sentences: where grammar becomes ambiguous."""

import sys
sys.path.insert(0, "..")

from spectral_grammar import analyze


def main():
    """Analyze garden-path sentences (structural ambiguity)."""

    garden_path_pairs = [
        {
            "clear": "The horse raced past the barn.",
            "ambiguous": "The horse raced past the barn fell.",
            "explanation": "Garden path: 'raced' initially seems like the main verb, but 'fell' reveals it's a participle"
        },
        {
            "clear": "I saw the man with the binoculars.",
            "ambiguous": "I saw the man with the binoculars yesterday.",
            "explanation": "Attachment ambiguity: is 'yesterday' modifying the seeing or the man?"
        },
        {
            "clear": "The girl told the story.",
            "ambiguous": "The girl told the boy she would leave.",
            "explanation": "Pronoun ambiguity: who is 'she'? The girl or another girl?"
        },
        {
            "clear": "The man expected the letter to arrive.",
            "ambiguous": "The man expected the letter to arrive opened his mail.",
            "explanation": "Garden path: 'to arrive' seems like infinitive, but it's actually a participle"
        },
    ]

    print("="*80)
    print("GARDEN-PATH SENTENCES: Structural Ambiguity Detection")
    print("="*80)
    print()

    all_pairs = []

    for i, pair in enumerate(garden_path_pairs, 1):
        print(f"Example {i}: {pair['explanation']}")
        print(f"Explanation: {pair['explanation']}")
        print()

        clear_result = analyze(pair["clear"])
        ambiguous_result = analyze(pair["ambiguous"])

        all_pairs.append({
            "clear": clear_result,
            "ambiguous": ambiguous_result,
            "gap_diff": ambiguous_result.spectral_gap - clear_result.spectral_gap,
            "freq_diff": ambiguous_result.frequency - clear_result.frequency
        })

        print(f"  Clear version: '{pair['clear']}'")
        print(f"    Δλ={clear_result.spectral_gap:.4f}  f={clear_result.frequency:.1f} Hz  conf={clear_result.confidence:.1%}")
        print()

        print(f"  Ambiguous version: '{pair['ambiguous']}'")
        print(f"    Δλ={ambiguous_result.spectral_gap:.4f}  f={ambiguous_result.frequency:.1f} Hz  conf={ambiguous_result.confidence:.1%}")
        print()

        # Analysis
        print(f"  Analysis:")
        if ambiguous_result.spectral_gap < clear_result.spectral_gap:
            print(f"    ✓ Ambiguous version has LOWER spectral gap ({ambiguous_result.spectral_gap:.3f} vs {clear_result.spectral_gap:.3f})")
            print(f"    ✓ Predicts LOWER frequency ({ambiguous_result.frequency:.1f} vs {clear_result.frequency:.1f} Hz)")
            print(f"    ✓ Theory matches: ambiguity → lower frequency → lower confidence")
        else:
            print(f"    ✗ Spectral gap didn't decrease as predicted")

        print()
        print("-" * 80)
        print()

    # Summary statistics
    print("="*80)
    print("SUMMARY: Can Spectral Grammar Detect Ambiguity?")
    print("="*80)
    print()

    correct_predictions = sum(1 for p in all_pairs if p["gap_diff"] < 0)
    total = len(all_pairs)

    print(f"Predictions: {correct_predictions}/{total} pairs showed lower Δλ for ambiguous version")
    print()

    avg_gap_diff = sum(p["gap_diff"] for p in all_pairs) / len(all_pairs)
    avg_freq_diff = sum(p["freq_diff"] for p in all_pairs) / len(all_pairs)

    print(f"Average spectral gap decrease: {avg_gap_diff:.4f}")
    print(f"Average frequency decrease: {avg_freq_diff:.2f} Hz")
    print()

    if correct_predictions == total:
        print("✓ PERFECT: Spectral grammar correctly identifies ambiguous structures!")
    elif correct_predictions >= total * 0.75:
        print("✓ STRONG: Spectral grammar mostly identifies ambiguity")
    else:
        print("✗ WEAK: Spectral grammar didn't consistently detect ambiguity")

    print()
    print("="*80)


if __name__ == "__main__":
    main()
