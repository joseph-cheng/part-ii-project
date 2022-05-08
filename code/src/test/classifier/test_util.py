import classifier.util as util
import unittest

class ReadAudioTestCase(unittest.TestCase):
    def test_mono_file(self):
        audio = util.read_audio("../res/test_data/3samples.wav")

        self.assertEqual(audio.sample_rate, 44100)
        self.assertTrue((audio.signal == [0, 250, 500]).all())

    def test_stereo_file(self):
        audio = util.read_audio("../res/test_data/3samples_stereo.wav")

        self.assertEqual(audio.sample_rate, 44100)
        self.assertTrue((audio.signal == [0, 0, 0]).all())


class MovingAverageTestCase(unittest.TestCase):
    def test_moving_average_smaller_than_window(self):
        data = [0,2,4]
        average = util.moving_average(data, 5)
        self.assertTrue((average == [0, 1, 2]).all())

    def test_moving_average_regular_window(self):
        data = [0,2,4,6,8]
        average = util.moving_average(data, 2)
        self.assertTrue((average == [0,1,3,5,7]).all())
