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
            case_usage,
            mood_usage,
            aspect_usage,
            tags):
        self.conjugation_lookups = conjugation_lookups
        self.declension_lookups = declension_lookups
        self.case_usage = case_usage
        self.mood_usage = mood_usage
        self.aspect_usage = aspect_usage
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
        if tags not in self.case_usage:
            return missing_value
        sememe = {
            **tags, 
            **self.tags, 
            'case':self.case_usage[tags]['case'], 
            'noun':content[1] if len(content)>1 else None
        }
        # if sememe not in self.declension_lookups[sememe] and sememe['noun'] != 'the':
        #     breakpoint()
        return [content[0], 
            missing_value if sememe not in self.declension_lookups
            else missing_value if sememe not in self.declension_lookups[sememe]
            else self.format_alternates(self.declension_lookups[sememe][sememe], tags)]
    def conjugate(self, treemap, content, tags):
        # print(tags)
        # print(self.aspect_usage.content)
        # print(self.aspect_usage[tags].content)
        # if 'aspect' not in self.aspect_usage[tags]:
        #     breakpoint()
        sememe = {
            **tags, 
            **self.tags, 
            'aspect':self.aspect_usage[tags]['aspect'],
            'verb':content[1],
        }
        return [content[0], 
            None if sememe not in self.conjugation_lookups[sememe]
            else self.format_alternates(self.conjugation_lookups[sememe][sememe], tags)]
    def stock_modifier(self, language_type):
        def _stock_modifier(treemap, content, tags):
            sememe = {**tags, **self.tags, 'language-type': language_type}
            return [content[0], 
                None if sememe not in self.conjugation_lookups['argument']
                else self.conjugation_lookups['argument'][sememe]]
        return _stock_modifier
    def stock_adposition(self, treemap, content, tags):
        sememe = {
            **tags, 
            **self.tags, 
            'case':self.case_usage[tags]['case'], 
        }
        return ([] if sememe not in self.case_usage 
            else [] if 'preposition' not in self.case_usage[sememe]
            else [content[0], self.case_usage[sememe]['preposition']])

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
    def __init__(self, affix_delimiter='-'):
        self.affix_delimiter = affix_delimiter
        self.affix_regex = re.compile('\s*-\s*')
        self.space_regex = re.compile('\s+')
        self.empty_regex = re.compile('∅')
    def default(self, treemap, element):
        newline = '&#xA;'
        def format_section(lookup, tags):
            return newline.join([
                f'{key} : {lookup[key]}'
                for key in tags
                if key in lookup])
        def format_lookup(lookup):
            return (newline*2).join([
                format_section(lookup, 'mood evidentiality confidence'.split()),
                format_section(lookup, 'aspect progress'.split()),
                format_section(lookup, 'verb completion strength voice tense'.split()),
                format_section(lookup, 'case valency motion role'.split()),
                format_section(lookup, 'noun person number gender clusivity formality clitic partitivity'.split()),
                format_section(lookup, 'Language-type script'.split()),
            ])
        result ={
            str:        lambda text: text,
            Rule:       lambda rule: f'<span title="{format_lookup(rule.tags)}">{" ".join([str(treemap.map(subrule)) for subrule in rule.content])}</span>',
            type(None): lambda none: f'[MISSING]',
        }[type(element)](element)
        result = self.affix_regex.sub(self.affix_delimiter, result)
        result = self.space_regex.sub(' ', result)
        result = self.empty_regex.sub('', result)
        result = result.strip()
        return result
    def cloze(self, treemap, rule):
        return '{{c'+str(1)+'::'+' '.join(str(treemap.map(element)) for element in rule.content)+'}}'
    def implicit(self, treemap, rule):
        return '['+str(' '.join([str(treemap.map(element)) for element in rule.content]))+']'
    def parentheses(self, treemap, rule):
        return '('+str(' '.join([str(treemap.map(element)) for element in rule.content]))+')'

class RuleValidation:
    """
    `RuleValidation` is a library of functions that can be used in conjunction with `RuleTrees` 
    to determine whether a sytax tree can be represented as a string of natural language.
    """
    def __init__(self, disabled=False):
        self.disabled = disabled
    def exists(self, treemap, rule):
        return all([
            {
                Rule:       lambda subrule: treemap.map(subrule),
                str:        lambda text:    '—' not in text,
                type(None): lambda none:    self.disabled,
            }[type(element)](element)
            for element in rule.content])

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

class RuleTools:
    def __init__(self):
        pass
    def filter_tags(self, tags):
        def _map(treemap, rule):
            return Rule(rule.tag,
                {key:value for key,value in rule.tags.items()
                 if tags is None or key in tags},
                treemap.map([content for content in rule.content]))
        return _map