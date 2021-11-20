import scipy.wavfile
import numpy as np
from audio import Audio

def read_audio(wavfile_path):
    """
    wavfile_path: string of the path to a WAV file that contains the audio that should be read

    returns: an Audio object containing the mono signal
    """

    rate, data = scipy.wavfile.read(wavfile)
    if data.ndim > 1:
        # mix to mono
        data = np.mean(data, axis=1)
    return Audio(data, rate)


