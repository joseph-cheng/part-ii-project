import scipy.fft
import numpy as np


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
    highest_freq = hertz_to_mel(sample_rate/2)

    # we add two for off by one
    mel_bands = np.linspace(lowest_freq, highest_freq, num=num_filters+2)
    hertz_bands = mel_to_hertz(mel_bands)

    # now we create our filter bank
    filter_bank = np.zeros((num_filters, int(sample_rate/2)))
    for i, band in enumerate(hertz_bands[1:-1]):
        band_i = i + 1
        previous_band = hertz_bands[band_i - 1]
        next_band = hertz_bands[band_i + 1]
        for j in range(previous_band, band):
            filter_bank[i, j] = (j - previous_band) / (band - previous_band)
        for j in range(band, next_band):
            filter_bank[i, j] = (j - band) / (next_band - band)

    # now we compute all of the filtered spectrums
    filtered_spectrums = []
    for f in filter_bank:
        filtered_spectrums.append(np.dot(f, spectrum))

    # now compute the mel filtered power spectra
    filtered_spectrums = np.array(filtered_specturms)

    filter_bank_energies = np.sum(filtered_powers, axis=1)

    return filter_bank_energies


def calculate_mfccs(audio):
    """
    Calculates the MFCCs of a signal

    audio: an Audio object containing the signal for which the MFCCs should be calculated

    returns: a list containing the MFCCs
    """

    # first, we calculate the spectrum of our signal
    spectrum = scipy.fft.rfft(audio.signal)

    #now we calculate the power spectrum (by converting each frequency to a power and normalising)
    power_spectrum = 1/len(audio.signal) * (np.abs(spectrum) ** 2)

    filter_bank_energies = spectrum_to_mel_bands(
        power_spectrum, audio.sample_rate)

    mfccs = scipy.fft.dct(filter_bank_energies)

    return mfccs
