#!/usr/bin/env python3
"""
Command-line interface for spectral grammar analysis.

Usage:
  spectral-grammar analyze "The cat sat on the mat"
  spectral-grammar batch --file sentences.txt --output results.json
  spectral-grammar serve --port 8000
  spectral-grammar train --corpus corpus.txt --epochs 10
"""

import argparse
import json
import sys
from pathlib import Path
from spectral_grammar import analyze


def cmd_analyze(args):
    """Analyze a single sentence."""
    result = analyze(args.text)

    output = {
        "text": result.text,
        "n_words": result.n_words,
        "spectral_gap": float(result.spectral_gap),
        "frequency": float(result.frequency),
        "confidence": float(result.confidence),
        "eigenvalues": result.eigenvalues[:5].tolist(),
        "structure_clarity": "clear" if result.spectral_gap > 1.0 else "ambiguous"
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        result.pretty_print()

    return 0


def cmd_batch(args):
    """Analyze multiple sentences from file."""
    results = []

    try:
        with open(args.file, 'r') as f:
            sentences = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    print(f"Analyzing {len(sentences)} sentences...")

    for i, sent in enumerate(sentences):
        try:
            result = analyze(sent)
            results.append({
                "text": result.text,
                "spectral_gap": float(result.spectral_gap),
                "frequency": float(result.frequency),
                "confidence": float(result.confidence),
                "structure_clarity": "clear" if result.spectral_gap > 1.0 else "ambiguous"
            })

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(sentences)}")
        except Exception as e:
            print(f"  Error processing '{sent}': {e}", file=sys.stderr)

    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved results to {args.output}")
    else:
        print(json.dumps(results, indent=2))

    return 0


def cmd_serve(args):
    """Start API server."""
    from http.server import HTTPServer
    from api_paid import PaidAnalysisHandler, init_db

    init_db()

    server = HTTPServer(("localhost", args.port), PaidAnalysisHandler)

    print(f"Spectral Grammar API Server")
    print(f"Listening on http://localhost:{args.port}")
    print(f"POST /analyze with X-API-Key header")
    print(f"GET / for documentation")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        return 0


def cmd_train(args):
    """Train the spectral grammar network."""
    try:
        from spectral_grammar.trainer import LanguageDataset, Trainer, SpectralGrammarNetwork
        from torch.utils.data import DataLoader, random_split
        import torch
    except ImportError:
        print("Error: PyTorch not installed. Run: pip install torch", file=sys.stderr)
        return 1

    # Read corpus
    try:
        with open(args.corpus, 'r') as f:
            sentences = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Corpus file not found: {args.corpus}", file=sys.stderr)
        return 1

    print(f"Training on {len(sentences)} sentences")
    print(f"Epochs: {args.epochs}, Batch size: {args.batch_size}")
    print()

    # Build vocab
    vocab = {"<PAD>": 0, "<UNK>": 1}
    from spectral_grammar.parser import SpectralParser
    parser = SpectralParser()

    for sent in sentences:
        try:
            doc = parser.nlp(sent)
            for token in doc:
                word = token.text.lower()
                if word not in vocab:
                    vocab[word] = len(vocab)
        except:
            pass

    print(f"Vocabulary size: {len(vocab)}")

    # Create dataset
    dataset = LanguageDataset(sentences, vocab, seq_length=20)
    print(f"Dataset size: {len(dataset)}")

    if len(dataset) < args.batch_size:
        print("Error: Dataset too small for batch size", file=sys.stderr)
        return 1

    # Split
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    # Model
    model = SpectralGrammarNetwork(
        vocab_size=len(vocab),
        embedding_dim=args.embedding_dim,
        hidden_dim=args.hidden_dim,
        num_layers=args.layers
    )

    # Train
    trainer = Trainer(model, vocab, learning_rate=args.learning_rate)
    trainer.fit(train_loader, val_loader, epochs=args.epochs)

    # Save
    if args.output:
        trainer.save(args.output)
        print(f"✓ Model saved to {args.output}")

    return 0


def cmd_demo(args):
    """Run demo analysis."""
    sentences = [
        "The cat sat on the mat.",
        "The horse raced past the barn fell.",
        "She saw the man with the telescope.",
        "Dogs bark loudly.",
    ]

    print("Spectral Grammar Demo")
    print("=" * 70)
    print()

    for sent in sentences:
        result = analyze(sent)
        print(f"Text: {sent}")
        print(f"  Δλ = {result.spectral_gap:.4f}")
        print(f"  f  = {result.frequency:.2f} Hz")
        print(f"  Confidence = {result.confidence:.1%}")
        print()

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Spectral Grammar: Grammar has eigenvalues"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze a sentence")
    p_analyze.add_argument("text", help="Text to analyze")
    p_analyze.add_argument("--json", action="store_true", help="JSON output")
    p_analyze.set_defaults(func=cmd_analyze)

    # batch
    p_batch = subparsers.add_parser("batch", help="Analyze multiple sentences")
    p_batch.add_argument("--file", required=True, help="Input file (one sentence per line)")
    p_batch.add_argument("--output", help="Output JSON file")
    p_batch.set_defaults(func=cmd_batch)

    # serve
    p_serve = subparsers.add_parser("serve", help="Start API server")
    p_serve.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    p_serve.set_defaults(func=cmd_serve)

    # train
    p_train = subparsers.add_parser("train", help="Train neural network")
    p_train.add_argument("--corpus", required=True, help="Corpus file")
    p_train.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    p_train.add_argument("--batch-size", type=int, default=8, help="Batch size")
    p_train.add_argument("--embedding-dim", type=int, default=64, help="Embedding dimension")
    p_train.add_argument("--hidden-dim", type=int, default=128, help="Hidden dimension")
    p_train.add_argument("--layers", type=int, default=1, help="Number of LSTM layers")
    p_train.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    p_train.add_argument("--output", help="Save model to file")
    p_train.set_defaults(func=cmd_train)

    # demo
    p_demo = subparsers.add_parser("demo", help="Run demo")
    p_demo.set_defaults(func=cmd_demo)

    # Parse
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
