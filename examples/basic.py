#!/usr/bin/env python3
"""Basic example: parse sentences and show spectral properties."""

import sys
sys.path.insert(0, "..")

from spectral_grammar import analyze


def main():
    """Analyze example sentences."""

    # Test sentences
    test_sentences = [
        # Clear structure
        "The cat sat on the mat.",
        "I saw the man with the telescope.",

        # Ambiguous (garden-path)
        "The horse raced past the barn fell.",
        "The girl told the boy she would leave.",

        # Simple
        "Dogs bark.",
        "Cats sleep.",

        # Complex
        "Although the weather was nice, the game was cancelled.",
        "The book which the student read was very interesting.",
    ]

    print("="*70)
    print("SPECTRAL GRAMMAR ANALYSIS")
    print("="*70)
    print()

    results = []
    for text in test_sentences:
        try:
            result = analyze(text)
            results.append(result)

            result.pretty_print()
            print()
        except Exception as e:
            print(f"Error analyzing '{text}': {e}")
            print()

    # Aggregate analysis
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()

    print(f"Analyzed {len(results)} sentences")
    print()

    # Sort by spectral gap
    sorted_by_gap = sorted(results, key=lambda r: r.spectral_gap, reverse=True)

    print("Most CLEAR structure (high Δλ):")
    for r in sorted_by_gap[:3]:
        print(f"  • [{r.spectral_gap:.3f}] {r.text}")

    print()
    print("Most AMBIGUOUS structure (low Δλ):")
    for r in sorted_by_gap[-3:]:
        print(f"  • [{r.spectral_gap:.3f}] {r.text}")

    print()

    # Sort by frequency
    sorted_by_freq = sorted(results, key=lambda r: r.frequency, reverse=True)

    print("Highest predicted frequency (most certain):")
    for r in sorted_by_freq[:3]:
        print(f"  • [{r.frequency:.1f} Hz] {r.text}")

    print()
    print("Lowest predicted frequency (most uncertain):")
    for r in sorted_by_freq[-3:]:
        print(f"  • [{r.frequency:.1f} Hz] {r.text}")

    print()
    print("="*70)


if __name__ == "__main__":
    main()
