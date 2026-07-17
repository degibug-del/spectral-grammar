"""Spectral Grammar: Grammar has eigenvalues."""

from .parser import SpectralParser
from .analysis import SpectralAnalysis

__version__ = "0.1.0"
__author__ = "Diego Rincón"

def analyze(text: str) -> SpectralAnalysis:
    """Parse text and return spectral analysis."""
    parser = SpectralParser()
    return parser.analyze(text)

__all__ = ["analyze", "SpectralParser", "SpectralAnalysis"]
