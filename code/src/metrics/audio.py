import tempo
import scipy.signal

class Audio:

    def __init__(self, signal, sample_rate):
        self.signal = signal
        self.sample_rate = sample_rate
        self.onset_function = None
        self.beat_times = None
        self.cached_metrics = {}

    def cache_metric(self, metric, value):
        self.cached_metrics[metric] = value

    def get_cached_metric(self, metric):
        return self.cached_metrics.get(metric, None)

    def get_duration(self):
        return self.to_seconds(len(self.signal))

    def to_seconds(self, num_samples):
        return num_samples/self.sample_rate

    def to_samples(self, num_seconds):
        return int(num_seconds * self.sample_rate)

    def get_onset_function(self):
        if self.onset_function is None:
            self.onset_function = tempo.calculate_onset_func(self)
            return self.onset_function
        else:
            return self.onset_function

    def get_beat_times(self):
        if self.beat_times is None:
            self.beat_times = tempo.calculate_beats(self)
            return self.beat_times
        else:
            return self.beat_times

    def resample(self, new_sample_rate):
        new_signal = scipy.signal.resample(self.signal, int(len(self.signal) * new_sample_rate/self.sample_rate))
        return Audio(new_signal, new_sample_rate)


