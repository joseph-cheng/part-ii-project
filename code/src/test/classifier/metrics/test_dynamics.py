import classifier.metrics.dynamics as dynamics
import numpy as np
import unittest

class DynamicsTestCase(unittest.TestCase):
    def test_freqweighting(self):
        freqs = [100, 200, 400, 800, 1000, 5000, 12500]
        actual_weightings = [-19.8, -13.8, -7.8, -1.9, 0.0, 11.7, 0.0]

        for i, freq in enumerate(freqs):
            self.assertAlmostEqual(actual_weightings[i], dynamics.DynamicsCalculator.freqweighting(freq), places=0)



