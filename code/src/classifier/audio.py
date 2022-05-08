import os.path
import os
import classifier.metrics.tempo as tempo
import scipy.signal

class Audio:
    def __init__(self, signal, sample_rate, name=""):
        """
        signal: 1D np array of the signal
        sample_rate: sample_rate in samples/sec for the signal
        name: optionally, the name of the this audio, for debugging/plotting, e.g. the filename
        """
        self.signal = signal
        self.sample_rate = sample_rate

        self.name = name

        self.onset_function = None
        self.beat_times = None
        self.global_tempo = None
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
            self.onset_function = tempo.TempoCalculator.calculate_onset_func(self)
            return self.onset_function
        else:
            return self.onset_function

    def get_beat_times(self):
        if self.beat_times is None:
            self.beat_times = tempo.TempoCalculator.calculate_beats(self)
            return self.beat_times
        else:
            return self.beat_times

    def get_global_tempo(self):
        if self.global_tempo is None:
            self.global_tempo = tempo.TempoCalculator.calculate_global_tempo(self)
        return self.global_tempo

    def resample(self, new_sample_rate):
        new_signal = scipy.signal.resample(self.signal, int(len(self.signal) * new_sample_rate/self.sample_rate))
        return Audio(new_signal, new_sample_rate)


