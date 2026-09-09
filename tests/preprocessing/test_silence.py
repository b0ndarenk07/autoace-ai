import numpy as np

from workers.audio.features.silence import detect_silence


def test_detect_silence_finds_sustained_silence():
    sample_rate = 16_000
    waveform = np.concatenate(
        [
            np.ones(sample_rate, dtype=np.float32) * 0.1,
            np.zeros(sample_rate * 2, dtype=np.float32),
            np.ones(sample_rate, dtype=np.float32) * 0.1,
        ]
    )

    result = detect_silence(waveform, sample_rate)

    assert result["long_silence_present"] is True
    assert result["longest_silence_seconds"] >= 1.0


def test_detect_silence_does_not_mark_short_pause_as_long():
    sample_rate = 16_000
    waveform = np.concatenate(
        [
            np.ones(sample_rate, dtype=np.float32) * 0.1,
            np.zeros(sample_rate // 2, dtype=np.float32),
            np.ones(sample_rate, dtype=np.float32) * 0.1,
        ]
    )

    result = detect_silence(waveform, sample_rate)

    assert result["long_silence_present"] is False