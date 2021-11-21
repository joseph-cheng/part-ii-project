import numpy as np
import scipy.fft
import scipy.signal.windows
import timbre


def calculate_onset_func(audio, window_size=0.032, window_advance=0.004):
    """
    Calculates the onset function as used by Ellis for beat tracking

    audio: an Audio object containing the signal for which the onset function should be calculated for
    window_size: size of the window in s for which onset values are calculated
    window_advance: how far along each window is in s

    returns: a 1d NP array containing calculated values of the onset function for each window
    """

    onset_array = np.zeros((audio.get_duration() - window_size) / window_advance)

    num_windows = len(onset_array)

    for window in num_windows:

        #TODO: resample to 8kHz
        window_start = window * window_advance * audio.sample_rate
        window_end = (window * window_advance + window_size) * audio.sample_rate

        window_signal = audio.signal[window_start:window_end]

        spectrum = scipy.fft.rfft(window_signal)

        power_spectrum = 1/len(window_signal) * (np.abs(spectrum) ** 2)

        mel_spectrum = timbre.spectrum_to_mel_bands(
            power_spectrum, audio.sample_rate)

        # normalise to 0dB max
        # the paper does not specify what reference to convert to dB from, there are potentially other choices worth exploring
        mel_spectrum_db = 10 * np.log10(mel_spectrum/max(mel_spectrum))

        # take first order difference
        diff = np.diff(mel_spectrum_db)

        # set negative values to 0
        rectified_diff = diff.clip(min=0)

        onset_val = sum(rectified_diff)

        onset_array[window] = onset_val

    # TODO: high pass filter 0.4Hz

    # now we smooth by convolving with gaussian envelope
    envelope_length = 0.020
    
    # just made this number up, might be better choices
    envelope_sigma = 0.003

    gaussian_window = scipy.signal.windows.gaussian(int(envelope_length * audio.sample_rate), int(envelope_sigma * audio.sample_rate))

    return np.convolve(onset_array, gaussian_window)

def calculate_global_tempo(audio, onset_function=None):
