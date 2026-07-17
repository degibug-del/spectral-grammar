#!/usr/bin/env python3
"""
BCI EEG Decoder: Decode which sentence a user is thinking about from brain oscillations.

The core hypothesis:
- User thinks about a sentence → brain oscillates at the sentence's spectral frequency
- EEG measures this oscillation → FFT extracts the frequency
- Match to sentence candidates → BCI knows what they're thinking

Usage:
  # Decode with real EEG data
  from bci_eeg_decoder import BCIEEGDecoder
  bci = BCIEEGDecoder(sentences=["Yes", "No", "Help"])

  # Process EEG chunk (256 Hz sampling, 2.56 seconds = 256 samples)
  eeg_signal = np.random.randn(256)  # Mock EEG
  prediction = bci.decode(eeg_signal)
  print(f"Thought: {prediction['sentence']}, Confidence: {prediction['confidence']:.1%}")
"""

import numpy as np
from scipy import signal
from scipy.signal.windows import hann
from scipy.fft import fft, fftfreq
from spectral_grammar.parser import SpectralParser


class BCIEEGDecoder:
    """Decode sentences from EEG frequency."""

    def __init__(self, sentences, sampling_rate=256, freq_range=(4, 12)):
        """
        Initialize BCI decoder.

        Args:
            sentences: List of candidate sentences (user can think about any of these)
            sampling_rate: EEG sampling frequency in Hz (default: Muse/Emotiv standard)
            freq_range: Band to extract (theta-alpha, 4-12 Hz)
        """
        self.sentences = sentences
        self.sampling_rate = sampling_rate
        self.freq_range = freq_range

        # Precompute spectral properties of each sentence
        self.parser = SpectralParser()
        self.sentence_freqs = {}
        for sent in sentences:
            result = self.parser.analyze(sent)
            self.sentence_freqs[sent] = result.frequency

        print(f"BCI initialized with {len(sentences)} sentences")
        for sent, freq in self.sentence_freqs.items():
            print(f"  {sent:40s} → {freq:.2f} Hz")
        print()

    def extract_frequency(self, eeg_signal):
        """
        Extract dominant frequency from EEG signal using FFT.

        Args:
            eeg_signal: Raw EEG data (1D or 2D array, units: microvolts)

        Returns:
            dict with 'frequency' (Hz), 'power' (magnitude)
        """
        # Handle 2D input (take first channel if multi-channel)
        if len(eeg_signal.shape) > 1:
            eeg_signal = eeg_signal[:, 0]

        # Remove DC and low-frequency drift
        eeg_signal = signal.detrend(eeg_signal)

        # Apply window to reduce spectral leakage
        windowed = eeg_signal * hann(len(eeg_signal))

        # Compute FFT
        freqs = fftfreq(len(windowed), 1.0 / self.sampling_rate)
        fft_vals = np.abs(fft(windowed))

        # Only look at positive frequencies in band
        freq_mask = (freqs >= self.freq_range[0]) & (freqs <= self.freq_range[1])
        band_freqs = freqs[freq_mask]
        band_power = fft_vals[freq_mask]

        # Find peak frequency
        if len(band_power) == 0:
            return {"frequency": self.freq_range[0], "power": 0}

        peak_idx = int(np.argmax(band_power))
        dominant_freq = float(band_freqs[peak_idx])
        peak_power = float(band_power[peak_idx])

        return {
            "frequency": dominant_freq,
            "power": peak_power,
        }

    def decode(self, eeg_signal, verbose=False):
        """
        Decode which sentence the user is thinking about.

        Args:
            eeg_signal: EEG data (1D array)
            verbose: Print intermediate results

        Returns:
            dict with 'sentence', 'confidence', 'freq_extracted', 'matches'
        """
        # Extract frequency from EEG
        freq_result = self.extract_frequency(eeg_signal)
        extracted_freq = freq_result["frequency"]

        if verbose:
            print(f"Extracted frequency: {extracted_freq:.2f} Hz")
            print(f"Peak power: {freq_result['power']:.2f} µV")
            print()

        # Match to sentence candidates
        matches = []
        for sent, sent_freq in self.sentence_freqs.items():
            # Frequency error (Hz)
            error = abs(extracted_freq - sent_freq)

            # Confidence: inverse of error (Gaussian)
            # Max confidence when error = 0
            # Drops by half at error = 0.5 Hz
            confidence = np.exp(-error**2 / (2 * 0.5**2))

            matches.append(
                {
                    "sentence": sent,
                    "sentence_freq": sent_freq,
                    "freq_error": error,
                    "confidence": confidence,
                }
            )

        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)

        if verbose:
            print("Sentence candidates:")
            for i, m in enumerate(matches, 1):
                print(
                    f"  {i}. {m['sentence']:40s} ({m['sentence_freq']:.2f} Hz) → "
                    f"error={m['freq_error']:.2f} Hz, confidence={m['confidence']:.1%}"
                )
            print()

        return {
            "sentence": matches[0]["sentence"],
            "confidence": matches[0]["confidence"],
            "freq_extracted": extracted_freq,
            "matches": matches,
        }

    def stream(self, eeg_stream, chunk_size=256, overlap=128):
        """
        Process continuous EEG stream.

        Args:
            eeg_stream: Continuous EEG data (1D array, any length)
            chunk_size: Samples per prediction (256 = 1 sec at 256 Hz)
            overlap: Overlap between chunks (samples)

        Yields:
            Predictions from each chunk
        """
        stride = chunk_size - overlap
        for i in range(0, len(eeg_stream) - chunk_size, stride):
            chunk = eeg_stream[i : i + chunk_size]
            yield self.decode(chunk)


def demo():
    """Demonstrate BCI with synthetic EEG data."""
    print("=" * 70)
    print("BCI DEMO: Decode sentences from synthetic EEG")
    print("=" * 70)
    print()

    # Sentence set (small, easy to test)
    sentences = [
        "Yes",
        "No",
        "Help",
        "Water",
        "The cat sat on the mat.",
        "I think that is strange.",
    ]

    # Create BCI
    bci = BCIEEGDecoder(sentences, sampling_rate=256)

    # Test 1: User thinks "Yes" → brain oscillates at "Yes" frequency
    print("-" * 70)
    print("TEST 1: User thinks 'Yes'")
    print("-" * 70)
    yes_freq = bci.sentence_freqs["Yes"]
    # Generate EEG with dominant oscillation at that frequency
    t = np.arange(256) / 256.0  # 1 second
    eeg_yes = (
        np.sin(2 * np.pi * yes_freq * t) + 0.3 * np.random.randn(256)
    )  # Signal + noise
    result = bci.decode(eeg_yes, verbose=True)
    print(f"✓ Decoded: {result['sentence']} (confidence: {result['confidence']:.1%})")
    print()

    # Test 2: User thinks "Help"
    print("-" * 70)
    print("TEST 2: User thinks 'Help'")
    print("-" * 70)
    help_freq = bci.sentence_freqs["Help"]
    eeg_help = np.sin(2 * np.pi * help_freq * t) + 0.3 * np.random.randn(256)
    result = bci.decode(eeg_help, verbose=True)
    print(f"✓ Decoded: {result['sentence']} (confidence: {result['confidence']:.1%})")
    print()

    # Test 3: Ambiguous case (halfway between two frequencies)
    print("-" * 70)
    print("TEST 3: Ambiguous - brain oscillates between two sentences")
    print("-" * 70)
    freq1 = bci.sentence_freqs["The cat sat on the mat."]
    freq2 = bci.sentence_freqs["I think that is strange."]
    mid_freq = (freq1 + freq2) / 2
    eeg_ambig = np.sin(2 * np.pi * mid_freq * t) + 0.3 * np.random.randn(256)
    result = bci.decode(eeg_ambig, verbose=True)
    print(f"✓ Best match: {result['sentence']} (confidence: {result['confidence']:.1%})")
    print()

    # Test 4: Real-time stream (simulated)
    print("-" * 70)
    print("TEST 4: Real-time streaming")
    print("-" * 70)
    print("Simulating 5 seconds of EEG (user thinking different sentences each second)")
    print()

    eeg_stream = np.array([])
    for sent in ["Yes", "Help", "Water", "The cat sat on the mat.", "I think that is strange."]:
        freq = bci.sentence_freqs[sent]
        t_chunk = np.arange(256) / 256.0
        chunk = np.sin(2 * np.pi * freq * t_chunk) + 0.2 * np.random.randn(256)
        eeg_stream = np.concatenate([eeg_stream, chunk])

    print("Processing stream (chunk_size=256, overlap=128)...")
    for i, pred in enumerate(bci.stream(eeg_stream, chunk_size=256, overlap=128)):
        t_sec = i
        print(f"  t={t_sec}s: {pred['sentence']:40s} (confidence: {pred['confidence']:.1%})")

    print()
    print("=" * 70)


if __name__ == "__main__":
    demo()
