class Audio:

    def __init__(self, signal, sample_rate):
        self.signal = signal
        self.sample_rate = sample_rate

    def get_duration(self):
        return len(self.signal)/self.sample_rate
