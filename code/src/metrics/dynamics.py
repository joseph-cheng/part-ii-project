import numpy as np

def calculate_power(signal):
    """
    Calculates the power of a signal

    signal: a 1d np array to calculate the power of

    returns: a coefficient representing the power of the signal
    """


    return np.sqrt(sum(np.square(np.abs(signal), dtype="float64"))/len(signal))


def calculate_dynamics_metric(audio, window_size=0.04, window_advance=0.04):
    """
    Calculates the dynamic over time metric of a signal by taking the power of successive windows

    audio: an Audio object to calculate the dynamics metrics for
    window_size: the length in seconds a window should be calculated for
    window_advance: the length in seconds to advance to the next window

    returns: a 1D np array of powers of successive windows in the signal
    """

    power_array = np.zeros(int((audio.get_duration() - window_size) / window_advance))

    num_windows = len(power_array)
    for window in range(num_windows):
        window_start = int(window * window_advance * audio.sample_rate)
        window_end = int((window * window_advance + window_size) * audio.sample_rate)

        window_signal = audio.signal[window_start:window_end]
        power_array[window] = calculate_power(window_signal)

    return (window_advance, power_array)


def dynamics_metric_similarity(audio1, audio2, metric1, metric2):
    """
    Calculates the similarity between two dynamics metrics

    audio1: audio signal corresponding to metric1 (need for alignment) 
    audio2: audio signal corresponding to metric2 (need for alignment)
    metric1: an output of the calculate_dynamics_metric function
    metric2: another output of the calculate_dynamics_metric function

    returns: a number between 0 and 1 representing the similarity between the two metrics
    """

    # to find the similarity, we find the sum of the squared errors

    # we also normalise the metrics to the max dynamic meausred by the two metrics, because we care about relative difference

    # unfortunately, the two signals might not be aligned, so we find the first beat time after 0 and align to this point instead, and we truncate to the smaller array

    first_beat1 = audio1.get_beat_times()[1]
    first_beat2 = audio2.get_beat_times()[1]

    # now we truncate the start of each signal up until the first beat

    window_advance1, power_array1 = metric1
    window_advance2, power_array2 = metric2

    starting_time_windows1 = first_beat1 // window_advance1
    starting_time_windows2 = first_beat2 // window_advance2

    power_array1 = power_array1[starting_time_windows1:]
    power_array2 = power_array2[starting_time_windows2:]

    # now we truncate the end off

    truncated_length = min(len(power_array1), len(power_array2))

    power_array1 = power_array1[:truncated_length]
    power_array2 = power_array2[:truncated_length]

    # normalisation
    highest_value = max(max(power_array1), max(power_array2))
    power_array1 = power_array1 / highest_value
    power_array2 = power_array2 / highest_value

    # now we find the sum of the squared errors

    squared_differences_sum = np.sum((power_array1 - power_array2)**2)

    # when the signals are identical, this value will be 0 (similarity=1), and can grow to be infinitely large, and similarity tapers to 0

    # for tis reason, we apply exp(-squared_differences_sum) to get our similarity score

    return np.exp(-squared_differences_sum)



    

