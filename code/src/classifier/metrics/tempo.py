import numpy as np
import util
import scipy.fft
import scipy.signal.windows
import scipy.signal
import metrics.timbre as timbre
import matplotlib.pyplot as plt
import metrics.metric as metric

class OnsetFunction:
    def __init__(self, data, window_advance, sample_rate):
        self.data = data
        self.window_advance = window_advance
        self.sample_rate = sample_rate

    def index_samples(self, samples):
        return self.data[min(len(self.data)-1, self.samples_to_windows(samples))]

    def index_time(self, t):
        return self.data[min(len(self.data)-1, self.time_to_windows(t))]

    def index_window(self, w):
        return self.data[min(len(self.data)-1, w)]

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

class TempoCalculator(metric.MetricCalculator):
    def __init__(self):
        # we use this for certain debugging/plotting stuff
        self.calls = 0

    def calculate_metric(self, audio):
        """
        Calculates the tempo variation over time metric

        audio: Audio object for which to calculate the metric for

        returns: 1D np array of the first order difference between beat times
        """
        self.calls += 1

        # this makes sure we cache the beat times
        beat_times = audio.get_beat_times()


        diff = np.diff(beat_times)

        # now we apply some smoothing to this diff such that small variations are smoothed out

        # we just smooth by taking moving average, we choose 4 relatively arbitrarily, although it does correspond to the number of beats in a bar in a 4/4 time signature piece, which is the most common time signature for a lot of Western music
        smoothed =  util.moving_average(diff, 4)


        """
        # PLOTTING CODE
        #beat_graph = np.cumsum(smoothed) - ((1/audio.get_global_tempo()) * 60) * np.arange(1, len(smoothed) + 1)
        #plt.plot(np.cumsum(smoothed), beat_graph, label=audio.name)
        plt.plot(np.arange(0, len(smoothed)), smoothed, label=audio.name)
        if self.calls % 8 == 7:
            plt.xticks([])
            plt.legend()
            plt.show()
        """


        return smoothed

    def calculate_similarity(self, audio1, audio2, metric1, metric2):
        """
        Calculates the similarity between two tempo metrics.

        audio1: Audio object containing the signal used to compute metric1
        audio2: Audio object containing the signal used to compute metric2
        metric1: metric computed by calculate_tempo_metric function
        metric2: metric computed by calculate_tempo_metric function

        returns: similarity score between 0 and 1 of the similarity of the two metrics
        """

        # To compute similarity, we will just naively take sum of the squared errors, might be a smarter way to do this

        # again we truncate to minimum length in case they are different sizes

        beat_diffs1 = metric1[:min(len(metric1), len(metric2))]
        beat_diffs2 = metric2[:min(len(metric1), len(metric2))]

        squared_errors_sum = np.sum((beat_diffs1 - beat_diffs2) ** 2)

        mse = squared_errors_sum / len(beat_diffs1)

        """
        # more plotting code
        plt.plot(beat_diffs1, label=audio1.name)
        plt.plot(beat_diffs2, label=audio2.name)
        plt.legend()
        plt.show()

        """

        # when the two metrics are identical, squared_errors_sum is 0, and becomes larger and larger the less similar the metrics are, so we apply exp(-squared_errors_sum) to get our metric
        return np.exp(-mse)

    def calculate_beats(audio, advance=0.004):
        """
        Calculates beat onset times using techniques developed by Ellis

        audio: an Audio object that contains the signal to calculate the beat onsets for
        advance: the time in seconds for which beats are searched, grid interval

        returns: a sorted 1d np array of beat onset times in seconds
        """


        # alpha
        WEIGHTING = 200 

        # initialise C* and P*
        score_array = np.zeros(int(audio.get_duration() / advance))
        backtrace_array = np.zeros(int(audio.get_duration() / advance))

        onset_function = audio.get_onset_function()

        global_tempo = audio.get_global_tempo()
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
                score = WEIGHTING * TempoCalculator.beat_consistency(t, potential_beat_seconds, ideal_spacing)
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

        ret = np.array([beat * advance for beat in beats])
        return ret


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

        mel_bands = 40

        num_windows = len(onset_array)


        audio = audio.resample(8000)

        mel_spectrogram = np.zeros((len(onset_array), mel_bands))

        for window in range(num_windows):

            window_start = int(window * window_advance * audio.sample_rate)
            window_end = int((window * window_advance +
                          window_size) * audio.sample_rate)

            window_signal = audio.signal[window_start:window_end]
            window_filter = scipy.signal.windows.hann(len(window_signal))
            window_signal = window_signal * window_filter

            spectrum = scipy.fft.rfft(window_signal)


            power_spectrum = 1/len(window_signal) * (np.abs(spectrum) ** 2)


            mel_spectrum = timbre.TimbreCalculator.spectrum_to_mel_bands(
                power_spectrum, audio.sample_rate, num_filters=mel_bands)

            mel_spectrogram[window] = mel_spectrum


        # normalise to 0dB max
        # the paper does not specify what reference to convert to dB from, don't think it matters though
        reference_point = np.amax(mel_spectrogram)
        mel_spectrogram_db = 10 * np.log10(mel_spectrogram/reference_point)

        # take first order difference
        diff = np.diff(mel_spectrogram_db, axis=0)

        # set negative values to 0
        rectified_diff = diff.clip(min=0)

        onset_array = np.sum(rectified_diff, axis=1)

        highpass_filter = scipy.signal.butter(5, 0.3, btype="highpass", output="sos", fs=1/window_advance)

        filtered_onsets = scipy.signal.sosfilt(highpass_filter, onset_array)
        # now we smooth by convolving with gaussian envelope
        envelope_length = 0.080

        # just made this number up, might be better choices
        envelope_sigma = 0.020

        gaussian_window = scipy.signal.windows.gaussian(
            int(envelope_length / window_advance), int(envelope_sigma / window_advance))




        convolved_onsets = np.convolve(filtered_onsets, gaussian_window)

        normalized_onsets = convolved_onsets / np.std(convolved_onsets)




        offset_added_by_window = int(window_size/window_advance)
        normalized_onsets = np.insert(normalized_onsets, offset_added_by_window, np.zeros(offset_added_by_window))
        onset_function = OnsetFunction(normalized_onsets, window_advance, audio.sample_rate)


        """
        # PLOTTING CODE
        plt.rcParams.update({'font.size': 30})
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), audio.signal/max(audio.signal), label="Audio signal")
        plt.plot(np.linspace(0, audio.get_duration(), len(normalized_onsets)), normalized_onsets/max(normalized_onsets), label="Onset function")
        plt.legend(loc="upper left")
        plt.yticks([])
        plt.xticks([])
        plt.show()
        """



        return onset_function


    def calculate_global_tempo(audio, tempo_bias=0.5, envelope_width=0.9):
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

        # tempo shouldn't go lower than 20
        min_tempo = 20

        auto_correlation = np.zeros(int(60 / min_tempo * audio.sample_rate))

        # now we iterate over potential tempos and find hte best
        # iterate over possible delays from 0 to min_tempo samples through
        for tau_samples in range(1, int(60/min_tempo * audio.sample_rate)):
            tau = tau_samples / audio.sample_rate
            delayed_onset = onset_function.delay_samples(tau_samples)
            truncated_onset = onset_function.delay_samples(-tau_samples)

            # calculate weighted correlation
            correlation = weighting_func(tau) * delayed_onset.dot(truncated_onset)

            auto_correlation[tau_samples] = correlation


        best_tempo_samples = np.argmax(auto_correlation)
        best_tempo = 60 / (best_tempo_samples / audio.sample_rate)

        return best_tempo


    def beat_consistency(current_t, previous_t, ideal_spacing):
        delta_t = current_t - previous_t
        return -(np.log(delta_t / ideal_spacing) ** 2)

    def __repr__(self):
        return "Tempo"
