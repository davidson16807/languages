from tools.indexing import DictKeyIndexing, DictTupleIndexing
from tools.dictstores import DictSpace, DictList, DictSet, DictLookup, DefaultDictLookup

class TermLabelEditing:
    '''
    Edits labels that are appended to the keys and values of `dictstores`.
    '''
    def __init__(self):
        pass
    def term(self, term, append='', strip=''):
        return f'{term.removesuffix(strip)}-{append}' if term.endswith(strip) else term
    def termaxis(self, termaxis, append='', strip=''):
        return f'{append}-{termaxis.removeprefix(strip)}' if termaxis.startswith(strip) else termaxis
    def term_list(self, terms, append='', strip=''):
        return [self.term(term, append, strip) for term in terms]
    def termaxis_list(self, termaxes, append='', strip=''):
        return [self.termaxis(termaxis, append, strip) for termaxis in termaxes]
    def termaxis_to_term_dict(self, termaxis_to_term_dict, label='', strip=''):
        return {self.termaxis(termaxis):self.term(term) for termaxis,term in termaxis_to_term_dict.items()}
    def termaxis_to_terms_dict(self, termaxis_to_terms_dict, label='', strip=''):
        return {self.termaxis(termaxis):self.term_list(terms) for termaxis,terms in termaxis_to_terms_dict.items()}
    def term_tuple(self, terms, append='', strip=''):
        return tuple([self.term(term, append, strip) for term in terms])
    def term_tuples(self, term_tuples, append='', strip=''):
        return [self.term_tuple(term_tuple, append, strip) for term_tuple in term_tuples]
    def terms_to_token_dict(self, terms_to_token_dict, label='', strip=''):
        return {self.term_tuple(term_tuple):token for term_tuple,token in terms_to_token_dict.items()}
    def term_indexing(self, indexing, append='', strip=''):
        '''NOTE: fuck polymorphism, I don't want to pollute *Indexing classes
        with design decisions that regard how *Labeling represents labels in strings'''
        return {
            DictKeyIndexing:   lambda: DictKeyIndexing(self.termaxis(indexing.key, append, strip)),
            DictTupleIndexing: lambda: DictTupleIndexing(
                self.termaxis_list(indexing.keys, append, strip),
                self.termaxis_to_terms_dict(indexing.defaults, append, strip)
            )
        }[type(indexing)]()
    def term_space(self, term_space, append='', strip=''):
        return DictSpace(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            self.termaxis_to_terms_dict(term_space.key_to_values, append, strip)
        )
    def term_set(self, term_set, append='', strip=''):
        return DictSet(term_set.name, 
            self.term_indexing(term_set.indexing, append, strip),
            set(self.term_tuples(term_set.content, append, strip))
        )
    def term_list(self, term_list, append='', strip=''):
        return DictList(term_list.name, 
            self.term_indexing(term_list.indexing, append, strip),
            self.term_tuples(term_list.sequence, append, strip)
        )
    def term_lookup(self, term_lookup, append='', strip=''):
        return DictLookup(term_lookup.name, 
            self.term_indexing(term_lookup.indexing, append, strip),
            self.terms_to_token_dict(term_lookup.content, append, strip)
        )

class TermLabelFiltering:
    '''
    Edits labels that are appended to the keys and values of `dictstores`.
    '''
    def __init__(self):
        pass
    def term(self, term, append='', strip=''):
        return term.endswith(strip)
    def termaxis(self, termaxis, append='', strip=''):
        return termaxis.startswith(strip)
    def term_list(self, terms, append='', strip=''):
        return [term for term in terms if self.term(term, append, strip)]
    def termaxis_list(self, termaxes, append='', strip=''):
        return [termaxis for termaxis in termaxes if self.termaxis(termaxis, append, strip)]
    def termaxis_to_term_dict(self, termaxis_to_term_dict, label='', strip=''):
        return {termaxis:term for termaxis,term in termaxis_to_term_dict.items() if self.termaxis(termaxis)}
    def termaxis_to_terms_dict(self, termaxis_to_term_dict, label='', strip=''):
        return {termaxis:terms for termaxis,terms in termaxis_to_term_dict.items() if self.termaxis(termaxis)}
    def term_tuple(self, terms, append='', strip=''):
        return tuple([term for term in terms if self.term(term, append, strip)])
    def term_tuples(self, term_tuples, append='', strip=''):
        return [term_tuple for term_tuple in term_tuples if self.term_tuple(term_tuple, append, strip)]
    def terms_to_token_dict(self, terms_to_token_dict, label='', strip=''):
        return {self.term_tuple(term_tuple):value for term_tuple,value in terms_to_token_dict.items()}
    def term_indexing(self, indexing, append='', strip=''):
        #NOTE: this function only makes sense if indexing is an instance of DictTupleIndexing
        return DictTupleIndexing(
            self.termaxis_list(indexing.keys, append, strip),
            self.termaxis_to_terms_dict(indexing.defaults, append, strip)
        )
    def term_space(self, term_space, append='', strip=''):
        return DictSpace(term_space.name, 
            self.term_indexing(term_space.indexing, append, strip),
            self.termaxis_to_terms_dict(term_space.key_to_values, append, strip)
        )
    def term_set(self, term_set, append='', strip=''):
        return DictSet(term_set.name, 
            self.term_indexing(term_set.indexing, append, strip),
            set(self.term_tuples(term_set.content, append, strip))
        )
    def term_list(self, term_list, append='', strip=''):
        return DictList(term_list.name, 
            self.term_indexing(term_list.indexing, append, strip),
            self.term_tuples(term_list.sequence, append, strip)
        )
    def term_lookup(self, term_lookup, append='', strip=''):
        return DictLookup(term_lookup.name, 
            self.term_indexing(term_lookup.indexing, append, strip),
            self.terms_to_token_dict(term_lookup.content, append, strip)
        )
