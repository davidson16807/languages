import copy

class FlatLookupPopulation:
    '''
    `FlatLookupIndexing` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in a lookup.
    The cells are indexed by their annotations according to the indexing behavior 
    within a given `template_lookup`.
    '''
    def __init__(self, template_lookup):
        self.template_lookup = template_lookup
    def index(self, annotations):
        lookups = copy.deepcopy(self.template_lookup)
        for annotation,cell in annotations:
            lookups[annotation] = cell
        return lookups

class NestedLookupPopulation:
    '''
    `NestedLookupPopulation` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in nested lookups.
    The cells are indexed by their annotations according to 
    the indexing behavior within a given `template_lookups`.
    Nested lookups can be especially useful if the data 
    that they are indexing is nonnormalized, 
    since inner nested lookups can each use separate indexing methods,
    so that their content is a strict function of the key and nothing else.
    '''
    def __init__(self, template_lookups):
        self.template_lookups = template_lookups
    def index(self, annotations):
        lookups = copy.deepcopy(self.template_lookups)
        for annotation,cell in annotations:
            lookup = lookups[annotation]
            lookup[annotation] = cell
        return lookups
