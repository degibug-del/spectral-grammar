#!/usr/bin/env python3
"""
Hyperparameter tuning for Spectral Grammar Network.

Sweep over key parameters:
- Learning rate
- Dropout
- Attention heads
- Number of LSTM layers
- Hidden dimension

Trains multiple models and logs results for comparison.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import json
import os
from datetime import datetime
from spectral_grammar.network import SpectralGrammarNetwork, SpectralGrammarLoss
from spectral_grammar.trainer import LanguageDataset, Trainer
from train_improved import get_expanded_corpus


def train_and_evaluate(
    config,
    train_loader,
    val_loader,
    sentences,
    vocab,
    device="cpu"
):
    """Train a model with given config and return metrics."""

    print(f"  Training with config...")

    # Create model
    model = SpectralGrammarNetwork(
        vocab_size=len(vocab),
        embedding_dim=config["embedding_dim"],
        hidden_dim=config["hidden_dim"],
        num_layers=config["num_layers"],
        dropout=config["dropout"],
        num_attention_heads=config["num_attention_heads"]
    )

    model.to(device)

    # Train and track losses
    trainer = Trainer(
        model,
        vocab,
        learning_rate=config["learning_rate"],
        device=device
    )

    best_val_loss = float("inf")
    final_train_loss = 0
    final_val_loss = 0

    for epoch in range(config["epochs"]):
        train_loss = trainer.train_epoch(train_loader)
        val_loss = trainer.validate(val_loader)

        final_train_loss = train_loss
        final_val_loss = val_loss

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            trainer.save("best_model.pt")

        if epoch % 3 == 2:  # Print every 3 epochs
            print(f"    Epoch {epoch+1}: train={train_loss:.4f}, val={val_loss:.4f}")

    return {
        "config": config,
        "final_train_loss": final_train_loss,
        "final_val_loss": final_val_loss,
        "params": sum(p.numel() for p in model.parameters()),
    }


def main():
    print("=" * 80)
    print("HYPERPARAMETER TUNING: Spectral Grammar Network")
    print("=" * 80)
    print()

    # Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}\n")

    # Load data
    print("Preparing data...")
    sentences = get_expanded_corpus()

    # Build vocabulary
    vocab = {"<PAD>": 0, "<UNK>": 1}
    from spectral_grammar.parser import SpectralParser
    parser_tool = SpectralParser()

    for i, sent in enumerate(sentences):
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(sentences)}")
        try:
            doc = parser_tool.nlp(sent)
            for token in doc:
                word = token.text.lower()
                if word not in vocab:
                    vocab[word] = len(vocab)
        except:
            pass

    print(f"Vocabulary: {len(vocab)}")

    # Create dataset
    dataset = LanguageDataset(sentences, vocab, seq_length=20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    print(f"Train: {len(train_set)}, Val: {len(val_set)}\n")

    # Hyperparameter grid
    param_grid = {
        "learning_rate": [0.0005, 0.001, 0.002],
        "dropout": [0.1, 0.2],
        "num_attention_heads": [2, 4],
        "num_layers": [1, 2],
        "embedding_dim": [96, 128],
        "hidden_dim": [192, 256],
    }

    # Base config
    base_config = {
        "epochs": 10,
        "batch_size": 16,
    }

    # Generate configurations to test
    configs = []

    # Test 1: Best from previous training
    configs.append({
        **base_config,
        "learning_rate": 0.002,
        "dropout": 0.2,
        "num_attention_heads": 4,
        "num_layers": 2,
        "embedding_dim": 128,
        "hidden_dim": 256,
        "name": "Baseline (previous best)"
    })

    # Test 2: Lower learning rate
    configs.append({
        **base_config,
        "learning_rate": 0.001,
        "dropout": 0.2,
        "num_attention_heads": 4,
        "num_layers": 2,
        "embedding_dim": 128,
        "hidden_dim": 256,
        "name": "Lower LR (0.001)"
    })

    # Test 3: More dropout
    configs.append({
        **base_config,
        "learning_rate": 0.002,
        "dropout": 0.3,
        "num_attention_heads": 4,
        "num_layers": 2,
        "embedding_dim": 128,
        "hidden_dim": 256,
        "name": "More dropout (0.3)"
    })

    # Test 4: Larger model
    configs.append({
        **base_config,
        "learning_rate": 0.001,
        "dropout": 0.2,
        "num_attention_heads": 8,
        "num_layers": 2,
        "embedding_dim": 128,
        "hidden_dim": 512,
        "name": "Larger (hidden=512, heads=8)"
    })

    # Test 5: Deeper model
    configs.append({
        **base_config,
        "learning_rate": 0.001,
        "dropout": 0.2,
        "num_attention_heads": 4,
        "num_layers": 3,
        "embedding_dim": 128,
        "hidden_dim": 256,
        "name": "Deeper (3 layers)"
    })

    # Test 6: Conservative
    configs.append({
        **base_config,
        "learning_rate": 0.0005,
        "dropout": 0.1,
        "num_attention_heads": 2,
        "num_layers": 1,
        "embedding_dim": 96,
        "hidden_dim": 192,
        "name": "Conservative (small model)"
    })

    # Run experiments
    results = []

    for i, config in enumerate(configs, 1):
        print(f"\n{'='*80}")
        print(f"Experiment {i}/{len(configs)}: {config.get('name', 'Config')}")
        print(f"{'='*80}")

        # Create dataloaders
        train_loader = DataLoader(
            train_set,
            batch_size=config["batch_size"],
            shuffle=True
        )
        val_loader = DataLoader(
            val_set,
            batch_size=config["batch_size"]
        )

        # Train
        result = train_and_evaluate(
            config,
            train_loader,
            val_loader,
            sentences,
            vocab,
            device=device
        )
        results.append(result)

        print(f"\n  Final train loss: {result['final_train_loss']:.4f}")
        print(f"  Final val loss:   {result['final_val_loss']:.4f}")
        print(f"  Model params:     {result['params']:,}")

    # Summary
    print(f"\n\n{'='*80}")
    print("RESULTS SUMMARY")
    print(f"{'='*80}\n")

    # Sort by validation loss
    results_sorted = sorted(results, key=lambda x: x["final_val_loss"])

    print("Ranking by validation loss (lower is better):\n")
    for rank, result in enumerate(results_sorted, 1):
        config = result["config"]
        print(f"{rank}. {config.get('name', 'Config')}")
        print(f"   Val loss: {result['final_val_loss']:.4f}")
        print(f"   Train loss: {result['final_train_loss']:.4f}")
        print(f"   LR={config['learning_rate']}, dropout={config['dropout']}, "
              f"heads={config['num_attention_heads']}, layers={config['num_layers']}")
        print(f"   Embedding={config['embedding_dim']}, hidden={config['hidden_dim']}")
        print()

    # Save results
    results_file = f"tuning_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w") as f:
        json.dump(
            [
                {
                    "config": r["config"],
                    "final_train_loss": float(r["final_train_loss"]),
                    "final_val_loss": float(r["final_val_loss"]),
                    "params": r["params"],
                }
                for r in results
            ],
            f,
            indent=2
        )

    print(f"Results saved to: {results_file}")
    print()

    # Best config
    best = results_sorted[0]
    print(f"\n{'='*80}")
    print("BEST CONFIG")
    print(f"{'='*80}")
    print(json.dumps(best["config"], indent=2))
    print()
    print("To retrain with best config:")
    print(f"python train_improved.py --epochs 20 --batch-size 16 "
          f"--learning-rate {best['config']['learning_rate']} "
          f"--output model_best.pt")


if __name__ == "__main__":
    main()
