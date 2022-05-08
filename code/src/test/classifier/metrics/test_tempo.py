import classifier.metrics.tempo as tempo
import numpy as np
import unittest
import classifier.util as util

class OnsetFunctionTestCase(unittest.TestCase):
    def setUp(self):
        self.data = np.array([0,1,50,2,3])
        self.window_advance = 5.0
        self.sample_rate = 1
        self.onset_func = tempo.OnsetFunction(self.data, self.window_advance, self.sample_rate)

    def test_index_samples(self):
        index_wanted = 2
        samples = self.window_advance * index_wanted
        self.assertEqual(self.onset_func.index_samples(samples), self.data[index_wanted])

    def test_index_time(self):
        index_wanted = 2
        time = self.window_advance * index_wanted

        self.assertEqual(self.onset_func.index_time(time), self.data[index_wanted])

    def test_index_window(self):
        index_wanted = 2
        self.assertEqual(self.onset_func.index_window(index_wanted), self.data[index_wanted])



class TempoTestCase(unittest.TestCase):
    def setUp(self):
        self.audio = util.read_audio("../res/test_data/metronome.wav")

    def test_global_tempo(self):
        estimated_tempo = tempo.TempoCalculator.calculate_global_tempo(self.audio)
        self.assertEqual(estimated_tempo, 120)
