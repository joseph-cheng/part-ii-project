import classifier.audio as audio
import numpy as np
import unittest

class AudioTestCase(unittest.TestCase):
    def setUp(self):
        self.data = np.array([0,1,2,3,4])
        self.sample_rate = 44100
        self.audio = audio.Audio(self.data, self.sample_rate)

    def test_caching(self):
        metric_name = "MyMetric"
        value = 111
        self.audio.cache_metric(metric_name, value)
        self.assertEqual(self.audio.get_cached_metric(metric_name), value)

    def test_duration(self):
        actual_duration = len(self.data) / self.sample_rate
        self.assertEqual(self.audio.get_duration(), actual_duration)

    def test_to_seconds(self):
        self.assertEqual(self.audio.to_seconds(self.sample_rate), 1.0)

    def test_to_samples(self):
        self.assertEqual(self.audio.to_samples(1.0), self.sample_rate)

