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

class Translation:
    """
    `Translation` is a library of functions that can be used in conjunction with `RuleProcessing` 
    to perform operations on a syntax tree of rules that are specific to a language.
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
        tags = {**rule.tags, **self.tags, 'noun':rule.content[0]}
        # NOTE: if content is a None type, then rely solely on the tag
        #  This logic provides a natural way to encode for pronouns
        missing_value = '' if rule.tag in {'art'} else None
        return (missing_value if tags not in self.declension_lookups
                else missing_value if tags not in self.declension_lookups[tags]
                else self.declension_lookups[tags][tags])
    def conjugate(self, processing, rule):
        tags = {**rule.tags, **self.tags, 'verb':rule.content[0]}
        return (None if tags not in self.conjugation_lookups['finite']
                else self.conjugation_lookups['finite'][tags])
    def stock_modifier(self, processing, rule):
        tags = {**rule.tags, **self.tags, 'verb':rule.content[0]}
        return (None if tags not in self.conjugation_lookups['argument']
                else self.conjugation_lookups['argument'][tags])
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

class English:
    def __init__(self, 
            plurality,
            declension_lookups, 
            conjugation_lookups, 
            predicate_templates, 
            mood_templates):
        self.plurality = plurality
        self.declension_lookups = declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.predicate_templates = predicate_templates
        self.mood_templates = mood_templates
    def format(self, content):
        if type(content) in {Clause}:
            clause = content
            dependant_clause = {
                **clause.tags,
                'language-type': 'english',
            }
            independant_clause = {
                **clause.tags,
                'language-type': 'english',
                'aspect': 'aorist',
                'tense':     
                    'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                    'present' if dependant_clause['tense'] in {'future'} else
                    dependant_clause['tense']
            }
            verb = self.format(clause.verb)
            lemmas = ['be', 'have', 'command', 'forbid', 'permit', 'wish', 'intend', 'be able', verb]
            mood_replacements = [
                ('{predicate}',            self.predicate_templates[{**dependant_clause,'verb-form':'finite'}]),
                ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'verb-form':'infinitive'}]),
            ]
            sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
            for replaced, replacement in mood_replacements:
                sentence = sentence.replace(replaced, replacement)
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                sentence = sentence.replace('{'+noun+'}', 
                    self.format(self.decline(clause.tags, 
                        clause.nouns[noun] if noun in clause.nouns else [])))
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                for case in ['nominative','oblique','genitive']:
                    sentence = sentence.replace('{'+f'{noun}|{case}'+'}', 
                        self.format(self.decline({**clause.tags, 'case':case}, 
                            clause.nouns[noun] if noun in clause.nouns else [])))
            sentence = sentence.replace('{verb', '{'+verb)
            table = self.conjugation_lookups['finite']
            for lemma in lemmas:
                replacements = [
                    ('{'+lemma+'|independant}',         table[{**independant_clause, 'verb':lemma, }]),
                    ('{'+lemma+'|independant|speaker}', table[{**independant_clause, 'verb':lemma, 'person':'1', 'number':'singular'}]),
                    ('{'+lemma+'|present}',             table[{**dependant_clause,   'verb':lemma, 'tense':  'present',  'aspect':'aorist'}]),
                    ('{'+lemma+'|past}',                table[{**dependant_clause,   'verb':lemma, 'tense':  'past',     'aspect':'aorist'}]),
                    ('{'+lemma+'|perfect}',             table[{**dependant_clause,   'verb':lemma, 'aspect': 'perfect'    }]),
                    ('{'+lemma+'|imperfect}',           table[{**dependant_clause,   'verb':lemma, 'aspect': 'imperfect'  }]),
                    ('{'+lemma+'|infinitive}',          lemma),
                ]
                for replaced, replacement in replacements:
                    sentence = sentence.replace(replaced, replacement)
            if dependant_clause['voice'] == 'middle':
                sentence = f'[middle voice:] {sentence}'
            sentence = re.sub('\s+', ' ', sentence)
            return sentence
        if content is None:
            return ''
        if type(content) in {list,set}:
            return ' '.join([self.format(element) for element in content])
        elif type(content) in {str}:
            return content
        elif type(content) in {NounPhrase}:
            return self.format(self.decline(content.tags, content.content))
        elif type(content) in {Adjective, Article}:
            return self.format(content.content)
        elif type(content) in {Adposition}:
            return self.format(content.native)
        elif type(content) in {Cloze}:
            # NOTE: Cloze is only ever used to prompt for the foreign language being learned,
            # so for the user's native language it is simply equal to the formatted content.
            return self.format(content.content) 
    def decline(self, tags, content):
        tags = {**tags, 'language-type':'english'}
        if content is None:
            case = tags['case'] if tags['case'] in {'nominative','genitive'} else 'oblique'
            tags = {**tags, 'case': case}
            return (
                self.declension_lookups[tags][tags] if tags['noun-form'] != 'common'
                else self.plurality.pluralize(tags['noun']) if tags['number'] != 'singular'
                else tags['noun'])
        if type(content) in {list,set}:
            return [self.decline(tags, element) for element in content]
        elif type(content) in {str}:
            # NOTE: string types are degenerate cases of None types invocations
            #  where tags contain the lemma for the declension
            return self.decline({**tags, 'noun':content}, None) 
        elif type(content) in {NounPhrase}:
            tags = {**tags, **content.tags}
            case = tags['case'] if tags['case'] in {'nominative','genitive'} else 'oblique'
            tags = {**tags, 'case': case}
            return NounPhrase(tags, self.decline(tags, content.content))
        elif type(content) in {StockModifier}:
            return content.lookup[tags] if tags in content.lookup else []
        elif type(content) in {Adjective, Article}:
            return (content if tags['noun-form'] == 'common' else [])
        elif type(content) in {Adposition}:
            return content
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.decline(tags, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def conjugate(self, tags, content):
        if type(content) in {list,set}:
            return [self.conjugate(tags, element) for element in content]
        elif type(content) in {str}:
            tags = {**tags, 'language-type':'translated'}
            if tags not in self.conjugation_lookups['finite']:
                return None
            return self.conjugation_lookups['finite'][tags]
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.conjugate(tags, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')

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
        return '{{c'+str(1)+'::'+rule.content[0]+'}}'

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
    def tag(self, modifications):
        def _process(machine, tree, memory):
            return machine.process(tree[1:], {**memory, **modifications})
        return _process
    def passthrough(self):
        def _process(machine, tree, memory):
            return [tree[0], machine.process(tree[1:], memory)]
        return _process

class Rule:
    def __init__(self, tag, tags, content):
        self.tag = tag
        self.tags = tags
        self.content = content
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
            else self.operations[rule.tag](self, rule) if rule.tag in self.operations
            else Rule(rule.tag, rule.tags, processing.process(rule.content)))
