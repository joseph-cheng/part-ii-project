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



