#!/usr/bin/env python3
"""
EEG Hardware Driver: Connect to Muse/Emotiv headsets or simulate data.

This module provides a unified interface for EEG hardware:
- Muse 2/S via BlueMuse or muse-lsl
- Emotiv EPOC X via Emotiv SDK
- Simulator for testing without hardware

Install hardware drivers:
  # Muse via Lab Streaming Layer
  pip install pylsl

  # Emotiv (requires registration at emotiv.com)
  pip install cortex-python

Usage:
  # Muse via LSL (preferred, no SDK needed)
  driver = MuseLSL()
  driver.start()
  eeg_data = driver.read(duration=1.0)  # Read 1 second
  driver.stop()

  # Emotiv (requires Emotiv app running)
  driver = EmotivDriver(username="user@example.com", password="pwd")
  driver.start()
  eeg_data = driver.read(duration=1.0)
  driver.stop()

  # Simulator (no hardware needed)
  driver = SimulatedEEG()
  driver.start()
  eeg_data = driver.read(duration=1.0)
  driver.stop()
"""

import numpy as np
import threading
import time
from collections import deque
from abc import ABC, abstractmethod


class EEGDriver(ABC):
    """Abstract base class for EEG drivers."""

    def __init__(self, sampling_rate=256, channels=1):
        self.sampling_rate = sampling_rate
        self.channels = channels
        self.running = False
        self.buffer = None

    @abstractmethod
    def start(self):
        """Start recording."""
        pass

    @abstractmethod
    def stop(self):
        """Stop recording."""
        pass

    @abstractmethod
    def read(self, duration=None):
        """Read EEG data. Returns (n_samples, n_channels) array."""
        pass


class SimulatedEEG(EEGDriver):
    """Simulator that generates synthetic EEG data."""

    def __init__(self, sampling_rate=256, channels=1, target_frequency=None):
        super().__init__(sampling_rate, channels)
        self.target_frequency = target_frequency or 6.0
        self.buffer = deque(maxlen=sampling_rate * 10)  # 10 second buffer
        self.recording_thread = None

    def start(self):
        """Start recording synthetic EEG."""
        self.running = True
        self.recording_thread = threading.Thread(target=self._generate_eeg)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        print(f"Simulated EEG started (target frequency: {self.target_frequency:.1f} Hz)")

    def stop(self):
        """Stop recording."""
        self.running = False
        if self.recording_thread:
            self.recording_thread.join()
        print("Simulated EEG stopped")

    def _generate_eeg(self):
        """Generate synthetic EEG with target oscillation."""
        t = 0
        dt = 1.0 / self.sampling_rate

        while self.running:
            # Generate EEG with dominant frequency
            oscillation = np.sin(2 * np.pi * self.target_frequency * t)
            noise = 0.3 * np.random.randn()
            sample = oscillation + noise

            self.buffer.append([sample])
            t += dt
            time.sleep(dt * 0.9)  # Slight speedup to prevent lag

    def read(self, duration=None):
        """
        Read EEG data.

        Args:
            duration: Seconds to read (None = all available)

        Returns:
            numpy array (n_samples, n_channels)
        """
        if duration is None:
            # Return all buffered data
            data = np.array(list(self.buffer))
        else:
            # Read exactly `duration` seconds
            n_samples = int(duration * self.sampling_rate)
            data = np.zeros((n_samples, self.channels))

            for i in range(n_samples):
                if self.buffer:
                    data[i] = self.buffer.popleft()
                else:
                    # Wait for data
                    time.sleep(1.0 / self.sampling_rate)
                    if self.buffer:
                        data[i] = self.buffer.popleft()

        return data


class MuseLSL(EEGDriver):
    """Muse headset via Lab Streaming Layer (LSL)."""

    def __init__(self, sampling_rate=256, channels=4):
        super().__init__(sampling_rate, channels)
        self.stream_info = None
        self.inlet = None

        try:
            import pylsl

            self.pylsl = pylsl
        except ImportError:
            raise ImportError(
                "pylsl not installed. Install with: pip install pylsl"
            )

    def start(self):
        """Start recording from Muse via LSL."""
        # Find Muse stream
        streams = self.pylsl.resolve_byprop("type", "EEG", timeout=5)

        if not streams:
            raise RuntimeError(
                "Muse not found. Make sure:\n"
                "  1. Muse is paired (Bluetooth)\n"
                "  2. BlueMuse is running on Windows\n"
                "  3. OR muse-lsl is running: pip install muse-lsl && muse-lsl\n"
                "  4. OR connect manually via: python -m muse_lsl.stream"
            )

        print(f"Found Muse stream: {streams[0].name()}")
        self.inlet = self.pylsl.StreamInlet(streams[0])
        self.running = True

    def stop(self):
        """Stop recording."""
        self.running = False

    def read(self, duration=1.0):
        """
        Read EEG data from Muse.

        Args:
            duration: Seconds to read

        Returns:
            numpy array (n_samples, n_channels)
        """
        n_samples = int(duration * self.sampling_rate)
        data = np.zeros((n_samples, self.channels))

        for i in range(n_samples):
            sample, _ = self.inlet.pull_sample()
            data[i] = sample

        return data


class EmotivDriver(EEGDriver):
    """Emotiv EPOC X via Emotiv SDK."""

    def __init__(self, username, password, sampling_rate=256, channels=14):
        super().__init__(sampling_rate, channels)
        self.username = username
        self.password = password
        self.cortex = None

        try:
            from cortex import Cortex
            self.Cortex = Cortex
        except ImportError:
            raise ImportError(
                "cortex-python not installed. Install with: "
                "pip install cortex-python\n"
                "Also register at: https://www.emotiv.com/api/"
            )

    def start(self):
        """Start recording from Emotiv."""
        self.cortex = self.Cortex(username=self.username, password=self.password)
        self.cortex.connect()
        # Headset must be plugged in and running Emotiv app
        self.cortex.start_stream()
        print(f"Emotiv connected ({self.channels} channels)")

    def stop(self):
        """Stop recording."""
        if self.cortex:
            self.cortex.stop_stream()
            self.cortex.disconnect()

    def read(self, duration=1.0):
        """Read EEG data from Emotiv."""
        n_samples = int(duration * self.sampling_rate)
        data = np.zeros((n_samples, self.channels))

        for i in range(n_samples):
            sample = self.cortex.get_latest_sample()
            if sample:
                data[i] = sample

        return data


def get_driver(backend="simulated", **kwargs):
    """
    Get an EEG driver.

    Args:
        backend: "simulated", "muse", or "emotiv"
        **kwargs: Arguments for the driver (e.g., username, password for Emotiv)

    Returns:
        EEGDriver instance
    """
    if backend == "simulated":
        return SimulatedEEG(**kwargs)
    elif backend == "muse":
        return MuseLSL(**kwargs)
    elif backend == "emotiv":
        return EmotivDriver(**kwargs)
    else:
        raise ValueError(
            f"Unknown backend: {backend}. "
            "Choose from: simulated, muse, emotiv"
        )


def demo():
    """Demonstrate EEG driver with simulator."""
    print("=" * 70)
    print("EEG HARDWARE DEMO")
    print("=" * 70)
    print()

    # Start simulated EEG at 6.5 Hz
    print("Starting simulator (target frequency = 6.5 Hz)...")
    driver = SimulatedEEG(target_frequency=6.5)
    driver.start()
    time.sleep(0.5)

    # Read 2 seconds
    print("Reading 2 seconds of EEG data...")
    eeg_data = driver.read(duration=2.0)
    print(f"Acquired {eeg_data.shape[0]} samples, {eeg_data.shape[1]} channels")

    # Compute frequency spectrum
    from scipy.fft import fft, fftfreq
    from scipy.signal.windows import hann

    windowed = eeg_data[:, 0] * hann(len(eeg_data))
    freqs = fftfreq(len(windowed), 1.0 / driver.sampling_rate)
    power = np.abs(fft(windowed))

    # Find peak in 4-12 Hz band
    mask = (freqs >= 4) & (freqs <= 12)
    peak_idx = np.argmax(power[mask])
    peak_freq = freqs[mask][peak_idx]

    print(f"Detected frequency: {peak_freq:.2f} Hz")
    print()

    driver.stop()

    print("=" * 70)


if __name__ == "__main__":
    demo()
