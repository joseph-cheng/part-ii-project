import util
import scipy.fft
import numpy as np
import matplotlib.pyplot as plt

def calculate_chroma_metric(audio, window_size=0.1, window_advance=0.025):
    """
    Calculates the pitch class profile or chroma metric of an audio signal

    audio: an Audio object containing the signal to calculate the metric for
    window_size: the size of the window to take spectras from in seconds
    window_advance: how far to move along the signal per window in seconds

    returns: a 12xn NP array containing a series of pitch class profiles for windows of the audio signal
    """

    chroma_array = np.zeros((int((audio.get_duration() - window_size) / window_advance), 12))
    num_windows = len(chroma_array)
    for window in range(num_windows):
        window_start = int(window * window_advance * audio.sample_rate)
        window_end = int((window * window_advance +
                      window_size) * audio.sample_rate)

        window_signal = audio.signal[window_start:window_end]

        #TODO: maybe apply hanning window?

        chroma_array[window] = calculate_pitch_profile(window_signal, audio.sample_rate)


    # now we normalise
    max_val = np.amax(chroma_array)
    chroma_array = chroma_array / max_val

    return (window_advance, chroma_array)



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
            ret[pitch % 12] += np.absolute(spectrum[index])


    return ret

def chroma_metric_similarity(audio1, audio2, metric1, metric2):
    """
    Calculates the similarity between two chroma metrics

    audio1: audio signal corresponding to metric1 (need for alignment) 
    audio2: audio signal corresponding to metric2 (need for alignment)
    metric1: an output of the calculate_chroma_metric function
    metric2: another output of the calculate_chroma_metric function

    returns: a number between 0 and 1 representing the similarity between the two metrics
    """

    # again, like timbre/dynamics, we take the sum of squared errors, where the error between two chroma profiles is the sum of the squared errors of each of the pitch classes

    # Furthermore, since the two signals might not be aligned, we find the first beat and align to that, and truncate the end

    first_beat1 = audio1.get_beat_times()[1]
    first_beat2 = audio2.get_beat_times()[1]

    # now we truncate the start of each signal up until the first beat

    window_advance1, chroma_array1 = metric1
    window_advance2, chroma_array2 = metric2

    starting_time_windows1 = first_beat1 // window_advance1
    starting_time_windows2 = first_beat2 // window_advance2

    chroma_array1 = chroma_array1[starting_time_windows1:]
    chroma_array2 = chroma_array2[starting_time_windows2:]

    # now we truncate the end

    truncated_length = min(len(chroma_array1), len(chroma_array2))
    chroma_array1 = chroma_array1[:truncated_length]
    chroma_array2 = chroma_array2[:truncated_length]

    # then we normalise to the highest value between the two 
    highest_value = max(np.amax(chroma_array1), np.amax(chroma_array2))
    chroma_array1 = chroma_array1 / highest_value
    chroma_array2 = chroma_array2 / highest_value

    # now calculate the error within each pcp
    pcp_errors = np.sum((chroma_array1 - chroma_array2) ** 2, axis=1)

    squared_errors_sum = np.sum(pcp_errors)

    # when the two metrics are identical, squared_errors_sum is 0, and becomes larger and larger the less similar the metrics are, so we apply exp(-squared_errors_sum) to get our metric

    return np.exp(-squared_errors_sum)

    



