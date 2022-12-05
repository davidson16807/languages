import re

from shorthands import EmojiPerson

class Emoji:
    def __init__(self, 
            mood_templates, 
            emojiInflectionShorthand, 
            htmlTenseTransform, 
            htmlAspectTransform):
        self.emojiInflectionShorthand = emojiInflectionShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.mood_templates = mood_templates
    def conjugate(self, tags, argument, persons):
        audience_lookup = {
            'voseo':    '\\background{🇦🇷}\\n2{🧑\\g2\\c2}',
            'polite':   '\\n2{🧑\\g2\\c2\\💼}',
            'formal':   '\\n2{🤵\\c2\\g2}',
            'elevated': '\\n2{🤴\\g2\\c2}',
        }
        # TODO: reimplement formality as emoji modifier shorthand
        # audience = (audience_lookup[tags['formality']] 
        #          if tags['formality'] in audience_lookup 
        #          else '\\n2{🧑\\g2\\c2}')
        scene = getattr(self.htmlTenseTransform, tags['tense'])(
                    getattr(self.htmlAspectTransform, tags['aspect'].replace('-','_'))(argument))
        encoded_recounting = self.mood_templates[{**tags,'column':'template'}]
        subject = EmojiPerson(
            ''.join([
                    (tags['number'][0]),
                    ('i' if tags['clusivity']=='inclusive' else ''),
                ]), 
            tags['gender'][0], 
            persons[int(tags['person'])-1].color)
        persons = [
            subject if str(i+1)==tags['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiInflectionShorthand.decode(recounting, subject, persons)
        return recounting
    def decline(self, tags, scene, noun, persons):
        scene = scene.replace('\\declined', noun)
        scene = self.emojiInflectionShorthand.decode(scene, 
            EmojiPerson(
                tags['number'][0], 
                tags['gender'][0], 
                persons[int(tags['person'])-1].color), 
            persons)
        return scene

class RuleGrammar:
    """
    `RuleGrammar` is a library of functions that can be used in conjunction with `RuleProcessing` 
    to perform operations on a syntax tree of rules that encapsulate the grammar of a natural language.
    Examples include word translation, verb conjugation, noun and adjective declension, 
    and the structuring of clauses and noun phrases.
    """
    def __init__(self, 
            conjugation_lookups, 
            declension_lookups, 
            use_case_to_grammatical_case,
            sentence_structure,
            tags):
        self.conjugation_lookups = conjugation_lookups
        self.declension_lookups = declension_lookups
        self.use_case_to_grammatical_case = use_case_to_grammatical_case
        self.sentence_structure = sentence_structure
        self.tags = tags
    def decline(self, processing, rule):
        # NOTE: if content is a None type, then rely solely on the tag
        #  This logic provides a natural way to encode for pronouns
        missing_value = '' if rule.tag in {'art'} else None
        if rule.tags not in self.use_case_to_grammatical_case:
            return missing_value
        sememe = {
            **rule.tags, 
            **self.tags, 
            'case':self.use_case_to_grammatical_case[rule.tags]['case'], 
            'noun':rule.content[0]
        }
        return (missing_value if sememe not in self.declension_lookups
                else missing_value if sememe not in self.declension_lookups[sememe]
                else self.declension_lookups[sememe][sememe])
    def conjugate(self, processing, rule):
        tags = {**rule.tags, **self.tags, 'verb':rule.content[0]}
        return (None if tags not in self.conjugation_lookups[tags]
                else self.conjugation_lookups[tags][tags])
    def stock_modifier(self, language_type):
        def _stock_modifier(processing, rule):
            tags = {**rule.tags, **self.tags, 'verb':rule.content[0], 'language-type': language_type}
            return (None if tags not in self.conjugation_lookups['argument']
                    else self.conjugation_lookups['argument'][tags])
        return _stock_modifier
    def stock_adposition(self, processing, rule):
        tags = {**rule.tags, **self.tags}
        return (None if tags not in self.use_case_to_grammatical_case
                else self.use_case_to_grammatical_case[tags]['adposition'])
    def order_clause(self, processing, clause):
        verbs = [phrase for phrase in clause.content if phrase.tag in {'vp'}]
        nouns = [phrase for phrase in clause.content if phrase.tag in {'np'}]
        subject_roles = {'solitary','agent'}
        direct_object_roles = {'theme','patient'}
        indirect_object_roles = {'indirect-object'}
        nonmodifier_roles = {*subject_roles, *direct_object_roles, *indirect_object_roles}
        phrase_lookup = {
            'verb':            verbs,
            'subject':         [noun for noun in nouns if noun.tags['role'] in subject_roles],
            'direct-object':   [noun for noun in nouns if noun.tags['role'] in direct_object_roles],
            'indirect-object': [noun for noun in nouns if noun.tags['role'] in indirect_object_roles],
            'modifiers':       [noun for noun in nouns if noun.tags['role'] not in nonmodifier_roles],
        }
        return Rule(clause.tag, 
            clause.tags,
            processing.process([
                phrase
                for phrase_type in self.sentence_structure
                for phrase in phrase_lookup[phrase_type]
            ]))
    def order_noun_phrase(self, processing, phrase):
        return Rule(phrase.tag, 
            phrase.tags,
            processing.process([
                content for content in phrase.content 
                if content.tag not in {'art'} or 
                    ('noun-form' in content.tags and content.tags['noun-form'] in {'common'})
            ]))
    def passthrough(self, processing, rule):
        return Rule(rule.tag, rule.tags, processing.process(rule.content))
    def remove(self, processing, rule):
        return processing.process(rule.content)

class RuleFormatting:
    """
    `RuleFormatting` is a library of functions that can be used in conjunction with `RuleProcessing` 
    to cast a syntax tree to a string of natural language.
    """
    def __init__(self):
        pass
    def default(self, processing, rule):
        return ' '.join([processing.process(subrule) if isinstance(subrule, Rule) else str(subrule) 
                         for subrule in rule.content])
    def cloze(self, processing, rule):
        return '{{c'+str(1)+'::'+' '.join(str(element) for element in rule.content)+'}}'
    def implicit(self, processing, rule):
        return '['+str(' '.join([str(element) for element in rule.content]))+']'

class RuleValidation:
    """
    `RuleFormatting` is a library of functions that can be used in conjunction with `RuleProcessing` 
    to determine whether a sytax tree can be represented as a string of natural language.
    """
    def __init__(self):
        pass
    def exists(self, processing, rule):
        return all([processing.process(subrule) if isinstance(subrule, Rule) else subrule is not None
                    for subrule in rule.content])

class ListProcessing:
    """
    `ListProcessing` captures the transformation of tree like structures that are made out of lists.
    Its functionality is roughly comparable to that of the Lisp programming language.
    The content of lists is roughly comparable to that of the phase marker notation used in linguiustics:
        https://en.wikipedia.org/wiki/Parse_tree#Phrase_markers
    """
    def __init__(self, operations={}):
        self.operations = operations
    def process(self, tree, context={}):
        def wrap(x): 
            return x if isinstance(x, list) else [x]
        if len(tree) < 1: return tree
        opcode = tree[0]
        operands = tree[1:]
        return ([self.process(opcode, context), 
                *wrap(self.process(operands, context))] if isinstance(opcode, list)
            else self.operations[opcode](self, tree, context) if opcode in self.operations
            else [opcode, *wrap(self.process(operands, context))])

class ListTools:
    def __init__(self):
        pass
    def rule(self):
        def flatten(x): 
            return [xij for xi in x for xij in flatten(xi)] if isinstance(x, list) else [x]
        def _process(machine, tree, memory):
            return Rule(tree[0], memory, flatten(machine.process(tree[1:], memory)))
        return _process
    def replace(self, replacement):
        def _process(machine, tree, memory):
            return [replacement, *machine.process(tree[1:], memory)]
        return _process
    def remove(self):
        def _process(machine, tree, memory):
            return [*machine.process(tree[1:], memory)]
        return _process
    def tag(self, modifications, remove=False):
        def _process(machine, tree, memory):
            arguments = machine.process(tree[1:], {**memory, **modifications})
            return arguments if remove else [tree[0], *arguments]
        return _process
    def passthrough(self):
        def _process(machine, tree, memory):
            return [tree[0], machine.process(tree[1:], memory)]
        return _process

class EnglishListSubstitution:
    def __init__(self):
        pass
    def tense(self, machine, tree, memory):
        tense = memory['tense']
        verbform = memory['verb-form']
        if (tense, verbform) == ('future', 'finite'):       return ['will',        'infinitive', tree]
        if (tense, verbform) == ('past',   'infinitive'):   return ['[back then]', tree]
        if (tense, verbform) == ('present','infinitive'):   return ['[right now]', tree]
        if (tense, verbform) == ('future', 'infinitive'):   return ['[by then]',   tree]
        return tree
    def aspect(self, machine, tree, memory):
        '''same as self.inflection.conjugate(), but creates auxillary verb phrases when conjugation of a single verb is insufficient'''
        aspect = memory['aspect']
        if aspect == 'imperfect':           return [['aorist', 'v', 'be'],   'finite', tree]
        if aspect == 'perfect':             return [['aorist', 'v', 'have'], 'finite', tree]
        if aspect == 'perfect-progressive': return [['aorist', 'v', 'have'], 'finite', ['perfect', 'v', 'be'], ['imperfect', tree]]
        return tree
    def voice(self, machine, tree, memory):
        '''same as self.inflection.conjugate(), but creates auxillary verb phrases when conjugation of a single verb is insufficient'''
        voice = memory['voice']
        if voice  == 'passive': return [['active', 'v', 'be'],             'finite', ['active', 'perfect', tree]]
        if voice  == 'middle':  return [['active', 'implicit', 'v', 'be'], 'finite', ['active', 'perfect', tree]]
        return tree

class Rule:
    def __init__(self, tag, tags, content):
        self.tag = tag
        self.tags = tags
        self.content = content
    def __getitem__(self, key):
        return self.content[key]
    def __str__(self):
        return '' + self.tag + '{'+' '.join([
            member if isinstance(member, str) else str(member) 
            for member in self.content])+'}'
    def __repr__(self):
        return '' + self.tag + '{'+' '.join([
            member if isinstance(member, str) else repr(member) 
            for member in self.content])+'}'

class RuleProcessing:
    """
    `RuleProcessing` performs functionality analogous to ListProcessing 
    when transforming nested syntax trees that are made out of `Rule` objects.
    """
    def __init__(self, operations={}):
        self.operations = operations
    def process(self, rule):
        return ([self.process(subrule) for subrule in rule] if isinstance(rule, list)
            else rule if isinstance(rule, str)
            else self.operations[rule.tag](self, rule) if rule.tag in self.operations
            else Rule(rule.tag, rule.tags, processing.process(rule.content)))
