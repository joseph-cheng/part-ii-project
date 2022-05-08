import classifier.metrics.offsets as offsets
import numpy as np
import unittest
import classifier.util as util

class OffsetsTestCase(unittest.TestCase):
    def test_best_nearest_onset(self):
        audio = util.read_audio("../res/test_data/metronome.wav")
        tempo = 120
        epsilon = 0.01

        # construct a fake beat time
        actual_beat_time = 60/tempo
        off_beat_time = actual_beat_time + epsilon


        onset_distance, _ = offsets.OffsetsCalculator.get_best_nearest_onset(audio.get_onset_function(), off_beat_time, 0.1)

        # have to account for granularity of windows
        self.assertAlmostEqual(onset_distance, actual_beat_time - off_beat_time, places=2)

    def test_divergence(self):

        mean1 = 2
        stdev1 = 3

        mean2 = 3
        stdev2 = 1.1

        kl_divergence = offsets.OffsetsCalculator.calculate_divergence(mean1, stdev1, mean2, stdev2)

        self.assertAlmostEqual(kl_divergence, 2.6289, 4)


