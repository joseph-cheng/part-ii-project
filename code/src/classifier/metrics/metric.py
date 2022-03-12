class MetricCalculator:
    def __init__(self):
        raise NotImplementedError("Please override this method")

    def calculate_metric(self, audio):
        raise NotImplementedError("Please override this method")

    def calculate_similarity(self, audio1, audio2, metric1, metric2):
        raise NotImplementedError("Please override this method")

