import numpy as np

from workers.audio.preprocessing.normalizer import normalize_waveform


def test_normalize_waveform_removes_dc_offset_and_limits_peak():
    waveform = np.array([0.5, 1.5, 0.5], dtype=np.float32)

    normalized = normalize_waveform(waveform)

    assert np.isclose(np.mean(normalized), 0.0)
    assert np.isclose(np.max(np.abs(normalized)), 0.95)


def test_normalize_waveform_does_not_amplify_silence():
    waveform = np.zeros(100, dtype=np.float32)

    normalized = normalize_waveform(waveform)

    assert np.array_equal(normalized, waveform)