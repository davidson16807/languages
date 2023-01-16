
class CellEvaluation:
    def __init__(self):
        pass
    def __call__(self, cell):
        return cell

class KeyEvaluation:
    def __init__(self, key):
        self.key = key
    def __call__(self, cell):
        return cell[self.key]

class MultiKeyEvaluation:
    def __init__(self, keys):
        self.keys = keys
    def __call__(self, cell):
        return {key:cell[key] for key in self.keys}
