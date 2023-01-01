'''
"inflections.py" contains helpful datasets and 

See README.txt and GLOSSARY.txt for notes on terminology
'''

import collections

from tools.transforms import *
from tools.shorthands import *

from tools.parsing import SeparatedValuesFileParsing
from tools.annotation import RowAnnotation, CellAnnotation
from tools.predicates import Predicate
from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.evaluation import KeyEvaluation, MultiKeyEvaluation
from tools.population import NestedLookupPopulation, ListLookupPopulation, FlatLookupPopulation
from tools.nodemaps import (
    ListTools, ListGrammar,
    RuleValidation, RuleFormatting, RuleSyntax,
    EnglishListSubstitution,
)
from tools.languages import Emoji, Language
from tools.cards import DeclensionTemplateMatching, CardFormatting, CardGeneration

tagaxis_to_tags = {

    # needed to lookup the argument that is used to demonstrate a verb
    'language-type':   ['native', 'foreign'], 

    'plicity': ['implicit', 'explicit'],

    'script':[
        # scripts that were derived from the phoenecian alphabet:
        'latin','cyrillic','greek','hebrew','arabic','phoenician','ipa',
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

    # needed for infinitives in Old English and Swedish

    # needed for infinitives in Old English and Swedish
    'completion': ['full', 'bare'],

    # needed for Sinhalese
    'definiteness':   ['definite', 'indefinite'],

    # needed for Sinhalese
    'volition':   ['volitive', 'involitive'],

    # needed for K'iche' Mayan
    'transitivity':['transitive', 'intransitive'],

    # needed for Old English
    'strength':   ['strong', 'weak'],

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

    # needed for Spanish
    'formality':  ['familiar', 'polite', 'elevated', 'formal', 'tuteo', 'voseo'],

    # animacy ordered as follows:
    # 1st column: represents any of the tags that precede the entry in the middle column of that row
    # 2nd column: represents its own unique tag that excludes all preceding rows and following entries
    # 3rd column: represents any of the tags that follow the entry in the middle column of that row
    # As an example, all "animate" things are "living" but not all "dynamic" things are "living",
    # all "static" things are "nonliving" but not all static things are "abstract",
    # and a "plant" is "living", "dynamic", "nonagent", and "inanimate", among others.
    'animacy':    [            'human',         'nonhuman',    # member of the species homo sapiens
                   'rational', 'humanoid',      'nonsapient',  # having the ability to think and speak
                   'animate',  'creature',      'inanimate',   # able to move around on its own
                   'living',   'plant',         'nonliving',   # able to grow and reproduce
                   'concrete', 'manifestation', 'abstract',    # able to take physical form
                   'thing'],
    'partitivity':['nonpartitive', 'partitive', 'bipartitive'],
    'clitic':     ['tonic', 'proclitic', 'mesoclitic', 'endoclitic', 'enclitic'],
    'distance':   ['proximal','medial','distal'],

    # needed for possessive pronouns
    'possessor-person':    ['1st-possessor', '2nd-possessor', '3rd-possessor'],
    'possessor-number':    ['singular-possessor', 'dual-possessor', 'plural-possessor'],
    'possessor-gender':    ['masculine-possessor', 'feminine-possessor', 'neuter-possessor'],
    'possessor-clusivity': ['inclusive-possessor', 'exclusive-possessor'],
    'possessor-formality': ['familiar-possessor', 'polite-possessor', 'elevated-possessor', 'formal-possessor', 'tuteo-possessor', 'voseo-possessor'],

    # needed for Sanskrit and Japanese
    'stem':       ['primary', 'causative', 'intensive',],

    # needed for gerunds, supines, participles, and gerundives
    'gender':     ['masculine', 'feminine', 'neuter'],
    'case':       ['nominative', 'ergative',
                   'oblique', 'accusative', 'absolutive', 
                   'genitive', 'dative', 'ablative', 'locative', 'instrumental', 'vocative', 
                   'partitive', 'prepositional', 'abessive', 'adessive', 'allative', 'comitative', 'delative', 
                   'elative', 'essive', 'essive-formal', 'essive-modal', 'exessive', 'illative', 
                   'inessive', 'instructive', 'instrumental-comitative', 'sociative', 'sublative', 'superessive', 
                   'temporal', 'terminative', 'translative','disjunctive', 'undeclined'],

    # NOTE: "role" is used in the sense of "semantic role", a.k.a. "thematic relation": https://en.wikipedia.org/wiki/Thematic_relation
    #   In our analysis, semantic role forms one part of what is referred to here as "use case" 
    #    (the other part is referred to as "motion", which is defined below).
    #   Each language has a unique map from use case to the grammatical case, 
    #    and it is grammatical case that language learners are typically most familiar with (e.g. nominative, ablative, etc.)
    #   Semantic roles are also categorized into "macroroles" (i.e. subject, direct-object, indirect-object, modifier) 
    #    and it is the macrorole that determines how noun phrases should be ordered within a clause.
    'role': [
        'solitary', # the subject of an intransitive verb
        'agent',    # the subject of a transitive verb
        'patient',  # the direct object of an active verb
        'theme',    # the direct object of a stative verb
        'possessor', 'location', 'extent', 'vicinity', 'interior', 'surface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 'possession', 
        'time', 'state of being', 'topic', 'company', 'resemblance'],
    # NOTE: "motion" is introduced here as a grammatical tagaxis to capture certain kinds of motion based use cases
    #  that differ only in whether something is moving towards or away from them, whether something is staying still, or whether something is being leveraged
    # To illustrate, in Finnish motion is what distinguishes the "lative" case from the "allative" case.
    'motion': ['departed', 'associated', 'acquired', 'leveraged'],

    # needed for infinitive forms, finite forms, participles, arguments, and graphic depictions
    'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
    'tense':      ['present', 'past', 'future',], 
    'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 

    # needed for correlatives in general
    'abstraction':['institution','location','origin',
                   'destination','time','manner','reason','quality','amount'],

    # needed for quantifiers/correlatives
    'quantity':   ['universal', 'negative', 'assertive', 'elective'],

    # needed to distinguish pronouns from common nouns and to further distinguish types of pronouns
    'noun-form':  ['common', 'personal', 
                   'demonstrative', 'interrogative', 'quantifier', 'numeral',
                   'reciprocal', 'reflexive', 'emphatic-reflexive',
                   'common-possessive', 'personal-possessive'],

    # needed to distinguish forms of verb that require different kinds of lookups with different primary keys
    'verb-form':  ['finite', 'infinitive', 
                   'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
                   'argument', 'group'],
}

tag_to_tagaxis = {
    instance:type_ 
    for (type_, instances) in tagaxis_to_tags.items() 
    for instance in instances
}

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
                    'number',     # needed for German
                    'gender',     # needed for Latin, German, Russian
                    'case',       # needed for Latin, German
                    'voice',      # needed for Russian
                    'tense',      # needed for Greek, Russian, Spanish, Swedish, French
                    'aspect',     # needed for Greek, Latin, German, Russian
                    'script',
                ])),
        # verbs used as adverbs
        'adverbial': DictLookup(
            'adverbial',
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
        'group': DictLookup('group', DictKeyIndexing('verb')),
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

reflexive_pronoun_declension_hashing = DictTupleIndexing([
        'person',     # needed for English
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'formality',   # needed for Spanish ('voseo')
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
                    'gender',           
                    'clusivity',   # needed for Quechua
                    'formality',   # needed for Spanish ('voseo')
                    'case',           
                    'clitic',
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
        'quantifier':    DictTupleIndexing([
                    'quantity',
                    'number',     # needed for German
                    'gender',     # needed for Latin, German, Russian
                    'animacy',    # needed for Old English, Russian
                    'partitivity',# needed for Old English, Quenya, Finnish
                    'case',       # needed for Latin
                    'script',     # needed for Greek, Russian, Quenya, Sanskrit, etc.
                ]),
        'interrogative':      DictLookup('interrogative',      basic_pronoun_declension_hashing),
        'numeral':            DictLookup('numeral',            basic_pronoun_declension_hashing),
        'reciprocal':         DictLookup('reciprocal',         reflexive_pronoun_declension_hashing),
        'reflexive':          DictLookup('reflexive',          reflexive_pronoun_declension_hashing),
        'emphatic-reflexive': DictLookup('emphatic-reflexive', reflexive_pronoun_declension_hashing),
        'common-possessive':  DictLookup(
            'common-possessive',
            DictTupleIndexing([
                    'possessor-noun',
                    'possessor-number', 
                    'number',           
                    'gender',           
                    'case',           
                    'clitic',
                    'script',
                ])),
        'personal-possessive': DictLookup(
            'personal-possessive',
            DictTupleIndexing([
                    'possessor-person', 
                    'possessor-number', 
                    'possessor-gender', 
                    'possessor-clusivity',   # needed for Quechua
                    'possessor-formality',   # needed for Spanish ('voseo')
                    'number',
                    'gender',
                    'case',
                    'clitic',
                    'script',
                ])),
    })

tsv_parsing = SeparatedValuesFileParsing()

finite_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {0:'verb'}, 
    {**tagaxis_to_tags, 'script':'latin', 'verb-form':'finite'})
nonfinite_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {0:'verb'},
    {**tagaxis_to_tags, 'script':'latin', 'verb-form':'infinitive'})
pronoun_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {}, 
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'personal'})
possessive_pronoun_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'personal-possessive'})
common_noun_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {0:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
noun_adjective_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {0:'adjective',1:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
declension_template_noun_annotation = CellAnnotation(
    tag_to_tagaxis, {0:'language'}, {0:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
mood_annotation = CellAnnotation(
    {}, {0:'column'}, {0:'mood'}, {'script':'latin'})

conjugation_population = NestedLookupPopulation(conjugation_template_lookups)
declension_population  = NestedLookupPopulation(declension_template_lookups)
emoji_noun_population = FlatLookupPopulation(DictLookup('emoji noun', DictTupleIndexing(['noun','number'])))
emoji_noun_adjective_population = FlatLookupPopulation(DictLookup('emoji noun adjective', DictTupleIndexing(['adjective','noun'])))
mood_population = FlatLookupPopulation(DictLookup('mood', DictTupleIndexing(['mood','column'])))

nonfinite_traversal = DictTupleIndexing(['tense', 'aspect', 'mood', 'voice'])

bracket_shorthand = BracketedShorthand(Enclosures())

html_group_positioning = HtmlGroupPositioning()

emoji_shorthand = EmojiInflectionShorthand(
    EmojiSubjectShorthand(), 
    EmojiPersonShorthand(
        EmojiNumberShorthand(
            HtmlNumberTransform(
                HtmlPersonPositioning(html_group_positioning)
            ), 
            bracket_shorthand
        )
    ),
    EmojiBubbleShorthand(HtmlBubble(), bracket_shorthand),
    TextTransformShorthand(HtmlTextTransform(), bracket_shorthand),
    EmojiAnnotationShorthand(html_group_positioning, bracket_shorthand),
    EmojiModifierShorthand(),
)

nouns_to_depictions = {
    'animal':'cow',
    'thing':'bolt',
    'phenomenon': 'eruption',
}

emoji = Emoji(
    nouns_to_depictions,
    emoji_noun_adjective_population.index(
        noun_adjective_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/adjective-agreement.tsv'), 1, 2)),
    emoji_noun_population.index(
        common_noun_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/noun-declension.tsv'), 1, 2)),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/mood-templates.tsv'), 1, 1)),
    emoji_shorthand, 
    HtmlTenseTransform(), 
    HtmlAspectTransform(), 
)

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
    'motion', 'role', 'specificity', 'syntax-tree', 
    'adposition', 'declined-noun-function', 'declined-noun-argument',
    'emoji'])
declension_template_population = ListLookupPopulation(
    DefaultDictLookup('declension-template',
        DictTupleIndexing(['motion','role']), lambda key:[]))
declension_templates = \
    declension_template_population.index(
        declension_template_annotation.annotate(
            tsv_parsing.rows(
                'data/inflection/declension-templates-minimal.tsv')))

case_annotation = RowAnnotation(['motion','role','case','adposition'])
case_population = FlatLookupPopulation(
    DictLookup('declension-use-case-to-grammatical-case', 
        DictTupleIndexing(['motion','role'])),
    MultiKeyEvaluation(['case','adposition'])
)

declension_verb_annotation = CellAnnotation(
    tag_to_tagaxis, {0:'language'}, {0:'verb'}, 
    {'script':'latin', 'verb-form':'finite','gender':['masculine','feminine','neuter']})


def write(filename, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(f'{row}\n')

def has_annotation(key, value):
    def _has_annotation(annotated_cell):
        annotation, cell = annotated_cell
        return key in annotation and annotation[key] == value or value in annotation[key]
    return _has_annotation

def replace(replacements):
    def _replace(content):
        for replaced, replacement in replacements:
            content = content.replace(replaced, replacement)
        return content
    return _replace

list_tools = ListTools()
english_list_substitution = EnglishListSubstitution()

english = Language(
    ListGrammar(
        conjugation_population.index([
            *finite_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/irregular-conjugations.tsv'), 4, 1),
            *finite_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/regular-conjugations.tsv'), 4, 1),
        ]),
        declension_population.index([
            *pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/pronoun-declensions.tsv'), 1, 5),
            *possessive_pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/pronoun-possessives.tsv'), 1, 4),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/declensions.tsv'), 1, 2),
        ]),
        case_population.index(
            case_annotation.annotate(
                tsv_parsing.rows('data/inflection/english/modern/declension-use-case-to-grammatical-case.tsv'))),
        {'language-type':'native'},
    ),
    RuleSyntax('subject verb direct-object indirect-object modifiers'.split()),
    list_tools,
    RuleFormatting(),
    None,
    substitutions = [
        {'cloze': list_tools.unwrap()}, # English serves as a native language here, so it never shows clozes
        {'v': english_list_substitution.verbform}, # English participles are encoded as perfect/imperfect forms and must be handled specially
        {'v': english_list_substitution.tense},    # English uses auxillary verbs ("will") to indicate tense
        {'v': english_list_substitution.aspect},   # English uses auxillary verbs ("be", "have") to indicate aspect
        {'v': english_list_substitution.voice},    # English uses auxillary verbs ("be") to indicate voice
    ]
)

card_generation = CardGeneration(
    english, 
    emoji, 
    CardFormatting(),
    DeclensionTemplateMatching(declension_templates, allthat),
    ListParsing(),
    list_tools
)
