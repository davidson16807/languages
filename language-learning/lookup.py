
class DictLookup:
    '''
    `DictLookup` is a lookup that indexes 'dictkeys' by a given `hashing` method,
    where `hashing` is of a class that shares the same iterface as `DictHashing`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, hashing, content=None):
        self.name = name
        self.hashing = hashing
        self.content = {} if content is None else content
    def __getitem__(self, key):
        '''
        Return the value that is indexed by `key` 
        if it is the only such value, otherwise return None.
        '''
        if isinstance(key, tuple):
            return self.content[key]
        else:
            tuplekeys = [tuplekey 
                for tuplekey in self.hashing.tuplekeys(key)
                if tuplekey in self.content]
            if len(tuplekeys) == 1:
                return self.content[tuplekeys[0]]
            elif len(tuplekeys) == 0:
                raise IndexError('\n'.join([
                                    'Key does not exist within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                ]))
            else:
                raise IndexError('\n'.join([
                                    'Key is ambiguous.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                    'Available interpretations:',
                                    *['\t'+str(self.hashing.dictkey(tuplekey)) 
                                      for tuplekey in tuplekeys]
                                ]))
    def __setitem__(self, key, value):
        '''
        Store `value` within the indices represented by `key`.
        '''
        if isinstance(key, tuple):
            return self.content[key]
        else:
            for tuplekey in self.hashing.tuplekeys(key):
                if tuplekey in self.content and value != self.content[tuplekey]:
                    raise IndexError('\n'.join([
                                    'Key already exists within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(self.hashing.dictkey(tuplekey)),
                                    'Old Value:', '\t'+str(self.content[tuplekey]),
                                    'New Value:', '\t'+str(value),
                                ]))
                else:
                    self.content[tuplekey] = value
    def __contains__(self, key):
        if isinstance(key, tuple):
            return key in self.content
        else:
            return any(tuplekey in self.content 
                       for tuplekey in self.hashing.tuplekeys(key))
    def __iter__(self):
        return self.content.__iter__()
    def __len__(self):
        return self.content.__len__()
    def values(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.content[tuplekey]
    def keys(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.hashing.dictkey(tuplekey)
    def items(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.hashing.dictkey(tuplekey), self.content[tuplekey]
