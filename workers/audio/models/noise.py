from __future__ import annotations

from typing import Any

import librosa
import numpy as np


NOISE_TYPES = (
    "traffic",
    "sharp static",
    "TV",
    "sports event",
    "crowd",
    "office chatter",
    "construction",
    "machinery",
    "music",
    "wind",
    "rain",
    "sirens",
    "background noise",
    "unknown",
)


def extract_noise_features(
    waveform: np.ndarray,
    sample_rate: int,
) -> dict[str, float]:
    if waveform.size == 0:
        raise ValueError("waveform is empty")

    spectral_centroid = librosa.feature.spectral_centroid(
        y=waveform,
        sr=sample_rate,
    )[0]

    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=waveform,
        sr=sample_rate,
    )[0]

    spectral_flatness = librosa.feature.spectral_flatness(y=waveform)[0]

    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=waveform)[0]

    rms = librosa.feature.rms(y=waveform)[0]
    onset_strength = librosa.onset.onset_strength(y=waveform, sr=sample_rate)
    onset_peaks = librosa.util.peak_pick(
        onset_strength,
        pre_max=3,
        post_max=3,
        pre_avg=3,
        post_avg=5,
        delta=0.5,
        wait=5,
    )

    return {
        "centroid": float(np.mean(spectral_centroid)),
        "bandwidth": float(np.mean(spectral_bandwidth)),
        "flatness": float(np.mean(spectral_flatness)),
        "zero_crossing_rate": float(np.mean(zero_crossing_rate)),
        "energy": float(np.mean(rms)),
        "energy_variability": float(np.std(rms)),
        "onset_rate": float(len(onset_peaks) / max(waveform.size / sample_rate, 1.0)),
    }


def classify_noise(
    features: dict[str, float],
) -> dict[str, Any]:
    energy = features["energy"]
    flatness = features["flatness"]
    centroid = features["centroid"]
    bandwidth = features["bandwidth"]
    energy_variability = features["energy_variability"]
    onset_rate = features.get("onset_rate", 0.0)

    if energy < 0.005:
        return {
            "present": False,
            "type": "",
            "severity": "none",
        }

    # Static tends to have broad frequency energy and high spectral flatness.
    if flatness >= 0.35 and bandwidth >= 2500:
        severity = "high" if flatness >= 0.55 else "medium"
        return {
            "present": True,
            "type": "sharp static",
            "severity": severity,
        }

    # High-frequency, noisy energy with steady variation is a rain baseline.
    if flatness >= 0.18 and centroid >= 2500 and energy_variability >= 0.015:
        return {
            "present": True,
            "type": "rain",
            "severity": "medium",
        }

    # Sirens have high pitch energy and strong changes over time.
    if centroid >= 1800 and energy_variability >= 0.025 and onset_rate < 1.5:
        return {
            "present": True,
            "type": "sirens",
            "severity": "high" if energy >= 0.05 else "medium",
        }

    # Repeating loud transients are common in construction or machinery.
    if onset_rate >= 1.5 and energy >= 0.02:
        noise_type = "construction" if flatness >= 0.2 else "machinery"
        return {
            "present": True,
            "type": noise_type,
            "severity": "high" if energy >= 0.08 else "medium",
        }

    # Sports events and crowds have energetic, variable broadband sound.
    if energy_variability >= 0.03 and bandwidth >= 2200:
        noise_type = "sports event" if onset_rate >= 0.8 else "crowd"
        return {
            "present": True,
            "type": noise_type,
            "severity": "high" if energy >= 0.06 else "medium",
        }

    # Speech-like background activity has moderate variation and bandwidth.
    if 1000 <= centroid <= 3500 and 1200 <= bandwidth <= 3000:
        return {
            "present": True,
            "type": "office chatter",
            "severity": "medium",
        }

    # Low-frequency, sustained energy is typical of traffic or wind.
    if centroid < 900 and bandwidth < 1800:
        noise_type = "wind" if energy_variability >= 0.02 else "traffic"
        return {
            "present": True,
            "type": noise_type,
            "severity": "medium" if energy >= 0.03 else "low",
        }

    # Rhythmic onsets with a broad spectrum are a useful music baseline.
    if onset_rate >= 0.5 and energy_variability >= 0.015:
        return {
            "present": True,
            "type": "music",
            "severity": "medium",
        }

    # TV-like background often has moderate energy and changing spectral content.
    if (
        800 <= centroid <= 3500
        and energy_variability >= 0.01
    ):
        return {
            "present": True,
            "type": "TV",
            "severity": "medium",
        }

    # Broad low-level environmental noise.
    if energy >= 0.01:
        return {
            "present": True,
            "type": "unknown",
            "severity": "low",
        }

    return {
        "present": False,
        "type": "",
        "severity": "none",
    }