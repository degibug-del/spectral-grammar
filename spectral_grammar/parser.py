"""Dependency parsing and spectral gap extraction."""

import numpy as np
import spacy
from .analysis import SpectralAnalysis


class SpectralParser:
    """Parse sentences and extract spectral properties."""

    def __init__(self, model: str = "en_core_web_sm"):
        """Initialize spaCy model for dependency parsing."""
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Model {model} not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model])
            self.nlp = spacy.load(model)

    def analyze(self, text: str) -> SpectralAnalysis:
        """
        Analyze text: parse → adjacency matrix → eigenvalues → frequency.

        Args:
            text: Input sentence

        Returns:
            SpectralAnalysis with eigenvalues, spectral gap, frequency, confidence
        """
        # Parse
        doc = self.nlp(text)

        # Build adjacency matrix
        n_words = len(doc)
        A = self._build_adjacency_matrix(doc)

        # Compute eigenvalues
        eigenvalues = self._compute_eigenvalues(A)

        # Extract spectral gap
        delta_lambda = eigenvalues[0] - eigenvalues[1] if len(eigenvalues) > 1 else eigenvalues[0]

        # Predict frequency
        frequency = self._predict_frequency(delta_lambda)

        # Confidence (normalized frequency)
        confidence = self._predict_confidence(delta_lambda)

        return SpectralAnalysis(
            text=text,
            n_words=n_words,
            adjacency_matrix=A,
            eigenvalues=eigenvalues,
            spectral_gap=delta_lambda,
            frequency=frequency,
            confidence=confidence,
            doc=doc
        )

    def _build_adjacency_matrix(self, doc) -> np.ndarray:
        """
        Build undirected adjacency matrix from dependency parse.

        A[i,j] = 1 if word i and word j have a direct dependency relation.
        """
        n = len(doc)
        A = np.zeros((n, n), dtype=float)

        for token in doc:
            # Get head index
            head_idx = token.head.i
            token_idx = token.i

            # Add edges (bidirectional)
            if head_idx != token_idx:  # Not self-loop
                A[token_idx, head_idx] = 1.0
                A[head_idx, token_idx] = 1.0

        return A

    def _compute_eigenvalues(self, A: np.ndarray) -> np.ndarray:
        """
        Compute eigenvalues of adjacency matrix.

        Returns eigenvalues in descending order.
        """
        if A.size == 0 or np.all(A == 0):
            return np.array([0.0])

        # Compute eigenvalues (symmetric matrix)
        eigenvalues = np.linalg.eigvalsh(A)

        # Sort descending
        eigenvalues = np.sort(eigenvalues)[::-1]

        # Filter out near-zero eigenvalues (numerical noise)
        eigenvalues = eigenvalues[eigenvalues > 1e-10]

        return eigenvalues if len(eigenvalues) > 0 else np.array([0.0])

    def _predict_frequency(self, delta_lambda: float) -> float:
        """
        Predict brain oscillation frequency from spectral gap.

        Formula: f = 5 + 2.5 * log(Δλ + 1)

        This is the core spectral grammar prediction.
        Larger Δλ (clearer structure) → higher frequency (more certain).
        """
        # Clamp delta_lambda to avoid log of negative
        delta_lambda = max(delta_lambda, 0.01)

        # Baseline 5 Hz + log-linear sensitivity
        frequency = 5.0 + 2.5 * np.log(delta_lambda + 1)

        # Clamp to reasonable range (4-12 Hz theta-alpha band)
        frequency = np.clip(frequency, 4.0, 12.0)

        return float(frequency)

    def _predict_confidence(self, delta_lambda: float) -> float:
        """
        Predict confidence (0-1) from spectral gap.

        Higher Δλ → higher confidence in structural interpretation.
        Uses sigmoid: confidence = 1 / (1 + exp(-10 * (Δλ - 0.5)))
        """
        # Clamp
        delta_lambda = max(delta_lambda, 0.0)

        # Sigmoid centered around 0.5
        confidence = 1.0 / (1.0 + np.exp(-10.0 * (delta_lambda - 0.5)))

        return float(np.clip(confidence, 0.0, 1.0))
