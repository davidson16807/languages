import re
import copy
import collections
import itertools
from transforms import *
from shorthands import *
from parsing import *
from annotation import *
from indexing import *
from lookup import *
from population import *

category_to_grammemes = {

    # needed to lookup the argument that is used to demonstrate a verb
    'language':   ['english', 'translated'], 

    # needed for infinitives
    'completion': ['full', 'bare'],

    # needed for finite forms
    'person':     ['1','2','3'],
    'number':     ['singular', 'dual', 'plural'],
    'clusivity':  ['inclusive', 'exclusive'],
    'mood':       ['indicative', 'subjunctive', 'conditional', 
                   'optative', 'benedictive', 'jussive', 'potential', 
                   'imperative', 'prohibitive', 'desiderative', 
                   'dubitative', 'hypothetical', 'presumptive', 'permissive', 
                   'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
                   'precative', 'volitive', 'involutive', 'inferential', 
                   'necessitative', 'interrogative', 'injunctive', 
                   'suggestive', 'comissive', 'deliberative', 
                   'propositive', 'dynamic', 
                  ],

    # needed for correlatives in general
    'proform':    ['personal', 'reflexive',
                   'demonstrative', 'interrogative', 'indefinite', 'elective', 'universal', 'negative', 
                   'relative', 'numeral'],
    'pronoun':    ['human','nonhuman','selection'],
    'clitic':     ['tonic', 'enclitic'],
    'proadverb':  ['location','source','goal','time','manner','reason','quality','amount'],
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

lemma_hashing = DictKeyIndexing('lemma')

verbial_declension_hashing = DictTupleIndexing([
        'lemma',           
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
                    'lemma',           
                    'person',           
                    'number',           
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
                    'lemma',           
                    'completion', # needed for Old English
                    'voice',      # needed for Latin, Swedish
                    'tense',      # needed for German, Latin
                    'aspect',     # needed for Greek
                ])),
        # verbs used as adjectives, indicating that an action is done upon a noun at some point in time
        'participle': DictLookup(
            'participle',
            DictTupleIndexing([
                    'lemma',           
                    'number',  # needed for German
                    'gender',     # needed for Latin, German, Russian
                    'case',       # needed for Latin, German
                    'voice',      # needed for Russian
                    'tense',      # needed for Greek, Russian, Spanish, Swedish, French
                    'aspect',     # needed for Greek, Latin, German, Russian
                ])),
        # verbs used as adjectives, indicating the purpose of something
        'gerundive': DictLookup('gerundive', verbial_declension_hashing),
        # verbs used as nouns
        'gerund': DictLookup('gerund', verbial_declension_hashing),
        # verbs used as nouns, indicating the objective of something
        'supine': DictLookup('supine', verbial_declension_hashing),
        # verbs used as adverbs
        'adverbial': DictLookup('adverbial', lemma_hashing),
        # a pattern in conjugation that the verb is meant to demonstrate
        'group': DictLookup('group', lemma_hashing),
        # text that follows a verb in a sentence that demonstrates the verb
        'argument': DictLookup(
            'argument',
            DictTupleIndexing([
                    'lemma',           
                    'language',           
                    'voice',      # needed for Greek
                    'gender',     # needed for Greek
                    'number',  # needed for Russian
                ])),
        # an emoji depiction of a sentence that demonstrates the verb
        'emoji': DictLookup(
            'emoji',
            DictTupleIndexing([
                    'lemma',           
                    'voice',      # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
                ])),
    })

basic_pronoun_declension_hashing = DictTupleIndexing([
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'case',       # needed for Latin
    ])

declension_template_lookups = DictLookup(
    'declension',
    DictKeyIndexing('proform'), 
    {
        'personal': DictLookup(
            'personal',
            DictTupleIndexing([
                    'person',           
                    'number',           
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
                    'case',       
                ])),
        'interrogative': DictLookup('interrogative', basic_pronoun_declension_hashing),
        'indefinite': DictLookup('indefinite', basic_pronoun_declension_hashing),
        'universal': DictLookup('universal', basic_pronoun_declension_hashing),
        'negative': DictLookup('negative', basic_pronoun_declension_hashing),
        'relative': DictLookup('relative', basic_pronoun_declension_hashing),
        'numeral': DictLookup('numeral', basic_pronoun_declension_hashing),
        'reflexive': DictLookup('reflexive', basic_pronoun_declension_hashing),
    })

class English:
    def __init__(self, 
            pronoun_declension_lookups, 
            conjugation_lookups, 
            predicate_templates, 
            mood_templates):
        self.pronoun_declension_lookups = pronoun_declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.predicate_templates = predicate_templates
        self.mood_templates = mood_templates
    def conjugate(self, grammemes, argument_lookup):
        dependant_clause = {
            **grammemes,
            'language': 'english',
        }
        independant_clause = {
            **grammemes,
            'language': 'english',
            'aspect': 'aorist',
            'tense':     
                'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                'present' if dependant_clause['tense'] in {'future'} else
                dependant_clause['tense']
        }
        lemmas = ['be', 'have', 
                  'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
                  dependant_clause['lemma']]
        if dependant_clause not in argument_lookup:
            # print('ignored english argument:', dependant_clause)
            return None
        argument = argument_lookup[dependant_clause]
        mood_replacements = [
            ('{subject}',              self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'nominative'}]),
            ('{subject|oblique}',      self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'oblique'}]),
            ('{predicate}',            self.predicate_templates[{**dependant_clause,'lookup':'finite'}]),
            ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'lookup':'infinitive'}]),
        ]
        sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
        for replaced, replacement in mood_replacements:
            sentence = sentence.replace(replaced, replacement)
        sentence = sentence.replace('{verb', '{'+dependant_clause['lemma'])
        sentence = sentence.replace('{argument}', argument)
        table = self.conjugation_lookups['finite']
        for lemma in lemmas:
            replacements = [
                ('{'+lemma+'|independant}',         table[{**independant_clause, 'lemma':lemma, }]),
                ('{'+lemma+'|independant|speaker}', table[{**independant_clause, 'lemma':lemma, 'person':'1', 'number':'singular'}]),
                ('{'+lemma+'|present}',             table[{**dependant_clause,   'lemma':lemma, 'tense':  'present',  'aspect':'aorist'}]),
                ('{'+lemma+'|past}',                table[{**dependant_clause,   'lemma':lemma, 'tense':  'past',     'aspect':'aorist'}]),
                ('{'+lemma+'|perfect}',             table[{**dependant_clause,   'lemma':lemma, 'aspect': 'perfect'    }]),
                ('{'+lemma+'|imperfect}',           table[{**dependant_clause,   'lemma':lemma, 'aspect': 'imperfect'  }]),
                ('{'+lemma+'|infinitive}',          lemma),
            ]
            for replaced, replacement in replacements:
                sentence = sentence.replace(replaced, replacement)
        if dependant_clause['voice'] == 'middle':
            sentence = f'[middle voice:] {sentence}'
        return sentence

class Person:
    def __init__(self, number, gender, color):
        self.number = number
        self.gender = gender
        self.color  = color 

class Emoji:
    def __init__(self, emojiShorthand, 
            htmlTenseTransform, htmlAspectTransform, mood_templates):
        self.emojiShorthand = emojiShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.mood_templates = mood_templates
    def conjugate(self, grammemes, argument_lookup, persons):
        if grammemes not in argument_lookup:
            # print('ignored emoji:', grammemes)
            return None
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
                    getattr(self.htmlAspectTransform, grammemes['aspect'].replace('-','_'))(
                        argument_lookup[grammemes]))
        encoded_recounting = self.mood_templates[{**grammemes,'column':'template'}]
        subject = Person(
            grammemes['number'][0]+('i' if grammemes['clusivity']=='inclusive' else ''), 
            grammemes['gender'][0], 
            persons[int(grammemes['person'])-1].color)
        persons = [
            subject if str(i+1)==grammemes['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiShorthand.decode(recounting, subject, persons)
        return recounting

class Translation:
    def __init__(self, 
            pronoun_declension_lookups, 
            conjugation_lookups, 
            mood_templates,
            category_to_grammemes,
            subject_map=lambda x:x):
        self.pronoun_declension_lookups = pronoun_declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.mood_templates = mood_templates
        self.category_to_grammemes = category_to_grammemes
        self.subject_map = subject_map
    def conjugate(self, grammemes, argument_lookup):
        grammemes = {**grammemes, 'language':'translated', 'case':'nominative'}
        if grammemes not in self.pronoun_declension_lookups['personal']:
            # print('ignored pronoun:', grammemes)
            return None
        if grammemes not in self.conjugation_lookups['finite']:
            # print('ignored finite:', grammemes)
            return None
        if grammemes not in argument_lookup:
            # print('ignored argument:', grammemes)
            return None
        else:
            sentence = self.mood_templates[grammemes['mood']]
            # TODO: read this as an attribute
            cases = self.category_to_grammemes['case']
            sentence = sentence.replace('{verb}',     self.conjugation_lookups['finite'][grammemes])
            sentence = sentence.replace('{argument}', argument_lookup[grammemes])
            for case in cases:
                subject_case = {**grammemes, 'case':case}
                if subject_case in self.pronoun_declension_lookups['personal']:
                    sentence = sentence.replace('{subject|'+case+'}', 
                        self.subject_map(self.pronoun_declension_lookups['personal'][subject_case]))
            return sentence

tsv_parsing = SeparatedValuesFileParsing()
conjugation_annotation  = TableAnnotation(
    grammeme_to_category, {}, {0:'lemma'}, 
    {**category_to_grammemes, 'lookup':'finite'})
pronoun_annotation  = TableAnnotation(
    grammeme_to_category, {}, {}, 
    {**category_to_grammemes, 'proform':'personal'})
predicate_annotation = TableAnnotation(
    grammeme_to_category, {0:'column'}, {}, 
    {**category_to_grammemes, 'lookup':'finite'})
mood_annotation        = TableAnnotation(
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

def valuemap(f):
    def _valuemap(items):
        for key, value in items:
            yield key, f(value)
    return _valuemap

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
    def generate(self, translation, filter_lookups, persons, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = {
                **self.finite_traversal.dictkey(tuplekey), 
                'proform': 'personal'
            }
            if all([dictkey in filter_lookup for filter_lookup in filter_lookups]):
                translated_text = translation.conjugate(dictkey, translation.conjugation_lookups['argument'])
                english_text    = self.english.conjugate(dictkey, translation.conjugation_lookups['argument'])
                emoji_text      = self.emoji.conjugate(dictkey, translation.conjugation_lookups['emoji'], persons)
                if translated_text and english_text:
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)), 
                            self.cardFormatting.foreign_focus(translated_text),
                        ])

infinitive_traversal = DictTupleIndexing(
    ['tense', 'aspect', 'mood', 'voice'])

bracket_shorthand = BracketedShorthand(Enclosures())

emoji_shorthand = EmojiShorthand(
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
    emoji_shorthand,
    HtmlTenseTransform(), HtmlAspectTransform(), 
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
        'formality','clusivity','person','number','gender','tense', 'aspect', 'mood', 'voice', 'lemma']))

def write(filename, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(f'{row}\n')

write('flashcards/verb-conjugation/ancient-greek.html', 
    card_generation.generate(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/ancient-greek/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index([
                    *conjugation_annotation.annotate(
                        tsv_parsing.rows('data/inflection/ancient-greek/finite-conjugations.tsv'), 3, 4),
                    *conjugation_annotation.annotate(
                        tsv_parsing.rows('data/inflection/ancient-greek/nonfinite-conjugations.tsv'), 6, 2)
                ]),
            mood_templates = {
                    'indicative':  '{subject|nominative} {{c1::{verb}}} {argument}',
                    'subjunctive': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'optative':    '{subject|nominative} {{c1::{verb}}} {argument}',
                    'imperative':  '{subject|nominative}, {{c1::{verb}}} {argument}!',
                },
            category_to_grammemes = {
                    **category_to_grammemes,
                    'proform':    'personal',
                    'number':    ['singular','plural'],
                    'clusivity':  'exclusive',
                    'formality':  'familiar',
                    'gender':    ['neuter', 'masculine'],
                    'mood':      ['indicative','subjunctive','optative','imperative'],
                    'lemma':     ['be','go','release'],
                },
            subject_map = first_of_options,
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

write('flashcards/verb-conjugation/swedish.html', 
    card_generation.generate(
        Translation(
            declension_population.index(
                pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/swedish/pronoun-declensions.tsv'), 1, 4)),
            conjugation_population.index(
                conjugation_annotation.annotate(
                    tsv_parsing.rows('data/inflection/swedish/conjugations.tsv'), 4, 3)),
            mood_templates = {
                    'indicative':  '{subject|nominative} {{c1::{verb}}} {argument}',
                    'subjunctive': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'imperative':  '{subject|nominative}, {{c1::{verb}}} {argument}!',
                },
            category_to_grammemes = {
                    **category_to_grammemes,
                    'proform':    'personal',
                    'number':    ['singular','plural'],
                    'clusivity':  'exclusive',
                    'formality':  'familiar',
                    'gender':    ['neuter', 'masculine'],
                    'mood':      ['indicative','subjunctive','imperative'],
                    'aspect':     'aorist',
                    'lemma':     ['be','go','call','close','read','sew','strike'],
                },
            subject_map = first_of_options,
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
        persons = [Person('s','n',color) for color in [2,3,1,4,5]],
    ))

write('flashcards/verb-conjugation/spanish.html', 
    card_generation.generate(
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
                    'indicative':  '{subject|nominative} {{c1::{verb}}} {argument}',
                    'conditional': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'subjunctive': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'imperative':  '{subject|nominative}, {{c1::{verb}}} {argument}!',
                    'prohibitive': '{subject|nominative}, {{c1::{verb}}} {argument}!',
                },
            category_to_grammemes = {
                    **category_to_grammemes,
                    'proform':    'personal',
                    'number':    ['singular','plural'],
                    'clusivity':  'exclusive',
                    'formality': ['familiar','tuteo','voseo','formal'],
                    'gender':    ['neuter', 'masculine'],
                    'voice':      'active',
                    'mood':      ['indicative','conditional','subjunctive','imperative','prohibitive'],
                    'lemma':     ['be [inherently]', 'be [temporarily]', 
                                  'have', 'have [in posession]', 
                                  'go', 'love', 'fear', 'part', 'know', 'drive'],
                },
            subject_map = first_of_options,
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

write('flashcards/verb-conjugation/french.html', 
    card_generation.generate(
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
                    'indicative':  '{subject|nominative} {{c1::{verb}}} {argument}',
                    'subjunctive': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'conditional': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'imperative':  '{subject|nominative}, {{c1::{verb}}} {argument}!',
                },
            category_to_grammemes = {
                    **category_to_grammemes,
                    'proform':    'personal',
                    'number':    ['singular','plural'],
                    'clusivity':  'exclusive',
                    'formality':  'familiar',
                    'gender':    ['neuter', 'masculine'],
                    'voice':      'active',
                    'mood':      ['indicative','conditional','subjunctive','imperative',],
                    'lemma':     ['have','be','go','speak','choose','lose','receive'],
                },
            subject_map = first_of_options,
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
    card_generation.generate(
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
                    'indicative':  '{subject|nominative} {{c1::{verb}}} {argument}',
                    'conditional': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'inferential': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'subjunctive': '{subject|nominative} {{c1::{verb}}} {argument}',
                    'imperative':  '{subject|nominative}, {{c1::{verb}}} {argument}!',
                },
            category_to_grammemes = {
                    **category_to_grammemes,
                    'proform':    'personal',
                    'number':    ['singular','plural'],
                    'clusivity':  'exclusive',
                    'formality': ['familiar','polite','formal','elevated'],
                    'gender':    ['neuter', 'masculine'],
                    'voice':      'active',
                    'mood':      ['indicative','conditional','inferential',
                                  'subjunctive','imperative',],
                    'lemma':     ['be', 'do', 'go', 'become', 'may', 
                                  'have', 'love', 'act', 'work', 'drive'], 
                },
            subject_map = first_of_options,
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

# print(emoji.conjugate(grammemes, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'imperative', 'aspect':'imperfect', 'person':'2', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'imperative', 'tense':'past', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'dynamic', 'tense':'future', 'number':'plural'}, translation.conjugation_lookups['emoji']))

# translation.conjugate({**grammemes, 'proform':'personal'}, translation.conjugation_lookups['argument'])


# for k,v in list(english_conjugation['finite'].items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_predicate_templates.items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(lookups['finite'].items({'lemma':'release',**category_to_grammemes}))[:100]: print(k,v)




# lookups = conjugation_population.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/latin/finite-conjugations.tsv'), 3, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/latin/nonfinite-conjugations.tsv'), 6, 2),
# ])

# lookups = conjugation_population.index(
#     conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/old-english/conjugations.tsv'), 5, 1))

# lookups = conjugation_population.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/proto-indo-european/finite-conjugations.tsv'), 2, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/proto-indo-european/nonfinite-conjugations.tsv'), 2, 2),
# ])

# lookups = conjugation_population.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/russian/finite-conjugations.tsv'), 2, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/russian/nonfinite-conjugations.tsv'), 2, 2),
# ])

# lookups = conjugation_population.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('data/inflection/sanskrit/conjugations.tsv'), 2, 4),
# ])







# grammemes = {
#     'lemma': 'release', 
#     'person': '3', 
#     'number': 'singular', 
#     'clusivity': 'exclusive', 
#     'formality': 'familiar', 
#     'voice': 'active', 
#     'tense': 'present', 
#     'aspect': 'aorist',
#     'mood': 'indicative', 
#     'gender': 'masculine', 
#     'language':'english',
# }
