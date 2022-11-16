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

from annotation import RowAnnotation
from predicates import Predicate
from lookup import DefaultDictLookup, DictLookup
from indexing import DictTupleIndexing, DictKeyIndexing
from evaluation import KeyEvaluation, MultiKeyEvaluation
from population import ListLookupPopulation, FlatLookupPopulation
from languages import English, Emoji, Translation
from syntax import (Cloze, NounPhrase, Adjective, Adposition, Article, StockModifier, Clause)

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
    'animacy':    [            'human',         'nonhuman',    # member of the species homo sapiens
                   'sapient',  'humanoid',      'nonsapient',  # having the ability to think and speak
                   'animate',  'creature',      'inanimate',   # able to move around on its own
                   'living',   'plant',         'nonliving',   # able to grow and reproduce
                   'concrete', 'manifestation', 'abstract',    # able to take physical form
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
    plurality.english,
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

def write(filename, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(f'{row}\n')

def has_annotation(key, value):
    def _has_annotation(annotated_cell):
        annotation, cell = annotated_cell
        return key in annotation and annotation[key] == value or value in annotation[key]
    return _has_annotation



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

declension_verb_annotation = CellAnnotation(
    grammeme_to_category, {0:'language'}, {0:'verb'}, 
    {'script':'latin', 'verb-form':'finite','gender':['masculine','feminine']})

class CardGeneration:
    def __init__(self, english, emoji, 
            cardFormatting, finite_traversal, declension_traversal, 
            nouns_to_predicates):
        self.english = english
        self.emoji = emoji
        self.cardFormatting = cardFormatting
        self.finite_traversal = finite_traversal
        self.declension_traversal = declension_traversal
        self.nouns_to_predicates = nouns_to_predicates
    def conjugation(self, translation, filter_lookups, default_grammemes={}, english_map=lambda x:x):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = {**default_grammemes, **self.finite_traversal.dictkey(tuplekey)}
            if all([dictkey in filter_lookup for filter_lookup in filter_lookups]):
                syntax_tree = Clause(dictkey, Cloze(1, dictkey['verb']),
                    {
                        'subject':    NounPhrase({'noun-form': 'personal', 'case':'nominative'}),
                        'modifiers':  StockModifier(translation.conjugation_lookups['argument']),
                    })
                translated_tree = translation.inflect(dictkey, syntax_tree)
                emoji_key  = {**dictkey, 'script':'emoji'}
                if translation.exists(translated_tree) and emoji_key in translation.conjugation_lookups['infinitive']:
                    english_text    = self.english.format(syntax_tree)
                    translated_text = translation.format(translated_tree)
                    emoji_argument  = translation.conjugation_lookups['infinitive'][emoji_key]
                    emoji_text      = self.emoji.conjugate(dictkey, emoji_argument, translation.persons)
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)), 
                            self.cardFormatting.foreign_focus(translated_text),
                        ])
    def declension(self, translation, default_grammemes={}):
        default_key = {
            'script':      'latin',
            'person':      '3',
            'clusivity':   'exclusive',
            'clitic':      'tonic',
            'partitivity': 'nonpartitive',
            'formality':   'familiar',
            'gender':      'masculine',
            'tense':       'present', 
            'voice':       'active',
            'aspect':      'aorist', 
            'mood':        'indicative',
            **default_grammemes,
        }
        for tuplekey in self.declension_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = self.declension_traversal.dictkey(tuplekey)
            if dictkey in use_case_to_grammatical_case:
                noun = dictkey['noun']
                predicate = self.nouns_to_predicates[noun] if noun in self.nouns_to_predicates else noun
                case = use_case_to_grammatical_case[dictkey]['case']
                adposition = use_case_to_grammatical_case[dictkey]['adposition']
                case_key = {**default_key, **dictkey, 'case':case, 'noun-form':'common'}
                emoji_key = {**default_key, **dictkey, 'noun':noun, 'case':case, 'noun-form':'common', 'script': 'emoji'}
                match = matching.match(predicate, dictkey['motion'], dictkey['cast'])
                if match and emoji_key in translation.declension_lookups['common']:
                    if case == 'genitive':
                        subject_key = {**default_key, 'case':'nominative', 'noun-form':'common', 'number':'singular'}
                        syntax_tree = [
                            NounPhrase(subject_key, [
                                Article('the'), 
                                match['subject-argument']]),
                            NounPhrase(case_key, [
                                Adposition(native=match['adposition'], foreign=''), 
                                Article(match['declined-noun-article']), 
                                Cloze(1, noun)]),
                        ]
                    else:
                        subject_key = {**default_key, 'case':'nominative', 'noun-form':'personal', 'number':'singular'}
                        direct_object_key = {**default_key, 'case':'accusative', 'noun-form':'common', 'number':'singular'}
                        syntax_tree = Clause(case_key if case == 'nominative' else subject_key, match['verb'], {
                            'subject': NounPhrase(subject_key, [match['subject-argument']]),
                            'direct-object': 
                                NounPhrase(direct_object_key, [
                                    Adjective(match['direct-object-adjective']), 
                                    *match['direct-object'].split(' ')]),
                            ('subject' if case == 'nominative' else 'modifiers'): 
                                NounPhrase(case_key, [
                                    Adposition(native=match['adposition'], foreign=adposition), 
                                    Article(match['declined-noun-article']), 
                                    Cloze(1, noun)]),
                        })
                    emoji_noun = translation.declension_lookups['common'][emoji_key]
                    emoji_template = match['emoji']
                    emoji_template = emoji_template.replace('\\declined', emoji_noun)
                    emoji_template = self.emoji.emojiInflectionShorthand.decode(emoji_template, 
                        Person(case_key['number'][0], case_key['gender'][0], translation.persons[4].color), translation.persons)
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_template), 
                            self.cardFormatting.english_word(self.english.format(syntax_tree)), 
                            self.cardFormatting.foreign_focus(
                                translation.format(
                                    translation.inflect(default_key, syntax_tree))),
                        ])

card_generation = CardGeneration(
    english, emoji, CardFormatting(),
    DictTupleIndexing([
        'number','formality','clusivity','person','clitic',
        'gender','tense', 'aspect', 'mood', 'voice', 'verb']),
    DictTupleIndexing([
        'motion','cast','number','noun']),
    {
        'animal':'cow',
        'thing':'bolt',
        'phenomenon': 'eruption',
    })

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
        'noun':      ['man', 'day', 'hand', 'night', 'thing', 'name', 'son', 'war',
                      'air', 'boy', 'animal', 'star', 'tower', 'horn', 'sailor', 'foundation',
                      'echo', 'phenomenon', 'vine', 'myth', 'atom', 'nymph', 'comet'],
    },
    persons = [Person('s','n',color) for color in [2,3,1,4,5]],
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
    ))

write('flashcards/noun-declension/latin.html', 
    card_generation.declension(
        latin, 
        default_grammemes={'script':'latin'},
    ))



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
