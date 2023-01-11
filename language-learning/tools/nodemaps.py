import re

from .nodes import Rule

"""
"nodes.py" contains functionality used to manipulate individual nodes in a syntax tree
"""

class ListGrammar:
    """
    `ListGrammar` is a library of functions that can be used in conjunction with `ListTrees` 
    to perform operations on a syntax tree of lists that encapsulate the grammar of a natural language.
    Examples include word translation, verb conjugation, noun and adjective declension, 
    and the structuring of clauses and noun phrases.
    """
    def __init__(self, 
            conjugation_lookups, 
            declension_lookups, 
            use_case_to_grammatical_case,
            tags):
        self.conjugation_lookups = conjugation_lookups
        self.declension_lookups = declension_lookups
        self.use_case_to_grammatical_case = use_case_to_grammatical_case
        self.tags = tags
        def format_alternates(text, tags):
            split = re.split(' *[|/,] *', text)
            show_alternates = 'show-alternates' in tags and tags['show-alternates']
            return split[0] if not show_alternates else '|'.join(split)
        self.format_alternates = format_alternates
    def decline(self, treemap, content, tags):
        # NOTE: if content is a None type, then rely solely on the tag
        #  This logic provides a natural way to encode for pronouns
        missing_value = '' if content[0] in {'det'} else None
        if tags not in self.use_case_to_grammatical_case:
            return missing_value
        sememe = {
            **tags, 
            **self.tags, 
            'case':self.use_case_to_grammatical_case[tags]['case'], 
            'noun':content[1] if len(content)>1 else None
        }
        return [content[0], 
            missing_value if sememe not in self.declension_lookups
            else missing_value if sememe not in self.declension_lookups[sememe]
            else self.format_alternates(self.declension_lookups[sememe][sememe], tags)]
    def conjugate(self, treemap, content, tags):
        sememe = {**tags, **self.tags, 'verb':content[1]}
        # print('conjugate')
        # print(sememe)
        return [content[0], 
            None if sememe not in self.conjugation_lookups[sememe]
            else self.format_alternates(self.conjugation_lookups[sememe][sememe], tags)]
    def stock_modifier(self, language_type):
        def _stock_modifier(treemap, content, tags):
            sememe = {**tags, **self.tags, 'language-type': language_type}
            # print('stock_modifier')
            # print(sememe)
            return [content[0], 
                None if sememe not in self.conjugation_lookups['argument']
                else self.conjugation_lookups['argument'][sememe]]
        return _stock_modifier
    def stock_adposition(self, treemap, content, tags):
        sememe = {
            **tags, 
            **self.tags, 
            'case':self.use_case_to_grammatical_case[tags]['case'], 
        }
        return ([] if sememe not in self.use_case_to_grammatical_case 
            else [content[0], self.use_case_to_grammatical_case[sememe]['adposition']])

class RuleSyntax:
    """
    `RuleSyntax` is a library of functions that can be used in conjunction with 
    `RuleTrees` to perform operations on a syntax tree of rules that encapsulate 
    the syntax of a natural language.
    Examples include word translation, verb conjugation, noun and adjective declension, 
    and the structuring of clauses and noun phrases.
    """
    def __init__(self, sentence_structure):
        self.sentence_structure = sentence_structure
    def order_clause(self, treemap, clause):
        rules = clause.content
        # rules = [element for element in clause.content if isinstance(element, Rule)]
        nouns = [phrase for phrase in rules if phrase.tag in {'np'}]
        subject_roles = {'solitary','agent'}
        direct_object_roles = {'theme','patient'}
        indirect_object_roles = {'indirect-object'}
        nonmodifier_roles = {*subject_roles, *direct_object_roles, *indirect_object_roles}
        subjects = [noun for noun in nouns if noun.tags['role'] in subject_roles]
        enclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'enclitic'}]
        proclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'proclitic'}]
        noun_lookup = {
            'direct-object':   [noun for noun in nouns if noun.tags['role'] in direct_object_roles],
            'indirect-object': [noun for noun in nouns if noun.tags['role'] in indirect_object_roles],
            'modifiers':       [noun for noun in nouns if noun.tags['role'] not in nonmodifier_roles],
        }
        verbs = [phrase
            for phrase in rules 
            if phrase.tag in {'vp'}]
        phrase_lookup = {
            **noun_lookup,
            'subject': subjects,
            'verb': verbs,
        }
        return Rule(clause.tag, 
            clause.tags,
            treemap.map([
                phrase
                for phrase_type in self.sentence_structure
                for phrase in phrase_lookup[phrase_type]
            ]))
    def order_noun_phrase(self, treemap, phrase):
        # rules = [element for element in phrase.content if isinstance(element, Rule)]
        return Rule(phrase.tag, 
            phrase.tags, 
            treemap.map([
                content for content in phrase.content 
                if not isinstance(content,Rule) or 
                   content.tag not in {'det'} or 
                   ('noun-form' in content.tags and content.tags['noun-form'] in {'common'})
            ]))

class RuleFormatting:
    """
    `RuleFormatting` is a library of functions that can be used in conjunction with `RuleTrees` 
    to cast a syntax tree to a string of natural language.
    """
    def __init__(self):
        pass
    def default(self, treemap, rule):
        return (' '.join([str(treemap.map(element)) for element in rule.content]) if isinstance(rule, Rule) else rule).replace('∅','')
    def cloze(self, treemap, rule):
        return '{{c'+str(1)+'::'+' '.join(str(treemap.map(element)) for element in rule.content)+'}}'
    def implicit(self, treemap, rule):
        return '['+str(' '.join([str(treemap.map(element)) for element in rule.content]))+']'
    def parentheses(self, treemap, rule):
        return '('+str(' '.join([str(treemap.map(element)) for element in rule.content]))+')'

class RuleValidation:
    """
    `RuleFormatting` is a library of functions that can be used in conjunction with `RuleTrees` 
    to determine whether a sytax tree can be represented as a string of natural language.
    """
    def __init__(self, disabled=False):
        self.disabled = disabled
    def exists(self, treemap, rule):
        return all([treemap.map(subrule) if isinstance(subrule, Rule) else (subrule is not None or self.disabled)
                    for subrule in rule.content])

class ListTools:
    def __init__(self):
        pass
    def tag(self, modifications, remove=False):
        def _map(machine, tree, memory):
            arguments = machine.map(tree[1:], {**memory, **modifications})
            return arguments if remove else [tree[0], *arguments]
        return _map
    def rule(self):
        def flatten(x): 
            return [xij for xi in x for xij in flatten(xi)] if isinstance(x, list) else [x]
        def _map(machine, tree, memory):
            return Rule(tree[0], memory, flatten(machine.map(tree[1:], memory)))
        return _map
    def replace(self, *functions):
        def _map(machine, tree, memory):
            return [*functions, *machine.map(tree[1:], memory)]
        return _map
    def constant(self, *values):
        def _map(machine, tree, memory):
            return [*values]
        return _map
    def postprocess(self, function):
        def _map(machine, tree, memory):
            return [function, tree[0], *machine.map(tree[1:], memory)]
        return _map
    def preprocess(self, function):
        def _map(machine, tree, memory):
            return [tree[0], function, *machine.map(tree[1:], memory)]
        return _map
    def wrap(self, function):
        def _map(machine, tree, memory):
            return [function, tree[0], *machine.map(tree[1:], memory)]
        return _map
    def unwrap(self):
        def _map(machine, tree, memory):
            return machine.map(tree[1:], memory)
        return _map
    def prune(self):
        def _map(machine, tree, memory):
            return []
        return _map
    def memory_to_preprocess(lookup):
        def tense(self, machine, tree, memory):
            return [*lookup[memory], tree[0], *machine.map(tree[1:], memory)]
    def memory_to_postprocess(lookup):
        def tense(self, machine, tree, memory):
            return [tree[0], *lookup[memory], *machine.map(tree[1:], memory)]
