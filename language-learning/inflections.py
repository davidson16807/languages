'''
"inflections.py" contains helpful datasets and 

See README.txt and GLOSSARY.txt for notes on terminology
'''

import collections
import re

from tools.transforms import (
    HtmlGroupPositioning, HtmlPersonPositioning,
    HtmlTextTransform,  HtmlNumberTransform, HtmlTenseTransform, HtmlProgressTransform, HtmlBubble
)
from tools.shorthands import (
    Enclosures, BracketedShorthand, TextTransformShorthand,
    EmojiSubjectShorthand, EmojiAnnotationShorthand, EmojiPersonShorthand, EmojiNumberShorthand, 
    EmojiModifierShorthand, EmojiBubbleShorthand, EmojiPerson, EmojiInflectionShorthand, EmojiVocabularyShorthand
)

from tools.parsing import SeparatedValuesFileParsing, TermParsing, ListParsing, LatexlikeParsing
from tools.annotation import RowAnnotation, CellAnnotation
from tools.predicates import Predicate
from tools.dictstores import DefaultDictLookup, DictLookup, DictSet, NestedDictLookup, FallbackDictLookup, ProceduralLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.labels import TermLabelEditing, TermLabelFiltering
from tools.evaluation import IdentityEvaluation, KeyEvaluation, MultiKeyEvaluation
from tools.population import NestedLookupPopulation, ListLookupPopulation, FlatLookupPopulation, DictSetPopulation
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleSyntax, RuleFormatting, 
)
from tools.languages import Language
from tools.orthography import Orthography
from tools.demonstration import TextDemonstration, EmojiDemonstration
from tools.cards import CardFormatting

'''
Given a mathematical bundle that is encoded as a dictionary,
`dict_bundle_to_map` returns the inverse of that bundle as a dictionary,
i.e., a pure function that is encoded as a dictionary and maps each germ in the bundle to its respective stalk.
'''
def dict_bundle_to_map(bundle):
    return {
        germ:stalk 
        for (stalk, germs) in bundle.items() 
        for germ in germs
    }


case_episemaxis_to_episemes = {
    # NOTE: "role" is used in the sense of "semantic role", a.k.a. "thematic relation": https://en.wikipedia.org/wiki/Thematic_relation
    #   In our analysis, the "role" forms one part (an "episeme") of what is referred to here as "semantic case" (a "seme").
    #   The other part of semantic case is referred to as "motion", which is defined below.
    #   The term "semantic case" is used in a similar sense as "deep case" in existing literature.
    #   The term "semantic case" is introduced both to place distinction with "role" 
    #    and to create a paradigm where we map between language-agnostic "semantic" semes 
    #    and language-specific "grammatical" tags, e.g. "semantic mood" to "grammatical mood",  
    #    "semantic aspect" to "grammatical aspect", etc.
    #   Each language has a unique map from a semantic case to grammatical case, 
    #    and it is grammatical case that language learners are typically most familiar with (e.g. nominative, ablative, etc.)
    #   A language's map from semantic case to grammatical case is known as its "case usage".
    #   Semantic roles are also categorized into "macroroles" (i.e. subject, direct-object, indirect-object, modifier) 
    #    and it is the macrorole that determines how noun phrases should be ordered within a clause.
    #   See README.txt and GLOSSARY.tsv for more information on these and related terms.
    'role': [
        # NON-INDIRECT:
        # 'existential', # a noun that is declared within an existential clause
        'agent',       # a sentient noun that is interacting with a "patient" or "theme"
        'force',       # a nonsentient noun that is interacting with a "patient" or "theme"
        'patient',     # a noun that passively undergoes a state change
        'theme',       # a noun that is passively mentioned without undergoing a state change
        'experiencer', # a noun that perceives a "stimulus"
        'stimulus',    # a noun that is being perceived by an "experiencer"
        'predicand',   # a noun that is considered part of a larger "predicate" set
        'predicate',   # a noun that is considered to contain a smaller "predicand" set
        # INDIRECT:
        'topic',       # a noun that is indicated as the topic of conversation, could be either indirect or nonindirect, and could exist in tandem with other nonindirect roles
        'comment',     # a noun that in some way relates to a "topic"
        'possessor',   # a noun that owns a "possession"
        'possession',  # a noun that is owned by a "possessor"
        'location', 'extent', 'vicinity', 'interior', 'medium', 'side', 'surface', 'subsurface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 
        'time', 'state-of-being', 'company', 'resemblance'],
    # NOTE: "motion" is introduced here as a grammatical episemaxis to capture certain kinds of motion based use cases
    #  that differ only in whether something is moving towards or away from them, whether something is staying still, or whether something is being leveraged
    # To illustrate, in Finnish motion is what distinguishes the "lative" case from the "allative" case.
    'subjectivity': 'addressee subject direct-object indirect-object modifier verb'.split(),
    'motion':  'departed associated acquired approached surpassed leveraged'.split(),
    'valency': 'impersonal intransitive transitive'.split(),
}

mood_episemaxis_to_episemes = {
    # NOTE: "evidentiality", "logic", "confidence", etc. are small parts ("episemes") to a larger part (a "seme") known as the "semantic mood".
    # A "seme" is simply the domain of any map "seme→tag" that creates distinction 
    #  between the meaning that the speaker intends to convey and the grammatical decision (bijective to a set of meanings) that could be interpreted by the audience.
    # The names for semes are assigned here by appending "semantic" to the name of whatever tag they map to, i.e. "semantic case", "semantic mood", etc.
    # See README.txt and GLOSSARY.tsv for more information on these and related terms.
    # how the statement arises in the context of logical discourse
    'evidentiality': [
        'promised',       # speaker attests to the event, speaker determines if the event occurs
    #   'useless',        # speaker attests to the event, addressee determines if the event occurs (not useful)
        'presumed',       # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, no evidence given
        'visual',         # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is visual
        'nonvisual',      # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is nonvisual
        'secondhand',     # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is secondhand
        'thirdhand',      # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is thirdhand
        'circumstantial', # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is circumstantial in some way
        'means',          # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is circumstantial, based on means
        'motive',         # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is circumstantial, based on motive
        'necessity',      # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence is circumstantial, based on need
        'conceded',       # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence of addressee is recognized
        'proposed',       # speaker attests to the event, subject determines if the event occurs, actuality of event is considered, evidence provided elsewhere
        'supposed',       # speaker attests to the event, subject determines if the event occurs, actuality of event is not considered, evidence provided elsewhere
        'antecedent',     # speaker attests to the event, subject determines if the event occurs, actuality of event is not considered, evidence provided elsewhere
        'consequent',     # speaker attests to the event, subject determines if the event occurs, actuality of event is not considered, evidence is contingent on other event
        'queried',        # addressee attests to the event, subject determines if the event occurs
        'deliberated',    # addressee attests to the event, addressee determines if the event occurs, subject has no persuation to give
        'pending',        # addressee attests to the event, addressee determines if the event occurs, addressee is likely persuaded and confirmation is pending
        'requested',      # addressee attests to the event, addressee determines if the event occurs, addressee not subject to persuasion
        'encouraged',     # addressee attests to the event, addressee determines if the event occurs, addressee is being persuaded by encouragement
        'implored',       # addressee attests to the event, addressee determines if the event occurs, addressee is being persuaded by emphasis
        'commanded',      # addressee attests to the event, addressee determines if the event occurs, addressee is subordinate
        'prayed',         # addressee attests to the event, addressee determines if the event occurs, addressee is supernatural
        'wished',         # subject attests to the event, subject determines if the event occurs, addressee is invested in outcome
        'deferred',       # subject attests to the event, subject determines if the event occurs, addressee is not invested in outcome
    ],
    # whether the event is confirmed or denied
    'polarity':         'positive negative'.split(),
    # how likely the statement is to be true
    'confidence':       'confident probable possible'.split(),
    # how surprised the speaker depicts himself
    'surprise':         'surprised unsurprised'.split(),
    # how ironic the speaker is
    'irony':            'ironic unironic'.split(),
}

aspect_episemaxis_to_episemes = {
    # NOTE: "duration", "consistency", etc. form what is known as the "semantic aspect".
    # The "semantic aspect" is an instance of a broader concept that we refer to as "seme".
    # A "seme" is simply the domain of any map "seme→tag" that creates distinction 
    #  between the meaning that the speaker intends to convey and the set of meanings that could be interpreted by the audience.
    # The names for semes are assigned here by appending "semantic" to the name of whatever tag they map to, i.e. "semantic case", "semantic aspect", etc.
    # See README.txt and GLOSSARY.tsv for more information on these and related terms.
    # how long the event occurs for
    'duration':            'brief protracted indeterminate'.split(), 
    # how consistently the event occurs
    'progress':            'atomic atelic started unfinished attempted transitioning paused arrested resumed continued finished'.split(),
    # whether the event is one part in a sequence of events
    'consistency':         'momentary experiential habitual customary frequent incessant'.split(), 
    # whether the event has intermediate states, and if so, what state it is in
    'ordinality':          'nonordinal ordinal'.split(),
    # whether the event has affects that linger after its occurrence, and for how long
    'persistence':         'static impermanent persistant'.split(),
    # whether the event occurs in the recent past/future
    'recency':             'nonrecent recent arecent'.split(),
    # whether the event is associated with motion, and if so, what kind
    'trajectory':          'rectilinear reversing returning directionless motionless'.split(),
    # whether the event is distributed among entities, and if so, how
    'distribution':        'centralized decentralized undistributed'.split(),
}

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
    'person':      '1 2 3 4'.split(),
    'number':      'singular dual trial paucal plural superplural'.split(),
    'definiteness':'definite indefinite adefinite'.split(),
    'clusivity':   'inclusive exclusive'.split(),

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
    'possessor-person':    '1-possessor 2-possessor 3-possessor'.split(),
    'possessor-number':    'singular-possessor dual-possessor plural-possessor'.split(),
    'possessor-gender':    'masculine-possessor feminine-possessor neuter-possessor'.split(),
    'possessor-clusivity': 'inclusive-possessor exclusive-possessor'.split(),
    'possessor-formality': 'familiar-possessor polite-possessor elevated-possessor formal-possessor tuteo-possessor voseo-possessor'.split(),

    # needed for gerunds, supines, participles, and gerundives
    'gender':     'masculine feminine neuter'.split(),
    'case':       
        '''nominative ergative
           oblique accusative absolutive 
           genitive dative ablative locative instrumental vocative 
           prepositional abessive adessive allative comitative delative 
           elative essive essive-formal essive-modal exessive illative 
           inessive instructive instrumental-comitative sociative sublative superessive 
           temporal terminative translative disjunctive undeclined'''.split(),

    # how the valency of the verb is modified to emphasize or deemphasize certain participants
    'voice':      'active passive middle antipassive applicative causative'.split(),
    # when an event occurs relative to the present
    'tense':      'present past future'.split(), 
    # when an event occurs relative to a reference in time
    'relative-tense': 'before during after'.split(),

    'mood': 
        '''indicative subjunctive conditional 
           optative benedictive jussive probable 
           imperative prohibitive desiderative 
           dubitative hypothetical presumptive permissive 
           admirative ironic-admirative hortative eventitive 
           precative volitive involutive inferential 
           necessitative interrogative injunctive 
           suggestive comissive deliberative 
           propositive potential conative obligative'''.split(),

    'aspect': 
        '''simple perfective imperfective
           habitual continuous
           progressive nonprogressive
           stative terminative prospective consecutive usitative iterative
           momentaneous continuative durative repetitive conclusive
           semelfactive distributive diversative reversative transitional cursive
           completive prolongative seriative inchoative reversionary semeliterative segmentative'''.split(),

    # # needed for correlatives in general
    # 'abstraction': 'organization location origin destination time manner reason quality amount'.split(),

    # needed when creating demonstrations for declensions
    'template': 
        '''organization sapient 
           carnivore herbivore granivore fruitivore nectarivore detritivore seacreature 
           plant bodypart bodyfluid viscera 
           food item fixture liquid gas event location side surface interior 
           heat-source visible audible vice virtue size quality quantity manner reason concept'''.split(),

    # needed for quantifiers/correlatives
    'quantity':    'universal nonexistential assertive elective'.split(),

    # needed to distinguish pronouns from common nouns and to further distinguish types of pronouns
    'noun-form':  
        '''common personal 
           demonstrative interrogative quantifier numeral
           reciprocal relative reflexive emphatic-reflexive
           common-possessive personal-possessive reflexive-possessive'''.split(),

    # needed to distinguish forms of verb that require different kinds of lookups with different primary keys
    'verb-form':  'finite infinitive participle gerundive gerund adverbial supine group'.split(),
}

tag_to_tagaxis = dict_bundle_to_map(tagaxis_to_tags)
episemes_to_case_episemaxis = dict_bundle_to_map(case_episemaxis_to_episemes)
episemes_to_mood_episemaxis = dict_bundle_to_map(mood_episemaxis_to_episemes)
episemes_to_aspect_episemaxis = dict_bundle_to_map(aspect_episemaxis_to_episemes)

termaxis_to_terms = {
    **tagaxis_to_tags,
    **case_episemaxis_to_episemes,
    **mood_episemaxis_to_episemes,
    **aspect_episemaxis_to_episemes,
}

term_to_termaxis = dict_bundle_to_map(termaxis_to_terms)
parse_any = TermParsing(term_to_termaxis)

verbial_declension_hashing = parse_any.tokenindexing('verb voice number gender case script')

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
    })

basic_pronoun_declension_hashing = parse_any.termindexing('number gender animacy partitivity case script')
reflexive_pronoun_declension_hashing = parse_any.termindexing('person number gender formality case script')

declension_template_lookups = DictLookup(
    'declension',
    DictKeyIndexing('noun-form'), 
    {
        'common': parse_any.tokenfield('common', 
            'noun number gender partitivity strength case script', ''),
        'personal': parse_any.termfield('personal', 
            'person number gender clusivity formality case clitic script', ''),
        'common-possessive': parse_any.tokenfield('common-possessive', 
            'possessor-noun possessor-number number gender case clitic script', ''),
        'personal-possessive': parse_any.termfield('personal-possessive', 
            'possessor-person possessor-number possessor-gender possessor-clusivity possessor-formality number gender case clitic script', ''),
        'reflexive-possessive': parse_any.termfield('reflexive-possessive', 
            'possessor-number number gender case clitic script', ''),
        'demonstrative': parse_any.termfield('demonstrative', 
            'distance number gender animacy partitivity case script', ''),
        'quantifier': parse_any.termfield('quantifier', 
            'quantity number gender animacy partitivity case script', ''),
        'interrogative':      DictLookup('interrogative',      basic_pronoun_declension_hashing),
        # 'indefinite':         DictLookup('indefinite',         basic_pronoun_declension_hashing),
        'relative':           DictLookup('relative',           basic_pronoun_declension_hashing),
        'numeral':            DictLookup('numeral',            basic_pronoun_declension_hashing),
        'reciprocal':         DictLookup('reciprocal',         reflexive_pronoun_declension_hashing),
        'reflexive':          DictLookup('reflexive',          reflexive_pronoun_declension_hashing),
        'emphatic-reflexive': DictLookup('emphatic-reflexive', reflexive_pronoun_declension_hashing),
    })

finite_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {0:'verb'}, 
    {**tagaxis_to_tags, 'script':'latin', 'verb-form':'finite'})
nonfinite_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {0:'verb'},
    {**tagaxis_to_tags, 'script':'latin', 'verb-form':'infinitive'})
personal_pronoun_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {}, 
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'personal'})
pronoun_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {}, 
    {**tagaxis_to_tags, 'script':'latin'})
possessive_pronoun_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'personal-possessive'})
common_noun_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {0:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
emoji_noun_adjective_annotation  = CellAnnotation(
    'inflection', tag_to_tagaxis, {}, {0:'adjective',1:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
emoji_noun_verb_annotation = RowAnnotation('flag noun verb emoji'.split())
emoji_verb_annotation = RowAnnotation('flag template verb emoji'.split())
emoji_noun_declensions_annotation = CellAnnotation(
    'inflection', term_to_termaxis, {}, {}, termaxis_to_terms)
declension_template_noun_annotation = CellAnnotation(
    'inflection', tag_to_tagaxis, {0:'language'}, {0:'noun'},
    {**tagaxis_to_tags, 'script':'latin', 'noun-form':'common', 'person':'3'})
mood_annotation = CellAnnotation(
    'inflection', {}, {0:'column'}, {0:'mood'}, {'script':'latin'})
declension_verb_annotation = CellAnnotation(
    'inflection', tag_to_tagaxis, {0:'language'}, {1:'verb'}, 
    {'script':'latin', 'verb-form':'finite','gender':['masculine','feminine','neuter']})
template_verb_annotation = CellAnnotation(
    'verb', term_to_termaxis, {0:'template'}, {}, {})
template_dummy_annotation = RowAnnotation('flag subjectivity verb voice valency dummy-motion dummy-role dummy-subjectivity dummy-definiteness dummy-noun'.split())
template_tree_annotation = RowAnnotation('flag valency subjectivity tree'.split())
noun_template_annotation = RowAnnotation('noun template'.split())

conjugation_population = NestedLookupPopulation(conjugation_template_lookups, KeyEvaluation('inflection'))
declension_population  = NestedLookupPopulation(declension_template_lookups, KeyEvaluation('inflection'))
emoji_noun_population = FlatLookupPopulation(DictLookup('emoji noun', DictTupleIndexing(['noun','number'])), KeyEvaluation('inflection'))
emoji_noun_adjective_population = FlatLookupPopulation(DictLookup('emoji noun adjective', DictTupleIndexing(['adjective','noun'])), KeyEvaluation('inflection'))
emoji_noun_verb_population = FlatLookupPopulation(DictLookup('emoji noun verb', DictTupleIndexing('noun verb'.split())), KeyEvaluation('emoji'))
emoji_verb_population = FlatLookupPopulation(DictLookup('emoji verb', DictTupleIndexing('template verb'.split())), KeyEvaluation('emoji'))
emoji_noun_declensions_population = FlatLookupPopulation(DictLookup('declension-templates', DictTupleIndexing('valency subjectivity motion role'.split())), KeyEvaluation('inflection'))
mood_population = FlatLookupPopulation(DictLookup('mood', DictTupleIndexing('mood column'.split())), KeyEvaluation('inflection'))
noun_template_population = DictSetPopulation(DictSet('noun-template', DictTupleIndexing('noun template'.split()), set()))
template_verb_population = DictSetPopulation(DictSet('template-verb', DictTupleIndexing('template role subjectivity valency verb'.split()), set()))
template_tree_population = FlatLookupPopulation(DictLookup('template-tree', DictTupleIndexing('valency subjectivity'.split())), KeyEvaluation('tree'))
template_dummy_population = FlatLookupPopulation(
    DictLookup('template-dummy', DictTupleIndexing('subjectivity verb voice valency'.split())), 
    MultiKeyEvaluation('dummy-motion dummy-role dummy-subjectivity dummy-definiteness dummy-noun'.split()) 
)

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

tsv_parsing = SeparatedValuesFileParsing()

template_verb_whitelist = (
    template_verb_population.index(
        template_verb_annotation.annotate(
            tsv_parsing.rows('data/inflection/template-verbs.tsv')))
)

template_dummy_lookup = (
    template_dummy_population.index(
        template_dummy_annotation.annotate(
            tsv_parsing.rows('data/inflection/template-dummies.tsv')))
)

noun_template_whitelist = (
    noun_template_population.index(
        noun_template_annotation.annotate(
            tsv_parsing.rows('data/inflection/noun-template.tsv')))
)

template_tree_lookup = (
    template_tree_population.index(
        template_tree_annotation.annotate(
            tsv_parsing.rows('data/inflection/template-trees.tsv')))
)

case_usage_annotation = CellAnnotation('case', dict_bundle_to_map(case_episemaxis_to_episemes), {0:'column'}, {}, {})
case_usage_population = NestedLookupPopulation(
    DefaultDictLookup('case-usage', 
        DictTupleIndexing(
            'valency subjectivity motion role'.split(),
            case_episemaxis_to_episemes,
        ),
        lambda dictkey: DictLookup('grammatical-case-columns',
            DictKeyIndexing('column'))),
    KeyEvaluation('case')
)

mood_usage_annotation = CellAnnotation('mood', dict_bundle_to_map(mood_episemaxis_to_episemes), {0:'column'}, {}, {}, debug=True)
mood_usage_population = NestedLookupPopulation(
    DefaultDictLookup('mood-usage', 
        DictTupleIndexing(
            [key for key in mood_episemaxis_to_episemes.keys()],
            mood_episemaxis_to_episemes,
        ),
        lambda dictkey: DictLookup('grammatical-mood-columns',
            DictKeyIndexing('column'))),
    KeyEvaluation('mood')
)

aspect_usage_annotation = CellAnnotation('aspect', dict_bundle_to_map(aspect_episemaxis_to_episemes), {0:'column'}, {}, {})
aspect_usage_population = NestedLookupPopulation(
    DefaultDictLookup('aspect-usage', 
        DictTupleIndexing(
            [key for key in aspect_episemaxis_to_episemes.keys()],
            aspect_episemaxis_to_episemes,
        ),
        lambda dictkey: DictLookup('grammatical-aspect-columns',
            DictKeyIndexing('column'))),
    KeyEvaluation('aspect'),
    # debug=True
)

nouns_to_depictions = {
    'animal':'cow',
    'thing':'bolt',
    'phenomenon': 'eruption',
};

LanguageSpecificTextDemonstration = TextDemonstration(
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/indo-european/english/modern/mood-templates.tsv'))),
    TermLabelEditing(),
    TermLabelFiltering(),
    ListParsing(), 
    ListTools()
)

LanguageSpecificEmojiDemonstration = EmojiDemonstration(
    nouns_to_depictions,
    emoji_noun_adjective_population.index(
        emoji_noun_adjective_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/noun-adjectives.tsv'))),
    emoji_noun_verb_population.index(
        emoji_noun_verb_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/noun-verbs.tsv'))),
    emoji_noun_declensions_population.index(
        emoji_noun_declensions_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/noun-declensions.tsv'))),
    emoji_noun_population.index(
        common_noun_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/nouns.tsv'))),
    emoji_verb_population.index(
        emoji_verb_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/verbs.tsv'))),
    mood_population.index(
        mood_annotation.annotate(
            tsv_parsing.rows('data/inflection/emoji/moods.tsv'))),
    TermLabelEditing(),
    TermLabelFiltering(),
    emoji_shorthand, 
    HtmlTenseTransform(), 
    HtmlProgressTransform(), 
)

def write(filename, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(f'{row}\n')

def has_annotation(key, value):
    def _has_annotation(annotation):
        return key in annotation and annotation[key] == value or value in annotation[key]
    return _has_annotation

def replace(replacements):
    def _replace(content):
        for replaced, replacement in replacements:
            content = content.replace(replaced, replacement)
        return content
    return _replace

class RegularEnglishGrammar:
    def __init__(self):
        self.plural_regex = [
            (r"(?i)(ous)$", r'ous'),
            (r"(?i)(man)$", r'men'),
            (r"(?i)(quiz)$", r'\1zes'),
            (r"(?i)^(oxen)$", r'\1'),
            (r"(?i)^(ox)$", r'\1en'),
            (r"(?i)(m|l)ice$", r'\1ice'),
            (r"(?i)(m|l)ouse$", r'\1ice'),
            (r"(?i)(passer)s?by$", r'\1sby'),
            (r"(?i)(matr|vert|ind)(?:ix|ex)$", r'\1ices'),
            (r"(?i)(x|ch|ss|sh)$", r'\1es'),
            (r"(?i)([^aeiouy]|qu)y$", r'\1ies'),
            (r"(?i)(hive)$", r'\1s'),
            (r"(?i)([lr])f$", r'\1ves'),
            (r"(?i)(staff)$", r'staves'),
            (r"(?i)([^f])fe$", r'\1ves'),
            (r"(?i)sis$", 'ses'),
            (r"(?i)([ti])a$", r'\1a'),
            (r"(?i)([ti])um$", r'\1a'),
            (r"(?i)(buffal|potat|tomat)o$", r'\1oes'),
            (r"(?i)(bu)s$", r'\1ses'),
            (r"(?i)(alias|status)$", r'\1es'),
            (r"(?i)(octop|vir)i$", r'\1i'),
            (r"(?i)(octop|vir)us$", r'\1i'),
            (r"(?i)^(ax|test)is$", r'\1es'),
            (r"(?i)s$", r's'),
            (r"$", r's'),
        ]
        self.uncountables = set('''
            equipment jeans money rice series sheep 
            species information food livestock English'''.split())
        self.irregular_plurals =[
            ('staff', 'staves'),
            ('tooth', 'teeth'),
            ('person', 'people'),
            ('human', 'humans'),
            ('child', 'children'),
            ('move', 'moves'),
            ('zombie', 'zombies'),
            ('sex', 'sexes'),
            ('phenomenon', 'phenomena'),
            ('datum', 'data'),
            ('goose', 'geese'),
        ]
        self.singular_third_regex = [
            (r"(?i)([^aeiouy])y$", r'\1ies'),
            (r"(?i)([zs])$", r'\1es'),
            (r"$", r's'),
        ]
        self.perfective_regex = [
            (r"(?i)ay$", r'aid'),
            (r"(?i)([^aeiou])y$", r'\1ied'),
            (r"(?i)([^aeiouyw])$", r'\1ed'),
            (r"$", r'd'),
        ]
        self.imperfective_regex = [
            (r"(?i)e$", r'ing'),
            (r"$", r'ing'),
        ]
    def plural_noun(self, noun):
        if noun in self.uncountables:
            return noun
        if noun in self.irregular_plurals:
            return self.irregular_plurals[noun]
        for replaced, replacement in self.plural_regex:
            if re.search(replaced, noun):
                return re.sub(replaced, replacement, noun)
    def singular_third_verb(self, verb):
        for replaced, replacement in self.singular_third_regex:
            if re.search(replaced, verb):
                return re.sub(replaced, replacement, verb)
    def perfective_verb(self, verb):
        for replaced, replacement in self.perfective_regex:
            if re.search(replaced, verb):
                return re.sub(replaced, replacement, verb)
    def imperfective_verb(self, verb):
        for replaced, replacement in self.imperfective_regex:
            if re.search(replaced, verb):
                return re.sub(replaced, replacement, verb)
    def decline(self, tags):
        is_plural = tags['number']!='singular'
        is_possessive = tags['case']=='possessive'
        noun = tags['noun']
        noun = noun if not is_plural else self.plural_noun(noun)
        noun = noun if not is_possessive else noun+"'" if noun.endswith("s") and is_plural else noun+"'s"
        return noun
    def conjugate(self, tags):
        verb = tags['verb']
        if tags['aspect']=='imperfective':
            return self.imperfective_verb(verb)
        if tags['tense']=='past' or tags['aspect']=='perfective':
            return self.perfective_verb(verb)
        if tags['number']=='singular' and tags['person']=='3':
            return self.singular_third_verb(verb)
        return verb
    def agree(self, tags):
        return tags['noun']#lol

class EnglishListSubstitution:
    def __init__(self):
        pass
    def verbform(self, machine, tree, memory):
        '''same as self.inflection.conjugate(), but creates auxillary verb phrases when conjugation of a single verb is insufficient'''
        form = memory['verb-form']
        tense = memory['tense']
        voice = memory['voice']
        if form  == 'participle': 
            return [['stock-adposition','that'], 'finite', tree]
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
        tense = memory['tense']
        duration = memory['duration']
        progress = memory['progress']
        consistency = memory['consistency']
        ordinality = memory['ordinality']
        persistence = memory['persistence']
        recency = memory['recency']
        trajectory = memory['trajectory']
        distribution = memory['distribution']
        preverb = []
        postverb = []
        if duration == 'protracted':
            postverb.append('[on and on]')
        if duration == 'indeterminate':
            postverb.append('[on and on endlessly]')
        if progress == 'unfinished':
            postverb.append('[still unfinished]')
        if ordinality == 'ordinal':
            postverb.append('[as part of a larger event]')
        if persistence == 'impermanent':
            postverb.append('[that changed things a while after]')
        if persistence == 'persistant':
            postverb.append('[that changed things]')
        postverb.append({
            ('recent',    'past'):    '[just recently]',
            ('recent',    'present'): '[just now]',
            ('recent',    'future'):  '[not long from now]',
            ('nonrecent', 'past'):    '[long ago]',
            ('nonrecent', 'present'): '',
            ('nonrecent', 'future'):  '[long from now]',
            ('arecent',   'past'):    '',
            ('arecent',   'present'): '',
            ('arecent',   'future'):  '',
        }[recency, tense])
        postverb.append({
            'rectilinear':    '[in a straight line]',
            'reversing':      '[reversing previous direction]',
            'returning':      '[returning to the start]',
            'motionless':     '[motionless]',
            'directionless':  '',
        }[trajectory])
        postverb.append({
            'centralized':     '[together]',
            'decentralized':   '[coming apart]',
            'undistributed':   '',
        }[distribution])
        preverb.append({
            'incessant': '[incessantly]',
            'habitual':  '[habitually]',
            'customary': '[customarily]',
            'frequent':  '[frequently]',
            'experiential':'',
            'momentary':  '',
        }[consistency])
        if progress in {'paused', 'resumed', 'continued', 'arrested'}:
            aspect = progress
        elif consistency in {'experiential'}:
            aspect = consistency
        elif any([
                persistence in {'impermanent','persistant'},
                recency in {'recent'},
                progress in {'atomic', 'finished'},
                consistency in {'experiential'}]):
            aspect = 'perfective'
        elif progress in {'started', 'unfinished'}:
            if duration in {'brief'}:
                aspect = 'imperfective'
            else:
                aspect = 'perfective-progressive'
        else:
            aspect = 'simple'
        aspect_to_tree = {
            'arrested':               [['passive','simple', 'implicit', 'v', 'halt'], 'from', 'finite', ['unfinished', tree]],
            'paused':                 [['active', 'simple', 'implicit', 'v', 'pause'], 'finite', ['unfinished', tree]],
            'resumed':                [['active', 'simple', 'implicit', 'v', 'resume'], 'finite', ['unfinished', tree]],
            'continued':              [['active', 'simple', 'implicit', 'v', 'continue'], 'finite', ['unfinished', tree]],
            # 'finished':             [['active', 'simple', 'implicit', 'v', 'finish'], 'finite', ['unfinished', tree]],
            'experiential':           [['active', 'simple', 'implicit', 'v', 'experience'], 'finite', ['unfinished', tree]],
            'simple':                 tree,
            'perfective-progressive': [['active', 'simple', 'atelic', 'v', 'have'], 'finite', ['finished', 'v', 'be'], ['unfinished', tree]],
            'imperfective':           [['active', 'simple', 'atelic', 'v', 'be'],   'unfinished', 'finite', tree],
            'perfective':             [['active', 'simple', 'atelic', 'v', 'have'], 'finished', 'finite', tree],
        }
        # if (memory['verb'], progress, tense, memory['mood']) == ('go', 'finished', 'present', 'indicative'):
        #     breakpoint()
        return aspect_to_tree[aspect]
        # return [*preverb, *verb, *postverb]
    def voice(self, machine, tree, memory):
        '''creates auxillary verb phrases when necessary to express voice'''
        voice = memory['voice']
        if voice  == 'passive': return [['active', 'v', 'be'],             'finite', ['active', 'finished', tree]]
        if voice  == 'middle':  return [['active', 'implicit', 'v', 'be'], 'finite', ['active', 'finished', tree]]
        return tree
    def definiteness(self, machine, tree, memory):
        '''creates articles when necessary to express definiteness'''
        definiteness = memory['definiteness'] if 'definiteness' in memory else 'indefinite'
        subjectivity = memory['subjectivity']
        nounform = memory['noun-form']
        if definiteness == 'definite' and subjectivity != 'addressee' and nounform != 'personal': 
            return [['det','the'], tree]
        else:
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
rule_tools = RuleTools()
card_formatting = CardFormatting()
english_list_substitution = EnglishListSubstitution()
regular_english_grammar = RegularEnglishGrammar()

english_conjugation_template_lookups = DictLookup(
    'english-conjugation',
    DictKeyIndexing('verb-form'), 
    {
        'finite': parse_any.tokenfield('english-finite-verb', 'verb person number tense aspect'),
        'infinitive': parse_any.tokenfield('english-infinitive-verb', 'verb'),
    })

english_conjugation_population = NestedLookupPopulation(
    english_conjugation_template_lookups, 
    KeyEvaluation('inflection'))

english_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/english/modern/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/english/modern/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/english/modern/aspect-usage.tsv'))),
        # debug=True,
    ),
    ListGrammar(
        FallbackDictLookup(
            NestedDictLookup(
                english_conjugation_population.index([
                    *finite_annotation.annotate(
                        tsv_parsing.rows('data/inflection/indo-european/english/modern/irregular-conjugations.tsv')),
                    *finite_annotation.annotate(
                        tsv_parsing.rows('data/inflection/indo-european/english/modern/regular-conjugations.tsv')),
                ])),
            ProceduralLookup(regular_english_grammar.conjugate),
        ),
        FallbackDictLookup(
            NestedDictLookup(
                declension_population.index([
                    *pronoun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/indo-european/english/modern/pronoun-declensions.tsv')),
                    *common_noun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/indo-european/english/modern/common-noun-declensions.tsv')),
                ])),
            ProceduralLookup(regular_english_grammar.decline),
        ),
        FallbackDictLookup(
            NestedDictLookup(
                declension_population.index([
                    *possessive_pronoun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/indo-european/english/modern/pronoun-possessives.tsv')),
                ])
            ),
            ProceduralLookup(regular_english_grammar.agree),
        ),
        # debug=True,
    ),
    RuleSyntax(parse_any.terms('subject verb direct-object indirect-object modifier')),
    {'language-type':'native'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = [
        {'cloze': list_tools.unwrap()}, # English serves as a native language here, so it never shows clozes
        {'v': english_list_substitution.verbform}, # English participles are encoded as perfective/imperfective forms and must be handled specially
        {'v': english_list_substitution.mood},     # English uses auxillary verbs (e.g. "mood") to indicate some moods
        {'v': english_list_substitution.tense},    # English uses auxillary verbs ("will") to indicate tense
        {'v': english_list_substitution.aspect},   # English uses auxillary verbs ("be", "have") to indicate aspect
        {'v': english_list_substitution.voice},    # English uses auxillary verbs ("be") to indicate voice
        {'n': english_list_substitution.definiteness},         # English needs annotations to clarify the formalities and genders of other languages
        {'n': english_list_substitution.formality_and_gender}, # English needs annotations to clarify the formalities and genders of other languages
    ],
    # debug=True,
)

english_orthography = Orthography('latin', english_language)

english_demonstration = LanguageSpecificTextDemonstration(
    card_formatting.native_word, english_orthography)

emoji_casts = {
    1: [
            EmojiPerson('s','n',1),
            EmojiPerson('s','f',2),
            EmojiPerson('s','m',3),
            EmojiPerson('s','n',4),
            EmojiPerson('s','n',5),
        ],
    2: [
            EmojiPerson('s','n',2),
            EmojiPerson('s','f',3),
            EmojiPerson('s','m',1),
            EmojiPerson('s','n',4),
            EmojiPerson('s','n',5),
        ],
    3: [
            EmojiPerson('s','n',3),
            EmojiPerson('s','f',4),
            EmojiPerson('s','m',2),
            EmojiPerson('s','n',1),
            EmojiPerson('s','n',5),
        ],
    4: [
            EmojiPerson('s','n',4),
            EmojiPerson('s','f',3),
            EmojiPerson('s','m',5),
            EmojiPerson('s','n',2),
            EmojiPerson('s','n',1),
        ],
    5: [
            EmojiPerson('s','n',5),
            EmojiPerson('s','f',4),
            EmojiPerson('s','m',3),
            EmojiPerson('s','n',2),
            EmojiPerson('s','n',1),
        ],
}


tag_defaults = parse_any.termaxis_to_term('''
    valency:      transitive
    subjectivity: direct-object
    
    clitic:       tonic
    clusivity:    exclusive
    formality:    familiar
    gender:       masculine
    #noun:        man
    noun-form:    common
    number:       singular
    partitivity:  nonpartitive
    person:       3
    strength:     strong

    duration:     brief
    progress:     atelic
    consistency:  momentary
    ordinality:   nonordinal
    persistence:  static
    recency:      arecent
    trajectory:   directionless
    distribution: undistributed

    evidentiality:presumed
    confidence:   confident
    polarity:     positive
    mood:         indicative

    tense:        present 
    voice:        active
    completion:   bare

    verb-form:    finite
''')
