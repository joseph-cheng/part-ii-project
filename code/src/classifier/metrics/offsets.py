import util
import numpy as np
import matplotlib.pyplot as plt
import metrics.metric as metric

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

        ret = np.zeros((len(tempo_variation_average), 3))
        for i, inter_onset_interval in enumerate(tempo_variation_average):
            current_loc += inter_onset_interval
            onset_loc, onset_strength = OffsetsCalculator.get_best_nearest_onset(onset_function, current_loc, onset_window_search_size)
            ret[i][0] = onset_loc
            ret[i][1] = onset_strength
            ret[i][2] = current_loc

        """ PLOTTING CODE
        for onset_loc, onset_strength, current_loc in ret:
            offset_plot[audio.to_samples(onset_loc + current_loc)] = 1
            onset_plot[audio.to_samples(current_loc)] = 1

        plt.rcParams.update({'font.size': 30})
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), offset_plot, label="Actual note onsets")
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), onset_plot, label="Expected note onsets")
        plt.legend(loc="upper left")
        plt.show()
        """



        return ret

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

        truncated_length = min(len(metric1), len(metric2))
        truncated_metric1 = metric1[:truncated_length]
        truncated_metric2 = metric2[:truncated_length]

        squared_errors_sum = 0

        for i in range(truncated_length):
            onset_offset1, onset_strength1, beat_time1 = truncated_metric1[i]
            onset_offset2, onset_strength2, beat_time2 = truncated_metric2[i]

            squared_errors_sum += (onset_offset1 - onset_offset2) ** 2 + (onset_strength1 - onset_strength2) ** 2



        mse = squared_errors_sum /truncated_length



        # when the two metrics are identical, squared_errors_sum is 0, and becomes larger and larger the less similar the metrics are, so we apply exp(-mse) to get our metric

        return np.exp(-mse)


    def get_best_nearest_onset(onset_function, expected_beat_time, window_size):
        """
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
