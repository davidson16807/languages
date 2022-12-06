
class KeyEvaluation:
    def __init__(self, key):
        self.key = key
    def __call__(self, value):
        return value[self.key]

class MultiKeyEvaluation:
    def __init__(self, keys):
        self.keys = keys
    def __call__(self, value):
        return {key:value[key] for key in self.keys}
