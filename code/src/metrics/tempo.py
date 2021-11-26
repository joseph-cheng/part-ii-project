import numpy as np
import scipy.fft
import scipy.signal.windows
import scipy.signal
import timbre
import matplotlib.pyplot as plt


class OnsetFunction:
    def __init__(self, data, window_advance, sample_rate):
        self.data = data
        self.window_advance = window_advance
        self.sample_rate = sample_rate

    def index_samples(self, samples):
        return self.data[self.samples_to_windows(samples)]

    def index_time(self, t):
        return self.data[self.time_to_windows(t)]

    def index_window(self, w):
        return self.data[w]

    def samples_to_windows(self, samples):
        return self.time_to_windows(samples / self.sample_rate)

    def time_to_windows(self, t):
        return int(t / self.window_advance)

    def windows_to_time(self, w):
        return self.window_advance * w

    def delay_samples(self, num_samples):
        if num_samples > 0:
            return OnsetFunction(self.data[self.samples_to_windows(num_samples):], self.window_advance, self.sample_rate)
        else:
            end_point = self.samples_to_windows(abs(num_samples))
            data = None 
            if end_point == 0:
                data = self.data
            else:
                data = self.data[:-end_point]

            return OnsetFunction(data, self.window_advance, self.sample_rate)

    def dot(self, other):
        return np.dot(self.data, other.data)


def calculate_onset_func(audio, window_size=0.064, window_advance=0.004):
    """
    Calculates the onset function as used by Ellis for beat tracking

    audio: an Audio object containing the signal for which the onset function should be calculated for
    window_size: size of the window in s for which onset values are calculated
    window_advance: how far along each window is in s

    returns: a 1d NP array containing calculated values of the onset function for each window
    """

    onset_array = np.zeros(
        int((audio.get_duration() - window_size) / window_advance))

    num_windows = len(onset_array)

    audio = audio.resample(8000)

    for window in range(num_windows):

        window_start = int(window * window_advance * audio.sample_rate)
        window_end = int((window * window_advance +
                      window_size) * audio.sample_rate)

        window_signal = audio.signal[window_start:window_end]
        window_filter = scipy.signal.windows.hann(len(window_signal))
        window_signal = window_signal * window_filter
        

        spectrum = scipy.fft.rfft(window_signal)

        power_spectrum = 1/len(window_signal) * (np.abs(spectrum) ** 2)

        mel_spectrum = timbre.spectrum_to_mel_bands(
            power_spectrum, audio.sample_rate)

        # normalise to 0dB max
        # the paper does not specify what reference to convert to dB from, there are potentially other choices worth exploring
        mel_spectrum_db = 10 * np.log10(mel_spectrum/max(mel_spectrum))

        # take first order difference
        mel_spectrum_db[mel_spectrum_db == -np.inf] =-60 
        diff = np.diff(mel_spectrum_db)

        # set negative values to 0
        rectified_diff = diff.clip(min=0)

        onset_val = sum(rectified_diff)

        onset_array[window] = onset_val

    highpass_filter = scipy.signal.butter(1, 0.4, btype="highpass", output="sos")

    filtered_onsets = scipy.signal.sosfilt(highpass_filter, onset_array)
    # now we smooth by convolving with gaussian envelope
    envelope_length = 0.020

    # just made this number up, might be better choices
    envelope_sigma = 0.002

    gaussian_window = scipy.signal.windows.gaussian(
        int(envelope_length * audio.sample_rate), int(envelope_sigma * audio.sample_rate))

    convolved_onsets = np.convolve(filtered_onsets, gaussian_window)

    normalized_onsets = convolved_onsets / np.std(convolved_onsets)

    onset_function = OnsetFunction(normalized_onsets, window_advance, audio.sample_rate)





    return onset_function


def calculate_global_tempo(audio, tempo_bias=0.5, envelope_width=1.4):
    """
    Calculates an estimate of the global tempo of an audio signal, using the techniques outlined by Ellis, basically by calculating autocorrelation

    audio: an Audio object that contains the signal to calculate the tempo for
    tempo_bias: the centre of the bias for the tempo estimate, defaults to 0.5 (120 BPM)
    envelope_width: the width of the bias envelope, in octaves, defaults to 1.4

    returns: an estimate of the global tempo in BPM
    """

    def weighting_func(tau): return np.exp(-0.5 *
                                           (np.log2(tau / tempo_bias)/envelope_width) ** 2)


    onset_function = audio.get_onset_function()

    # tempo shouldn't go higher than 250
    min_tempo = 20

    # now we iterate over potential tempos and find hte best
    best_correlation = np.NINF
    best_tempo = -1
    # iterate over possible delays from 0 to min_tempo samples through
    for tau_samples in range(1, int(60/min_tempo * audio.sample_rate)):
        tau = tau_samples / audio.sample_rate
        delayed_onset = onset_function.delay_samples(tau_samples)
        reverse_delayed_onset = onset_function.delay_samples(-tau_samples)

        # calculate weighted correlation
        correlation = weighting_func(tau) * delayed_onset.dot(reverse_delayed_onset)

        if correlation > best_correlation:
            
            best_correlation = correlation
            best_tempo = 60/tau

    return best_tempo


def beat_consistency(current_t, previous_t, ideal_spacing):
    delta_t = current_t - previous_t
    return -(np.log(delta_t / ideal_spacing) ** 2)


def calculate_beats(audio, advance=0.004):
    """
    Calculates beat onset times using techniques developed by Ellis

    audio: an Audio object that contains the signal to calculate the beat onsets for
    advance: the time in seconds for which beats are searched, grid interval

    returns: a sorted 1d np array of beat onset times in seconds
    """


    # alpha
    WEIGHTING = 10

    # initialise C* and P*
    score_array = np.zeros(int(audio.get_duration() / advance))
    backtrace_array = np.zeros(int(audio.get_duration() / advance))

    onset_function = audio.get_onset_function()

    global_tempo = calculate_global_tempo(audio)
    ideal_spacing = 60/global_tempo
    ideal_spacing_windows = int(ideal_spacing / advance)
    for window in range(1, int((audio.get_duration() / advance))):
        t = window * advance


        range_start = int(max(0, window - ideal_spacing_windows * 2))
        range_stop = int(max(0, window - ideal_spacing_windows / 2))

        best_score = -9e999
        best_tau = -1
        # do the max/argmax
        onset_value = onset_function.index_time(t)
        for potential_beat in range(range_start, range_stop):
            potential_beat_seconds = potential_beat * advance
            score = WEIGHTING * beat_consistency(t, potential_beat_seconds, ideal_spacing)
            score += score_array[potential_beat]

            if score > best_score:
                best_score = score
                best_tau = potential_beat

        score_array[window] = best_score + onset_value
        backtrace_array[window] = best_tau



    # now we have done the dynamic programming, just need to backtrace

    # so we first find the final beat, time, the highest scoring t

    final_beat_time = np.argmax(score_array)

    beats = [final_beat_time]

    current_beat = final_beat_time

    # while still need to backtrace
    while current_beat != 0:
        current_beat = backtrace_array[int(current_beat)]
        beats.append(current_beat)

    beats.reverse()
    return np.array([beat * advance for beat in beats])


def calculate_tempo_metric(audio):
    """
    Calculates the tempo variation over time metric

    audio: Audio object for which to calculate the metric for

    returns: 1D np array of the first order difference between beat times
    """

    beat_times = audio.get_beat_times()
    print(beat_times)

    return np.diff(beat_times)
