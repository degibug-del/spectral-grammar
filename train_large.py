#!/usr/bin/env python3
"""
Train on large corpus (5500+ sentences).

Expected improvements:
- Better generalization
- Lower validation loss
- Robust frequency prediction
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import argparse
from spectral_grammar.network import SpectralGrammarNetwork, SpectralGrammarLoss
from spectral_grammar.trainer import LanguageDataset, Trainer


def main():
    parser = argparse.ArgumentParser(description="Train on large corpus")
    parser.add_argument("--corpus", type=str, default="corpus_large.txt", help="Corpus file")
    parser.add_argument("--epochs", type=int, default=25, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (larger for more data)")
    parser.add_argument("--learning-rate", type=float, default=0.0015, help="Learning rate (tuned)")
    parser.add_argument("--embedding-dim", type=int, default=128, help="Embedding dimension")
    parser.add_argument("--hidden-dim", type=int, default=256, help="Hidden dimension")
    parser.add_argument("--output", type=str, default="model_large.pt", help="Output model")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda/cpu)")

    args = parser.parse_args()

    # Auto-detect device
    if args.device is None:
        args.device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 80)
    print("TRAINING ON LARGE CORPUS (5500+ SENTENCES)")
    print("=" * 80)
    print()

    # Load corpus
    print(f"Loading corpus from {args.corpus}...")
    try:
        with open(args.corpus, 'r') as f:
            sentences = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {args.corpus} not found")
        return 1

    print(f"Loaded {len(sentences)} sentences")

    # Build vocabulary
    print("Building vocabulary...")
    vocab = {"<PAD>": 0, "<UNK>": 1}
    from spectral_grammar.parser import SpectralParser

    parser_tool = SpectralParser()
    for i, sent in enumerate(sentences):
        if (i + 1) % 500 == 0:
            print(f"  Processing {i + 1}/{len(sentences)}")
        try:
            doc = parser_tool.nlp(sent)
            for token in doc:
                word = token.text.lower()
                if word not in vocab:
                    vocab[word] = len(vocab)
        except:
            pass

    print(f"Vocabulary size: {len(vocab)}")
    print()

    # Create dataset
    print("Creating dataset...")
    dataset = LanguageDataset(sentences, vocab, seq_length=20)
    print(f"Dataset size: {len(dataset)}")

    if len(dataset) < args.batch_size:
        print(f"Error: Dataset too small ({len(dataset)}) for batch size ({args.batch_size})")
        return 1

    # Split (80/20 train/val)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    print(f"Train: {len(train_set)}, Val: {len(val_set)}")
    print()

    # Create model (best config from tuning)
    print("Creating model (best configuration from tuning)...")
    print(f"  Embedding dim: {args.embedding_dim}")
    print(f"  Hidden dim: {args.hidden_dim}")
    print(f"  Attention heads: 4")
    print(f"  Layers: 2 (bidirectional LSTM)")
    print(f"  Device: {args.device}")
    print()

    model = SpectralGrammarNetwork(
        vocab_size=len(vocab),
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        num_layers=2,
        dropout=0.2,
        num_attention_heads=4
    )

    # Train
    print(f"Training for {args.epochs} epochs on {len(sentences)} sentences...\n")
    trainer = Trainer(
        model,
        vocab,
        learning_rate=args.learning_rate,
        device=args.device
    )
    trainer.fit(train_loader, val_loader, epochs=args.epochs, early_stopping_patience=5)

    # Save
    if args.output:
        trainer.save(args.output)
        print(f"\n✓ Large-corpus model saved to {args.output}")
        print(f"✓ Training corpus: {len(sentences)} sentences")
        print(f"✓ Vocabulary: {len(vocab)} tokens")
        print(f"✓ Model: {sum(p.numel() for p in model.parameters()):,} parameters")

    return 0


if __name__ == "__main__":
    exit(main())
