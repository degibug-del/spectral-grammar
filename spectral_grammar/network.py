"""
PyTorch implementation of Spectral Grammar Network.

Explicitly computes eigenvalues for interpretable language modeling.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional


class SpectralGrammarNetwork(nn.Module):
    """
    Improved neural network for spectral grammar language modeling.

    Architecture:
    1. Embed words
    2. Multi-head self-attention (focus on grammar structure)
    3. Learn dependency structure (as adjacency matrix)
    4. Compute eigenvalues of structure
    5. Bidirectional LSTM (forward and backward context)
    6. Predict next word based on frequency encoding
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.2,
        num_attention_heads: int = 4
    ):
        """Initialize network."""
        super().__init__()

        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim

        # Embeddings
        self.embed = nn.Embedding(vocab_size, embedding_dim)

        # Multi-head self-attention (learn grammar patterns)
        self.attention = nn.MultiheadAttention(
            embed_dim=embedding_dim,
            num_heads=num_attention_heads,
            dropout=dropout,
            batch_first=True
        )

        # Learn dependency structure
        self.dependency_net = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim)
        )

        # Learn frequency prediction from spectral gap
        self.frequency_net = nn.Sequential(
            nn.Linear(1, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

        # Bidirectional LSTM for sequence modeling
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim // 2,  # Bidirectional = 2x hidden
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=True
        )

        # Layer norm for stability
        self.norm = nn.LayerNorm(embedding_dim)

        # Output layer
        self.output = nn.Linear(hidden_dim, vocab_size)

        # Confidence scorer
        self.confidence_net = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(
        self,
        token_ids: torch.Tensor,
        return_spectral: bool = False
    ) -> Tuple[torch.Tensor, Optional[dict]]:
        """
        Forward pass with improved architecture.

        Args:
            token_ids: [batch_size, seq_len]
            return_spectral: If True, return spectral analysis

        Returns:
            logits: [batch_size, seq_len, vocab_size]
            spectral_info: dict with delta_lambda, frequency, confidence
        """
        batch_size, seq_len = token_ids.shape

        # Embed
        embeddings = self.embed(token_ids)  # [batch, seq_len, embed_dim]

        # Multi-head self-attention (learn grammar patterns)
        attn_out, _ = self.attention(embeddings, embeddings, embeddings)
        attn_out = attn_out + embeddings  # Residual connection
        embeddings = self.norm(attn_out)

        # Learn dependency structure
        dep_scores = self.dependency_net(embeddings)  # [batch, seq_len, embed_dim]

        # Compute adjacency matrix for each sequence
        # A[i,j] = sigmoid(dot(dep_scores[i], dep_scores[j]))
        A = torch.sigmoid(torch.bmm(dep_scores, dep_scores.transpose(1, 2)))
        # [batch, seq_len, seq_len]

        # Compute eigenvalues (approximate via power iteration)
        delta_lambda = self._compute_spectral_gap(A)  # [batch]

        # Predict frequency from spectral gap
        frequency = self._predict_frequency(delta_lambda)  # [batch]

        # Scale embeddings by predicted frequency (adaptive weighting)
        freq_weights = frequency.unsqueeze(1).unsqueeze(2) / 10.0  # [batch, 1, 1]
        weighted_embeddings = embeddings * (0.5 + 0.5 * freq_weights.clamp(0, 1))

        # Bidirectional LSTM (reads forward and backward)
        lstm_out, _ = self.lstm(weighted_embeddings)  # [batch, seq_len, hidden_dim]

        # Predict next token
        logits = self.output(lstm_out)  # [batch, seq_len, vocab_size]

        # Confidence score
        confidence = self.confidence_net(lstm_out[:, -1, :])  # [batch, 1]

        spectral_info = None
        if return_spectral:
            spectral_info = {
                "delta_lambda": delta_lambda.detach().cpu().numpy(),
                "frequency": frequency.detach().cpu().numpy(),
                "confidence": confidence.detach().cpu().numpy().flatten(),
                "adjacency": A.detach().cpu().numpy()
            }

        return logits, spectral_info

    def _compute_spectral_gap(self, A: torch.Tensor) -> torch.Tensor:
        """
        Compute spectral gap via eigenvalue decomposition.

        Args:
            A: [batch, seq_len, seq_len] adjacency matrices

        Returns:
            delta_lambda: [batch] spectral gaps
        """
        batch_size = A.shape[0]
        delta_lambdas = []

        for i in range(batch_size):
            # Compute eigenvalues of A[i]
            try:
                eigenvalues = torch.linalg.eigvalsh(A[i])
                # Sort descending
                eigenvalues = torch.sort(eigenvalues, descending=True)[0]
                # Spectral gap: λ₁ - λ₂
                if len(eigenvalues) > 1:
                    delta_lambda = eigenvalues[0] - eigenvalues[1]
                else:
                    delta_lambda = eigenvalues[0]
            except:
                # Fallback: use Frobenius norm as proxy
                delta_lambda = torch.norm(A[i], p='fro') / A[i].shape[0]

            # Softer clamp: allow wider range with smoother boundaries
            # Use tanh to prevent hard saturation
            delta_lambda = torch.tanh(delta_lambda) + 0.5  # Range: [0.2, 1.5]
            delta_lambdas.append(delta_lambda)

        return torch.stack(delta_lambdas)

    def _predict_frequency(self, delta_lambda: torch.Tensor) -> torch.Tensor:
        """
        Predict brain oscillation frequency from spectral gap.

        Formula: f = 5 + 2.5 * log(Δλ + 1)

        Args:
            delta_lambda: [batch]

        Returns:
            frequency: [batch]
        """
        # Ensure positive
        delta_lambda = torch.clamp(delta_lambda, 0.01, 2.0)

        # Base formula
        frequency = 5.0 + 2.5 * torch.log(delta_lambda + 1)

        # Clamp to theta-alpha band
        frequency = torch.clamp(frequency, 4.0, 12.0)

        return frequency

    def get_confidence(
        self,
        token_ids: torch.Tensor,
        delta_lambda: torch.Tensor
    ) -> torch.Tensor:
        """
        Get confidence score (0-1) from spectral gap.

        Higher Δλ → higher confidence.
        """
        # Sigmoid centered around 0.5
        confidence = torch.sigmoid(10.0 * (delta_lambda - 0.5))
        return confidence


class SpectralGrammarLoss(nn.Module):
    """
    Custom loss combining prediction + spectral weighting.

    Key idea: Balance prediction accuracy with spectral diversity.
    Don't aggressively maximize Δλ; instead focus on accurate predictions.
    """

    def __init__(self, alpha: float = 0.15, beta: float = 0.01):
        """
        Args:
            alpha: Weight for spectral weighting (0-1)
            beta: Weight for spectral regularization (very small, 0-0.1)
        """
        super().__init__()
        self.alpha = alpha
        self.beta = beta  # Much smaller now
        self.ce_loss = nn.CrossEntropyLoss(reduction='none')

    def forward(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
        delta_lambda: torch.Tensor
    ) -> torch.Tensor:
        """
        Loss function with soft spectral guidance.

        Args:
            logits: [batch, seq_len, vocab_size]
            targets: [batch, seq_len]
            delta_lambda: [batch] spectral gaps

        Returns:
            loss: scalar
        """
        batch_size, seq_len, vocab_size = logits.shape

        # Main loss: prediction accuracy
        pred_loss_per_sample = self.ce_loss(
            logits.view(-1, vocab_size),
            targets.view(-1)
        ).view(batch_size, seq_len)

        # Soft spectral weighting (don't over-emphasize)
        # All sentences get similar loss, with slight boost for hard cases
        spectral_weights = 1.0 / (0.5 + delta_lambda).unsqueeze(1)
        spectral_weights = spectral_weights / spectral_weights.mean()

        # Apply gentle weighting
        weighted_pred_loss = (
            (1 - self.alpha) * pred_loss_per_sample +
            self.alpha * pred_loss_per_sample * spectral_weights
        ).mean()

        # Minimal spectral regularization: just gentle guidance
        # Target mid-range spectral gaps (not maximum)
        spectral_target = 0.8  # Target Δλ ≈ 0.8 (middle of range)
        spectral_reg = torch.abs(torch.mean(delta_lambda) - spectral_target)

        # Combined loss (spectral component is minimal)
        loss = (1 - self.beta) * weighted_pred_loss + self.beta * spectral_reg

        return loss
