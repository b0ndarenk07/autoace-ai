import numpy as np

from workers.audio.features.quality import assess_audio_quality


def test_assess_audio_quality_marks_normal_signal_clear():
    sample_rate = 16_000
    time = np.arange(sample_rate, dtype=np.float32) / sample_rate
    waveform = 0.1 * np.sin(2 * np.pi * 220 * time)

    result = assess_audio_quality(waveform, sample_rate)

    assert result["quality"] == "clear"


def test_assess_audio_quality_marks_quiet_signal_severely_impaired():
    waveform = np.ones(16_000, dtype=np.float32) * 0.001

    result = assess_audio_quality(waveform, 16_000)

    assert result["quality"] == "severely_impaired"


def test_assess_audio_quality_detects_clipping():
    waveform = np.ones(16_000, dtype=np.float32)

    result = assess_audio_quality(waveform, 16_000)

    assert result["quality"] == "severely_impaired"