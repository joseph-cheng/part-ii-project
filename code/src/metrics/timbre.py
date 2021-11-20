import scipy.fft
import numpy as np

FILTERS = 40

def hertz_to_mel(to_convert):
    """
    to_convert: number of 1d np array of spectrum to convert to mel scale

    returns: to_convert converted to mel scale, using formula from https://en.wikipedia.org/wiki/Mel_scale
    """
    return  2595 * np.log10(1 + to_convert/700)

def mel_to_hertz(to_convert):
    """
    to_convert: number of 1d np array of spectrum to convert to hertz scale

    returns: to_convert converted to hertz scale, using inverse formula from https://en.wikipedia.org/wiki/Mel_scale
    """

    return 700 * (10 ** (to_convert / 2595) - 1)



def calculate_mfccs(audio):
    """
    Calculates the timbre metric from an Audio object by calculating the MFCCs

    audio: an Audio object containing the signal for which the timbre metric should be calculated

    returns: a list containing the MFCCs
    """

    # first, we calculate the spectrum of our signal
    spectrum = scipy.fft.rfft(audio.signal)

    #now we calculate the power spectrum (by converting each frequency to a power and normalising)
    power_spectrum = 1/len(audio.signal) * (np.abs(spectrum) ** 2)

    # now we take a number of band pass filters, equally spaced in the Mel-scale, and find the power of each of these bands in the power spectrum. We choose 40 filters

    lowest_freq = 0
    # highest frequency we get is half the sample rate
    highest_freq = hertz_to_mel(audio.sample_rate/2)

    # we add to for off by one
    mel_bands = np.linspace(lowest_freq, highest_freq, num=FILTERS+2)
    hertz_bands = mel_to_hertz(mel_bands)

    # now we create our filter bank
    filter_bank = np.zeros((FILTERS, int(audio.sample_rate/2)))
    for i, band in enumerate(hertz_bands[1:-1]):
        band_i = i + 1
        previous_band = hertz_bands[band_i - 1]
        next_band = hertz_bands[band_i + 1]
        for j in range(previous_band, band):
            filter_bank[i, j] = (j - previous_band) / (band - previous_band)
        for j in range(band, next_band):
            filter_bank[i, j] = (j - band) / (next_band - band)

    # now we compute all of the filtered power spectrums
    filtered_powers = []
    for f in filter_bank:
        spectrums.append(np.dot(f, power_spectrum))

    filtered_powers = np.array(filtered_powers)

    #finally, we sum up the power of each filtered spectrum to give us a single coefficient, and take the dct
    filter_bank_energies = np.sum(filtered_powers, axis=1)

    mfccs = scipy.fft.dct(filter_bank_energies)

    return mfccs
