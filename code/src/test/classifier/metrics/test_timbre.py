import classifier.metrics.timbre as timbre
import classifier.util as util
import numpy as np
import unittest


class TimbreTestCase(unittest.TestCase):
    def test_hertz_to_mel(self):
        hertz = 440
        mels = 549.6386754

        self.assertAlmostEqual(mels, timbre.TimbreCalculator.hertz_to_mel(hertz))

    def test_mel_to_hertz(self):
        mels = 549.6386754
        hertz = 440

        self.assertAlmostEqual(hertz, timbre.TimbreCalculator.mel_to_hertz(mels))

    def test_mel_bands(self):
        highest_freq_mel = 500
        sample_rate = timbre.TimbreCalculator.mel_to_hertz(highest_freq_mel) * 2
        num_bands = 5
        mel_bands = np.array([50,150,250,350,450])
        hertz_bands = timbre.TimbreCalculator.mel_to_hertz(mel_bands)

        calculated_bands = timbre.TimbreCalculator.calculate_band_freqs(sample_rate, num_filters=len(mel_bands))

        np.testing.assert_almost_equal(calculated_bands, hertz_bands)

    def test_spectrum_to_mel_bands(self)





