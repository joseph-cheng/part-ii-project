import numpy as np
import scipy.io.wavfile
import audio
import util
import transformations.transformation as transformation

class Noise(transformation.Transformation):
    def __init__(self, noise, crossfade=0.5):
        """
        noise: path to a wavfile containing the noise
        crossfade: time in seconds that the noise should crossfade, in case we need to repeat it. defaults to 0.5
        """
        self.noise_path = noise
        self.noise = util.read_audio(noise).signal
        self.crossfade = crossfade

    def apply(self, audio_obj, out=None):
        """
        adds background noise to a signal, using pre-recorded noise

        audio_obj: Audio object containing the file to apply noise to
        out: optionally a path to where a wav file of the noise-added-audio should be saved

        returns: an Audio object containing the noise-added-audio
        """

        signal = audio_obj.signal
        # we naively interpret the noise's sample rate as the same as the audios, probably fine
        sample_rate = audio_obj.sample_rate

        # might need to repeat noise if it is not long enough, or truncate it if it is too long
        length_matched_noise = self.noise
        while len(length_matched_noise) < len(signal):
            crossfade_length_samples = int(self.crossfade * sample_rate)
            crossfade_down = np.linspace(1, 0, crossfade_length_samples)
            crossfade_up = np.linspace(0, 1, crossfade_length_samples)

            crossfade_out = length_matched_noise[-crossfade_length_samples:] * crossfade_down
            crossfade_in = self.noise[:crossfade_length_samples] * crossfade_up

            # doesn't matter if we add too much noise, we truncate after this while loop
            length_matched_noise = np.concatenate((
                    length_matched_noise[:-crossfade_length_samples],
                    crossfade_out + crossfade_in,
                    self.noise[crossfade_length_samples:],
                    ))
        # truncate if too long
        if len(length_matched_noise) > len(signal):
            length_matched_noise = length_matched_noise[:len(signal)]

        noisy_signal = length_matched_noise + signal
        if out != None:
            scipy.io.wavfile.write(out, sample_rate, noisy_signal)

        return audio.Audio(noisy_signal, sample_rate)

    def __repr__(self):
        return f"Noise | path: {self.noise_path} | crossfade: {self.crossfade}"
