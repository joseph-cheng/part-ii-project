import scipy.fft
import matplotlib.pyplot as plt
import numpy as np
import classifier.metrics.metric as metric

class TimbreCalculator(metric.MetricCalculator):
    def __init__(self, window_size=0.3, target_pitch=440):
        """
        window_size: the size in seconds of the window to calculate the MFCCs for
        target_pitch: the frequency in Hz we should normalise to when calculating the spectrum
        """

        self.window_size = window_size
        self.target_pitch = target_pitch

    def calculate_metric(self, audio):
        """
        Calculates the timbre metric of a signal. It does this by calculating MFCCs of a particular window at note onsets using beat onsets

        audio: an Audio object containing the signal for which the timbre metric should be calculated

        returns: a 2d np array of mfccs for each onset
        """

        beat_times = audio.get_beat_times()
        num_filters = 40

        timbre_array = np.zeros((len(beat_times), num_filters))

        for i, beat_time in enumerate(beat_times):
            window_start = int(beat_time * audio.sample_rate)
            window_end = int((beat_time + self.window_size) * audio.sample_rate)

            window_signal = audio.signal[window_start:window_end]

            timbre_array[i] = self.calculate_mfccs(window_signal, audio.sample_rate)

        return timbre_array

    def calculate_similarity(self, audio1, audio2, metric1, metric2):
        """
        Calculates the similarity between two timbre metrics.

        audio1: Audio object containing the signal used to compute metric1
        audio2: Audio object containing the signal used to compute metric2
        metric1: metric computed by calculate_timbre_metric function
        metric2: metric computed by calculate_timbre_metric function

        returns: similarity score between 0 and 1 of the similarity of the two metrics
        """

        #TODO: normalisation? might not need to

        # since the timbre metric is calculated at times where there are note onsets, the assumption is that the beats already correspond, although this might not necessarily be true

        # To calculate similarity, we take the sum of squared errors of each mfcc, and the errors between two mfccs is the sum of the squared errors between each spectrum bin

        # here we naively align the two metrics, hopefully this shouldn't make a difference because the metrics should be aligned, but in the case they are not then we should probably do something smarter
        timbre_array1 = metric1[:min(len(metric1), len(metric2))]
        timbre_array2 = metric2[:min(len(metric1), len(metric2))]
        mfcc_errors = np.sum((timbre_array1 - timbre_array2) ** 2, axis=1)

        squared_errors_sum = np.sum(mfcc_errors)

        mse = squared_errors_sum / len(timbre_array1)

        # when the two metrics are identical, squared_errors_sum is 0, and becomes larger and larger the less similar the metrics are, so we apply exp(-squared_errors_sum) to get our metric

        return np.exp(-mse)

    def hertz_to_mel(to_convert):
        """
        to_convert: number of 1d np array of spectrum to convert to mel scale

        returns: to_convert converted to mel scale, using formula from https://en.wikipedia.org/wiki/Mel_scale
        """
        return 2595 * np.log10(1 + to_convert/700)


    def mel_to_hertz(to_convert):
        """
        to_convert: number of 1d np array of spectrum to convert to hertz scale

        returns: to_convert converted to hertz scale, using inverse formula from https://en.wikipedia.org/wiki/Mel_scale
        """

        return 700 * (10 ** (to_convert / 2595) - 1)


    def calculate_band_freqs(sample_rate, num_filters=40):
        """
        Calculates the middle of each of the mel bands in Hertz

        sample_rate: sample rate of the audio
        num_filters: number of mel filters to use

        returns: a num_filters length np array containing the middle of each of the mel bands in Hertz
        """
        lowest_freq = 0
        # highest frequency we get is half the sample rate
        highest_freq_hertz = sample_rate/2
        highest_freq = TimbreCalculator.hertz_to_mel(highest_freq_hertz)

        # we add two for off by one
        mel_bands = np.linspace(lowest_freq, highest_freq, num=num_filters+1)
        hertz_bands = TimbreCalculator.mel_to_hertz(mel_bands)
        middles = np.zeros(num_filters)
        for i in range(1, len(mel_bands)):
            bottom = mel_bands[i-1]
            top = mel_bands[i]
            middles[i-1] = TimbreCalculator.mel_to_hertz((top + bottom) / 2)

        return middles



    def spectrum_to_mel_bands(spectrum, sample_rate, num_filters=40):
        """
        Converts a spectrum to mel bands

        spectrum: the spectrum to convert
        sample_rate: the sample rate of the audio from which the spectrum was taken
        num_filters: number of mel filters to use

        returns: a num_filters length np array of the filtered spectra
        """
        lowest_freq = 0
        # highest frequency we get is half the sample rate
        highest_freq_hertz = sample_rate/2
        highest_freq = TimbreCalculator.hertz_to_mel(highest_freq_hertz)

        # we add two for off by one
        mel_bands = np.linspace(lowest_freq, highest_freq, num=num_filters+2)
        hertz_bands = TimbreCalculator.mel_to_hertz(mel_bands).astype(int)

        bins = np.floor((len(spectrum) + 1) * hertz_bands / sample_rate)

        # now we create our filter bank
        filter_bank = np.zeros((num_filters, len(spectrum)))
        for i in range(1, num_filters + 1):
            previous_band = int(bins[i - 1])
            band = int(bins[i])
            next_band = int(bins[i + 1])
            for j in range(previous_band, band):
                filter_bank[i-1, j] = (j - previous_band) / (band - previous_band)
            for j in range(band, next_band):
                filter_bank[i-1, j] = (next_band-j) / (next_band - band)

        # now we compute all of the filtered spectrums
        filtered_spectrums = []
        for f in filter_bank:
            filtered_spectrums.append(f * spectrum)

        # now compute the mel filtered power spectra
        filtered_spectrums = np.array(filtered_spectrums)

        filter_bank_energies = np.sum(filtered_spectrums, axis=1)

        return filter_bank_energies

    def normalise_spectrum(self, spectrum, spectrum_freqs):
        """
        Shifts a spectrum towards a target pitch, naively finds the `pitch' of the signal by finding the frequency with the largest amplitude
        normalises towards self.target_pitch

        spectrum: 1D array of the spectrum, from np.fft.rfft()
        spectrum_freqs: 1D array of the frequency bins for the spectrum, from np.fft.rfftfreq()
        target_pitch: target pitch in Hz to shift towards

        returns: a shifted spectrum where the maximal frequency is target_pitch
        """

        fundamental_freq = spectrum_freqs[np.argmax(spectrum)]
        shift = self.target_pitch - fundamental_freq
        spacing = spectrum_freqs[1] - spectrum_freqs[0]
        shift_idx = int(shift / spacing)
        shifted = np.roll(spectrum, shift_idx)
        # rolling makes frequencies at the ends reappear, so we zero these instead
        if shift_idx >= 0:
            shifted[:shift_idx] = 0
        else:
            shifted[shift_idx:] = 0

        return shifted



    def calculate_mfccs(self, signal, sample_rate):
        """
        Calculates the MFCCs of a signal

        signal: a 1D array of the signal to calculate the mfccs for
        sample_rate: the sample rate of the audio

        returns: a list containing the MFCCs
        """

        # first, we calculate the spectrum of our signal
        spectrum = scipy.fft.rfft(signal)
        spectrum_freqs = scipy.fft.rfftfreq(len(signal), d=1/sample_rate)
        shifted_spectrum = self.normalise_spectrum(spectrum, spectrum_freqs)

        #now we calculate the power spectrum (by converting each frequency to a power and normalising)
        power_spectrum = 1/len(signal) * (np.abs(shifted_spectrum) ** 2)

        filter_bank_energies = TimbreCalculator.spectrum_to_mel_bands(
            power_spectrum, sample_rate)

        mfccs = scipy.fft.dct(filter_bank_energies)

        return mfccs

    def __repr__(self):
        return "Timbre"

