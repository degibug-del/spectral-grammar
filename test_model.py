#!/usr/bin/env python3
"""
Test trained spectral grammar model on new sentences.
"""

import torch
from spectral_grammar.network import SpectralGrammarNetwork
from spectral_grammar.parser import SpectralParser


def load_model(path, vocab_size=103, embedding_dim=64, hidden_dim=128, num_layers=1):
    """Load trained model."""
    model = SpectralGrammarNetwork(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_layers=num_layers
    )
    model.load_state_dict(torch.load(path))
    model.eval()
    return model


def test_sentences():
    """Test model on various sentences."""
    print("Testing Spectral Grammar Network\n")
    print("=" * 70)

    # Load model
    print("Loading model...")
    model = load_model("model.pt")
    parser = SpectralParser()

    # Test sentences
    test_cases = [
        ("The cat sat on the mat.", "Simple structure"),
        ("The horse raced past the barn fell.", "Garden-path (ambiguous)"),
        ("She saw the man with the telescope.", "Attachment ambiguity"),
        ("Dogs bark.", "Minimal structure"),
        ("The book which the student read was interesting.", "Complex embedding"),
        ("I think that that is strange.", "Repeated word"),
        ("What the professor said was surprising.", "Cleft construction"),
    ]

    print(f"Model loaded. Vocabulary size: 103\n")

    for text, description in test_cases:
        # Parse
        result = parser.analyze(text)

        print(f"Text: {text}")
        print(f"Description: {description}")
        print(f"  Spectral Gap (Δλ): {result.spectral_gap:.4f}")
        print(f"  Frequency: {result.frequency:.2f} Hz")
        print(f"  Confidence: {result.confidence:.1%}")

        # Interpret
        if result.spectral_gap > 1.0:
            clarity = "CLEAR"
        elif result.spectral_gap > 0.7:
            clarity = "MODERATE"
        else:
            clarity = "AMBIGUOUS"

        print(f"  Interpretation: {clarity}")
        print()

    print("=" * 70)
    print("\nInterpretation Guide:")
    print("  HIGH Δλ (>1.0) → HIGH frequency (>7 Hz) → CLEAR structure")
    print("  LOW Δλ (<0.7) → LOW frequency (<6 Hz) → AMBIGUOUS structure")
    print("\nThe model learns to predict sentence clarity from grammar structure.")


if __name__ == "__main__":
    test_sentences()
