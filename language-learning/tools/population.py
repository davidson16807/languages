import copy

class FlatLookupPopulation:
    '''
    `FlatLookupIndexing` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in a lookup.
    The cells are indexed by their annotations according to the indexing behavior 
    within a given `template_lookup`.
    '''
    def __init__(self, template_lookup, evaluation, debug=False):
        self.template_lookup = template_lookup
        self.evaluation = evaluation
        self.debug = debug
    def index(self, annotations):
        if self.debug: breakpoint()
        lookup = copy.deepcopy(self.template_lookup)
        for annotation,cell in annotations:
            lookup[annotation] = self.evaluation(cell)
        return lookup

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
    def __init__(self, template_lookups, evaluation, debug=False):
        self.template_lookups = template_lookups
        self.evaluation = evaluation
        self.debug = debug
    def index(self, annotations):
        if self.debug: breakpoint()
        lookups = copy.deepcopy(self.template_lookups)
        for annotation,cell in annotations:
            for tuplekey in lookups.indexing.tuplekeys(annotation):
                lookup = lookups[tuplekey]
                lookup[annotation] = self.evaluation(cell)
            if self.debug: breakpoint()
        return lookups

class ListLookupPopulation:
    '''
    `FlatLookupIndexing` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in a lookup.
    The cells are indexed by their annotations according to the indexing behavior 
    within a given `template_lookup`.
    '''
    def __init__(self, template_lookup, evaluation, debug=False):
        self.template_lookup = template_lookup
        self.evaluation = evaluation
        self.debug = debug
    def index(self, annotations):
        if self.debug: breakpoint()
        lookup = copy.deepcopy(self.template_lookup)
        for annotation,cell in annotations:
            lookup[annotation].append(self.evaluation(cell))
        return lookup
