import numpy as np

from workers.audio.features.acoustic import (
    estimate_speaker_overlap,
    extract_acoustic_features,
)


def test_extract_acoustic_features_returns_signal_measurements():
    sample_rate = 16_000
    time = np.arange(sample_rate, dtype=np.float32) / sample_rate
    waveform = 0.2 * np.sin(2 * np.pi * 220 * time)

    features = extract_acoustic_features(waveform, sample_rate)

    assert features["rms_mean"] > 0.0
    assert features["spectral_centroid"] > 0.0
    assert 0.0 <= features["voiced_ratio"] <= 1.0


def test_estimate_speaker_overlap_is_conservative():
    features = {
        "voiced_ratio": 0.8,
        "pitch_std": 120.0,
        "rms_std": 0.04,
    }

    assert estimate_speaker_overlap(features) is True