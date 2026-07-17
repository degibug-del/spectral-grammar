#!/usr/bin/env python3
"""
Compare old model vs. improved model on test sentences.
"""

import torch
import numpy as np
from spectral_grammar.network import SpectralGrammarNetwork
from spectral_grammar.parser import SpectralParser


def load_model(path, vocab_size=103):
    """Load a model (use original dimensions from training)."""
    model = SpectralGrammarNetwork(
        vocab_size=vocab_size,
        embedding_dim=64,  # Original training dimensions
        hidden_dim=128,
        num_layers=1
    )
    model.load_state_dict(torch.load(path, weights_only=True))
    model.eval()
    return model


def load_improved_model(path, vocab_size=175):
    """Load improved model."""
    model = SpectralGrammarNetwork(
        vocab_size=vocab_size,
        embedding_dim=128,
        hidden_dim=256,
        num_layers=2,  # Improved uses 2 layers
        num_attention_heads=4
    )
    model.load_state_dict(torch.load(path, weights_only=True))
    model.eval()
    return model


def compare():
    print("=" * 80)
    print("MODEL COMPARISON: Old vs. Improved")
    print("=" * 80)
    print()

    # Test sentences
    test_sentences = [
        ("The cat sat on the mat.", "Simple, clear structure"),
        ("The horse raced past the barn fell.", "Garden-path (ambiguous)"),
        ("She saw the man with the telescope.", "Attachment ambiguity"),
        ("Dogs bark.", "Minimal structure"),
        ("The book which the student read was interesting.", "Complex embedding"),
        ("I think that that is strange.", "Repeated word"),
        ("What the professor said was surprising.", "Cleft construction"),
    ]

    parser = SpectralParser()

    print("Test Sentences:")
    for text, desc in test_sentences:
        result = parser.analyze(text)
        print(f"  {text:45s} | Δλ={result.spectral_gap:.3f} | f={result.frequency:.2f} Hz | {desc}")

    print()
    print("-" * 80)
    print()

    # Load improved model
    print("Loading improved model...")
    try:
        improved_model = load_improved_model("model_improved.pt")
        print("✓ Improved model loaded (attention + bidirectional LSTM + spectral weighting)")
    except Exception as e:
        print(f"✗ Could not load improved model: {e}")
        improved_model = None

    print()

    if not improved_model:
        print("Cannot compare: model not found")
        return

    # Build vocabulary for testing
    all_sentences = [s[0] for s in test_sentences]
    vocab_improved = {"<PAD>": 0, "<UNK>": 1}

    for sent in all_sentences:
        doc = parser.nlp(sent)
        for token in doc:
            word = token.text.lower()
            if word not in vocab_improved:
                vocab_improved[word] = len(vocab_improved)

    print("Test: Improved Model vs. Ground Truth")
    print()

    errors = []
    for text, desc in test_sentences:
        # Tokenize
        doc = parser.nlp(text)
        tokens = [token.text.lower() for token in doc]
        token_ids = torch.tensor([[vocab_improved.get(t, vocab_improved["<UNK>"]) for t in tokens]])

        # Improved model
        with torch.no_grad():
            logits, spectral = improved_model(token_ids, return_spectral=True)
            freq_pred = spectral["frequency"][0] if spectral else 0
            delta_lambda = spectral["delta_lambda"][0] if spectral else 0

        # Ground truth from parser
        true_result = parser.analyze(text)
        true_freq = true_result.frequency
        true_delta_lambda = true_result.spectral_gap

        error = abs(freq_pred - true_freq)
        errors.append(error)

        print(f"Text: {text}")
        print(f"  Spectral gap:  True={true_delta_lambda:.3f}, Pred={delta_lambda:.3f}")
        print(f"  Frequency:     True={true_freq:.2f} Hz, Pred={freq_pred:.2f} Hz")
        print(f"  Error:         {error:.3f} Hz")
        if error < 0.3:
            print(f"  ✓ Excellent prediction")
        elif error < 0.5:
            print(f"  ✓ Good prediction")
        elif error < 0.8:
            print(f"  ~ OK prediction")
        else:
            print(f"  ✗ Poor prediction")
        print()

    # Summary stats
    print("-" * 80)
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Mean absolute error: {np.mean(errors):.3f} Hz")
    print(f"Median error:        {np.median(errors):.3f} Hz")
    print(f"Max error:           {np.max(errors):.3f} Hz")
    print(f"Min error:           {np.min(errors):.3f} Hz")

    print("=" * 80)


if __name__ == "__main__":
    compare()
