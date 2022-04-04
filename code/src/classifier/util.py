import scipy.io.wavfile
import numpy as np
from audio import Audio
import matplotlib.pyplot as plt

def read_audio(wavfile_path):
    """
    wavfile_path: string of the path to a WAV file that contains the audio that should be read

    returns: an Audio object containing the mono signal
    """

    rate, data = scipy.io.wavfile.read(wavfile_path)
    if data.ndim > 1:
        # mix to mono
        data = np.mean(data, axis=1)
    return Audio(data, rate, name=wavfile_path)


def moving_average(data, n):
    """
    Calculates the moving average of an array of data.

    data: a NP array to take the average over
    n: size of window to take average over
    """
    ret = np.cumsum(data)
    ret[n:] = ret[n:] - ret[:-n]

    # correctly take moving average for first n-2 elements
    for k in range(min(n-1, len(data)-1)):
        ret[k] /= (k+1)

    ret[n-1:] = ret[n-1:] / n
    return ret

