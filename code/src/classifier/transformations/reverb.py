import numpy as np
import scipy.io.wavfile
import util
import audio
import transformations.transformation as transformation

class Reverb(transformation.Transformation):
    def __init__(self, ir):
        """
        ir: path to a wavfile containing the impulse reseponse
        """
        self.ir_path = ir
        self.ir = util.read_audio(ir).signal

    def apply(self, audio_obj, out=None):
        """
        applies reverb to a signal, using a convolutional method

        audio_obj: Audio object representing the signal to apply reverb to
        out: optionally a path to where a wav file of the reverbed audio should be saved

        returns: an Audio object containing the reverbed signal
        """

        sample_rate = audio_obj.sample_rate
        signal = audio_obj.signal

        convolved = np.convolve(signal, self.ir)

        if out != None:
            # we normalise  to max 1.0 here to avoid clipping
            scipy.io.wavfile.write(out, sample_rate, convolved/max(convolved))

        return audio.Audio(convolved, sample_rate, name=audio_obj.name)

    def __repr__(self):
        return f"Reverb | IR : {self.ir_path}"

