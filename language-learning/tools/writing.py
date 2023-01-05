
class Writing:
    """
    `Writing` is the product of a `Language` and a "script".
    It represents a single language being depicted in a single writing system.
    `Writing` is a "tree mapping" class, analogous to those found under nodemaps.py.
    As a tree mapping class, `Writing` is a category with at least one arrow
    that maps a syntax tree in one representation to another syntax tree in another representation.
    In this case, `Writing` contains a single method `map()`
    that maps a syntax tree that is represented as nested lists storing language-agnostic codes
    to a syntax tree that is represented as a string containing one possible translation 
    of the meaning of the input tree to the natural language that is represented by `Writing`.
    See `Language` for implementation details.
    """
    def __init__(self, script, language):
        self.script = script
        self.language = language
    def map(self, syntax_tree, semes={}, substitutions=[]):
        return self.language.map(syntax_tree, self.script, semes, substitutions)
