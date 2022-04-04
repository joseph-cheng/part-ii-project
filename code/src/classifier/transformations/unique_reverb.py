import numpy as np
import scipy.io.wavfile
import util
import audio
import transformations.transformation as transformation

class UniqueReverb(transformation.Transformation):
    def __init__(self, irs):
        """
        ir: path to a wavfile containing the impulse reseponse
        """
        self.ir_paths = irs
        self.irs = [util.read_audio(ir).signal for ir in irs]

    def apply(self, audio_obj, out=None):
        """
        applies reverb to a signal, using a convolutional method

        audio_obj: Audio object representing the signal to apply reverb to
        out: optionally a path to where a wav file of the reverbed audio should be saved

        returns: an Audio object containing the reverbed signal
        """

        sample_rate = audio_obj.sample_rate
        signal = audio_obj.signal

        # find the performer name
        audio_name = audio_obj.name.split("_")
        performer_num = int(audio_name[-3])

        ir = self.irs[performer_num - 1]
        print(self.ir_paths[performer_num - 1])

        convolved = np.convolve(signal, ir)

        if out != None:
            # we normalise  to max 1.0 here to avoid clipping
            scipy.io.wavfile.write(out, sample_rate, convolved/max(convolved))

        return audio.Audio(convolved, sample_rate, name=audio_obj.name)

    def __repr__(self):
        return f"Reverb | IRs : {self.ir_paths}"

