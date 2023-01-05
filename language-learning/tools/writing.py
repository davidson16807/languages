
class Writing:
    """
    `Writing` is the product of a `Language` and script.
    `Writing` is a "tree mapping" class, analogous to those found under nodemaps.py.
    As a tree mapping class, `Language` is a category with at least one arrow
    that maps a syntax tree in one representation to another syntax tree in another representation.
    In this case, `Language` contains a single method `map()`
    that maps a syntax tree that is represented as nested lists storing language-agnostic codes
    to a syntax tree that is represented as a string containing one possible translation 
    of the meaning of the input tree to the natural language that is represented by `Language`.

    A `Language` can alternately be defined in a bottom-up way as a series of "node mapping" class instances that contain maps for individual nodes on trees
    These node mapping class instances can be seen in the parameters of the constructor for `Language`:
        grammar:    contains maps from nodes represented as nested lists of language agnostic codes to nodes represented as nested lists of inflected words as they would appear in a language
        syntax:     contains maps from nodes represented as nested and unordered `Rule` objects to nodes represented as nested `Rule` objects ordered as they would appear according to language ordering rules (e.g. sentence structure)
        formatting: contains maps between nodes represented as nested lists of strings indicating how constructs such as Anki "cloze" statements should be rendered as strings
        validation: contains maps from nodes represented as nested lists of Noneable strings to boolean indicating whether the node should be rendered as a string
        tools:      contains maps of nodes represented as nested lists of strings without concern to what the strings represent
    """
    def __init__(self, script, language):
        self.script = script
        self.language = language
    def map(self, syntax_tree, semes={}, substitutions=[]):
        return self.language.map(syntax_tree, self.script, semes, substitutions)
