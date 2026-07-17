#!/usr/bin/env python3
"""
Spectral Grammar BCI Application

Complete brain-to-speech pipeline:
  1. Capture brain oscillation (EEG)
  2. Decode which sentence they're thinking about
  3. Speak it back via text-to-speech

This is a paralyzed-patient communication system.

Usage:
  python bci_app.py --backend simulated --duration 10
  python bci_app.py --backend muse --duration 30
  python bci_app.py --backend emotiv --username user@example.com --password pwd
"""

import argparse
import time
import numpy as np
from bci_eeg_decoder import BCIEEGDecoder
from eeg_hardware_driver import get_driver


def speak(text):
    """Speak text using system text-to-speech."""
    import os
    import platform

    system = platform.system()
    if system == "Darwin":  # macOS
        os.system(f'say "{text}"')
    elif system == "Linux":
        os.system(f'espeak "{text}"')
    elif system == "Windows":
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"[SPEAK] {text}")


class BCIApplication:
    """BCI app: EEG → decode → speech."""

    def __init__(
        self,
        sentences,
        backend="simulated",
        chunk_size=256,
        confidence_threshold=0.6,
        **kwargs
    ):
        """
        Initialize BCI app.

        Args:
            sentences: List of sentences the user can think about
            backend: "simulated", "muse", or "emotiv"
            chunk_size: EEG samples per prediction (256 = 1 sec at 256 Hz)
            confidence_threshold: Only decode if confidence > this
            **kwargs: Arguments for EEG driver
        """
        self.sentences = sentences
        self.chunk_size = chunk_size
        self.confidence_threshold = confidence_threshold

        print("Initializing BCI Application...")
        print(f"  Backend: {backend}")
        print(f"  Sentences: {len(sentences)}")
        print(f"  Chunk size: {chunk_size} samples")
        print(f"  Confidence threshold: {confidence_threshold:.1%}")
        print()

        # Initialize EEG driver
        self.driver = get_driver(backend, **kwargs)

        # Initialize BCI decoder
        self.decoder = BCIEEGDecoder(sentences, sampling_rate=256)

    def run(self, duration=60, display_interval=1.0):
        """
        Run BCI in real-time.

        Args:
            duration: Total seconds to run
            display_interval: Update display every N seconds
        """
        print("=" * 70)
        print("BRAIN-TO-SPEECH BCI")
        print("=" * 70)
        print()
        print("Instructions:")
        print("  1. Think about one of these sentences:")
        for sent in self.sentences:
            print(f"     - {sent}")
        print()
        print("  2. Maintain your thought for 1 second")
        print("  3. The system will decode what you're thinking")
        print("  4. Listen to the text-to-speech output")
        print()
        print("-" * 70)
        print()

        self.driver.start()
        time.sleep(1)  # Let driver stabilize

        start_time = time.time()
        last_display = time.time()
        n_decoded = 0
        last_predictions = []

        try:
            while time.time() - start_time < duration:
                # Read 1 second of EEG
                eeg_chunk = self.driver.read(duration=1.0)

                if len(eeg_chunk) == 0:
                    continue

                # Decode
                pred = self.decoder.decode(eeg_chunk, verbose=False)

                # Check confidence
                if pred["confidence"] >= self.confidence_threshold:
                    n_decoded += 1
                    last_predictions.append(pred["sentence"])

                    # Display prediction
                    elapsed = time.time() - start_time
                    print(
                        f"t={elapsed:6.1f}s: DECODED '{pred['sentence']}' "
                        f"({pred['confidence']:.0%} confidence)"
                    )

                    # Speak it
                    speak(pred["sentence"])

                # Periodic display of stats
                if time.time() - last_display >= display_interval:
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        rate = n_decoded / elapsed
                        print(
                            f"[{elapsed:6.1f}s] "
                            f"Successful decodes: {n_decoded}, "
                            f"Rate: {rate:.2f} Hz"
                        )
                    last_display = time.time()

        except KeyboardInterrupt:
            print("\n\nStopped by user")

        finally:
            self.driver.stop()

        print()
        print("=" * 70)
        print("SESSION SUMMARY")
        print("=" * 70)
        elapsed = time.time() - start_time
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Successful decodes: {n_decoded}")
        if elapsed > 0:
            print(f"Decode rate: {n_decoded / elapsed:.2f} Hz")

        # Most common predictions
        if last_predictions:
            from collections import Counter

            counts = Counter(last_predictions)
            print()
            print("Prediction distribution:")
            for sent, count in counts.most_common():
                print(f"  {sent:40s}: {count} times")


def main():
    parser = argparse.ArgumentParser(
        description="BCI Application: Decode thoughts from EEG"
    )
    parser.add_argument(
        "--sentences",
        type=str,
        default="Yes,No,Help,Water,The cat sat on the mat.,I think that is strange.",
        help="Comma-separated list of sentences",
    )
    parser.add_argument(
        "--backend", type=str, default="simulated", help="EEG backend: simulated, muse, emotiv"
    )
    parser.add_argument(
        "--duration", type=int, default=10, help="Duration in seconds"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=256, help="Samples per prediction"
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.6,
        help="Confidence threshold for decoding (0-1)",
    )
    parser.add_argument(
        "--username", type=str, help="Emotiv username (if using emotiv backend)"
    )
    parser.add_argument(
        "--password", type=str, help="Emotiv password (if using emotiv backend)"
    )

    args = parser.parse_args()

    # Parse sentences
    sentences = [s.strip() for s in args.sentences.split(",")]

    # Prepare driver kwargs
    driver_kwargs = {}
    if args.backend == "emotiv":
        if not args.username or not args.password:
            print("Error: --username and --password required for emotiv backend")
            return 1
        driver_kwargs["username"] = args.username
        driver_kwargs["password"] = args.password

    # Create and run app
    app = BCIApplication(
        sentences,
        backend=args.backend,
        chunk_size=args.chunk_size,
        confidence_threshold=args.confidence_threshold,
        **driver_kwargs
    )

    app.run(duration=args.duration)
    return 0


if __name__ == "__main__":
    exit(main())
