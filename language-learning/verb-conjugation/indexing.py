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
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through possible values for the given `key`
        given values from a `dictkey` dict that maps a key to either a value or a set of possible values.
        '''
        key = self.key
        if type(dictkey) in {dict}:
            return dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
        elif type(dictkey) in {set,list}:
            return dictkey
        else:
            return [dictkey]

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
    def __init__(self, keys):
        self.keys = keys
    def dictkey(self, tuplekey):
        return {key:tuplekey[i] for i, key in enumerate(self.keys)}
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through 
        possible tuples whose keys are given by `keys`
        and whose values are given by a `dictkey` dict 
        that maps a key from `keys` to either a value or a set of possible values.
        '''
        return [tuple(reversed(tuplekey)) 
                for tuplekey in itertools.product(
                    *[dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
                      for key in reversed(self.keys)])]
