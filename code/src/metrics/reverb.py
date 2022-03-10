import transformation
import util
from audio import Audio
import numpy as np

class Reverb(transformation.Transformation):
    def __init__(self, ir):
        """
        ir: path to a wavfile containing the impulse reseponse
        """
        self.ir_path = ir
        self.ir = util.read_audio(ir).signal

    def apply(self, audio, out=None):
        """
        applies reverb to a signal, using a convolutional method

        audio: Audio object representing the signal to apply reverb to
        out: optionally a path to where a wav file of the reverbed audio should be saved

        returns: an Audio object containing the reverbed signal
        """

        sample_rate = audio.sample_rate
        signal = audio.signal

        convolved = np.convolve(signal, self.ir)

        if out != None:
            scipy.io.wavfile.write(out, sample_rate, convolved)

        return Audio(convolved, sample_rate)

    def __repr__(self):
        return f"Reverb | IR : {self.ir_path}"

