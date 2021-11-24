import util
import scipy.fft
import numpy as np

def calculate_chroma_metric(audio, window_size=0.032, window_advance=0.004):
    """
    Calculates the pitch class profile or chroma metric of an audio signal

    audio: an Audio object containing the signal to calculate the metric for
    window_size: the size of the window to take spectras from in seconds
    window_advance: how far to move along the signal per window in seconds

    returns: a 12xn NP array containing a series of pitch class profiles for windows of the audio signal
    """

    chroma_array = np.zeros((audio.get_duration() - window_size) / window_advance)
    num_windows = len(chroma_array)
    for window in num_windows:
        window_start = window * window_advance * audio.sample_rate
        window_end = (window * window_advance +
                      window_size) * audio.sample_rate

        window_signal = audio.signal[window_start:window_end]

        chroma_array[window] = calculate_pitch_profile(window_signal, audio.sample_rate)

    return chroma_array



def calculate_pitch_profile(signal, sample_rate):
    """
    Calculates the pitch profile of a signal

    signal: a signal to calculate the pitch profile for
    sample_rate: the sample rate of the signal

    returns: a 12-length NP array containing a coefficient for each pitch class
    """

    spectrum = scipy.fft.rfft(signal)
    max_frequency = sample_rate/2

    freq_to_index = lambda f: int(f * (len(spectrum)/max_frequency))

    ret = np.zeros(12)

    for pitch in range(128):
        lower_frequency = int(2 ** ((pitch - 0.5 - 69)/12) * 440)
        upper_frequency = int(2 ** ((pitch + 0.5 - 69)/12) * 440)

        for index in range(freq_to_index(lower_frequency), freq_to_index(upper_frequency)):
            ret[pitch // 12] += spectrum[index]

    return ret
