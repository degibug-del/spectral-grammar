"""
Training pipeline for Spectral Grammar Network.

Train on language corpora to predict next word using spectral reasoning.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Tuple
import random

from .network import SpectralGrammarNetwork, SpectralGrammarLoss
from .parser import SpectralParser


class LanguageDataset(Dataset):
    """Dataset of sentences for language modeling."""

    def __init__(
        self,
        sentences: List[str],
        vocab: dict,
        seq_length: int = 20,
        overlap: int = 5
    ):
        """
        Args:
            sentences: List of text sentences
            vocab: {word: id} dictionary
            seq_length: Max sequence length
            overlap: Overlap between windows (for more data)
        """
        self.vocab = vocab
        self.seq_length = seq_length
        self.unk_id = vocab.get("<UNK>", 0)
        self.pad_id = vocab.get("<PAD>", 1)

        self.sequences = []
        self._build_sequences(sentences, overlap)

    def _build_sequences(self, sentences: List[str], overlap: int):
        """Convert sentences to token sequences."""
        parser = SpectralParser()

        for sent in sentences:
            try:
                # Parse to get tokens
                doc = parser.nlp(sent)
                tokens = [token.text.lower() for token in doc]

                # Convert to IDs
                token_ids = [self.vocab.get(t, self.unk_id) for t in tokens]

                # Sliding window
                if len(token_ids) >= 2:
                    for i in range(0, len(token_ids) - 1, max(1, self.seq_length - overlap)):
                        window = token_ids[i : i + self.seq_length + 1]

                        if len(window) > 1:
                            self.sequences.append(window)
            except:
                pass

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            (input_tokens, target_tokens)
        """
        seq = self.sequences[idx]

        # Input: all but last token
        input_ids = torch.tensor(seq[:-1], dtype=torch.long)

        # Target: all but first token (next word prediction)
        target_ids = torch.tensor(seq[1:], dtype=torch.long)

        # Pad to fixed length
        if len(input_ids) < self.seq_length:
            pad_len = self.seq_length - len(input_ids)
            input_ids = torch.cat([
                input_ids,
                torch.full((pad_len,), self.pad_id, dtype=torch.long)
            ])
            target_ids = torch.cat([
                target_ids,
                torch.full((pad_len,), self.pad_id, dtype=torch.long)
            ])

        return input_ids[:self.seq_length], target_ids[:self.seq_length]


class Trainer:
    """Train spectral grammar network."""

    def __init__(
        self,
        model: SpectralGrammarNetwork,
        vocab: dict,
        learning_rate: float = 0.001,
        device: str = "cpu"
    ):
        """
        Args:
            model: SpectralGrammarNetwork instance
            vocab: {word: id} dictionary
            learning_rate: Adam learning rate
            device: "cpu" or "cuda"
        """
        self.model = model.to(device)
        self.vocab = vocab
        self.device = device

        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = SpectralGrammarLoss(alpha=0.1)

        self.train_losses = []
        self.val_losses = []

    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train one epoch."""
        self.model.train()
        total_loss = 0.0
        n_batches = 0

        for batch_idx, (input_ids, target_ids) in enumerate(train_loader):
            input_ids = input_ids.to(self.device)
            target_ids = target_ids.to(self.device)

            # Forward
            self.optimizer.zero_grad()
            logits, spectral_info = self.model(input_ids, return_spectral=True)

            # Loss
            loss = self.criterion(
                logits,
                target_ids,
                torch.tensor(spectral_info["delta_lambda"], device=self.device)
            )

            # Backward
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

            if (batch_idx + 1) % 10 == 0:
                print(f"  Batch {batch_idx + 1}: loss={loss.item():.4f}")

        avg_loss = total_loss / max(1, n_batches)
        self.train_losses.append(avg_loss)
        return avg_loss

    def validate(self, val_loader: DataLoader) -> float:
        """Validate on validation set."""
        self.model.eval()
        total_loss = 0.0
        n_batches = 0

        with torch.no_grad():
            for input_ids, target_ids in val_loader:
                input_ids = input_ids.to(self.device)
                target_ids = target_ids.to(self.device)

                logits, spectral_info = self.model(input_ids, return_spectral=True)

                loss = self.criterion(
                    logits,
                    target_ids,
                    torch.tensor(spectral_info["delta_lambda"], device=self.device)
                )

                total_loss += loss.item()
                n_batches += 1

        avg_loss = total_loss / max(1, n_batches)
        self.val_losses.append(avg_loss)
        return avg_loss

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 10,
        early_stopping_patience: int = 3
    ):
        """
        Train the model.

        Args:
            train_loader: Training data
            val_loader: Validation data
            epochs: Number of epochs
            early_stopping_patience: Stop if val loss doesn't improve
        """
        best_val_loss = float("inf")
        patience_counter = 0

        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")

            # Train
            train_loss = self.train_epoch(train_loader)
            print(f"  Train loss: {train_loss:.4f}")

            # Validate
            val_loss = self.validate(val_loader)
            print(f"  Val loss: {val_loss:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.save("best_model.pt")
                print("  ✓ Saved best model")
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"  Early stopping (patience={early_stopping_patience})")
                    break

        print(f"\nTraining complete. Best val loss: {best_val_loss:.4f}")

    def save(self, path: str):
        """Save model weights."""
        torch.save(self.model.state_dict(), path)
        print(f"  Saved to {path}")

    def load(self, path: str):
        """Load model weights."""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        print(f"  Loaded from {path}")


def example_training():
    """Example: train on sample sentences."""
    # Sample corpus
    sentences = [
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
    ] * 10  # Repeat for more training data

    # Build vocabulary
    vocab = {"<PAD>": 0, "<UNK>": 1}
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
    dataset = LanguageDataset(sentences, vocab, seq_length=10)
    print(f"Dataset size: {len(dataset)}")

    # Split train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = torch.utils.data.random_split(
        dataset,
        [train_size, val_size]
    )

    train_loader = DataLoader(train_set, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=4)

    # Create model
    model = SpectralGrammarNetwork(
        vocab_size=len(vocab),
        embedding_dim=64,
        hidden_dim=128,
        num_layers=1
    )

    # Train
    trainer = Trainer(model, vocab, learning_rate=0.001)
    trainer.fit(train_loader, val_loader, epochs=5)

    print("\n" + "=" * 70)
    print("Training complete!")
    print("Model ready for next-word prediction with spectral reasoning")
    print("=" * 70)


if __name__ == "__main__":
    example_training()
