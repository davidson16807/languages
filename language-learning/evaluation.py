
class KeyEvaluation:
    def __init__(self, key):
        self.key = key
    def __call__(self, value):
        return value[self.key]
