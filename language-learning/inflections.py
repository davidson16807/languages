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
from tools.evaluation import CellEvaluation, KeyEvaluation, MultiKeyEvaluation
from tools.population import NestedLookupPopulation, ListLookupPopulation, FlatLookupPopulation
from tools.nodemaps import (
    ListTools, ListGrammar,
    RuleValidation, RuleFormatting, RuleSyntax,
)
from tools.emoji import Emoji
from tools.languages import Language
from tools.writing import Writing
from tools.cards import DeclensionTemplateMatching, CardFormatting, CardGeneration

tagaxis_to_tags = {

    # needed to lookup the argument that is used to demonstrate a verb
    'language-type':  'native foreign'.split(), 

    'plicity': 'implicit explicit'.split(),

    # 'encoding': 'attestation transliteration pronunciation'.split(),

    'script': 
        # scripts that were derived from the phoenecian alphabet:
        'latin cyrillic greek hebrew arabic phoenician ipa transliteration '
        # scripts that were derived, borrowing aesthetics from chinese logograms:
        'hirigana katakana hangul '
        # scripts that were derived from chinese logograms:
        'traditional-han simplified-han kanji hanja chữ-hán chữ-nôm '
        'devanagari bengali gujarati gurmukhi oria tibetan '
        'simhala malayalam tamil telugu kannada '
        'burmese khmer thai lao balinese javanese sudanese brahmic '
        # scripts that were derived from egyptian heiroglyphs:
        'coptic meroitic demotic hieratic '
        # broad categories of script to handle niche applications:
        'runes heiroglyphs cuneiform emoji'.split(),

    # needed for infinitives in Old English and Swedish
    'completion': 'full bare'.split(),

    # needed for Old English
    'strength':   'strong weak'.split(),

    # needed for finite forms
    'person':     '1 2 3'.split(),
    'number':     'singular dual trial paucal plural superplural'.split(),
    'clusivity':  'inclusive exclusive'.split(),

    # needed for Spanish
    'formality':  'familiar polite elevated formal tuteo voseo'.split(),

    # "animacy" is ordered as follows:
    # 1st column: represents any of the tags that precede the entry in the middle column of that row
    # 2nd column: represents its own unique tag that excludes all preceding rows and following entries
    # 3rd column: represents any of the tags that follow the entry in the middle column of that row
    # As an example, all "motile" things are "living" but not all "dynamic" things are "living",
    # all "static" things are "nonliving" but not all static things are "abstract",
    # and a "plant" is "living", "dynamic", "nonagent", and "nonmotile", among others.
    'animacy':    [            'human',         'nonhuman',    # member of the species homo sapiens
                   'rational', 'humanoid',      'nonrational', # having the ability to think and speak
                   'motile',   'creature',      'nonmotile',   # able to perceptibly move of its own will
                   'living',   'plant',         'nonliving',   # able to grow and reproduce
                   'concrete', 'manifestation', 'abstract',    # able to take physical form
                   'thing'],
    'partitivity':'nonpartitive partitive bipartitive'.split(),
    'clitic':     'tonic prefix suffix proclitic mesoclitic endoclitic enclitic'.split(),
    'distance':   'proximal medial distal'.split(),

    # needed for possessive pronouns
    'possessor-person':    '1st-possessor 2nd-possessor 3rd-possessor'.split(),
    'possessor-number':    'singular-possessor dual-possessor plural-possessor'.split(),
    'possessor-gender':    'masculine-possessor feminine-possessor neuter-possessor'.split(),
    'possessor-clusivity': 'inclusive-possessor exclusive-possessor'.split(),
    'possessor-formality': 'familiar-possessor polite-possessor elevated-possessor formal-possessor tuteo-possessor voseo-possessor'.split(),

    # needed for gerunds, supines, participles, and gerundives
    'gender':     'masculine feminine neuter'.split(),
    'case':       ['nominative', 'ergative',
                   'oblique', 'accusative', 'absolutive', 
                   'genitive', 'dative', 'ablative', 'locative', 'instrumental', 'vocative', 
                   'prepositional', 'abessive', 'adessive', 'allative', 'comitative', 'delative', 
                   'elative', 'essive', 'essive-formal', 'essive-modal', 'exessive', 'illative', 
                   'inessive', 'instructive', 'instrumental-comitative', 'sociative', 'sublative', 'superessive', 
                   'temporal', 'terminative', 'translative','disjunctive', 'undeclined'],

    # NOTE: "role" is used in the sense of "semantic role", a.k.a. "thematic relation": https://en.wikipedia.org/wiki/Thematic_relation
    #   In our analysis, the "role" forms one part of what is referred to here as "usage case".
    #    The other part of usage case is referred to as "motion", which is defined below.
    #   Each language has a unique map from usage case to grammatical case, 
    #    and it is grammatical case that language learners are typically most familiar with (e.g. nominative, ablative, etc.)
    #   Semantic roles are also categorized into "macroroles" (i.e. subject, direct-object, indirect-object, modifier) 
    #    and it is the macrorole that determines how noun phrases should be ordered within a clause.
    #   The "usage case" is an instance of a broader concept that we refer to as "seme".
    #   A "seme" is simply the domain of any map "seme→tag" that creates distinction 
    #    between the meaning that the speaker intends to convey and the set of meanings that could be interpreted by the audience.
    #   The names for semes are assigned here by appending "usage" to the name of whatever tag they map to, i.e. "usage case", "usage mood", etc.
    #   See README.txt and GLOSSARY.tsv for more information on these and related terms.
    'role': [
        # NON-INDIRECT:
        'existential', # a noun that is declared within an existential clause
        'solitary',    # a noun that performs the action of a intransitive verb
        'agent',       # a sentient noun that is interacting with a "patient" or "theme"
        'force',       # a nonsentient noun that is interacting with a "patient" or "theme"
        'patient',     # a noun that passively undergoes a state change
        'theme',       # a noun that is passively mentioned without undergoing a state change
        'experiencer', # a noun that perceives a "stimulus"
        'stimulus',    # a noun that is being perceived by an "experiencer"
        'predicand',   # a noun that is considered part of a larger "predicate" set
        'predicate',   # a noun that is considered to contain a smaller "predicand" set
        # INDIRECT:
        'audience',    # a noun that indicates the audience, i.e. the "vocative"
        'possessor',   # a noun that owns a "possession"
        'possession',  # a noun that is owned by a "possessor"
        'topic',       # a noun that is indicated as the topic of conversation, could be either indirect or nonindirect, and could exist in tandem with other nonindirect roles
        'comment',     # a noun that in some way relates to a "topic"
        'location', 'extent', 'vicinity', 'interior', 'surface', 'subsurface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 
        'time', 'state of being', 'company', 'resemblance'],
    # NOTE: "motion" is introduced here as a grammatical episemaxis to capture certain kinds of motion based use cases
    #  that differ only in whether something is moving towards or away from them, whether something is staying still, or whether something is being leveraged
    # To illustrate, in Finnish motion is what distinguishes the "lative" case from the "allative" case.
    'motion': 'departed associated acquired leveraged'.split(),
    'transitivity': 'transitive intransitive'.split(),
    # 'valency': 'impersonal intransitive transitivity'.split(),
    # 'subjectivity': 'subject direct-object indirect-object'.split(),

    # how the valency of the verb is modified to emphasize or deemphasize certain nouns
    'voice':      'active passive middle antipassive applicative causative'.split(),
    # when an event occurs relative to the present
    'tense':      'present past future'.split(), 
    # when an event occurs relative to a reference in time
    'relative-tense': 'before during after'.split(),

    'mood':       ['indicative', 'subjunctive', 'conditional', 
                   'optative', 'benedictive', 'jussive', 'probable', 
                   'imperative', 'prohibitive', 'desiderative', 
                   'dubitative', 'hypothetical', 'presumptive', 'permissive', 
                   'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
                   'precative', 'volitive', 'involutive', 'inferential', 
                   'necessitative', 'interrogative', 'injunctive', 
                   'suggestive', 'comissive', 'deliberative', 
                   'propositive', 'potential', 'conative', 'obligative',
                  ],

    # NOTE: "evidentiality", "logic", "probability", etc. form what is known as the "usage mood".
    # The "usage mood" is an instance of a broader concept that we refer to as "seme".
    # A "seme" is simply the domain of any map "seme→tag" that creates distinction 
    #  between the meaning that the speaker intends to convey and the set of meanings that could be interpreted by the audience.
    # The names for semes are assigned here by appending "usage" to the name of whatever tag they map to, i.e. "usage case", "usage mood", etc.
    # See README.txt and GLOSSARY.tsv for more information on these and related terms.
    'evidentiality':    'visual nonvisual circumstantial secondhand thirdhand accepted promised presumed supposed counterfactual'.split(),
    'implicativity':    'antecedant consequent positive negative'.split(),
    'probability':      'probable potential improbable aprobable'.split(),
    'subject-motive':   'subject-wanted subject-unwanted'.split(),
    'speaker-motive':   'speaker-wanted speaker-unwanted'.split(),
    'speaker-emphasis': 'emphatic encouraging dispassionate'.split(),
    'speaker-action':   'statement intent deferral request query proposal verification'.split(),
    'addressee-power':  'supernatural inferior aferior'.split(),

    # NOTE: "atomicity", "consistency", etc. form what is known as the "usage aspect".
    # The "usage aspect" is an instance of a broader concept that we refer to as "seme".
    # A "seme" is simply the domain of any map "seme→tag" that creates distinction 
    #  between the meaning that the speaker intends to convey and the set of meanings that could be interpreted by the audience.
    # The names for semes are assigned here by appending "usage" to the name of whatever tag they map to, i.e. "usage case", "usage aspect", etc.
    # See README.txt and GLOSSARY.tsv for more information on these and related terms.
    # how long the event occurs for
    'duration':            'short long indefinite'.split(), 
    # how consistently the event occurs
    'consistency':         'incessant habitual customary frequent momentary'.split(), 
    # whether the event has intermediate states
    'atomicity':           'atomic nonatomic'.split(), 
    # whether the event is part of a series of events
    'series-partitivity':  'series-partitive series-nonpartitive'.split(),
    # whether the event has affects that linger after its occurrence, and for how long
    'persistance':         'static impermanent persistant'.split(),
    # how far along the nonatomic event is, and what action has been taken on its progress
    'progress':            'started progressing paused arrested resumed continued finished'.split(),
    # whether the event occurs in the recent past/future
    'recency':             'recent nonrecent'.split(),
    # whether the event is associated with motion, and if so, what kind
    'direction':    'coherent reversing returning undirected unmoving'.split(),
    # whether the event is distributed among entities, and if so, how
    'distribution': 'centralized decentralized undistributed'.split(),

    'aspect': ['aorist', 'perfective','imperfective',
               'habitual', 'continuous',
               'progressive', 'nonprogressive',
               'stative', 'terminative', 'prospective', 'consecutive', 'usitative','iterative',
               'momentaneous','continuative','durative','repetitive','conclusive',
                'semelfactive','distributive','diversative','reversative','transitional','cursive',
               'completive','prolongative','seriative','inchoative','reversionary','semeliterative','segmentative'],

    # needed for correlatives in general
    'abstraction':['institution','location','origin',
                   'destination','time','manner','reason','quality','amount'],

    # needed for quantifiers/correlatives
    'quantity':   'universal nonexistential assertive elective'.split(),

    # needed to distinguish pronouns from common nouns and to further distinguish types of pronouns
    'noun-form':  ['common', 'personal', 
                   'demonstrative', 'interrogative', 'quantifier', 'numeral',
                   'reciprocal', 'relative', 'reflexive', 'emphatic-reflexive',
                   'common-possessive', 'personal-possessive', 'reflexive-possessive'],

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
                    'strength',    # needed for Old English
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
        'indefinite':         DictLookup('indefinite',         basic_pronoun_declension_hashing),
        'relative':           DictLookup('relative',           basic_pronoun_declension_hashing),
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
        'reflexive-possessive':  DictLookup(
            'reflexive-possessive',
            DictTupleIndexing([
                    'possessor-number', 
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
personal_pronoun_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {}, 
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'personal'})
pronoun_annotation  = CellAnnotation(
    tag_to_tagaxis, {}, {}, 
    {**tagaxis_to_tags, 'script':'latin'})
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

cell_evaluation = CellEvaluation()
conjugation_population = NestedLookupPopulation(conjugation_template_lookups, cell_evaluation)
declension_population  = NestedLookupPopulation(declension_template_lookups, cell_evaluation)
emoji_noun_population = FlatLookupPopulation(DictLookup('emoji noun', DictTupleIndexing(['noun','number'])), cell_evaluation)
emoji_noun_adjective_population = FlatLookupPopulation(DictLookup('emoji noun adjective', DictTupleIndexing(['adjective','noun'])), cell_evaluation)
mood_population = FlatLookupPopulation(DictLookup('mood', DictTupleIndexing(['mood','column'])), cell_evaluation)

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
            tsv_parsing.rows('data/inflection/emoji/adjective-agreement.tsv'))),
    emoji_noun_population.index(
        common_noun_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/common-noun-declensions.tsv'))),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/mood-templates.tsv'))),
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
        DictTupleIndexing(['motion','role']), lambda key:[]),
    cell_evaluation)
declension_templates = \
    declension_template_population.index(
        declension_template_annotation.annotate(
            tsv_parsing.rows(
                'data/inflection/declension-templates-minimal.tsv')))

case_annotation = CellAnnotation(
    tag_to_tagaxis, {0:'column'}, {}, {'script':'latin'})
case_population = NestedLookupPopulation(
    DefaultDictLookup('usage-case-to-grammatical-case', 
        DictTupleIndexing(['motion','role']),
        lambda dictkey: DictLookup('grammatical-case-columns',
            DictKeyIndexing('column'))),
    cell_evaluation
)

# annotations = tsv_parsing.rows('data/inflection/english/modern/usage-case-to-grammatical-case.tsv')
# test = case_population.index(case_annotation.annotate(tsv_parsing.rows('data/inflection/english/modern/usage-case-to-grammatical-case.tsv')))
# tags = {'motion':'associated','role':'agent'}
# breakpoint()

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

class EnglishListSubstitution:
    def __init__(self):
        pass
    def verbform(self, machine, tree, memory):
        '''same as self.inflection.conjugate(), but creates auxillary verb phrases when conjugation of a single verb is insufficient'''
        form = memory['verb-form']
        tense = memory['tense']
        aspect = memory['aspect']
        voice = memory['voice']
        if form  == 'participle': 
            return ['implicit', 'that', 'finite', tree]
        return tree
    def mood(self, machine, tree, memory):
        '''creates auxillary verb phrases when necessary to express mood'''
        mood = memory['mood']
        lookup = {
            'conditional':  ['indicative', 'would', 'infinitive', tree],
            'jussive':      ['indicative', 'should', 'infinitive', tree],
            'eventitive':   ['indicative', 'likely', 'infinitive', tree],
            'hypothetical': ['indicative', 'might', 'infinitive', tree],
            'desiderative': ['indicative', ['v','want'], 'to', 'infinitive', tree],
            'necessitative':['indicative', ['v','need'], 'to', 'infinitive', tree],
            'potential':    ['indicative', ['v','be able'], 'to', 'infinitive', tree],
            # NOTE: the following are nice ideas, but can be misinterpreted as supposition, 
            # and are superfluous if other markers are added to disambiguate:
            # 'imperative':   ['indicative', 'must', 'infinitive', tree],
            # 'prohibitive':  ['indicative', 'must', 'not', 'infinitive', tree],
        }
        return tree if mood not in lookup else lookup[mood]
    def tense(self, machine, tree, memory):
        '''creates auxillary verb phrases and bracketed subtext when necessary to express tense'''
        tense = memory['tense']
        verbform = memory['verb-form']
        if (tense, verbform) == ('future', 'finite'):       return ['will',        'infinitive', tree]
        if (tense, verbform) == ('past',   'infinitive'):   return ['[back then]', tree]
        # if (tense, verbform) == ('present','infinitive'):   return ['[right now]', tree]
        if (tense, verbform) == ('future', 'infinitive'):   return ['[later on]',   tree]
        return tree
    def aspect(self, machine, tree, memory):
        '''creates auxillary verb phrases when necessary to express aspect'''
        aspect = memory['aspect']
        if aspect == 'imperfective':           return [['active', 'aorist', 'v', 'be'],   'finite', tree]
        if aspect == 'perfective':             return [['active', 'aorist', 'v', 'have'], 'finite', tree]
        if aspect == 'perfective-progressive': return [['active', 'aorist', 'v', 'have'], 'finite', ['perfective', 'v', 'be'], ['imperfective', tree]]
        return tree
    def voice(self, machine, tree, memory):
        '''creates auxillary verb phrases when necessary to express voice'''
        voice = memory['voice']
        if voice  == 'passive': return [['active', 'v', 'be'],             'finite', ['active', 'perfective', tree]]
        if voice  == 'middle':  return [['active', 'implicit', 'v', 'be'], 'finite', ['active', 'perfective', tree]]
        return tree
    def formality_and_gender(self, machine, tree, memory):
        '''creates pronouns procedurally when necessary to capture distinctions in formality from other languages'''
        formality = memory['formality']
        gender = memory['gender']
        person = memory['person']
        number = memory['number']
        nounform = memory['noun-form']
        nonsingular_3rd_gender_marker = {
            'masculine': '♂',
            'feminine': "♀",
            'neuter': "⚲",
        }
        formal_singular_gender_marker = {
            'masculine': '[sir]',
            'feminine': "[ma'am]",
            'neuter': "[respectfully]",
        }
        formal_nonsingular_gender_marker = {
            'masculine': '[gentlemen]',
            'feminine': "[ladies]",
            'neuter': "[respectfully]",
        }
        gender_marker = {
            ('3','singular'): {
                'formal': {
                    'singular': formal_singular_gender_marker[gender]
                }.get(number, formal_nonsingular_gender_marker[gender])
            }.get(formality, nonsingular_3rd_gender_marker[gender])
        }.get((person, number), '')
        formality_marker = {
            'polite': '[politely]',
            'elevated': '[elevated]',
            'voseo': '[voseo]',
        }.get(formality, '')
        return [tree, 
            gender_marker if 'show-gender' in memory and memory['show-gender'] else '', 
            formality_marker] if nounform == 'personal' else tree


list_tools = ListTools()
english_list_substitution = EnglishListSubstitution()

english = Writing(
    'latin',
    Language(
        ListGrammar(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/irregular-conjugations.tsv')),
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/regular-conjugations.tsv')),
            ]),
            declension_population.index([
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/pronoun-declensions.tsv')),
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/common-noun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/adjective-agreement.tsv')),
            ]),
            case_population.index(
                case_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/modern/usage-case-to-grammatical-case.tsv'))),
            {'language-type':'native'},
        ),
        RuleSyntax('subject verb direct-object indirect-object modifiers'.split()),
        list_tools,
        RuleFormatting(),
        None,
        substitutions = [
            {'cloze': list_tools.unwrap()}, # English serves as a native language here, so it never shows clozes
            {'v': english_list_substitution.verbform}, # English participles are encoded as perfective/imperfective forms and must be handled specially
            {'v': english_list_substitution.mood},     # English uses auxillary verbs (e.g. "mood") to indicate some moods
            {'v': english_list_substitution.tense},    # English uses auxillary verbs ("will") to indicate tense
            {'v': english_list_substitution.aspect},   # English uses auxillary verbs ("be", "have") to indicate aspect
            {'v': english_list_substitution.voice},    # English uses auxillary verbs ("be") to indicate voice
            {'n': english_list_substitution.formality_and_gender}, # English needs annotations to clarify the formalities and genders of other languages
        ]
    )
)

card_generation = CardGeneration(
    english, 
    emoji, 
    CardFormatting(),
    DeclensionTemplateMatching(declension_templates, allthat),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/english/modern/mood-templates.tsv'))),
    ListParsing(),
    list_tools
)

tag_defaults = {
    **tagaxis_to_tags,
    
    'clitic':     'tonic',
    'clusivity':  'exclusive',
    'formality':  'familiar',
    'gender':     'masculine',
    'noun':       'man',
    'number':     'singular',
    'partitivity':'nonpartitive',
    'person':     '3',
    'strength':   'strong',

    'aspect':     'aorist', 
    'mood':       'indicative',
    'tense':      'present', 
    'voice':      'active',
}

