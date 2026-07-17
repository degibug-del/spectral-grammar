#!/usr/bin/env python3
"""
Train Spectral Grammar Network on a real corpus.

Usage:
  python train_on_corpus.py --corpus corpus.txt --epochs 10 --output model.pt
"""

import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from spectral_grammar.network import SpectralGrammarNetwork, SpectralGrammarLoss
from spectral_grammar.trainer import LanguageDataset, Trainer


def get_sample_corpus():
    """Return sample corpus for quick testing."""
    return [
        "The cat sat on the mat.",
        "The dog ran in the park.",
        "She saw the man with the telescope.",
        "The horse raced past the barn.",
        "I think that that is strange.",
        "The girl told the boy she would leave.",
        "Although the weather was nice, the game was cancelled.",
        "The book which the student read was interesting.",
        "What the supervisor said was surprising.",
        "The fact that he left surprised me.",
        "The president of the company announced the merger.",
        "The students in the class studied hard for the exam.",
        "The researcher discovered a new species in the rainforest.",
        "The musician played the violin beautifully at the concert.",
        "The athlete trained every day to prepare for the competition.",
        "The chef prepared the meal with fresh ingredients.",
        "The architect designed the building with modern features.",
        "The teacher explained the lesson to the students.",
        "The doctor examined the patient in the clinic.",
        "The lawyer reviewed the contract carefully.",
    ] * 50  # Repeat for more training data


def main():
    parser = argparse.ArgumentParser(description="Train Spectral Grammar Network")
    parser.add_argument("--corpus", type=str, help="Path to corpus file (one sentence per line)")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--embedding-dim", type=int, default=64, help="Embedding dimension")
    parser.add_argument("--hidden-dim", type=int, default=128, help="Hidden dimension")
    parser.add_argument("--output", type=str, default="model.pt", help="Output model path")
    parser.add_argument("--use-sample", action="store_true", help="Use sample corpus instead of file")

    args = parser.parse_args()

    # Load corpus
    if args.use_sample or not args.corpus:
        print("Using sample corpus (20 sentences x 50 = 1000 sentences)")
        sentences = get_sample_corpus()
    else:
        print(f"Loading corpus from {args.corpus}")
        try:
            with open(args.corpus, 'r') as f:
                sentences = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: Corpus file not found: {args.corpus}")
            print("Run with --use-sample to use sample data instead")
            return 1

    print(f"Loaded {len(sentences)} sentences")

    # Build vocabulary
    print("Building vocabulary...")
    vocab = {"<PAD>": 0, "<UNK>": 1}
    from spectral_grammar.parser import SpectralParser
    parser_tool = SpectralParser()

    for i, sent in enumerate(sentences):
        if (i + 1) % 100 == 0:
            print(f"  Processing sentence {i + 1}/{len(sentences)}")
        try:
            doc = parser_tool.nlp(sent)
            for token in doc:
                word = token.text.lower()
                if word not in vocab:
                    vocab[word] = len(vocab)
        except:
            pass

    print(f"Vocabulary size: {len(vocab)}")

    # Create dataset
    print("Creating dataset...")
    dataset = LanguageDataset(sentences, vocab, seq_length=20)
    print(f"Dataset size: {len(dataset)}")

    if len(dataset) < args.batch_size:
        print(f"Error: Dataset too small ({len(dataset)}) for batch size ({args.batch_size})")
        return 1

    # Split
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    print(f"Train samples: {len(train_set)}, Val samples: {len(val_set)}")

    # Create model
    print(f"\nCreating model...")
    print(f"  Embedding dim: {args.embedding_dim}")
    print(f"  Hidden dim: {args.hidden_dim}")
    print(f"  Vocab size: {len(vocab)}")

    model = SpectralGrammarNetwork(
        vocab_size=len(vocab),
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        num_layers=1
    )

    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")

    # Train
    print(f"\nTraining for {args.epochs} epochs...\n")
    trainer = Trainer(model, vocab, learning_rate=args.learning_rate, device=device)
    trainer.fit(train_loader, val_loader, epochs=args.epochs, early_stopping_patience=3)

    # Save
    if args.output:
        trainer.save(args.output)
        print(f"\n✓ Model saved to {args.output}")
        print(f"✓ To use: model = SpectralGrammarNetwork(...); model.load_state_dict(torch.load('{args.output}'))")

    return 0


if __name__ == "__main__":
    exit(main())
