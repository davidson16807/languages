
class DictLookup:
    '''
    `DictLookup` is a lookup that indexes 'dictkeys' by a given `indexing` method,
    where `indexing` is of a class that shares the same iterface as `DictIndexing`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, indexing, content=None):
        self.name = name
        self.indexing = indexing
        self.content = {} if content is None else content
    def __getitem__(self, key):
        '''
        Return the value that is indexed by `key` 
        if it is the only such value, otherwise return None.
        '''
        if type(key) in {tuple,str}:
            return self.content[key]
        else:
            tuplekeys = [tuplekey 
                for tuplekey in self.indexing.tuplekeys(key)
                if tuplekey in self.content]
            if len(tuplekeys) == 1:
                return self.content[tuplekeys[0]]
            elif len(tuplekeys) == 0:
                raise IndexError('\n'.join([
                                    'Key does not exist within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                    'Attempted interpretations:',
                                    *['\t'+str(self.indexing.dictkey(tuplekey)) 
                                      for tuplekey in self.indexing.tuplekeys(key)]
                                ]))
            else:
                raise IndexError('\n'.join([
                                    'Key is ambiguous.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                    'Available interpretations:',
                                    *['\t'+str(self.indexing.dictkey(tuplekey)) 
                                      for tuplekey in tuplekeys]
                                ]))
    def __setitem__(self, key, value):
        '''
        Store `value` within the indices represented by `key`.
        '''
        if type(key) in {tuple,str}:
            return self.content[key]
        else:
            for tuplekey in self.indexing.tuplekeys(key):
                if tuplekey in self.content and value != self.content[tuplekey]:
                    raise IndexError('\n'.join([
                                    'Key already exists within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(self.indexing.dictkey(tuplekey)),
                                    'Old Value:', '\t'+str(self.content[tuplekey]),
                                    'New Value:', '\t'+str(value),
                                ]))
                else:
                    self.content[tuplekey] = value
    def __contains__(self, key):
        if type(key) in {tuple,str}:
            return key in self.content
        else:
            return any(tuplekey in self.content 
                       for tuplekey in self.indexing.tuplekeys(key))
    def __iter__(self):
        return self.content.__iter__()
    def __len__(self):
        return self.content.__len__()
    def values(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.content[tuplekey]
    def keys(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.indexing.dictkey(tuplekey)
    def items(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.indexing.dictkey(tuplekey), self.content[tuplekey]

class DefaultDictLookup:
    '''
    `DictLookup` is a lookup that indexes 'dictkeys' by a given `indexing` method,
    where `indexing` is of a class that shares the same iterface as `DictIndexing`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, indexing, get_default, content=None):
        self.name = name
        self.indexing = indexing
        self.get_default = get_default
        self.content = {} if content is None else content
    def __getitem__(self, key):
        '''
        Return the value that is indexed by `key` 
        if it is the only such value, otherwise return None.
        '''
        if type(key) in {tuple, str}:
            if key in self.content:
                return self.content[key]
            else:
                value = self.get_default(self.indexing.dictkey(key))
                self.content[key] = value
                return value
        else:
            tuplekeys = list(self.indexing.tuplekeys(key))
            if len(tuplekeys) == 1:
                return self.__getitem__(tuplekeys[0])
            else:
                raise IndexError('\n'.join([
                                    'Key is ambiguous.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                    'Available interpretations:',
                                    *['\t'+str(self.indexing.dictkey(tuplekey)) 
                                      for tuplekey in tuplekeys]
                                ]))
    def __setitem__(self, key, value):
        '''
        Store `value` within the indices represented by `key`.
        '''
        if type(key) in {tuple, str}:
            self.content[key] = value
        else:
            for tuplekey in self.indexing.tuplekeys(key):
                if tuplekey in self.content and value != self.content[tuplekey]:
                    raise IndexError('\n'.join([
                                    'Key already exists within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(self.indexing.dictkey(tuplekey)),
                                    'Old Value:', '\t'+str(self.content[tuplekey]),
                                    'New Value:', '\t'+str(value),
                                ]))
                else:
                    self.content[tuplekey] = value
    def __contains__(self, key):
        if type(key) in {tuple,str}:
            return key in self.content
        else:
            return any(tuplekey in self.content 
                       for tuplekey in self.indexing.tuplekeys(key))
    def __iter__(self):
        return self.content.__iter__()
    def __len__(self):
        return self.content.__len__()
    def values(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.content[tuplekey]
            else:
                yield default
    def keys(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            yield tuplekey
    def items(self, dictkey):
        for tuplekey in self.indexing.tuplekeys(dictkey):
            dictkey = self.indexing.dictkey(tuplekey)
            if tuplekey in self.content:
                yield dictkey, self.content[tuplekey]
            else:
                yield dictkey, self.get_default(dictkey)
