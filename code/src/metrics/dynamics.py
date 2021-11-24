import numpy as np

def calculate_power(signal):
    """
    Calculates the power of a signal

    signal: a 1d np array to calculate the power of

    returns: a coefficient representing the power of the signal
    """

    return sum(abs(signal) ** 2)/len(signal)

def calculate_dynamics_metric(audio, window_size=0.32, window_advance=0.04):
    """
    Calculates the dynamic over time metric of a signal by taking the power of successive windows

    audio: an Audio object to calculate the dynamics metrics for
    window_size: the length in seconds a window should be calculated for
    window_advance: the length in seconds to advance to the next window

    returns: a 1D np array of powers of successive windows in the signal
    """

    power_array = np.zeros((audio.get_duration() - window_size) / window_advance)

    num_windows = len(power_array)
    for window in num_windows:
        window_start = window * window_advance * audio.sample_rate
        window_end = (window * window_advance + window_size) * audio.sample_rate

        window_signal = audio.signal[window_start:window_end]
        power_array[window] = calculate_power(signal)

    return power_array


    


