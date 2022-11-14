import re
import copy
import collections
import itertools

import plurality

from transforms import *
from shorthands import *
from parsing import SeparatedValuesFileParsing
from annotation import *
from indexing import *
from lookup import *
from population import *

category_to_grammemes = {

    # needed to lookup the argument that is used to demonstrate a verb
    'language-type':   ['english', 'translated', 'transcripted'], 

    'script':[
        # scripts that were derived from the phoenecian alphabet:
        'latin','cyrillic','greek','hebrew','arabic','phoenician',
        # scripts that were invented, borrowing aesthetics from chinese logograms:
        'hirigana','katakana','hangul',
        # scripts that were derived from chinese logograms:
        'traditional han','simplified han','kanji','hanja','chữ hán','chữ nôm',
        # scripts that were derived from the brahmic abugida:
        'devanagari','bengali','gujarati','gurmukhi','oria','tibetan',
        'simhala','malayalam','tamil','telugu','kannada',
        'burmese','khmer','thai','lao','balinese','javanese','sundanese','brahmic',
        # scripts that were derived from egyptian heiroglyphs:
        'coptic','meroitic','demotic','hieratic',
        # broad categories of script to handle niche applications:
        'runes','heiroglyphs','cuneiform','emoji'],

    # needed for infinitives
    'completion': ['full', 'bare'],

    # needed for finite forms
    'person':     ['1','2','3'],
    'number':     ['singular', 'dual', 'plural'],
    'clusivity':  ['inclusive', 'exclusive'],
    'mood':       ['indicative', 'subjunctive', 'conditional', 
                   'optative', 'benedictive', 'jussive', 'probable', 
                   'imperative', 'prohibitive', 'desiderative', 
                   'dubitative', 'hypothetical', 'presumptive', 'permissive', 
                   'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
                   'precative', 'volitive', 'involutive', 'inferential', 
                   'necessitative', 'interrogative', 'injunctive', 
                   'suggestive', 'comissive', 'deliberative', 
                   'propositive', 'potential', 
                  ],

    # animacy ordered as follows:
    # 1st column: represents any of the grammemes that precede the entry in the middle column of that row
    # 2nd column: represents its own unique grammeme that excludes all preceding rows and following entries
    # 3rd column: represents any of the grammemes that follow the entry in the middle column of that row
    # As an example, all "animate" things are "living" but not all "dynamic" things are "living",
    # all "static" things are "nonliving" but not all static things are "abstract",
    # and a "plant" is "living", "dynamic", "nonagent", and "inanimate", among others.
    'animacy':    [            'human',       'nonhuman',    # member of the species homo sapiens
                   'sapient',  'humanoid',    'nonsapient',  # having the ability to think and speak
                   'animate',  'creature',    'inanimate',   # able to move around on its own
                   'living',   'plant',       'nonliving',   # able to grow and reproduce
                   'concrete', 'perceptible', 'abstract',    # able to take physical form
                   'thing'],
    'partitivity':['nonpartitive', 'partitive', 'bipartitive'],
    'clitic':     ['tonic', 'proclitic', 'mesoclitic', 'endoclitic', 'enclitic'],
    'distance':   ['proximal','medial','distal'],

    # needed for possessive pronouns
    'possession-gender': ['masculine-possession', 'feminine-possession', 'neuter-possession'],
    'possession-number': ['singular-possession', 'dual-possession', 'plural-possession'],

    # needed for Spanish
    'formality':  ['familiar', 'polite', 'elevated', 'formal', 'tuteo', 'voseo'],

    # needed for Sanskrit
    'stem':       ['primary', 'causative', 'intensive',],

    # needed for gerunds, supines, participles, and gerundives
    'gender':     ['masculine', 'feminine', 'neuter'],
    'case':       ['nominative', 'oblique', 
                   'accusative', 'genitive', 'dative', 'ablative', 'locative', 'instrumental', 'vocative', 
                   'partitive', 'prepositional', 'abessive', 'adessive', 'allative', 'comitative', 'delative', 
                   'elative', 'essive', 'essive-formal', 'essive-modal', 'exessive', 'illative', 
                   'inessive', 'instructive', 'instrumental-comitative', 'sociative', 'sublative', 'superessive', 
                   'temporal', 'terminative', 'translative','disjunctive', 'undeclined'],
    'motion': ['departed', 'associated', 'acquired', 'leveraged'],
    'cast': [
        'subject', 'direct-object', 'possessor',
        'location', 'extent', 'vicinity', 'interior', 'surface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 'ownership', 
        'time', 'state of being', 'topic', 'company', 'resemblance'],
    

    # needed for infinitive forms, finite forms, participles, arguments, and graphic depictions
    'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
    'tense':      ['present', 'past', 'future',], 
    'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 

    # needed for correlatives in general
    'abstraction':['institution','location','origin',
                   'destination','time','manner','reason','quality','amount'],
    # needed to distinguish pronouns from common nouns and to further distinguish types of pronouns
    'noun-form':  ['common', 'personal', 'reflexive', 'emphatic-reflexive',
                   'demonstrative', 'interrogative', 'indefinite', 'elective', 'universal', 'negative', 
                   'relative', 'numeral'],
    # needed to distinguish forms of verb that require different kinds of lookups with different primary keys
    'verb-form':     ['finite', 'infinitive', 
                      'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
                      'argument', 'group'],
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes.items() 
    for instance in instances
}

lemma_hashing = DictKeyIndexing('verb')

verbial_declension_hashing = DictTupleIndexing([
        'verb',           
        'voice',      # needed for Swedish
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'case',       # needed for Latin
        'script',     # needed for Greek, Russian, Sanskrit, etc.
    ])

conjugation_template_lookups = DictLookup(
    'conjugation',
    DictKeyIndexing('verb-form'), 
    {
        # verbs that indicate a subject
        'finite': DictLookup(
            'finite',
            DictTupleIndexing([
                    'verb',           
                    'person',           
                    'number',           
                    'gender',     # needed for Russian
                    'formality',  # needed for Spanish ('voseo')
                    'mood',        
                    'voice',           
                    'tense',           
                    'aspect',      
                    'script',     # needed for Greek, Russian, Sanskrit, etc.
                ])),
        # verbs that do not indicate a subject
        'infinitive': DictLookup(
            'infinitive',
            DictTupleIndexing([
                    'verb',           
                    'completion', # needed for Old English
                    'voice',      # needed for Latin, Swedish
                    'tense',      # needed for German, Latin
                    'aspect',     # needed for Greek
                    'script',     # needed for Emoji, Greek, Russian, Sanskrit, etc.
                ],
                {'completion':'bare'}
            )),
        # verbs used as adjectives, indicating that an action is done upon a noun at some point in time
        'participle': DictLookup(
            'participle',
            DictTupleIndexing([
                    'verb',           
                    'number',  # needed for German
                    'gender',     # needed for Latin, German, Russian
                    'case',       # needed for Latin, German
                    'voice',      # needed for Russian
                    'tense',      # needed for Greek, Russian, Spanish, Swedish, French
                    'aspect',     # needed for Greek, Latin, German, Russian
                    'script',
                ])),
        # verbs used as adverbs
        'adverbial': DictLookup(
            'participle',
            DictTupleIndexing([
                    'verb',           
                    'tense',      # needed for Russian
                    'script',
                ])),
        # verbs used as adjectives, indicating the purpose of something
        'gerundive': DictLookup('gerundive', verbial_declension_hashing),
        # verbs used as nouns
        'gerund': DictLookup('gerund', verbial_declension_hashing),
        # verbs used as nouns, indicating the objective of something
        'supine': DictLookup('supine', verbial_declension_hashing),
        # a pattern in conjugation that the verb is meant to demonstrate
        'group': DictLookup('group', lemma_hashing),
        # text that follows a verb in a sentence that demonstrates the verb
        'argument': DictLookup(
            'argument',
            DictTupleIndexing([
                    'verb',           
                    'language-type',           
                    'voice',    # needed for Greek
                    'gender',   # needed for Greek
                    'number',   # needed for Russian
                    'script',
                ])),
    })

basic_pronoun_declension_hashing = DictTupleIndexing([
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'animacy',    # needed for Old English, Russian
        'partitivity',# needed for Old English, Quenya, Finnish
        'case',       # needed for Latin
        'script',     # needed for Greek, Russian, Quenya, Sanskrit, etc.
    ])

declension_template_lookups = DictLookup(
    'declension',
    DictKeyIndexing('noun-form'), 
    {
        'common': DictLookup(
            'common',
            DictTupleIndexing([
                    'noun',
                    'number',           
                    'gender',           
                    'partitivity', # needed for Quenya, Finnish
                    'case',           
                    'script',
                ])),
        'personal': DictLookup(
            'personal',
            DictTupleIndexing([
                    'person',           
                    'number',           
                    'clitic',
                    'clusivity',   # needed for Quechua
                    'formality',   # needed for Spanish ('voseo')
                    'gender',           
                    'case',           
                    'script',
                ])),
        'demonstrative': DictLookup(
            'demonstrative',
            DictTupleIndexing([
                    'distance',
                    'number',     
                    'gender',     
                    'animacy',     # needed for Russian
                    'partitivity', # needed for Old English, Quenya, Finnish
                    'case',       
                    'script',
                ])),
        'interrogative':      DictLookup('interrogative',      basic_pronoun_declension_hashing),
        'indefinite':         DictLookup('indefinite',         basic_pronoun_declension_hashing),
        'universal':          DictLookup('universal',          basic_pronoun_declension_hashing),
        'negative':           DictLookup('negative',           basic_pronoun_declension_hashing),
        'relative':           DictLookup('relative',           basic_pronoun_declension_hashing),
        'numeral':            DictLookup('numeral',            basic_pronoun_declension_hashing),
        'reflexive':          DictLookup('reflexive',          basic_pronoun_declension_hashing),
        'emphatic-reflexive': DictLookup('emphatic-reflexive', basic_pronoun_declension_hashing),
    })

class English:
    def __init__(self, 
            declension_lookups, 
            conjugation_lookups, 
            predicate_templates, 
            mood_templates):
        self.declension_lookups = declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.predicate_templates = predicate_templates
        self.mood_templates = mood_templates
    def decline(self, grammemes, content):
        grammemes = {**grammemes, 'language-type':'english'}
        if content is None:
            return (
                self.declension_lookups[grammemes][grammemes] if grammemes['noun-form'] != 'common'
                else plurality.english.pluralize(grammemes['noun']) if grammemes['number'] != 'singular'
                else grammemes['noun'])
        if type(content) in {list,set}:
            return [self.decline(grammemes, element) for element in content]
        elif type(content) in {str}:
            # NOTE: string types are degenerate cases of None types invocations
            #  where grammemes contain the lemma for the declension
            return self.decline({**grammemes, 'noun':content}, None) 
        elif type(content) in {NounPhrase}:
            return NounPhrase({**grammemes, **content.grammemes}, 
                self.decline({**grammemes, **content.grammemes}, content.content))
        elif type(content) in {StockModifier}:
            return content.lookup[grammemes] if grammemes in content.lookup else []
        elif type(content) in {Adjective, Article, Adposition}:
            return content
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.decline(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def conjugate(self, grammemes, content):
        if type(content) in {list,set}:
            return [self.conjugate(grammemes, element) for element in content]
        elif type(content) in {str}:
            grammemes = {**grammemes, 'language-type':'translated'}
            if grammemes not in self.conjugation_lookups['finite']:
                return None
            return self.conjugation_lookups['finite'][grammemes]
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.conjugate(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def format(self, content):
        if type(content) in {Clause}:
            clause = content
            dependant_clause = {
                **clause.grammemes,
                'language-type': 'english',
            }
            independant_clause = {
                **clause.grammemes,
                'language-type': 'english',
                'aspect': 'aorist',
                'tense':     
                    'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                    'present' if dependant_clause['tense'] in {'future'} else
                    dependant_clause['tense']
            }
            verb = self.format(clause.verb)
            lemmas = ['be', 'have', 
                      'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
                      verb]
            mood_replacements = [
                ('{predicate}',            self.predicate_templates[{**dependant_clause,'verb-form':'finite'}]),
                ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'verb-form':'infinitive'}]),
            ]
            sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
            for replaced, replacement in mood_replacements:
                sentence = sentence.replace(replaced, replacement)
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                sentence = sentence.replace('{'+noun+'}', 
                    self.format(self.decline(clause.grammemes, 
                        clause.nouns[noun] if noun in clause.nouns else [])))
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                for case in ['nominative','oblique']:
                    sentence = sentence.replace('{'+f'{noun}|{case}'+'}', 
                        self.format(self.decline({**clause.grammemes, 'case':case}, 
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
        elif type(content) in {NounPhrase, Adjective, Article}:
            return self.format(content.content)
        elif type(content) in {Adposition}:
            return self.format(content.native)
        elif type(content) in {Cloze}:
            # NOTE: Cloze is only ever used to prompt for the foreign language being learned,
            # so for the user's native language it is simply equal to the formatted content.
            return self.format(content.content) 
    def parse(self, NodeClass, text):
        if NodeClass in {set}:
            return set(text.split(' '))
        if NodeClass in {list}:
            return text.split(' ')
        elif NodeClass in {str}:
            return text
        else:
            return NodeClass(self.parse(text))

class Emoji:
    def __init__(self, emojiInflectionShorthand, 
            htmlTenseTransform, htmlAspectTransform, mood_templates):
        self.emojiInflectionShorthand = emojiInflectionShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.mood_templates = mood_templates
    def inflect(self, grammemes, argument, persons):
        audience_lookup = {
            'voseo':    '\\background{🇦🇷}\\n2{🧑\\g2\\c2}',
            'polite':   '\\n2{🧑\\g2\\c2\\💼}',
            'formal':   '\\n2{🤵\\c2\\g2}',
            'elevated': '\\n2{🤴\\g2\\c2}',
        }
        # TODO: reimplement formality as emoji modifier shorthand
        # audience = (audience_lookup[grammemes['formality']] 
        #          if grammemes['formality'] in audience_lookup 
        #          else '\\n2{🧑\\g2\\c2}')
        scene = getattr(self.htmlTenseTransform, grammemes['tense'])(
                    getattr(self.htmlAspectTransform, grammemes['aspect'].replace('-','_'))(argument))
        encoded_recounting = self.mood_templates[{**grammemes,'column':'template'}]
        subject = Person(
            ''.join([
                    (grammemes['number'][0]),
                    ('i' if grammemes['clusivity']=='inclusive' else ''),
                ]), 
            grammemes['gender'][0], 
            persons[int(grammemes['person'])-1].color)
        persons = [
            subject if str(i+1)==grammemes['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiInflectionShorthand.decode(recounting, subject, persons)
        return recounting

class Cloze:
    def __init__(self, id_, content):
        self.id = id_
        self.content = content

class NounPhrase:
    def __init__(self, grammemes, content=None):
        self.grammemes = grammemes
        self.content = content

class Adjective:
    def __init__(self, content):
        self.content = content

class Adposition:
    def __init__(self, native, foreign):
        self.native = native
        self.foreign = foreign

class Article:
    def __init__(self, content):
        self.content = content

class StockModifier:
    def __init__(self, lookup):
        self.lookup = lookup

class Clause:
    def __init__(self, grammemes, verb, nouns=[]):
        self.grammemes = grammemes
        self.verb = verb
        self.nouns = nouns

class Translation:
    def __init__(self, 
            declension_lookups, 
            conjugation_lookups, 
            mood_templates,
            category_to_grammemes):
        self.declension_lookups = declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.mood_templates = mood_templates
        self.category_to_grammemes = category_to_grammemes
    def parse(self, NodeClass, text):
        if NodeClass in {set}:
            return set(text.split(' '))
        elif NodeClass in {list}:
            return text.split(' ')
        elif NodeClass in {str}:
            return text
        else:
            return NodeClass(text.split(' '))
    def format(self, content):
        if type(content) in {Clause}:
            sentence = self.mood_templates[content.grammemes['mood']]
            sentence = sentence.replace('{verb}', self.format(content.verb))
            for noun_tag in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                sentence = sentence.replace('{'+noun_tag+'}', 
                    self.format(content.nouns[noun_tag] if noun_tag in content.nouns else ''))
            sentence = re.sub('\s+', ' ', sentence)
            return sentence
        elif content is None:
            return ''
        elif type(content) in {list,set}:
            return ' '.join([self.format(element) for element in content])
            # TODO: implement language agnostic way to specify word order in noun phrases
        elif type(content) in {str}:
            return content
        elif type(content) in {NounPhrase}:
            return self.format(content.content)
            # TODO: implement language agnostic way to specify location of adpositions
        elif type(content) in {Adjective, Article}:
            return self.format(content.content)
        elif type(content) in {Adposition}:
            return self.format(content.foreign)
        elif type(content) in {Cloze}:
            return '{{c'+str(content.id)+'::'+self.format(content.content)+'}}'
    def exists(self, content):
        if content is None:
            return False
        elif type(content) in {list,set}:
            return all([self.exists(element) for element in content])
        elif type(content) in {str}:
            return True
        elif type(content) in {Adjective, Article, Adposition}:
            return True
        elif type(content) in {NounPhrase}:
            return True
        elif type(content) in {Clause}:
            return self.exists(content.verb)
        elif type(content) in {Cloze}:
            return self.exists(content.content)
    def decline(self, grammemes, content):
        grammemes = {**grammemes, 'language-type':'translated'}
        if content is None:
            # NOTE: if content is a None type, then rely solely on the grammeme
            #  This logic provides a natural way to encode for pronouns
            if grammemes not in self.declension_lookups:
                return None
            if grammemes not in self.declension_lookups[grammemes]:
                return None
            return self.declension_lookups[grammemes][grammemes]
        elif type(content) in {list,set}:
            return [self.decline(grammemes, element) for element in content]
        elif type(content) in {str}:
            # NOTE: string types are degenerate cases of None types invocations
            #  where grammemes contain the lemma for the declension
            return self.decline({**grammemes, 'noun':content}, None) 
        elif type(content) in {NounPhrase}:
            return NounPhrase(content.grammemes, 
                self.decline({**grammemes, **content.grammemes}, content.content))
        elif type(content) in {StockModifier}:
            return content.lookup[grammemes] if grammemes in content.lookup else []
        elif type(content) in {Adjective}:
            return Adjective(self.decline(grammemes, content.content))
        elif type(content) in {Article}:
            return Article(self.decline(grammemes, content.content))
        elif type(content) in {Adposition}:
            return Adposition(
                native=content.native, 
                foreign=self.decline(grammemes, content.foreign))
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.decline(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def conjugate(self, grammemes, content):
        if type(content) in {list,set}:
            return [self.conjugate(grammemes, element) for element in content]
        elif type(content) in {str}:
            grammemes = {**grammemes, 'language-type':'translated', 'verb':content}
            if grammemes not in self.conjugation_lookups['finite']:
                return None
            else:
                return self.conjugation_lookups['finite'][grammemes]
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.conjugate(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def inflect(self, grammemes, content):
        if type(content) in {Clause}:
            grammemes = {**grammemes, **content.grammemes}
            return Clause(grammemes,
                self.conjugate(grammemes, content.verb), 
                {key:self.decline(grammemes, value) for (key,value) in content.nouns.items()})
        elif type(content) in {list,set}:
            return [self.inflect(grammemes, element) for element in content]
        elif type(content) in {NounPhrase}:
            grammemes = {**grammemes, **content.grammemes}
            return self.decline(grammemes, content)

tsv_parsing = SeparatedValuesFileParsing()

finite_annotation  = CellAnnotation(
    grammeme_to_category, {}, {0:'verb'}, 
    {**category_to_grammemes, 'script':'latin', 'verb-form':'finite'})
infinitive_annotation  = CellAnnotation(
    grammeme_to_category, {}, {0:'verb'},
    {**category_to_grammemes, 'script':'latin', 'verb-form':'infinitive'})
pronoun_annotation  = CellAnnotation(
    grammeme_to_category, {}, {}, 
    {**category_to_grammemes, 'script':'latin', 'noun-form':'personal', 'language-type':'translated'})
noun_annotation  = CellAnnotation(
    grammeme_to_category, {}, {0:'noun'}, 
    {**category_to_grammemes, 'script':'latin', 'noun-form':'common', 'person':'3', 'language-type':'translated'})
declension_template_noun_annotation = CellAnnotation(
    grammeme_to_category, {0:'language'}, {0:'noun'}, 
    {**category_to_grammemes, 'script':'latin', 'noun-form':'common', 'person':'3', 'language-type':'translated'})
predicate_annotation = CellAnnotation(
    grammeme_to_category, {0:'column'}, {}, 
    {**category_to_grammemes, 'script':'latin', 'verb-form':'finite'})
mood_annotation        = CellAnnotation(
    {}, {0:'column'}, {0:'mood'}, {'script':'latin'})

conjugation_population = NestedLookupPopulation(conjugation_template_lookups)
declension_population  = NestedLookupPopulation(declension_template_lookups)
predicate_population = FlatLookupPopulation(DictLookup('predicate', DictTupleIndexing(['verb-form','voice','tense','aspect'])))
mood_population = FlatLookupPopulation(DictLookup('mood', DictTupleIndexing(['mood','column'])))

class CardFormatting:
    def __init__(self):
        pass
    def emoji_focus(self, content):
        fonts = ''' sans-serif, Twemoji, "Twemoji Mozilla", "Segoe UI Emoji", "Noto Color Emoji" '''
        return f'''<div style='font-size:3em; padding: 0.5em; display:inline-box; font-family: {fonts}'>{content}</div>'''
    def foreign_focus(self, content):
        return f'''<div style='font-size:3em'>{content}</div>'''
    def foreign_side_note(self, content):
        return f'''<div style='font-size:2em'>{content}</div>'''
    def english_word(self, content):
        return f'''<div>{content}</div>'''

def first_of_options(content):
    return content.split('/')[0]

def replace(replacements):
    def _replace(content):
        for replaced, replacement in replacements:
            content = content.replace(replaced, replacement)
        return content
    return _replace

def require(content):
    return content if content.strip() else None

def compose(*text_functions):
    if len(text_functions) > 1:
        return lambda content: text_functions[0](compose(text_functions[1:]))
    else:
        return text_functions[0]

class CardGeneration:
    def __init__(self, english, emoji, cardFormatting, finite_traversal):
        self.english = english
        self.emoji = emoji
        self.cardFormatting = cardFormatting
        self.finite_traversal = finite_traversal
    def declension(self, translation, filter_lookups, persons, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = self.finite_traversal.dictkey(tuplekey)
    def conjugation(self, translation, filter_lookups, persons, default_grammemes={}, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = {**default_grammemes, **self.finite_traversal.dictkey(tuplekey)}
            if all([dictkey in filter_lookup for filter_lookup in filter_lookups]):
                clause = Clause(dictkey, Cloze(1, dictkey['verb']),
                    {
                        'subject':    NounPhrase({'noun-form': 'personal', 'case':'nominative'}),
                        'modifiers':  StockModifier(translation.conjugation_lookups['argument']),
                    })
                emoji_key       = {**dictkey, 'script':'emoji'}
                if translation.exists(clause) and emoji_key in translation.conjugation_lookups['infinitive']:
                    english_text    = self.english.format(clause)
                    translated_text = translation.format(translation.inflect(dictkey,clause))
                    emoji_argument  = translation.conjugation_lookups['infinitive'][emoji_key]
                    emoji_text      = self.emoji.inflect(dictkey, emoji_argument, persons)
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)), 
                            self.cardFormatting.foreign_focus(translated_text),
                        ])

infinitive_traversal = DictTupleIndexing(['tense', 'aspect', 'mood', 'voice'])

bracket_shorthand = BracketedShorthand(Enclosures())

html_text_transform = HtmlTextTransform()
html_group_positioning = HtmlGroupPositioning()
html_person_positioning = HtmlPersonPositioning(html_group_positioning)

emoji_shorthand = EmojiInflectionShorthand(
    EmojiSubjectShorthand(), 
    EmojiPersonShorthand(
        EmojiNumberShorthand(
            HtmlNumberTransform(html_person_positioning), bracket_shorthand)),
    EmojiBubbleShorthand(HtmlBubble(), bracket_shorthand),
    TextTransformShorthand(html_text_transform, bracket_shorthand),
    EmojiAnnotationShorthand(html_group_positioning, bracket_shorthand),
    EmojiModifierShorthand(),
)

emoji = Emoji(
    emoji_shorthand, HtmlTenseTransform(), HtmlAspectTransform(), 
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/mood-templates.tsv'), 1, 1)),
    )

english = English(
    declension_population.index(
        pronoun_annotation.annotate(tsv_parsing.rows('data/inflection/english/modern/pronoun-declensions.tsv'), 1, 5)),
    conjugation_population.index(
        finite_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/modern/conjugations.tsv'), 4, 2)),
    predicate_population.index(
        predicate_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/modern/predicate-templates.tsv'), 1, 4)),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/modern/mood-templates.tsv'), 1, 1)),
)

card_generation = CardGeneration(
    english, emoji, CardFormatting(),
    DictTupleIndexing([
        'number','formality','clusivity','person','clitic','gender',
        'tense', 'aspect', 'mood', 'voice', 'verb']))

def write(filename, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(f'{row}\n')

def has_annotation(key, value):
    def _has_annotation(annotated_cell):
        annotation, cell = annotated_cell
        return key in annotation and annotation[key] == value or value in annotation[key]
    return _has_annotation

'''
write('flashcards/verb-conjugation/ancient-greek.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/finite-conjugations.tsv'), 3, 4),
                *infinitive_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/nonfinite-conjugations.tsv'), 6, 2),
            ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'optative':    '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'imperative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine'],
                'mood':      ['indicative','subjunctive','optative','imperative'],
                'verb':     ['be','go','release'],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'dual',     'neuter'),
                    ('2', 'dual',     'neuter'),
                    ('3', 'dual',     'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                }),
        ],
        persons = [Person('s','n',color) for color in [3,2,4,1,5]],
    ))

write('flashcards/verb-conjugation/french.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/french/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/french/finite-conjugations.tsv'), 4, 3),
                *infinitive_annotation.annotate(
                    tsv_parsing.rows('data/inflection/french/nonfinite-conjugations.tsv'), 3, 1),
            ]),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'subjunctive': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'conditional': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'imperative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine'],
                'voice':      'active',
                'mood':      ['indicative','conditional','subjunctive','imperative',],
                'verb':      ['have','be','go','speak','choose','lose','receive'],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [2,3,1,4,5]],
    ))

write('flashcards/verb-conjugation/german.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/german/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index([
                    *finite_annotation.annotate(
                        tsv_parsing.rows('data/inflection/german/finite-conjugations.tsv'), 4, 3),
                    *infinitive_annotation.annotate(
                        tsv_parsing.rows('data/inflection/german/nonfinite-conjugations.tsv'), 7, 1),
                ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'conditional': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'inferential': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'imperative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality': ['familiar','polite','formal','elevated'],
                'gender':    ['neuter', 'masculine'],
                'voice':      'active',
                'mood':      ['indicative','conditional','inferential',
                              'subjunctive','imperative',],
                'verb':     ['be', 'do', 'go', 'become', 'may', 
                              'have', 'love', 'act', 'work', 'drive'], 
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'formality', 'gender']),
                content = {
                    ('1', 'singular', 'familiar', 'neuter'),
                    ('2', 'singular', 'familiar', 'neuter'),
                    ('2', 'singular', 'polite',   'masculine'),
                    ('2', 'singular', 'polite',   'feminine'),
                    ('2', 'singular', 'elevated', 'neuter'),
                    ('3', 'singular', 'familiar', 'masculine'),
                    ('1', 'plural',   'familiar', 'neuter'),
                    ('2', 'plural',   'familiar', 'neuter'),
                    ('2', 'plural',   'polite',   'neuter'),
                    ('2', 'plural',   'elevated', 'neuter'),
                    ('3', 'plural',   'familiar', 'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [2,3,1,4,5]],
    ))
'''


declension_verb_annotation = CellAnnotation(
    grammeme_to_category, {0:'language'}, {0:'verb'}, 
    {'script':'latin', 'verb-form':'finite','gender':['masculine','feminine']})

latin = Translation(
    declension_population.index([
        *pronoun_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/classical/pronoun-declensions.tsv'), 1, 4),
        *noun_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/classical/declensions.tsv'), 1, 2),
        *filter(has_annotation('language','latin'),
            declension_template_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'), 2, 7)),
    ]),
    conjugation_population.index([
        *finite_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/classical/finite-conjugations.tsv'), 3, 4),
        *infinitive_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/classical/nonfinite-conjugations.tsv'), 6, 2),
        *filter(has_annotation('language','latin'),
            declension_verb_annotation.annotate(
                tsv_parsing.rows(
                    'data/inflection/declension-template-verbs.tsv'), 2, 9)),
    ]),
    mood_templates = {
        'indicative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
        'subjunctive': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
        'imperative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}!',
    },
    category_to_grammemes = {
        **category_to_grammemes,
        'script':     'latin',
        'noun-form':  'personal',
        'number':    ['singular','plural'],
        'animacy':    'human',
        'clitic':     'tonic',
        'clusivity':  'exclusive',
        'formality':  'familiar',
        'gender':    ['neuter', 'masculine'],
        'voice':     ['active', 'passive'],
        'mood':      ['indicative','subjunctive','imperative',],
        'verb':      ['be', 'be able', 'want', 'become', 'go', 
                      'carry', 'eat', 'love', 'advise', 'direct-object', 
                      'capture', 'hear'],
    },
)

write('flashcards/verb-conjugation/latin.html', 
    card_generation.conjugation(
        latin,
        default_grammemes={'script':'latin'},
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [2,3,1,4,5]],
    ))


from parsing import SeparatedValuesFileParsing
from annotation import RowAnnotation
from predicates import Predicate
from lookup import DefaultDictLookup, DictLookup
from indexing import DictTupleIndexing, DictKeyIndexing
from evaluation import KeyEvaluation, MultiKeyEvaluation
from population import ListLookupPopulation, FlatLookupPopulation

tsv_parsing = SeparatedValuesFileParsing()
rows = [
  *tsv_parsing.rows('data/predicates/mythical/greek.tsv'),
  *tsv_parsing.rows('data/predicates/mythical/hindi.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/animal-anatomy.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/animal.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/deity.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/human.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/humanoid.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/plant-anatomy.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/plant.tsv'),
  *tsv_parsing.rows('data/predicates/biotic/sapient.tsv'),
  *tsv_parsing.rows('data/predicates/abiotic/item.tsv'),
  *tsv_parsing.rows('data/predicates/abiotic/location.tsv'),
  *tsv_parsing.rows('data/predicates/abiotic/physical.tsv'),
  *tsv_parsing.rows('data/predicates/abstract/attribute.tsv'),
  *tsv_parsing.rows('data/predicates/abstract/time.tsv'),
  *tsv_parsing.rows('data/predicates/abstract/event.tsv'),
  *tsv_parsing.rows('data/predicates/abstract/concept.tsv'),
  *tsv_parsing.rows('data/predicates/animacy-hierarchy.tsv'),
  *tsv_parsing.rows('data/predicates/capability.tsv'),
]

level0_subset_relations = set()
level1_subset_relations = collections.defaultdict(
    set, 
    {
        'be':{'can'},
        'part':{'can-be-part'},
    })

for row in rows:
    f, x, g, y = row[:4]
    if all([f.strip(), x.strip(), g.strip(), y.strip()]):
        level0_subset_relations.add(((f,x),(g,y)))

allthat = collections.defaultdict(Predicate)
for (f,x),(g,y) in level0_subset_relations:
    allthat[f,x].name = str((f,x))
    allthat[g,y].name = str((g,y))
    allthat[g,y](allthat[f,x])
    for h in level1_subset_relations[f]:
        allthat[h,x].name = str((h,x))
        allthat[h,x](allthat[f,x])
    for h in level1_subset_relations[g]:
        allthat[h,y].name = str((h,y))
        allthat[h,y](allthat[g,y])
    # if g == f:
    #     for h in level1_subset_relations[f]:
    #         allthat[h,y](allthat[h,x])

declension_template_annotation = RowAnnotation([
    'motion', 'cast', 'specificity',
    'subject-adjective', 'subject-function', 'subject-argument', 
    'verb', 'direct-object-adjective', 'direct-object', 'adposition', 
    'declined-noun-article', 'declined-noun-function', 'declined-noun-argument',
    'emoji'])
template_population = ListLookupPopulation(
    DefaultDictLookup('declension-template',
        DictTupleIndexing(['motion','cast']), list))
templates = \
    template_population.index(
        declension_template_annotation.annotate(
            tsv_parsing.rows(
                'data/inflection/declension-templates-minimal.tsv')))

class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, motion, cast):
        def subject(template):
            return self.predicates[template['subject-function'], template['subject-argument']]
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        candidates = self.templates[motion, cast] if (motion, cast) in self.templates else []
        templates = sorted([template for template in candidates
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: (-int(template['specificity']), len(declined_noun(template))))
        return templates[0] if len(templates) > 0 else None

case_annotation = RowAnnotation(['motion','cast','case','adposition'])
case_indexing = DictTupleIndexing(['motion','cast'])
case_population = \
    FlatLookupPopulation(
        DictLookup('declension-use-case-to-grammatical-case', case_indexing),
        MultiKeyEvaluation(['case','adposition']))

use_case_to_grammatical_case = \
    case_population.index(
        case_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/classical/declension-use-case-to-grammatical-case.tsv')))

matching = DeclensionTemplateMatching(templates, allthat)

'''
ROADMAP:
* template maching should find the template for "walking", not "directing attention"
* fix issue where certain verbs cannot be found in csv
* template population should produce an error if no verb is found for them
* add templates for nominative, accusative, genitive, and dative
* add bracketed comments to english templates
'''

cardFormatting = CardFormatting()

declension_traversal = DictTupleIndexing(['motion','cast','number'])
lemmas = [
    'man', 'day', 'hand', 'night', 'thing', 'name', 'son', 'war',
    'air', 'boy', 'animal', 'star', 'tower', 'horn', 'sailor', 'foundation',
    'echo', 'phenomenon', 'vine', 'myth', 'atom', 'nymph', 'comet']
for lemma in lemmas:
    predicates = {
        'animal':'cow',
        'thing':'bolt',
        'phenomenon': 'eruption',
    }
    predicate = predicates[lemma] if lemma in predicates else lemma
    for tuplekey in declension_traversal.tuplekeys(category_to_grammemes):
        dictkey = declension_traversal.dictkey(tuplekey)
        if dictkey in use_case_to_grammatical_case:
            case = use_case_to_grammatical_case[dictkey]['case']
            adposition = use_case_to_grammatical_case[dictkey]['adposition']
            default_key = {
                'script':      'latin',
                'person':      '3',
                'clusivity':   'exclusive',
                'clitic':      'tonic',
                'partitivity': 'nonpartitive',
                'formality':   'familiar',
                'gender':      'masculine',
                'tense':  'present', 
                'voice':  'active',
                'aspect': 'aorist', 
                'mood':   'indicative',
            }
            subject_key = {**default_key, 'case':'nominative', 'noun-form':'personal', 'number':'singular'}
            common_subject_key = {**default_key, 'case':'nominative', 'noun-form':'common', 'number':'singular'}
            direct_object_key = {**default_key, 'case':'accusative', 'noun-form':'common', 'number':'singular'}
            case_key = {**default_key, **dictkey, 'case':case, 'noun-form':'common'}
            match = matching.match(predicate, dictkey['motion'], dictkey['cast'])
            if match:
                nouns = {}
                if match['subject-argument']:
                    nouns['subject'] = NounPhrase(subject_key, [match['subject-argument']])
                if match['direct-object'] or match['direct-object-adjective']:
                    nouns['direct-object'] = NounPhrase(direct_object_key, [
                        Adjective(match['direct-object-adjective']), 
                        *match['direct-object'].split(' ')])
                nouns['subject' if case == 'nominative' else 'modifiers'] = NounPhrase(case_key, [
                    Adposition(native=match['adposition'], foreign=adposition), 
                    Article(match['declined-noun-article']), 
                    Cloze(1, lemma)])
                if case == 'genitive':
                    tree = [
                        NounPhrase(common_subject_key, [
                            Article('the'), 
                            match['subject-argument']]),
                        NounPhrase(case_key, [
                            Adposition(native=match['adposition'], foreign=''), 
                            Article(match['declined-noun-article']), 
                            Cloze(1, lemma)]),
                    ]
                else:
                    tree = Clause(case_key if case == 'nominative' else subject_key, match['verb'], nouns)
                emoji_key = {**case_key, 'noun':lemma, 'case':case, 'number':dictkey['number'], 'script': 'emoji', 'noun-form':'common'}
                if emoji_key in latin.declension_lookups[emoji_key]:
                    emoji_noun = latin.declension_lookups['common'][emoji_key]
                    emoji_template = match['emoji']
                    emoji_template = emoji_template.replace('\\declined', emoji_noun)
                    emoji_template = emoji.emojiInflectionShorthand.decode(emoji_template, Person(case_key['number'][0], case_key['gender'][0],1), [])
                    print(tuplekey, case)
                    print(' '.join([
                            cardFormatting.emoji_focus(emoji_template), 
                            cardFormatting.english_word(english.format(tree)), 
                            cardFormatting.foreign_focus(latin.format(latin.inflect(default_key, tree))),
                        ]))

'''
write('flashcards/verb-conjugation/old-english.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index(
                finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/conjugations.tsv'), 5, 1)),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'subjunctive': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'imperative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine'],
                'voice':     ['active', 'passive'],
                'mood':      ['indicative','subjunctive','imperative',],
                'verb':     ['be [temporarily]', 'be [inherently]', 
                              'do', 'go', 'want', 
                              'steal', 'share', 'tame', 'move', 'love', 
                              'have', 'live', 'say', 'think',],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [2,3,1,4,5]],
    ))

write('flashcards/verb-conjugation/proto-indo-european.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/finite-conjugations.tsv'), 2, 4),
                *infinitive_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/nonfinite-conjugations.tsv'), 2, 2),
            ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'optative':    '{subject} {modifiers} {indirect-object} {direct-object} {verb}',
                'imperative':  '{subject} {modifiers} {indirect-object} {direct-object} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','dual','plural'],
                'tense':     ['present','past'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine'],
                'voice':     ['active', 'middle'],
                'mood':      ['indicative','imperative','subjunctive','optative'],
                'verb':     ['be','become','carry','leave','work','do','ask',
                              'stretch','know','sit','protect','be red','set down',
                              'want to see','renew','arrive','say','point out'],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [3,2,1,4,5]],
    ))

write('flashcards/verb-conjugation/russian.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/russian/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/russian/finite-conjugations.tsv'), 3, 4),
                *infinitive_annotation.annotate(
                    tsv_parsing.rows('data/inflection/russian/nonfinite-conjugations.tsv'), 2, 3),
            ]),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'imperative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine', 'feminine'],
                'tense':     ['present','future','past'],
                'voice':      'active',
                'aspect':     'aorist',
                'mood':      ['indicative','imperative'],
                'verb':     ['be', 'see', 'give', 'eat', 'live', 'call', 'go', 
                              'write', 'read', 'return', 'draw', 'spit', 'dance', 
                              'be able', 'bake', 'carry', 'lead', 'sweep', 'row', 
                              'steal', 'convey', 'climb', 'wash', 'beat', 'wind', 
                              'pour', 'drink', 'sew', 'live', 'swim', 'pass for', 
                              'speak', 'love', 'catch', 'sink', 'feed', 'ask', 
                              'convey', 'pay', 'go', 'forgive'],
            },
        ),
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['tense', 'person', 'number', 'gender']),
                content = {
                    ('present', '1', 'singular', 'neuter'    ),
                    ('present', '2', 'singular', 'neuter'    ),
                    ('present', '3', 'singular', 'masculine' ),
                    ('present', '1', 'plural',   'neuter'    ),
                    ('present', '2', 'plural',   'neuter'    ),
                    ('present', '3', 'plural',   'masculine' ),
                    ('future',  '1', 'singular', 'neuter'    ),
                    ('future',  '2', 'singular', 'neuter'    ),
                    ('future',  '3', 'singular', 'masculine' ),
                    ('future',  '1', 'plural',   'neuter'    ),
                    ('future',  '2', 'plural',   'neuter'    ),
                    ('future',  '3', 'plural',   'masculine' ),
                    ('past',    '3', 'singular', 'masculine' ),
                    ('past',    '3', 'singular', 'feminine'  ),
                    ('past',    '3', 'singular', 'neuter'    ),
                    ('past',    '3', 'plural',   'masculine' ),
                    ('past',    '3', 'plural',   'feminine'  ),
                    ('past',    '3', 'plural',   'neuter'    ),
                })
            ],
        persons = [Person('s','n',color) for color in [1,2,3,4,5]],
    ))

write('flashcards/verb-conjugation/spanish.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/spanish/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/spanish/finite-conjugations.tsv'), 3, 4),
                *infinitive_annotation.annotate(
                    tsv_parsing.rows('data/inflection/spanish/nonfinite-conjugations.tsv'), 3, 2)
            ]), 
            mood_templates = {
                'indicative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'conditional': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'subjunctive': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'imperative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
                'prohibitive': '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality': ['familiar','tuteo','voseo','formal'],
                'gender':    ['neuter', 'masculine'],
                'voice':      'active',
                'mood':      ['indicative','conditional','subjunctive','imperative','prohibitive'],
                'verb':     ['be [inherently]', 'be [temporarily]', 
                              'have', 'have [in possession]', 
                              'go', 'love', 'fear', 'part', 'know', 'drive'],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['formality', 'person', 'number', 'gender']),
                content = {
                    ('familiar', '1', 'singular', 'neuter'),
                    ('tuteo',    '2', 'singular', 'neuter'),
                    ('familiar', '3', 'singular', 'masculine'),
                    ('familiar', '1', 'plural',   'masculine'),
                    ('familiar', '2', 'plural',   'masculine'),
                    ('familiar', '3', 'plural',   'masculine'),
                    ('voseo',    '2', 'singular', 'neuter'),
                    ('formal',   '2', 'singular', 'masculine'),
                    ('formal',   '2', 'plural',   'masculine'),
                })
            ],
        persons = [Person('s','n',color) for color in [3,2,4,1,5]],
    ))

write('flashcards/verb-conjugation/swedish.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/swedish/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index(
                finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/swedish/conjugations.tsv'), 4, 3)),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'subjunctive': '{subject} {verb} {direct-object} {indirect-object} {modifiers}',
                'imperative':  '{subject} {verb} {direct-object} {indirect-object} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'noun-form':  'personal',
                'number':    ['singular','plural'],
                'animacy':    'human',
                'clitic':     'tonic',
                'clusivity':  'exclusive',
                'formality':  'familiar',
                'gender':    ['neuter', 'masculine'],
                'mood':      ['indicative','subjunctive','imperative'],
                'aspect':     'aorist',
                'verb':     ['be','go','call','close','read','sew','strike'],
            },
        ),
        english_map=replace([('♂','')]), 
        filter_lookups = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'neuter'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'neuter'),
                    ('3', 'plural',   'masculine'),
                }),
            DictLookup(
                'imperative filter', 
                DictTupleIndexing(['mood', 'person']),
                content = {
                    ('indicative',  '1'),
                    ('indicative',  '2'),
                    ('indicative',  '3'),
                    ('subjunctive', '1'),
                    ('subjunctive', '2'),
                    ('subjunctive', '3'),
                    ('imperative',  '2'),
                }),
        ],
        persons = [Person('s','n',color) for color in [2,1,3,4,5]],
    ))
'''

# print(pronoun_annotation.annotate(tsv_parsing.rows('data/inflection/english/old/pronoun-declensions.tsv'), 1, 5))

# print(emoji.inflect(grammemes, translation.conjugation_lookups['emoji']))
# print(emoji.inflect({**grammemes, 'mood':'imperative', 'aspect':'imperfect', 'person':'2', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.inflect({**grammemes, 'mood':'imperative', 'tense':'past', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.inflect({**grammemes, 'mood':'dynamic', 'tense':'future', 'number':'plural'}, translation.conjugation_lookups['emoji']))

# translation.inflect({**grammemes, 'noun-form':'personal'}, translation.conjugation_lookups['argument'])

# for k,v in list(english_conjugation['finite'].items({'verb':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_predicate_templates.items({'verb':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(lookups['finite'].items({'verb':'release',**category_to_grammemes}))[:100]: print(k,v)

# lookups = conjugation_population.index([
#     *finite_annotation.annotate(
#         tsv_parsing.rows('data/inflection/sanskrit/classical/conjugations.tsv'), 2, 4),
# ])

# grammemes = {
#     'verb': 'release', 
#     'person': '3', 
#     'number': 'singular', 
#     'clusivity': 'exclusive', 
#     'formality': 'familiar', 
#     'voice': 'active', 
#     'tense': 'present', 
#     'aspect': 'aorist',
#     'mood': 'indicative', 
#     'gender': 'masculine', 
#     'language-type':'english',
# }
