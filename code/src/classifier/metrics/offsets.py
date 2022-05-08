import classifier.util as util
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import classifier.metrics.metric as metric

class OffsetsCalculator(metric.MetricCalculator):
    def __init__(self):
        # just here for override
        pass
    
    def calculate_metric(self, audio):
        """
        Calculates the note onset offset metric by using the tempo variation metric

        audio: an Audio object containing the signal to calculate the metric for

        returns: a 2D array of distances between expected beat times and actual note onsets, along with the strength of the onset and the expected beat time
        """

        beat_times = audio.get_beat_times()
        tempo_variation = np.diff(beat_times)
        onset_function = audio.get_onset_function()

        moving_average_window = 4
        tempo_variation_average = util.moving_average(tempo_variation, moving_average_window)

        # basically, take the moving average tempo, and search for the nearest highest onset value in a small window around the expected beat time based on the moving average tempo
        current_loc = 0
        onset_window_search_size = 0.1
        # plotting
        """ PLOTTING CODE
        offset_plot = np.zeros(len(audio.signal))
        onset_plot = np.zeros(len(audio.signal))
        """


        offsets = np.zeros(len(tempo_variation_average))
        for i, inter_onset_interval in enumerate(tempo_variation_average):
            current_loc += inter_onset_interval
            onset_loc, onset_strength = OffsetsCalculator.get_best_nearest_onset(onset_function, current_loc, onset_window_search_size)
            # negative value is before current_loc
            offsets[i] = onset_loc - current_loc

        """ PLOTTING CODE
        #TODO: fix this
        for onset_loc, onset_strength, current_loc in ret:
            offset_plot[audio.to_samples(onset_loc + current_loc)] = 1
            onset_plot[audio.to_samples(current_loc)] = 1

        plt.rcParams.update({'font.size': 30})
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), offset_plot, label="Actual note onsets")
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), onset_plot, label="Expected note onsets")
        plt.legend(loc="upper left")
        plt.show()
        """

        mean = np.mean(offsets)
        stdev = np.std(offsets)

        return (mean, stdev)

    def calculate_similarity(self, audio1, audio2, metric1, metric2):
        """
        Calculates the similarity between two offsets metrics.

        audio1: Audio object containing the signal used to compute metric1
        audio2: Audio object containing the signal used to compute metric2
        metric1: metric computed by calculate_offsets_metric function
        metric2: metric computed by calculate_offsets_metric function

        returns: similarity score between 0 and 1 of the similarity of the two metrics
        """

        # To calculate similarity, for each expected beat, we compare the onset offset and the onset strength, by taking the squared error between each

        mean1, stdev1 = metric1
        mean2, stdev2 = metric2

        divergence_pq = OffsetsCalculator.calculate_divergence(mean1, stdev1, mean2, stdev2)
        divergence_qp = OffsetsCalculator.calculate_divergence(mean2, stdev2, mean1, stdev1)

        symmetrised_divergence = 0.5 * (divergence_pq + divergence_qp)

        return np.exp(-symmetrised_divergence)


    def get_best_nearest_onset(onset_function, expected_beat_time, window_size):
        """ovidtrack/
        Gets the distance from the expected beat time of the highest onset value in a small window around the expected beat time

        onset_function: an OnsetFunction object containing the onsets of the signal we are searching
        expected_beat_time: time in seconds of the expected beat time
        window_size: size in seconds of the window to search for the note onset

        returns: a tuple where the first element is the distance from the expected beat time to the best onset in the window, and the second element is the strength of this onset
        """

        window_size = onset_function.time_to_windows(window_size)
        min_window = onset_function.time_to_windows(expected_beat_time) - window_size
        max_window = min_window + 2 * window_size

        best_window = -1
        best_onset_value = np.NINF
        for window in range(min_window, max_window + 1):
            if onset_function.index_window(window) > best_onset_value:
                best_window = window
                best_onset_value = onset_function.index_window(window)

        onset_location = onset_function.windows_to_time(best_window)
        return (onset_location - expected_beat_time, best_onset_value)

    def __repr__(self):
        return "Offsets"

    def calculate_divergence(mean1, stdev1, mean2, stdev2):

        a = np.log(stdev2 / stdev1)

        numerator_b = stdev1 ** 2 + (mean1 - mean2)**2
        denominator_b = 2 * stdev2 ** 2

        return a + (numerator_b/denominator_b) - 0.5

