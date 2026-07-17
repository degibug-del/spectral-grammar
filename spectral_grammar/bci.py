"""
Brain-Computer Interface: Decode sentences from EEG frequency.

Real-time frequency extraction → sentence prediction.
"""

import numpy as np
from collections import deque
from typing import List, Tuple, Optional


class FrequencyDecoder:
    """Extract oscillation frequency from EEG signal."""

    def __init__(
        self,
        sampling_rate: float = 256.0,
        window_size: int = 256,
        freq_band: Tuple[float, float] = (4.0, 12.0)
    ):
        """
        Args:
            sampling_rate: Hz
            window_size: FFT window size
            freq_band: (low, high) Hz for analysis
        """
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.freq_band = freq_band

        # Precompute frequency bins
        self.freqs = np.fft.rfftfreq(window_size, 1.0 / sampling_rate)

    def extract_frequency(self, eeg_signal: np.ndarray) -> Tuple[float, float]:
        """
        Extract dominant frequency and power from EEG signal.

        Args:
            eeg_signal: [window_size] raw EEG values

        Returns:
            (frequency_Hz, power_normalized)
        """
        # Compute FFT
        fft = np.abs(np.fft.rfft(eeg_signal))
        power = fft ** 2

        # Get frequencies in band of interest
        mask = (self.freqs >= self.freq_band[0]) & (self.freqs <= self.freq_band[1])
        band_power = power[mask]
        band_freqs = self.freqs[mask]

        if len(band_freqs) == 0:
            return 5.0, 0.0

        # Peak frequency
        peak_idx = np.argmax(band_power)
        peak_freq = band_freqs[peak_idx]

        # Normalize power
        total_power = np.sum(band_power)
        peak_power = band_power[peak_idx] / (total_power + 1e-10)

        return float(peak_freq), float(peak_power)


class SentenceDecoder:
    """Decode which sentence user is thinking from brain frequency."""

    def __init__(self, sentence_candidates: List[str]):
        """
        Args:
            sentence_candidates: List of possible sentences
        """
        self.candidates = sentence_candidates
        # Store Δλ and predicted frequency for each
        self.candidate_frequencies = {}
        self._compute_candidate_frequencies()

    def _compute_candidate_frequencies(self):
        """Precompute frequency for each candidate sentence."""
        from spectral_grammar import analyze

        for sent in self.candidates:
            try:
                result = analyze(sent)
                self.candidate_frequencies[sent] = {
                    "delta_lambda": result.spectral_gap,
                    "frequency": result.frequency,
                    "confidence": result.confidence
                }
            except:
                self.candidate_frequencies[sent] = {
                    "delta_lambda": 0.5,
                    "frequency": 6.0,
                    "confidence": 0.5
                }

    def decode(self, observed_frequency: float) -> Tuple[str, float]:
        """
        Decode which sentence matches observed frequency.

        Args:
            observed_frequency: Measured brain frequency (Hz)

        Returns:
            (best_sentence, confidence)
        """
        best_sentence = None
        best_score = -float("inf")

        for sent, info in self.candidate_frequencies.items():
            pred_freq = info["frequency"]
            delta = abs(observed_frequency - pred_freq)

            # Score: higher is better (penalize large differences)
            score = info["confidence"] * np.exp(-delta / 1.0)

            if score > best_score:
                best_score = score
                best_sentence = sent

        # Confidence: how sure are we?
        confidence = min(1.0, best_score / 0.8)

        return best_sentence, confidence


class BCISystem:
    """Complete BCI system: EEG → frequency → sentence → speech."""

    def __init__(
        self,
        sentence_set: List[str],
        sampling_rate: float = 256.0,
        window_size: int = 256,
        update_rate: float = 2.0  # Hz
    ):
        """
        Args:
            sentence_set: List of possible sentences
            sampling_rate: EEG sampling rate
            window_size: FFT window size
            update_rate: How often to update predictions (Hz)
        """
        self.freq_decoder = FrequencyDecoder(sampling_rate, window_size)
        self.sent_decoder = SentenceDecoder(sentence_set)
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.update_interval = 1.0 / update_rate

        # For online tracking
        self.freq_history = deque(maxlen=10)
        self.freq_smoothed = 5.0

    def process_eeg(self, eeg_chunk: np.ndarray) -> Tuple[float, str, float]:
        """
        Process EEG data and predict sentence.

        Args:
            eeg_chunk: [window_size] EEG sample

        Returns:
            (frequency, predicted_sentence, confidence)
        """
        # Extract frequency
        freq, power = self.freq_decoder.extract_frequency(eeg_chunk)
        self.freq_history.append(freq)

        # Smooth frequency (moving average)
        self.freq_smoothed = np.mean(list(self.freq_history))

        # Decode sentence
        best_sent, confidence = self.sent_decoder.decode(self.freq_smoothed)

        return self.freq_smoothed, best_sent, confidence

    def stream(self, eeg_stream: np.ndarray, verbose: bool = True):
        """
        Process continuous EEG stream.

        Args:
            eeg_stream: [n_samples] continuous EEG
            verbose: Print predictions
        """
        n_windows = len(eeg_stream) // self.window_size
        predictions = []

        for i in range(n_windows):
            window = eeg_stream[i * self.window_size:(i + 1) * self.window_size]
            freq, sent, conf = self.process_eeg(window)

            predictions.append({
                "window": i,
                "frequency": freq,
                "sentence": sent,
                "confidence": conf
            })

            if verbose:
                print(f"[{i:03d}] f={freq:5.1f}Hz | {sent[:40]:40s} | conf={conf:.1%}")

        return predictions


# Example usage
def example_bci():
    """Demo BCI system."""
    import matplotlib.pyplot as plt

    # Sentence set
    sentences = [
        "The cat sat on the mat.",
        "The dog ran in the park.",
        "She saw the man with the telescope.",
        "The horse raced past the barn fell.",
        "I think that that is strange.",
    ]

    # Create BCI
    bci = BCISystem(sentences)

    # Simulate EEG (fake data)
    np.random.seed(42)
    n_samples = 2560  # 10 seconds at 256 Hz

    # Create synthetic EEG with embedded frequency
    t = np.arange(n_samples) / 256.0
    true_freq = 7.0  # 7 Hz (corresponds to clear structure)
    eeg = np.sin(2 * np.pi * true_freq * t) + 0.5 * np.random.randn(n_samples)

    # Process
    print("BCI System Test")
    print("=" * 70)
    print(f"True frequency: {true_freq} Hz")
    print(f"Sentence set: {len(sentences)} candidates")
    print("=" * 70)
    print()

    predictions = bci.stream(eeg, verbose=True)

    # Summary
    print()
    print("=" * 70)
    predicted_sentences = [p["sentence"] for p in predictions[-5:]]
    most_common = max(set(predicted_sentences), key=predicted_sentences.count)
    print(f"Best guess: {most_common}")
    print("=" * 70)

    return bci, predictions


if __name__ == "__main__":
    example_bci()
