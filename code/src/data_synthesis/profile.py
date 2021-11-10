import scipy.stats

class Profile:

    # default pianist profile parameters
    DEFAULT_TEMPO_ENVELOPE = lambda t: 1
    DEFAULT_AMPLITUDE_DISTRIBUTION = lambda: 100
    DEFAULT_ONSET_DISTRIBUTION = lambda: 0

    def __init__(self, tempo_envelope=DEFAULT_TEMPO_ENVELOPE, amplitude_distribution=DEFAULT_AMPLITUDE_DISTRIBUTION, onset_distribution=DEFAULT_ONSET_DISTRIBUTION):
        """
        Constructor for pianist profiles

        tempo_envelope: function that generates tempo multipliers for inputs between 0 and 1 that represents how the tempo changes over the piece
        amplitude_distribution: function that can be sampled for amplitudes/velocities of notes
        onset_distribution: function that can be sampled for onset offsets
        """
        self.tempo_envelope = tempo_envelope
        self.amplitude_distribution = amplitude_distribution
        self.onset_distribution = onset_distribution

    def set_normal_onset_distribution(self, loc, scale):
        self.onset_distribution = lambda : scipy.stats.norm.rvs(loc=loc, scale=scale)

    def set_binom_amplitude_distribution(self, loc):
        n = 128
        loc = max(0, min(n, loc))
        p = loc/n
        self.amplitude_distribution = lambda: scipy.stats.binom.rvs(n, p)


