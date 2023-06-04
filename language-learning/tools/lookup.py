from .indexing import DictTupleIndexing

import math
import itertools

class DictLookup:
    '''
    `DictLookup` is a data structure that maps 'dictkeys' to values by hashing them with a given `indexing` method,
    where `indexing` is of a class that shares the same iterface as `DictIndexing`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, indexing, content=None):
        self.name = name
        self.indexing = indexing
        self.content = {} if content is None else content
    def __getitem__(self, dictkey):
        '''
        Return the value that is indexed by `dictkey` 
        if it is the only such value, otherwise return None.
        '''
        if type(dictkey) in {tuple,str}:
            return self.content[dictkey]
        else:
            tuplekeys = [tuplekey 
                for tuplekey in self.indexing.tuplekeys(dictkey)
                if tuplekey in self.content]
            if len(tuplekeys) == 1:
                return self.content[tuplekeys[0]]
            elif len(tuplekeys) == 0:
                self.indexing.check(dictkey)
                raise KeyError('\n'.join([
                                    'Key does not exist within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(dictkey),
                                    'Attempted interpretations:',
                                    *['\t'+str(self.indexing.dictkey(tuplekey)) 
                                      for tuplekey in self.indexing.tuplekeys(dictkey)]
                                ]))
            else:
                raise KeyError('\n'.join([
                                    'Key is ambiguous.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(dictkey),
                                    'Available interpretations:',
                                    *['\t'+str(self.indexing.dictkey(tuplekey)) 
                                      for tuplekey in tuplekeys]
                                ]))
    def __setitem__(self, dictkey, value):
        '''
        Store `value` within the indices represented by `dictkey`.
        '''
        if type(dictkey) in {tuple,str}:
            return self.content[dictkey]
        else:
            for tuplekey in self.indexing.tuplekeys(dictkey):
                if tuplekey in self.content and value != self.content[tuplekey]:
                    raise KeyError('\n'.join([
                                    'Key already exists within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(self.indexing.dictkey(tuplekey)),
                                    'Old Value:', '\t'+str(self.content[tuplekey]),
                                    'New Value:', '\t'+str(value),
                                ]))
                else:
                    self.content[tuplekey] = value
    def __contains__(self, dictkey):
        if type(dictkey) in {tuple,str}:
            return dictkey in self.content
        else:
            tuplekeys = list(self.indexing.tuplekeys(dictkey))
            return len(tuplekeys) == 1 and tuplekeys[0] in self
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

class DictSet:
    '''
    `DictSet` is a data structure that uniquely stores 'dictkeys' by hashing them with a given `indexing` method,
    where `indexing` is of a class that shares the same iterface as `DictIndexing`.
    It can be considered a set of points within a `DictSpace`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, indexing, sequence=None):
        self.name = name
        self.indexing = indexing
        sequence = [] if sequence is None else sequence
        misaligned = [len(tuplekey) for tuplekey in sequence if len(tuplekey) != len(indexing.keys)]
        if misaligned:
            raise ValueError(
                f'DictSpace indexing is misaligned with keys: expected {len(indexing.keys)}, got '+
                ', '.join(misaligned))
        self.sequence = []
        self.content = set()
        for element in sequence:
            if element not in self.content:
                self.sequence.append(element)
                self.content.add(element)
    def __contains__(self, key):
        if type(key) in {tuple,str}:
            return key in self.content
        else:
            tuplekeys = list(self.indexing.tuplekeys(key))
            return len(tuplekeys) == 1 and tuplekeys[0] in self
    def __str__(self):
        cell_width = 12
        return '\n'.join([
                ' '.join([element.rjust(cell_width) for element in self.indexing.keys]),
                *[' '.join([element.rjust(cell_width) for element in tuplekey]) for tuplekey in self.sequence]
            ])
    def __repr__(self):
        cell_width = 12
        return '\n'.join([
                ' '.join([element.rjust(cell_width) for element in self.indexing.keys]),
                *[' '.join([element.rjust(cell_width) for element in tuplekey]) for tuplekey in self.sequence]
            ])
    def __iter__(self):
        return self.sequence.__iter__()
    def __len__(self):
        return len(self.sequence)
    def empty(self):
        return len(self.sequence) < 1
    def fallback(self, other):
        assert type(other) == DictSpace
        return self|DictSpace('fallback',
                        other.indexing - self.indexing,
                        other.key_to_values)
    def __or__(self, other):
        '''
        Return the union of two `DictSet`s.
        Preserve the order of keys from `self`. Only add keys from `other` if they are unique
        '''
        name = f'{self.name} | {other.name}'
        indexing = self.indexing | other.indexing
        result = DictSet(name,
            indexing,
            [
                tuplekey
                for dictkeys in itertools.product(
                    [other.indexing.dictkey(tuplekey) for tuplekey in other],
                    [self.indexing.dictkey(tuplekey) for tuplekey in self])
                for tuplekey in indexing.tuplekeys({
                    key:{dictkey[key]
                         for dictkey in dictkeys
                         if key in dictkey}
                    for key in indexing.keys
                })
                # if indexing.dictkey(tuplekey) in self
                # or indexing.dictkey(tuplekey) in other
            ])
        if result.empty(): raise ValueError(f'Empty DictSet: {name}')
        return result
    def __and__(self, other):
        '''
        Return the intersection of two `DictSet`s whose keys are disjoint.
        If keys are not disjoint, replace values from `self` with those of `other`.
        '''
        product = self|(other if type(other) != DictSpace 
                        else DictSpace('temporary',
                                other.indexing - self.indexing,
                                other.key_to_values))
        name = f'{self.name} & {other.name}'
        result = DictSet(name,
            product.indexing,
            [tuplekey
             for tuplekey in product
             if product.indexing.dictkey(tuplekey) in self
             and product.indexing.dictkey(tuplekey) in other])
        if result.empty(): raise ValueError(f'Empty DictSet: {name}')
        return result
    def __sub__(self, other):
        '''
        Return the negation of two `DictSet`s.
        '''
        product = self|other
        name = f'({self.name}) - ({other.name})'
        result = DictSet(name,
            product.indexing,
            [tuplekey
             for tuplekey in product
             if product.indexing.dictkey(tuplekey) in self
             and product.indexing.dictkey(tuplekey) not in other])
        if result.empty(): raise ValueError(f'Empty DictSet: {name}')
        return result

class DictSpace:
    '''
    `DictSpace` is a representation for all possible states that could be assumed by a dictionary,
    given that the dictionary has a set of keys, and each key has a set of values that could be assigned, 
    as defined by a dictionary, `key_to_values`.
    '''
    def __init__(self, name, indexing, key_to_values):
        missing = [key for key in indexing.keys if key not in key_to_values.keys()]
        if missing:
            raise ValueError(f'DictSpace indexing is missing keys: ' + ', '.join(missing))
        # missing = [key for key in key_to_values.keys() if key not in indexing.keys or type(key_to_values[key]) in {set,list}]
        # if missing:
        #     raise ValueError(f'DictSpace key_to_values is missing keys: ' + ', '.join(missing))
        constants = [key 
            for (key, values) in key_to_values.items()
            if type(values) not in {set, list}]
        self.name = name
        self.indexing = indexing | DictTupleIndexing(constants)
        # self.key_to_values = key_to_values
        self.key_to_values = {
            key: (values if type(values) in {set, list} else [values])
            for key, values in key_to_values.items()
        }
    def __str__(self):
        return '\n'.join([f'{key:10}:{values}' for (key,values) in self.key_to_values.items()])
    def __repr__(self):
        return '\n'.join([f'{key:10}:{values}' for (key,values) in self.key_to_values.items()])
    def __contains__(self, dictkey):
        return all([
            key in dictkey and dictkey[key] in values
            for (key,values) in self.key_to_values.items()])
        # return all([
        #     key in self.key_to_values and value in self.key_to_values[key]
        #     for (key,value) in dictkey.items()])
    def __iter__(self):
        return self.indexing.tuplekeys(self.key_to_values).__iter__()
    def __len__(self):
        return math.prod([len(self.key_to_values[key]) for key in self.indexing])
    def empty(self):
        return not any([value for value in self.key_to_values.values()])
    def fallback(self, other):
        indexing = self.indexing | other.indexing
        assert type(other) == DictSpace
        return DictSpace(
            f'({self.name}) ? ({other.name})',
            indexing,
            {**other.key_to_values,
             **self.key_to_values})
    def update(self, other):
        indexing = self.indexing | other.indexing
        assert type(other) in {DictSpace, DictSet}
        if type(other) == DictSpace:
            return DictSpace(
                f'({self.name}), ({other.name})',
                indexing,
                {**self.key_to_values, 
                 **other.key_to_values})
        elif type(other) == DictSet:
            return other|DictSpace('fallback',
                            self.indexing - other.indexing,
                            self.key_to_values)
    def __or__(self, other):
        '''
        Return the union of two `DictSpace`s.
        Preserve the order of keys from `self`. Only add keys from `other` if they are unique
        '''
        indexing = self.indexing | other.indexing
        return (
            # the type of `other` could be anything, but union is commutative, so just ask `other` what to do if you don't know
            other|self if type(other) != DictSpace
            else DictSpace(
                f'{self.name} | {other.name}',
                indexing, 
                {key: set(self.key_to_values[key] if key in self.key_to_values else []) | 
                      set(other.key_to_values[key] if key in other.key_to_values else [])
                 for key in indexing.keys})
        )
    def __and__(self, other):
        '''
        Return the intersection of two `DictSpace`s whose keys are disjoint.
        If keys are not disjoint, replace values from `self` with those of `other`.
        '''
        indexing = self.indexing | other.indexing
        return (
            # the type of `other` could be anything, but union is commutative, so just ask `other` what to do if you don't know
            other&self if type(other) != DictSpace 
            else DictSpace(
                f'{self.name} & {other.name}',
                indexing, 
                {key: set(self.key_to_values[key] if key in self.key_to_values else other.key_to_values[key]) & 
                      set(other.key_to_values[key] if key in other.key_to_values else self.key_to_values[key])
                 for key in indexing.keys})
        )
    def __sub__(self, other):
        '''
        Return the negation of two `DictSpace`s.
        '''
        indexing = self.indexing | other.indexing
        if type(other) != DictSpace:
            product = self|other
            return DictSet(f'({self.name})-({other.name})',
                product.indexing,
                [tuplekey
                 for tuplekey in product
                 if product.indexing.dictkey(tuplekey) in self
                 and product.indexing.dictkey(tuplekey) not in other])
        else:
            return DictSpace(
                    f'({self.name})-({other.name})',
                    indexing, 
                    {key: set(self.key_to_values[key] if key in self.key_to_values else []) - 
                          set(other.key_to_values[key] if key in other.key_to_values else [])
                     for key in indexing.keys})

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
                raise KeyError('\n'.join([
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
                    raise KeyError('\n'.join([
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
            tuplekeys = list(self.indexing.tuplekeys(key))
            return len(tuplekeys) == 1 and tuplekeys[0] in self
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
