import itertools

class DictKeyIndexing:
    '''
    `DictKeyIndexing` represents a method for using dictionaries as hashable objects.
    It does so by converting between two domains, known as 'dictkeys' and 'tuplekeys'.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values
     that can be indexed natively in Python dictionaries.
    `DictKeyIndexing` works by selecting a single key:value pair 
     within a dictkey to serve as the tuplekey(s) to index by.
    It offers several conveniences to allow 
     working with both dictkeys and the values they are indexed by
    '''
    def __init__(self, key):
        self.key = key
    def dictkey(self, tuplekey):
        return {self.key:tuplekey}
    def check(self, dictkey):
        if self.key not in dictkey:
            raise KeyError(' '.join(['Dictionary is missing required key:', self.key]))
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through possible values for the given `key`
        given values from a `dictkey` dict that maps a key to either a value or a set of possible values.
        '''
        key = self.key
        if type(dictkey) in {dict}:
            return ([] if key not in dictkey 
                    else dictkey[key] if type(dictkey[key]) in {set,list} 
                    else [dictkey[key]])
        elif type(dictkey) in {set,list}:
            return dictkey
        else:
            return [dictkey]
    def count(self, dictkey):
        if type(dictkey) in {dict}:
            return (0 if key not in dictkey 
                    else len(dictkey[key]) if type(dictkey[key]) in {set,list} 
                    else 1)
        elif type(dictkey) in {set,list}:
            return len(dictkey)
        else:
            return 1

class DictTupleIndexing:
    '''
    `DictTupleIndexing` represents a method for using dictionaries as hashable objects.
    It does so by converting between two domains, known as 'dictkeys' and 'tuplekeys'.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values
     that can be indexed natively in Python dictionaries.
    `DictKeyIndexing` works by ordering values in a dictkey 
     into one or more tuplekeys according to a given list of `keys`.
    '''
    def __init__(self, keys, defaults={}):
        self.keys = keys
        self.defaults = defaults
    def dictkey(self, tuplekey):
        return {
            **self.defaults, 
            **{key:tuplekey[i] for i, key in enumerate(self.keys)}
        }
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through 
        possible tuples whose keys are given by `keys`
        and whose values are given by a `dictkey` dict 
        that maps a key from `keys` to either a value or a set of possible values.
        '''
        dictkey = {**self.defaults, **dictkey}
        return [tuple(reversed(tuplekey)) 
                for tuplekey in itertools.product(
                    *[[] if key not in dictkey
                      else dictkey[key] if type(dictkey[key]) in {set,list} 
                      else [dictkey[key]]
                      for key in reversed(self.keys)])]
    def check(self, dictkey):
        dictkey = {**self.defaults, **dictkey}
        missing = [key
                    for key in self.keys
                    if key not in dictkey
                ] if type(self) == DictTupleIndexing else []
        if missing:
            raise KeyError(' '.join(['Dictionary is missing required keys:', *missing]))
    def count(self, dictkey):
        '''
        Returns the number of possible tuples that can be generated from `self.tuplekeys(dictkey)`.
        '''
        dictkey = {**self.defaults, **dictkey}
        return math.prod([
                    0 if key not in dictkey
                    else len(dictkey[key]) if type(dictkey[key]) in {set,list}
                    else 1
                    for key in self.keys])
    def __iter__(self):
        return self.keys.__iter__()
    def __nonzero__(self):
        return len(self.keys) > 0
    def __bool__(self):
        return len(self.keys) > 0
    def __and__(self, other):
        '''
        Returns a new `DictKeyIndexing` that contains the intersection of keys from both `self` and `other`
        '''
        return DictTupleIndexing([key 
            for key in self.keys
            if key in other.keys])
    def __or__(self, other):
        '''
        Returns a new `DictKeyIndexing` that contains the union of keys from both `self` and `other`
        '''
        return DictTupleIndexing([
                *self.keys,
                *[key 
                  for key in other.keys
                  if key not in self.keys],
            ])
    def __sub__(self, other):
        '''
        Returns a new `DictKeyIndexing` that contains the negation of keys from `self` and `other`
        '''
        return DictTupleIndexing([key 
            for key in self.keys
            if key not in other.keys])

