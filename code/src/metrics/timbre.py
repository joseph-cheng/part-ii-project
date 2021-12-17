import scipy.fft
import matplotlib.pyplot as plt
import numpy as np
import tempo


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
    highest_freq = hertz_to_mel(highest_freq_hertz)

    # we add two for off by one
    mel_bands = np.linspace(lowest_freq, highest_freq, num=num_filters+2)
    hertz_bands = mel_to_hertz(mel_bands).astype(int)


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


def calculate_mfccs(signal, sample_rate):
    """
    Calculates the MFCCs of a signal

    signal: a 1D array of the signal to calculate the mfccs for
    sample_rate: the sample rate of the audio

    returns: a list containing the MFCCs
    """

    # first, we calculate the spectrum of our signal
    spectrum = scipy.fft.rfft(signal)

    #now we calculate the power spectrum (by converting each frequency to a power and normalising)
    power_spectrum = 1/len(signal) * (np.abs(spectrum) ** 2)

    filter_bank_energies = spectrum_to_mel_bands(
        power_spectrum, sample_rate)

    mfccs = scipy.fft.dct(filter_bank_energies)

    return mfccs

def calculate_timbre_metric(audio, window_size=0.3):
    """
    Calculates the timbre metric of a signal. It does this by calculating MFCCs of a particular window at note onsets using beat onsets

    audio: an Audio object containing the signal for which the timbre metric should be calculated
    window_size: the size in seconds of the window to calculate the MFCCs for

    returns: a 2d np array of mfccs for each onset
    """

    beat_times = audio.get_beat_times()
    num_filters = 40

    timbre_array = np.zeros((len(beat_times), num_filters))

    for i, beat_time in enumerate(beat_times):
        window_start = int(beat_time * audio.sample_rate)
        window_end = int((beat_time + window_size) * audio.sample_rate)

        window_signal = audio.signal[window_start:window_end]

        timbre_array[i] = calculate_mfccs(window_signal, audio.sample_rate)

    return timbre_array



