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

    onset_array = np.zeros(
        (audio.get_duration() - window_size) / window_advance)

    num_windows = len(onset_array)

    for window in num_windows:

        #TODO: resample to 8kHz
        window_start = window * window_advance * audio.sample_rate
        window_end = (window * window_advance +
                      window_size) * audio.sample_rate

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

    gaussian_window = scipy.signal.windows.gaussian(
        int(envelope_length * audio.sample_rate), int(envelope_sigma * audio.sample_rate))

    return np.convolve(onset_array, gaussian_window)


def calculate_global_tempo(audio, onset_function=None, tempo_bias=0.5, envelope_width=1.4):
    """
    Calculates an estimate of the global tempo of an audio signal, using the techniques outlined by Ellis, basically by calculating autocorrelation

    audio: an Audio object that contains the signal to calculate the tempo for
    onset_function: optionally, a pre-calculated onset function. If this is not provided, then it will be calculated from `audio`
    tempo_bias: the centre of the bias for the tempo estimate, defaults to 0.5 (120 BPM)
    envelope_width: the width of the bias envelope, in octaves, defaults to 1.4

    returns: an estimate of the global tempo in BPM
    """

    def weighting_func(tau): return np.exp(-0.5 *
                                           (np.log2(tau / tempo_bias)/envelope_width) ** 2)

    if onset_function == None:
        onset_function = calculate_onset_func(audio)

    # tempo shouldn't go higher than 250
    min_tempo = 20

    # now we iterate over potential tempos and find hte best
    best_correlation = np.NINF
    best_tempo = -1
    # iterate over possible delays from 0 to min_tempo samples through
    for tau_samples in range(0, 60/min_tempo * audio.sample_rate):
        tau = tau_samples / audio.sample_rate
        delayed_onset = onset_function[tau_samples:]

        # calculate weighted correlation
        correlation = weighting_func(tau) * np.dot(delayed_onset, onset_function[:-tau_samples])
        if correlation > best_correlation:
            best_correlation = correlation
            best_tempo = 60/tau

    return best_tempo

def beat_consistency(current_t, previous_t, ideal_spacing):
    delta_t = current_t - previous_t
    return -(np.log(delta_t / ideal_spacing) ** 2)

def calculate_beats(audio):
    """
    Calculates beat onset times using techniques developed by Ellis

    audio: an Audio object that contains the signal to calculate the beat onsets for

    returns: a sorted 1d np array of beat onset times in seconds
    """

    # alpha
    WEIGHTING = 100

    # initialise C* and P*
    score_array = np.full(len(audio.signal), 0)
    backtrace_array = np.full(len(audio.signal), 0)

    onset_function = calculate_onset_func(audio)
    global_tempo = calculate_global_tempo(audio, onset_function=onset_function)
    ideal_spacing = 60/global_tempo
    ideal_spacing_samples = audio.to_samples(ideal_spacing)

    for sample_num in range(1, len(audio.signal)):
        t = audio.to_seconds(sample_num)

        onset_value = onset_function[sample_num]
        range_start = max(0, sample_num - ideal_spacing_samples * 2)
        range_stop = max(0, sample_num - ideal_spacing_samples / 2) + 1

        best_score = -9e999
        best_tau = -1
        # do the max/argmax
        for potential_beat in range(range_start, range_stop):
            potential_beat = audio.to_seconds(previous_beat)
            score = WEIGHTING * beat_consistency(t, potential_beat_seconds, ideal_spacing)
            score += score_Array[potential_beat]
            if score > best_score:
                best_score = score
                best_tau = potential_beat

        score_array[sample_num] = best_score
        backtrace_array[sample_num] = best_tau

    # now we have done the dynamic programming, just need to backtrace

    # so we first find the final beat, time, the highest scoring t

    final_beat_time = np.argmax(score_array)

    beats = [final_beat_time]

    current_beat = final_beat_time

    # while still need to backtrace
    while current_beat != 0:
        current_beat = backtrace_array[current_beat]
        beats.append(current_beat)

    beats.reverse()
    return np.array([audio.to_seconds(beat) for beat in beats])





