
class Cloze:
    def __init__(self, id_, content):
        self.id = id_
        self.content = content

class NounPhrase:
    def __init__(self, grammemes, content=None):
        self.grammemes = grammemes
        self.content = content

class Adjective:
    def __init__(self, content):
        self.content = content

class Adposition:
    def __init__(self, native, foreign):
        self.native = native
        self.foreign = foreign

class Article:
    def __init__(self, content):
        self.content = content

class StockModifier:
    def __init__(self, lookup):
        self.lookup = lookup

class Clause:
    def __init__(self, grammemes, verb, nouns=[]):
        self.grammemes = grammemes
        self.verb = verb
        self.nouns = nouns
