import classifier.metrics.chroma as chroma
import numpy as np
import unittest
import classifier.util as util
import matplotlib.pyplot as plt

class ChromaTestCase(unittest.TestCase):
    def test_single_pitch(self):
        audio = util.read_audio("../res/test_data/A.wav")

        pitch_profile = chroma.ChromaCalculator.calculate_pitch_profile(audio.signal, audio.sample_rate)
        pitch_profile /= max(pitch_profile)

        np.testing.assert_array_almost_equal(pitch_profile, [0,0,0,0,0,0,0,0,0,1,0,0], decimal=3)

    def test_combined_pitch(self):
        audio = util.read_audio("../res/test_data/A_and_E.wav")
        pitch_profile = chroma.ChromaCalculator.calculate_pitch_profile(audio.signal, audio.sample_rate)
        pitch_profile /= max(pitch_profile)

        self.assertCountEqual([4,9], np.argsort(pitch_profile)[-2:])


