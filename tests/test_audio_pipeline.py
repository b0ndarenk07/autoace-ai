from workers.audio.pipeline import analyze_audio, failsafe_analyze_audio


def test_analyze_audio_returns_prediction_schema():
    result = analyze_audio(b"fake-audio-bytes-for-ogg", "sample.ogg")

    assert result["name"] == "sample.ogg"
    assert result["emotional_tone"] in {
        "neutral",
        "satisfied",
        "frustrated",
        "upset",
        "distressed",
    }
    assert result["emotional_intensity"] in {"low", "medium", "high"}
    assert isinstance(result["background_noise_present"], bool)
    assert result["background_noise_type"]
    assert result["background_noise_severity"] in {"none", "low", "medium", "high"}
    assert result["audio_quality"] in {
        "clear",
        "slightly_impaired",
        "severely_impaired",
    }
    assert isinstance(result["speaker_overlap_present"], bool)
    assert isinstance(result["long_silence_present"], bool)
    assert 0.0 <= result["confidence"] <= 1.0


def test_failsafe_analyze_audio_returns_valid_schema_on_error():
    result = failsafe_analyze_audio(b"", "sample.ogg")

    assert result["name"] == "sample.ogg"
    assert result["emotional_tone"] in {
        "neutral",
        "satisfied",
        "frustrated",
        "upset",
        "distressed",
    }
    assert result["emotional_intensity"] in {"low", "medium", "high"}
    assert isinstance(result["background_noise_present"], bool)
    assert result["background_noise_type"]
    assert result["background_noise_severity"] in {"none", "low", "medium", "high"}
    assert result["audio_quality"] in {
        "clear",
        "slightly_impaired",
        "severely_impaired",
    }
    assert isinstance(result["speaker_overlap_present"], bool)
    assert isinstance(result["long_silence_present"], bool)
    assert 0.0 <= result["confidence"] <= 1.0
