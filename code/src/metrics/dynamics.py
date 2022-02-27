import numpy as np
import matplotlib.pyplot as plt
import metric


class DynamicsCalculator(metric.MetricCalculator):
    def __init__(self, window_size=0.04, window_advance=0.04):
        """
        window_size: the length in seconds a window should be calculated for
        window_advance: the length in seconds to advance to the next window
        """

        self.window_size = window_size
        self.window_advance = window_advance

    def calculate_metric(self, audio):
        """
        Calculates the dynamic over time metric of a signal by taking the power of successive windows

        audio: an Audio object to calculate the dynamics metrics for

        returns: a 1D np array of powers of successive windows in the signal
        """

        power_array = np.zeros(int((audio.get_duration() - self.window_size) / self.window_advance))

        num_windows = len(power_array)
        for window in range(num_windows):
            window_start = int(window * self.window_advance * audio.sample_rate)
            window_end = int((window * self.window_advance + self.window_size) * audio.sample_rate)

            window_signal = audio.signal[window_start:window_end]
            power_array[window] = DynamicsCalculator.calculate_power(window_signal)

        """ PLOTTING CODE
        plt.rcParams.update({'font.size': 30})
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), audio.signal, label="Audio signal")
        plt.plot(np.linspace(0, audio.get_duration(), len(power_array)), power_array, label="Dynamics")
        plt.legend(loc="upper left")
        plt.show()
        """

        return power_array

    def calculate_similarity(self, audio1, audio2, metric1, metric2):

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




        power_array1 = metric1
        power_array2 = metric2

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

        mse = squared_differences_sum / truncated_length

        # when the signals are identical, this value will be 0 (similarity=1), and can grow to be infinitely large, and similarity tapers to 0

        # for tis reason, we apply exp(-x) to get our similarity score

        return np.exp(-mse)

    def calculate_power(signal):
        """
        Calculates the power of a signal

        signal: a 1d np array to calculate the power of

        returns: a coefficient representing the power of the signal
        """

        return np.sqrt(sum(np.square(np.abs(signal), dtype="float64"))/len(signal))

    def __repr__(self):
        return "Dynamics"
