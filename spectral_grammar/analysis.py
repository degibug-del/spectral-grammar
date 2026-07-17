"""Data class for spectral analysis results."""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class SpectralAnalysis:
    """Results of spectral grammar analysis on a sentence."""

    text: str
    n_words: int
    adjacency_matrix: np.ndarray
    eigenvalues: np.ndarray
    spectral_gap: float  # Δλ = λ₁ − λ₂
    frequency: float     # Predicted brain oscillation frequency (Hz)
    confidence: float    # Confidence in structural interpretation (0-1)
    doc: Optional[object] = None  # spaCy Doc object

    def __repr__(self) -> str:
        return (
            f"SpectralAnalysis(\n"
            f"  text='{self.text}'\n"
            f"  n_words={self.n_words}\n"
            f"  Δλ={self.spectral_gap:.3f}\n"
            f"  f={self.frequency:.1f} Hz\n"
            f"  confidence={self.confidence:.2f}\n"
            f")"
        )

    def pretty_print(self) -> None:
        """Print analysis in readable format."""
        print(f"Text: {self.text}")
        print(f"Words: {self.n_words}")
        print(f"Spectral Gap (Δλ): {self.spectral_gap:.4f}")
        print(f"Predicted Frequency: {self.frequency:.2f} Hz")
        print(f"Confidence: {self.confidence:.2%}")
        print(f"Eigenvalues (top 5): {self.eigenvalues[:5]}")
        print(f"Structure: {'Clear' if self.spectral_gap > 1.0 else 'Ambiguous'}")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "n_words": self.n_words,
            "spectral_gap": float(self.spectral_gap),
            "frequency": float(self.frequency),
            "confidence": float(self.confidence),
            "eigenvalues": self.eigenvalues[:5].tolist(),  # Top 5
            "structure_clarity": "clear" if self.spectral_gap > 1.0 else "ambiguous"
        }
