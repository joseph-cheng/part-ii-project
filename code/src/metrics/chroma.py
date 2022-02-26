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

    # the way this works is we take the sum of squared errors at each beat time.

    beat_times1 = audio1.get_beat_times()
    beat_times2 = audio2.get_beat_times()

    # truncate to the shortest, in case they are different lengths
    truncated_length = min(len(beat_times1), len(beat_times2))

    truncated_beat_times1 = beat_times1[:truncated_length]
    truncated_beat_times2 = beat_times2[:truncated_length]

    window_advance1, chroma_array1 = metric1
    window_advance2, chroma_array2 = metric2

    # now convert each beat time into a window position

    window_beat_times1 = [int(beat_time / window_advance1) for beat_time in truncated_beat_times1]
    window_beat_times2 = [int(beat_time / window_advance2) for beat_time in truncated_beat_times2]

    #then, get the metric values at each of the windows

    # we don't do the np indexing because sometimes our beat time is too late in the audio for there to be a window

    pcp_at_beats1 = []
    pcp_at_beats2 = []

    for i in range(truncated_length):
        if i < len(chroma_array1) and i < len(chroma_array2):
            pcp_at_beats1.append(chroma_array1[i])
            pcp_at_beats2.append(chroma_array2[i])
        else:
            break

    # turn into np array later to avoid expensive copying
    pcp_at_beats1 = np.array(pcp_at_beats1)
    pcp_at_beats2 = np.array(pcp_at_beats2)


    # now calculate the sum of squared differences
    squared_differences_sum = np.sum((pcp_at_beats1 - pcp_at_beats2)**2)

    # now, we divide by the number of elements in our array to get the average squared difference sum

    # we need this or longer signals get really low squared difference sum values
    mse = squared_differences_sum / truncated_length

    # when signals are identical, this value is 0 (similarity=1), and can grow to be infinitely large, and the similarity should taper to 0

    # so, we apply exp(-x) to get similarity
    return np.exp(-mse)









            


    



