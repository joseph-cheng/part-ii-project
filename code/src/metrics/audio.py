class Audio:

    def __init__(self, signal, sample_rate):
        self.signal = signal
        self.sample_rate = sample_rate

    def get_duration(self):
        return self.to_seconds(len(self.signal))

    def to_seconds(self, num_samples):
        return num_samples/self.sample_rate

    def to_samples(self, num_seconds):
        return num_seconds * self.sample_rate
