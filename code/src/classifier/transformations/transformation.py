class Transformation:
    def __init__(self):
        raise NotImplementedError("Please override this method")

    def apply(self, audio, out=None):
        raise NotImplementedError("Please override this method")
