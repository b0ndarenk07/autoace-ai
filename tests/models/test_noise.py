from workers.audio.models.noise import classify_noise


def test_classify_noise_returns_controlled_type_for_traffic():
	result = classify_noise(
		{
			"energy": 0.02,
			"flatness": 0.1,
			"centroid": 500.0,
			"bandwidth": 1200.0,
			"energy_variability": 0.01,
			"onset_rate": 0.1,
		}
	)

	assert result == {
		"present": True,
		"type": "traffic",
		"severity": "low",
	}


def test_classify_noise_returns_no_noise_with_empty_type():
	result = classify_noise(
		{
			"energy": 0.001,
			"flatness": 0.0,
			"centroid": 0.0,
			"bandwidth": 0.0,
			"energy_variability": 0.0,
			"onset_rate": 0.0,
		}
	)

	assert result == {
		"present": False,
		"type": "",
		"severity": "none",
	}
