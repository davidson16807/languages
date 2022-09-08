import re
import copy
import collections
import itertools

import inflector

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

    # needed for correlatives in general
    'proform':    ['common', 'personal', 'reflexive', 'emphatic-reflexive',
                   'demonstrative', 'interrogative', 'indefinite', 'elective', 'universal', 'negative', 
                   'relative', 'numeral'],
    # animacy ordered as follows:
    # 1st column: represents any of the grammemes that precede the entry in the middle column of that row
    # 2nd column: represents its own unique grammeme that excludes all preceding rows and following entries
    # 3rd column: represents any of the grammemes that follow the entry in the middle column of that row
    # As an example, all "animate" things are "living" but not all "dynamic" things are "living",
    # all "static" things are "nonliving" but not all static things are "abstract",
    # and a "plant" is "living", "dynamic", "nonagent", and "inanimate", among others.
    'animacy':    [             'human',               'nonhuman',    # member of the species homo sapiens
                   'sapient',   'humanoid',            'nonsapient',  # having the ability to think and speak
                   'animate',   'creature',            'inanimate',   # able to move around on its own
                   'living',    'plant',               'nonliving',   # able to grow and reproduce
                   'concrete',  'perceptible',         'abstract',    # able to take physical form
                   'thing'],
    'abstraction':['institution','location','origin',
                   'destination','time','manner','reason','quality','amount'],
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
    'case':       ['nominative', 'oblique', 'accusative', 'dative', 'ablative', 
                   'genitive', 'locative', 'instrumental','disjunctive', 'undeclined'],
    'motion': ['departed', 'associated', 'acquired', 'leveraged'],
    'attribute': [
        'location', 'extent', 'vicinity', 'interior', 'surface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 'owner', 
        'time', 'state of being', 'topic', 'company', 'resemblance'],
    

    # needed for infinitive forms, finite forms, participles, arguments, and graphic depictions
    'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
    'tense':      ['present', 'past', 'future',], 
    'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 
}

category_to_grammemes_with_lookups = {
    **category_to_grammemes,
    # needed to tip off which key/lookup should be used to stored cell contents
    'lookup':     ['finite', 'infinitive', 
                   'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
                   'argument', 'group', 'emoji'],
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes_with_lookups.items() 
    for instance in instances
}

lemma_hashing = DictKeyIndexing('verb')

verbial_declension_hashing = DictTupleIndexing([
        'verb',           
        'voice',      # needed for Swedish
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'case',       # needed for Latin
    ])

conjugation_template_lookups = DictLookup(
    'conjugation',
    DictKeyIndexing('lookup'), 
    {
        # verbs that indicate a subject
        'finite': DictLookup(
            'finite',
            DictTupleIndexing([
                    'verb',           
                    'person',           
                    'number',           
                    'gender',      # needed for Russian
                    'formality',   # needed for Spanish ('voseo')
                    'mood',        
                    'voice',           
                    'tense',           
                    'aspect',      
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
                ])),
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
                ])),
        # verbs used as adverbs
        'adverbial': DictLookup(
            'participle',
            DictTupleIndexing([
                    'verb',           
                    'tense',      # needed for Russian
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
                ])),
        # an emoji depiction of a sentence that demonstrates the verb
        'emoji': DictLookup(
            'emoji',
            DictTupleIndexing([
                    'verb',           
                    'voice',      # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
                ])),
    })

basic_pronoun_declension_hashing = DictTupleIndexing([
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'animacy',    # needed for Old English, Russian
        'partitivity',# needed for Old English, Quenya, Finnish
        'case',       # needed for Latin
    ])

declension_template_lookups = DictLookup(
    'declension',
    DictKeyIndexing('proform'), 
    {
        'common': DictLookup(
            'common',
            DictTupleIndexing([
                    'noun',
                    'number',           
                    'gender',           
                    'partitivity', # needed for Quenya, Finnish
                    'case',           
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
    def stock_argument(self, grammemes, argument_lookup):
        grammemes = {**grammemes, 'language-type':'translated'}
        if grammemes not in argument_lookup:
            return ''
        else:
            return argument_lookup[grammemes]
    def decline(self, grammemes):
        grammemes = {**grammemes, 'language-type':'translated'}
        return (
            self.declension_lookups[grammemes][grammemes] if grammemes['proform'] != 'common'
            else inflector.pluralize(grammemes['noun']) if grammemes['number'] != 'singular'
            else grammemes['noun'])
    def structure(self, grammemes, noun_phrases):
        dependant_clause = {
            **grammemes,
            'language-type': 'english',
        }
        independant_clause = {
            **grammemes,
            'language-type': 'english',
            'aspect': 'aorist',
            'tense':     
                'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                'present' if dependant_clause['tense'] in {'future'} else
                dependant_clause['tense']
        }
        lemmas = ['be', 'have', 
                  'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
                  dependant_clause['verb']]
        mood_replacements = [
            ('{predicate}',            self.predicate_templates[{**dependant_clause,'lookup':'finite'}]),
            ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'lookup':'infinitive'}]),
        ]
        sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
        for replaced, replacement in mood_replacements:
            sentence = sentence.replace(replaced, replacement)
        for noun_phrase in ['invocation', 'subject|nominative', 'subject|oblique', 'direct', 'indirect']:
            sentence = sentence.replace('{'+noun_phrase+'}', 
                noun_phrases[noun_phrase] if noun_phrase in noun_phrases else '')
        sentence = sentence.replace('{modifiers}', 
            ' '.join(noun_phrases['modifiers'] if 'modifiers' in noun_phrases else []))
        sentence = sentence.replace('{verb', '{'+dependant_clause['verb'])
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

class Emoji:
    def __init__(self, emojiInflectionShorthand, 
            htmlTenseTransform, htmlAspectTransform, mood_templates):
        self.emojiInflectionShorthand = emojiInflectionShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.mood_templates = mood_templates
    def stock_argument(self, grammemes, argument_lookup):
        return argument_lookup[grammemes] if grammemes in argument_lookup else ''
    def structure(self, grammemes, argument, persons):
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
    def stock_argument(self, grammemes, argument_lookup):
        grammemes = {**grammemes, 'language-type':'translated'}
        if grammemes not in argument_lookup:
            return ''
        else:
            return argument_lookup[grammemes]
    def decline(self, grammemes):
        grammemes = {**grammemes, 'language-type':'translated'}
        if grammemes not in self.declension_lookups:
            return None
        if grammemes not in self.declension_lookups[grammemes]:
            return None
        return self.declension_lookups[grammemes][grammemes]
    def conjugate(self, grammemes):
        grammemes = {**grammemes, 'language-type':'translated'}
        if grammemes not in self.conjugation_lookups['finite']:
            return None
        return self.conjugation_lookups['finite'][grammemes]
    def structure(self, grammemes, verb, noun_phrases):
        if verb is None: return None
        sentence = self.mood_templates[grammemes['mood']]
        # TODO: read this as an attribute
        cases = self.category_to_grammemes['case']
        sentence = sentence.replace('{verb}', verb)
        sentence = sentence.replace('{modifiers}', 
            ' '.join(noun_phrases['modifiers'] if 'modifiers' in noun_phrases else []))
        for noun_phrase in ['invocation', 'subject', 'direct', 'indirect']:
            sentence = sentence.replace('{'+noun_phrase+'}', 
                noun_phrases[noun_phrase] if noun_phrase in noun_phrases and noun_phrases[noun_phrase] is not None else '')
        sentence = re.sub('\s+', ' ', sentence)
        return sentence

tsv_parsing = SeparatedValuesFileParsing()
conjugation_annotation  = CellAnnotation(
    grammeme_to_category, {}, {0:'verb'}, 
    {**category_to_grammemes, 'lookup':'finite'})
pronoun_annotation  = CellAnnotation(
    grammeme_to_category, {}, {}, 
    {**category_to_grammemes, 'proform':'personal', 'language-type':'translated'})
noun_annotation  = CellAnnotation(
    grammeme_to_category, {}, {0:'noun'}, 
    {**category_to_grammemes, 'proform':'common', 'person':'3', 'language-type':'translated'})
template_annotation = CellAnnotation(
    grammeme_to_category, {0:'language'}, {0:'noun'}, 
    {**category_to_grammemes, 'proform':'common', 'person':'3', 'language-type':'translated'})
predicate_annotation = CellAnnotation(
    grammeme_to_category, {0:'column'}, {}, 
    {**category_to_grammemes, 'lookup':'finite'})
mood_annotation        = CellAnnotation(
    {}, {0:'column'}, {0:'mood'}, {})

conjugation_population = NestedLookupPopulation(conjugation_template_lookups)
declension_population  = NestedLookupPopulation(declension_template_lookups)
predicate_population = FlatLookupPopulation(DictLookup('predicate', DictTupleIndexing(['lookup','voice','tense','aspect'])))
mood_population = FlatLookupPopulation(DictLookup('mood', DictTupleIndexing(['mood','column'])))

class CardFormatting:
    def __init__(self):
        pass
    def emoji_focus(self, content):
        fonts = '''sans-serif', 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji'''
        return f'''<div style='font-size:3em; padding: 0.5em; font-family: {fonts}'>{content}</div>'''
    def foreign_focus(self, content):
        return f'''<div style='font-size:3em'>{content}</div>'''
    def foreign_side_note(self, content):
        return f'''<div style='font-size:2em'>{content}</div>'''
    def english_word(self, content):
        return f'''<div>{content}</div>'''

def first_of_options(content):
    return content.split('/')[0]

def cloze(id):
    return lambda content: '{{'+f'''c{id}::{content}'''+'}}'

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
    def declensions(self, translation, filter_lookups, persons, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = self.finite_traversal.dictkey(tuplekey)
    def conjugation(self, translation, filter_lookups, persons, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = self.finite_traversal.dictkey(tuplekey)
            if all([dictkey in filter_lookup for filter_lookup in filter_lookups]):
                translated_text = translation.structure(
                    dictkey, 
                    cloze(1)(translation.conjugate(dictkey)),
                    {
                        'subject':    translation.decline({**dictkey, 'proform': 'personal', 'case':'nominative'}),
                        'invocation': translation.decline({**dictkey, 'proform': 'personal', 'case':'vocative'}),
                        'modifiers': [translation.stock_argument(dictkey, translation.conjugation_lookups['argument'])],
                    })
                english_text = self.english.structure(
                    dictkey, 
                    {
                        'subject|nominative': self.english.decline({**dictkey, 'proform': 'personal', 'case':'nominative'}),
                        'subject|oblique':    self.english.decline({**dictkey, 'proform': 'personal', 'case':'oblique'}),
                        'modifiers':         [self.english.stock_argument(dictkey, translation.conjugation_lookups['argument'])],
                    })
                emoji_argument      = self.emoji.stock_argument(dictkey, translation.conjugation_lookups['emoji'])
                emoji_text          = self.emoji.structure(dictkey, emoji_argument, persons)
                if translated_text and english_text:
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)), 
                            self.cardFormatting.foreign_focus(translated_text),
                        ])

infinitive_traversal = DictTupleIndexing(['tense', 'aspect', 'mood', 'voice'])

bracket_shorthand = BracketedShorthand(Enclosures())

emoji_shorthand = EmojiInflectionShorthand(
    EmojiSubjectShorthand(), 
    EmojiPersonShorthand(
        EmojiNumberShorthand(
            HtmlNumberTransform(HtmlPersonPositioning()), bracket_shorthand)),
    EmojiBubbleShorthand(HtmlBubble(), bracket_shorthand),
    TextTransformShorthand(HtmlTextTransform(), bracket_shorthand),
    EmojiGestureShorthand(HtmlGesturePositioning(), bracket_shorthand),
    EmojiModifierShorthand()
)

emoji = Emoji(
    emoji_shorthand, HtmlTenseTransform(), HtmlAspectTransform(), 
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/mood-templates.tsv'), 1, 1)),
    )

english = English(
    declension_population.index(
        pronoun_annotation.annotate(tsv_parsing.rows('data/inflection/english/pronoun-declensions.tsv'), 1, 5)),
    conjugation_population.index(
        conjugation_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/conjugations.tsv'), 4, 2)),
    predicate_population.index(
        predicate_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/predicate-templates.tsv'), 1, 4)),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/mood-templates.tsv'), 1, 1)),
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
                    tsv_parsing.rows('data/inflection/ancient-greek/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index([
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/ancient-greek/finite-conjugations.tsv'), 3, 4),
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/ancient-greek/nonfinite-conjugations.tsv'), 6, 2),
            ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect} {direct} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect} {direct} {verb}',
                'optative':    '{subject} {modifiers} {indirect} {direct} {verb}',
                'imperative':  '{invocation}, {modifiers} {indirect} {direct} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/french/finite-conjugations.tsv'), 4, 3),
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/french/nonfinite-conjugations.tsv'), 3, 1),
            ]),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct} {indirect} {modifiers}',
                'subjunctive': '{subject} {verb} {direct} {indirect} {modifiers}',
                'conditional': '{subject} {verb} {direct} {indirect} {modifiers}',
                'imperative':  '{subject}, {verb} {direct} {indirect} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                    *conjugation_annotation.annotate(
                        tsv_parsing.rows('data/inflection/german/finite-conjugations.tsv'), 4, 3),
                    *conjugation_annotation.annotate(
                        tsv_parsing.rows('data/inflection/german/nonfinite-conjugations.tsv'), 7, 1),
                ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect} {direct} {verb}',
                'conditional': '{subject} {modifiers} {indirect} {direct} {verb}',
                'inferential': '{subject} {modifiers} {indirect} {direct} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect} {direct} {verb}',
                'imperative':  '{subject}, {modifiers} {indirect} {direct} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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

latin = Translation(
    declension_population.index([
        *pronoun_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/pronoun-declensions.tsv'), 1, 4),
        *noun_annotation.annotate(
            tsv_parsing.rows('data/noun-declension/latin/declensions.tsv'), 1, 6),
        *filter(has_annotation('language','latin'),
            template_annotation.annotate(
                tsv_parsing.rows('data/noun-declension/declension-template-accusatives.tsv'), 2, 7)),
    ]),
    conjugation_population.index([
        *conjugation_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/finite-conjugations.tsv'), 3, 4),
        *conjugation_annotation.annotate(
            tsv_parsing.rows('data/inflection/latin/nonfinite-conjugations.tsv'), 6, 2),
    ]),
    mood_templates = {
        'indicative':  '{subject} {modifiers} {indirect} {direct} {verb}',
        'subjunctive': '{subject} {modifiers} {indirect} {direct} {verb}',
        'imperative':  '{invocation}, {modifiers} {indirect} {direct} {verb}!',
    },
    category_to_grammemes = {
        **category_to_grammemes,
        'proform':    'personal',
        'number':    ['singular','plural'],
        'animacy':    'human',
        'clitic':     'tonic',
        'clusivity':  'exclusive',
        'formality':  'familiar',
        'gender':    ['neuter', 'masculine'],
        'voice':     ['active', 'passive'],
        'mood':      ['indicative','subjunctive','imperative',],
        'verb':     ['be', 'be able', 'want', 'become', 'go', 
                      'carry', 'eat', 'love', 'advise', 'direct', 
                      'capture', 'hear'],
    },
)

write('flashcards/verb-conjugation/latin.html', 
    card_generation.conjugation(
        latin,
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
from predicates import Predicate, Bipredicate
from lookup import DefaultDictLookup, DictLookup
from indexing import DictTupleIndexing, DictKeyIndexing
from evaluation import KeyEvaluation
from population import ListLookupPopulation, FlatLookupPopulation

tsv_parsing = SeparatedValuesFileParsing()
rows = [
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal-anatomy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/deity.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/human.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/humanoid.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/mythical.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/plant-anatomy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/plant.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/sapient.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/animacy-hierarchy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/capability.tsv'),
]

level0_subset_relations = set()
level1_subset_relations = collections.defaultdict(
    set, {'be':{'can','has-trait','has-part'}})
level1_function_domains = collections.defaultdict(set)

for row in rows:
    f, x, g, y = row[:4]
    if all([f.strip(), x.strip(), g.strip(), y.strip()]):
        fxgy = (f,x),(g,y)
        level0_subset_relations.add(fxgy)

allthat = collections.defaultdict(Predicate)
for (f,x),(g,y) in level0_subset_relations:
    allthat[g,y](allthat[f,x])
    if g == f:
        for f2 in level1_subset_relations[f]:
            allthat[f2,y](allthat[f2,x])

header_columns = [
    'motion', 'attribute', 
    'subject-function', 'subject-argument', 
    'verb', 'direct-object', 'preposition', 
    'declined-noun-function', 'declined-noun-argument']
template_annotation = RowAnnotation(header_columns)
template_population = ListLookupPopulation(
    DefaultDictLookup('declension-template',
        DictTupleIndexing(['motion','attribute']), list))
templates = \
    template_population.index(
        template_annotation.annotate(
            tsv_parsing.rows(
                'data/noun-declension/declension-templates-minimal.tsv')))

class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, motion, attribute):
        def subject(template):
            return self.predicates[template['subject-function'], template['subject-argument']]
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        templates = sorted([template 
                            for template in (self.templates[motion, attribute] 
                                if (motion, attribute) in self.templates else [])
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: len(declined_noun(template)))
        return templates[0] if len(templates) > 0 else None

case_annotation = RowAnnotation(['motion','attribute','case'])
case_indexing = DictTupleIndexing(['motion','attribute'])
case_population = \
    FlatLookupPopulation(
        DictLookup('declension-use-case-to-grammatical-case', case_indexing),
        KeyEvaluation('case'))
use_case_to_grammatical_case = \
    case_population.index(
        case_annotation.annotate(
            tsv_parsing.rows('data/noun-declension/latin/declension-use-case-to-grammatical-case.tsv')))

matching = DeclensionTemplateMatching(templates, allthat)

for lemma in ['animal']:
    for tuplekey in case_indexing.tuplekeys(category_to_grammemes):
        dictkey = case_indexing.dictkey(tuplekey)
        case = use_case_to_grammatical_case[dictkey]
        match = matching.match(lemma, dictkey['motion'], dictkey['attribute'])
        if match:
            base_noun_key = {
                'proform':     'common',
                'person':      '3',
                'number':      'singular', 
                'partitivity': 'nonpartitive',
                'formality':   'familiar',
                'gender':      'masculine',
            }
            nominative_key = {**base_noun_key, 'case':'nominative'}
            accusative_key = {**base_noun_key, 'case':'accusative'}
            oblique_key = {**base_noun_key, 'case':'oblique'}
            modifier_key = {**base_noun_key, 'case':case}
            verb_key = {
                **base_noun_key,
                'verb':   match['verb'], 
                'tense':  'present', 
                'voice':  'active',
                'aspect': 'aorist', 
                'mood':   'indicative',
            }
            print(tuplekey, case)
            declension = latin.decline({**base_noun_key, 'noun':lemma, 'case':case})
            translated_text = latin.structure(
                verb_key, 
                latin.conjugate(verb_key),
                {
                    'subject':    ' '.join([
                        latin.decline({**nominative_key, 'noun':'the'}) or '',
                        latin.decline({**nominative_key, 'noun':match['subject-argument']})
                    ]),
                    'direct':     ' '.join([
                        latin.decline({**accusative_key, 'noun':'the'}) or '',
                        latin.decline({**accusative_key, 'noun':match['direct-object']}) or ''
                    ]),
                    'modifiers': [' '.join([
                        latin.decline({**modifier_key, 'noun':'the', 'case':case}) or '', 
                        cloze(1)(latin.decline({**modifier_key, 'noun':lemma, 'case':case}))
                    ])],
                })
            english_text = card_generation.english.structure(
                verb_key,
                {
                    'subject|nominative': ' '.join(['the', card_generation.english.decline({**nominative_key, 'noun':match['subject-argument']})]),
                    'subject|oblique':    ' '.join(['the', card_generation.english.decline({**oblique_key, 'noun':match['direct-object']})]),
                    'direct':             ' '.join(['the', match['direct-object']]),
                    'modifiers':         [' '.join([
                        match['preposition'],
                        'the',
                        card_generation.english.decline({**oblique_key, 'noun':lemma})
                    ])],
                })
            print(translated_text)
            print(english_text)
                

'''
write('flashcards/verb-conjugation/old-english.html', 
    card_generation.conjugation(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/old-english/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index(
                conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/old-english/conjugations.tsv'), 5, 1)),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct} {indirect} {modifiers}',
                'subjunctive': '{subject} {verb} {direct} {indirect} {modifiers}',
                'imperative':  '{subject}, {verb} {direct} {indirect} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                    tsv_parsing.rows('data/inflection/proto-indo-european/pronoun-declensions.tsv'), 1, 5)),
            conjugation_population.index([
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/finite-conjugations.tsv'), 2, 4),
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/nonfinite-conjugations.tsv'), 2, 2),
            ]),
            mood_templates = {
                'indicative':  '{subject} {modifiers} {indirect} {direct} {verb}',
                'subjunctive': '{subject} {modifiers} {indirect} {direct} {verb}',
                'optative':    '{subject} {modifiers} {indirect} {direct} {verb}',
                'imperative':  '{invocation}, {modifiers} {indirect} {direct} {verb}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/russian/finite-conjugations.tsv'), 3, 4),
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/russian/nonfinite-conjugations.tsv'), 2, 3),
            ]),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct} {indirect} {modifiers}',
                'imperative':  '{subject}, {verb} {direct} {indirect} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/spanish/finite-conjugations.tsv'), 3, 4),
                *conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/spanish/nonfinite-conjugations.tsv'), 3, 2)
            ]), 
            mood_templates = {
                'indicative':  '{subject} {verb} {direct} {indirect} {modifiers}',
                'conditional': '{subject} {verb} {direct} {indirect} {modifiers}',
                'subjunctive': '{subject} {verb} {direct} {indirect} {modifiers}',
                'imperative':  '{subject}, {verb} {direct} {indirect} {modifiers}!',
                'prohibitive': '{subject}, {verb} {direct} {indirect} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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
                conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/swedish/conjugations.tsv'), 4, 3)),
            mood_templates = {
                'indicative':  '{subject} {verb} {direct} {indirect} {modifiers}',
                'subjunctive': '{subject} {verb} {direct} {indirect} {modifiers}',
                'imperative':  '{subject}, {verb} {direct} {indirect} {modifiers}!',
            },
            category_to_grammemes = {
                **category_to_grammemes,
                'proform':    'personal',
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

# print(pronoun_annotation.annotate(tsv_parsing.rows('data/inflection/old-english/pronoun-declensions.tsv'), 1, 5))

# print(emoji.structure(grammemes, translation.conjugation_lookups['emoji']))
# print(emoji.structure({**grammemes, 'mood':'imperative', 'aspect':'imperfect', 'person':'2', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.structure({**grammemes, 'mood':'imperative', 'tense':'past', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.structure({**grammemes, 'mood':'dynamic', 'tense':'future', 'number':'plural'}, translation.conjugation_lookups['emoji']))

# translation.structure({**grammemes, 'proform':'personal'}, translation.conjugation_lookups['argument'])

# for k,v in list(english_conjugation['finite'].items({'verb':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_predicate_templates.items({'verb':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(lookups['finite'].items({'verb':'release',**category_to_grammemes}))[:100]: print(k,v)

# lookups = conjugation_population.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/sanskrit/conjugations.tsv'), 2, 4),
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
