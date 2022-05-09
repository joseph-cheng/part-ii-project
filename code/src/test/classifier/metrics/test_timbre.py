import classifier.metrics.timbre as timbre
import classifier.util as util
import numpy as np
import unittest
import matplotlib.pyplot as plt


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

    def test_spectrum_to_mel_bands(self):
        spectrum = np.array([1 for _ in range(100)])
        sample_rate_hz = 6300*2
        sample_rate_mel = 2595
        mel_energies = timbre.TimbreCalculator.spectrum_to_mel_bands(spectrum, sample_rate_hz, num_filters=5)
        np.testing.assert_almost_equal(mel_energies, [3,5,7,10,15])

    def test_normalise_spectrum_up(self):
        audio = util.read_audio("../res/test_data/A.wav")
        pitch = 440
        target_pitch = 1000
        timbre_calculator = timbre.TimbreCalculator(target_pitch=target_pitch)
        spectrum = np.abs(np.fft.rfft(audio.signal))
        freqs = np.fft.rfftfreq(len(audio.signal), d = 1/audio.sample_rate)

        shifted_spectrum = timbre_calculator.normalise_spectrum(spectrum, freqs)
        self.assertAlmostEqual(freqs[np.argmax(shifted_spectrum)], target_pitch)









