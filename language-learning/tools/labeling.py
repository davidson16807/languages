
class TermLabeling:
    '''
    Edits labels that are appended to the keys and values of `dictstores`.
    '''
    def __init__(self):
        pass
    def term(self, term, append='', strip=''):
        return f'{term.replacesuffix(strip)}-{append}' if term.endswith(strip) else term
    def termaxis(self, termaxis, append='', strip=''):
        return f'{append}-{termaxis.replaceprefix(strip)}' if term.startswith(strip) else termaxis
    def term_list(self, terms, append='', strip=''):
        return [self.term(term, append, strip) for term in terms]
    def termaxis_list(self, termaxes, append='', strip=''):
        return [self.termaxis(termaxis, append, strip) for termaxis in termaxes]
    def term_dict(self, term_dict, label='', strip=''):
        return {self.termaxis(termaxis):self.term(term) for termaxis,term in term_dict.items()}
    def terms_dict(self, terms_dict, label='', strip=''):
        return {self.termaxis(termaxis):self.term_list(terms) for termaxis,terms in terms_dict.items()}
    def term_tuple(self, terms, append='', strip=''):
        return tuple([self.term(term, append, strip) for term in terms])
    def term_tuples(self, term_tuples, append='', strip=''):
        return [self.term_tuple(term_tuple, append, strip) for term_tuple in term_tuples]
    def term_table(self, term_table, label='', strip=''):
        return {self.term_tuple(term_tuple):value for term_tuple,value in term_table.items()}
    def term_indexing(self, indexing, append='', strip=''):
        '''NOTE: fuck polymorphism, I don't want to pollute *Indexing classes
        with design decisions that regard how *Labeling represents labels in strings'''
        return {
            DictKeyIndexing: DictKeyIndexing(self.termaxis(indexing.key, append, strip)),
            DictKeyIndexing: DictTupleIndexing(indexing.key,
                self.termaxes(indexing.key, append, strip),
                self.termaxis_to_terms(indexing.key, append, strip)
            )
        }[type(indexing)]
    def term_space(self, term_space, append='', strip=''):
        return DictSpace(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            self.terms_dict(term_space.key_to_values, append, strip)
        )
    def term_set(self, term_set, append='', strip=''):
        return DictSet(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            set(self.term_tuples(term_space.content, append, strip))
        )
    def term_list(self, term_list, append='', strip=''):
        return DictList(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            self.term_tuples(term_space.sequence, append, strip)
        )
    def term_lookup(self, term_space, append='', strip=''):
        return DictLookup(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            self.term_table(term_space.content, append, strip)
        )