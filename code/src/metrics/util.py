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


def moving_average(data, n):
    """
    Calculates the moving average of an array of data. Implementation taken from https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-python-numpy-scipy

    data: a NP array to take the average over
    n: size of window to take average over
    """
    ret = np.cumsum(data)
    ret[n:] = ret[n:] - ret[:-n]

    # correctly take moving average for first n-2 elements
    for k in range(n-1):
        ret[k] /= (k+1)

    ret[n-1:] = ret[n-1:] / n
    return ret
