import classifier.util as util
import unittest

class ReadAudioTestCase(unittest.TestCase):
    def test_mono_file(self):
        audio = util.read_audio("../res/test_data/3samples.wav")
        self.assertEqual(audio.rate, 44100)
