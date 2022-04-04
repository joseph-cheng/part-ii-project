import numpy as np
import metrics.timbre as timbre
import matplotlib.pyplot as plt
import metrics.metric as metric
import scipy.fft


class DynamicsCalculator(metric.MetricCalculator):
    def __init__(self, window_size=0.16, window_advance=0.04):
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

        level_array = np.zeros(int((audio.get_duration() - self.window_size) / self.window_advance))

        num_windows = len(level_array)
        for window in range(num_windows):
            window_start = int(window * self.window_advance * audio.sample_rate)
            window_end = int((window * self.window_advance + self.window_size) * audio.sample_rate)

            window_signal = audio.signal[window_start:window_end]

            spectrum = scipy.fft.rfft(window_signal)
            power_spectrum = 1/len(window_signal) * (np.abs(spectrum) ** 2)

            mel_power = timbre.TimbreCalculator.spectrum_to_mel_bands(
                    power_spectrum, audio.sample_rate)
            freqs = timbre.TimbreCalculator.calculate_band_freqs(audio.sample_rate)

            # we choose this relatively arbitraryil
            reference_point = 10000000

            db = 10 * np.log10(mel_power/reference_point)

            weighted_db = np.zeros(db.shape)

            for i in range(len(db)):
                weighted = db[i] + DynamicsCalculator.freqweighting(freqs[i])
                weighted_db[i] = weighted

            total_weighted = 10 * np.log10(sum(10**(weighted_db / 10)))

            level_array[window] = total_weighted

        """
        # PLOTTING CODE
        plt.rcParams.update({'font.size': 30})
        plt.plot(np.linspace(0, audio.get_duration(), len(audio.signal)), audio.signal, label="Audio signal")
        plt.plot(np.linspace(0, audio.get_duration(), len(level_array)), level_array * 100, label="Dynamics")
        plt.legend(loc="upper left")
        plt.show()
        """

        return level_array

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

        """
        # PLOTTING CODE
        plt.rcParams.update({'font.size': 30})
        plt.plot(power_array1, label=audio1.name[15:-4], linewidth=3.0)
        plt.plot(power_array2, label=audio2.name[15:-4], linewidth=3.0)
        plt.xticks([])
        plt.yticks([])
        plt.legend()
        plt.show()
        """

        # now we find the sum of the squared errors

        squared_differences_sum = np.sum((power_array1 - power_array2)**2)

        mse = squared_differences_sum / truncated_length

        # when the signals are identical, this value will be 0 (similarity=1), and can grow to be infinitely large, and similarity tapers to 0

        # for tis reason, we apply exp(-x) to get our similarity score

        return np.exp(-mse)


    def freqweighting(f):
        """
        Calculates the-weighting of a frequency, for perceived loudness.
        In particular, we use the ITU-R 468 curve

        f: frequency to calculate the weighting for

        returns: the weighting of the frequency
        """


        # taken from https://en.wikipedia.org/wiki/ITU-R_468_noise_weighting

        numerator = 1.246332637532143e-4 * f
        h1 = (-4.737338981378384e-24 * f**6 +
               2.043828333606125e-15 * f**4 - 
               1.363894795463638e-7  * f**2 +
               1)


        h2 = (1.306612257412824e-19 * f**5 - 
              2.118150887518656e-11 * f**3 +
              5.559488023498642e-4  * f    
              )


        denominator = np.sqrt(h1**2 + h2**2)
        aux = numerator/denominator

        return 18.2 + 20 * np.log10(aux)


    def __repr__(self):
        return "Dynamics"
