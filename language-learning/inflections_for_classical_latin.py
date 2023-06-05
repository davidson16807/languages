import time

start_time = time.time()

from tools.lookup import DictSet, DictSpace
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.cards import DeckGeneration
from tools.languages import Language
from tools.orthography import Orthography
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleSyntax, RuleFormatting, 
)
from inflections import (
    LanguageSpecificTextDemonstration, LanguageSpecificEmojiDemonstration, english_demonstration,
    card_formatting,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    tag_to_tagaxis,
    episemes_to_case_episemaxis,
    episemes_to_mood_episemaxis,
    episemes_to_aspect_episemaxis,
    tag_defaults, 
    write, 
    emoji_casts
)

deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/aspect-usage.tsv'))),
    ),
    ListGrammar(
        conjugation_population.index([
            *finite_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/finite-conjugations.tsv')),
            *nonfinite_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/nonfinite-conjugations.tsv')),
            *filter(has_annotation('language','classical-latin'),
                declension_verb_annotation.annotate(
                    tsv_parsing.rows(
                        'data/inflection/declension-template-verbs-minimal.tsv'))),
        ]),
        declension_population.index([
            *pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/pronoun-declensions.tsv')),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/common-noun-declensions.tsv')),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/adjective-agreement.tsv')),
            *possessive_pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/pronoun-possessives.tsv')),
            *filter(has_annotation('language','classical-latin'),
                declension_template_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'))),
        ]),
    ),
    RuleSyntax('subject modifier indirect-object direct-object verb'.split()),
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = []
)

foreign_demonstration = LanguageSpecificTextDemonstration(
    card_formatting.foreign_focus,
    Orthography('latin', foreign_language),
)

emoji_demonstration = LanguageSpecificEmojiDemonstration(
    card_formatting.emoji_focus,
    foreign_language.grammar.conjugation_lookups['argument'], 
    emoji_casts[3])

demonstrations = [
    emoji_demonstration,
    foreign_demonstration,
    english_demonstration,
]


axis = {
    axis: DictSpace(axis, DictTupleIndexing([axis]), {axis: tags})
    for (axis, tags) in {
        'gender' :  'masculine feminine neuter'.split(),
        'number' :  'singular plural'.split(),
        'motion' :  'associated departed acquired leveraged'.split(),
        'noun'   :  '''man day hand night thing name son war
                    air boy animal star tower horn sailor foundation
                    echo phenomenon vine myth atom nymph comet'''.split(),
        'adjective':'tall holy poor mean old nimble swift jovial'.split(),
        'progress': 'atelic unfinished finished'.split(),
        'tense':    'present past future'.split(),
        'voice':    'active passive'.split(),
        'mood':     'indicative subjunctive imperative'.split(),
        'verb':     '''be be-able want become go
                    carry eat love advise
                    capture hear'''.split(),
        'role':     '''agent patient 
                    location possessor interior surface presence 
                    aid lack interest time company'''.split(),
        'subjectivity': 'addressee subject direct-object indirect-object modifier'.split()
    }.items()
}

constant = {
    tag: DictSpace(tag, DictTupleIndexing([axis]), {axis: tag})
    for (tag, axis) in {
        **tag_to_tagaxis,
        **episemes_to_case_episemaxis,
        **episemes_to_mood_episemaxis,
        **episemes_to_aspect_episemaxis}.items()
}

defaults = DictSpace(
    'defaults',
    DictTupleIndexing([]),
    tag_defaults
)

genders = 'masculine feminine neuter'.split()
numbers = 'singular plural'.split()
verbs = '''be be-able want become go
           carry eat love advise
           capture hear'''.split()
roles = 'agent addressee patient location possessor interior surface presence aid lack interest time company'.split()
motions = 'associated departed acquired leveraged'.split()
nouns = '''man day hand night thing name son war
           air boy animal star tower horn sailor foundation
           echo phenomenon vine myth atom nymph comet'''.split()
adjectives = 'tall holy poor mean old nimble swift jovial'.split()
progress = 'atelic unfinished finished'.split()
moods = 'indicative subjunctive imperative'.split()
tenses = 'present past future'.split()
voices = 'active passive'.split()
subjectivity = 'addressee subject direct-object indirect-object modifier'.split()

subjectivity_role_blacklist = DictSet(
    'subjectivity_role_blacklist', 
    DictTupleIndexing('subjectivity role'.split()),
    sequence = [
        ('subject',       'audience'),
        ('subject',       'patient'),
        ('direct-object', 'agent'),
    ])

subjectivity_motion_whitelist = DictSet(
    'subjectivity_motion_whitelist', 
    DictTupleIndexing('subjectivity motion'.split()),
    sequence = [
        ('subject',  'associated'),
        ('direct-object', 'associated'),
        ('addressee', 'associated'),
        ('modifier', 'departed'),
        ('modifier', 'associated'),
        ('modifier', 'approached'),
        ('modifier', 'acquired'),
        ('modifier', 'surpassed'),
        ('modifier', 'leveraged'),
    ])

conjugation_subject_traversal = DictSet(
    'conjugation_subject_traversal', 
    DictTupleIndexing('person number gender'.split()),
    sequence = [
        ('1', 'singular', 'neuter'),
        ('2', 'singular', 'feminine'),
        ('3', 'singular', 'masculine'),
        ('1', 'plural',   'neuter'),
        ('2', 'plural',   'feminine'),
        ('3', 'plural',   'masculine'),
    ])

mood_tense_whitelist = DictSet(
    'mood_tense_whitelist', 
    DictTupleIndexing('mood tense'.split()),
    sequence = [
        ('indicative',  'present'),
        ('indicative',  'past'),
        ('indicative',  'future'),
        ('subjunctive', 'present'),
        ('subjunctive', 'past'),
        ('imperative',  'present'),
        ('imperative',  'future'),
    ])

finite_tense_progress_whitelist = DictSet(
    'finite_tense_progress_whitelist', 
    DictTupleIndexing('tense progress'.split()),
    sequence = [
        ('present', 'atelic'),
        ('future',  'atelic'),
        ('past',    'unfinished'),
        ('past',    'finished'),
        ('present', 'finished'),
        ('future',  'finished'),
    ])

voice_progress_whitelist = DictSet(
    'voice_progress_whitelist', 
    DictTupleIndexing('voice progress'.split()),
    sequence = [
        ('active',  'atelic'),
        ('active',  'unfinished'),
        ('active',  'finished'),
        ('passive', 'atelic'),
        ('passive', 'unfinished'),
    ])

verb_progress_blacklist = DictSet(
    'verb_progress_blacklist', 
    DictTupleIndexing('verb progress'.split()),
    sequence = [
        ('become', 'finished'),
    ])

verb_mood_blacklist = DictSet(
    'verb_mood_blacklist', 
    DictTupleIndexing('verb mood'.split()),
    sequence = [
        ('be-able', 'imperative'),
    ])

verb_voice_blacklist = DictSet(
    'verb_voice_blacklist', 
    DictTupleIndexing('verb  voice'.split()),
    sequence = [
        ('be',      'passive'),
        ('be-able', 'passive'),
        ('want',    'passive'),
        ('become',  'passive'),
    ])

declension_pronoun_traversal = DictSet(
    'declension_pronoun_traversal', 
    DictTupleIndexing('noun person number gender'.split()),
    sequence = [
        ('man',   '1', 'singular', 'neuter'   ),
        ('woman', '2', 'singular', 'feminine' ),
        ('man',   '3', 'singular', 'masculine'),
        ('woman', '3', 'singular', 'feminine' ),
        ('snake', '3', 'singular', 'neuter'   ),
        ('man',   '1', 'plural',   'neuter'   ),
        ('woman', '2', 'plural',   'feminine' ),
        ('man',   '3', 'plural',   'masculine'),
        ('woman', '3', 'plural',   'feminine' ),
        ('man',   '3', 'plural',   'neuter'   ),
    ])

gender_agreement_whitelist = DictSet(
    'gender_agreement_whitelist', 
    DictTupleIndexing('gender noun'.split()),
    sequence = [
        ('masculine', 'man'   ),
        ('feminine',  'woman' ),
        ('neuter',    'animal'),
    ])

nonfinite_tense_progress_whitelist = DictSet(
    'nonfinite_tense_progress_whitelist', 
    DictTupleIndexing('tense progress'.split()),
    sequence = [
        ('present', 'atelic'),
        ('past',    'finished'),
        ('future',  'atelic'),
    ])

possession_traversal = DictSet(
    'possession_traversal', 
    DictTupleIndexing('gender noun'.split()),
    sequence = [
        ('masculine', 'son'      ),
        ('feminine',  'daughter' ),
        ('neuter',    'livestock'),
        ('neuter',    'name'     ),
    ])


possessor_possession_whitelist = DictSet(
    'possessor_pronoun_whitelist', 
    DictTupleIndexing('possessor-noun noun'.split()),
    sequence = [
        ('man',   'son'),
        ('man',   'daughter'),
        ('man',   'livestock'),
        ('woman', 'son'),
        ('woman', 'daughter'),
        ('woman', 'livestock'),
        ('animal','son'),
        ('animal','daughter'),
        ('animal','name'),
    ])


possessor_pronoun_whitelist = DictSet(
    'possessor_pronoun_whitelist', 
    DictTupleIndexing('possessor-noun possessor-person possessor-number possessor-gender'.split()),
    sequence = [
        ('man',   '1st-possessor', 'singular-possessor', 'neuter-possessor'   ),
        ('woman', '2nd-possessor', 'singular-possessor', 'feminine-possessor' ),
        ('man',   '3rd-possessor', 'singular-possessor', 'masculine-possessor'),
        ('woman', '3rd-possessor', 'singular-possessor', 'feminine-possessor' ),
        ('snake', '3rd-possessor', 'singular-possessor', 'neuter-possessor'   ),
        ('man',   '1st-possessor', 'plural-possessor',   'neuter-possessor'   ),
        ('woman', '2nd-possessor', 'plural-possessor',   'feminine-possessor' ),
        ('man',   '3rd-possessor', 'plural-possessor',   'masculine-possessor'),
        ('woman', '3rd-possessor', 'plural-possessor',   'feminine-possessor' ),
        ('man',   '3rd-possessor', 'plural-possessor',   'neuter-possessor'   ),
    ])

tense_progress_mood_voice_verb_traversal = (
    (((((finite_tense_progress_whitelist
        * axis['mood'])
        & mood_tense_whitelist) 
        * axis['voice'])
        & voice_progress_whitelist) 
        * axis['verb'])
    - verb_progress_blacklist
    - verb_mood_blacklist
    - verb_voice_blacklist
)

conjugation_subject_defaults = (
    constant['subject'] * 
    constant['agent'] * 
    constant['associated'] * 
    constant['transitive'] * 
    constant['finite']
)

print('flashcards/latin/finite-conjugation.html')
write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = foreign_language.grammar.stock_modifier,
            # default_tree = 'clause test [np the n man] [vp conjugated] [modifier np test stock-modifier]',
            default_tree = 'clause [test [np the n man] [vp conjugated]] [test modifier np stock-modifier]',
        ) for demonstration in demonstrations],
        defaults.override(
              conjugation_subject_traversal 
            * tense_progress_mood_voice_verb_traversal 
            * conjugation_subject_defaults 
            * constant['personal']
        ),
    ))

print('flashcards/latin/nonfinite-conjugation.html')
write('flashcards/latin/nonfinite-conjugation.html', 
    deck_generation.generate(
        [
            emoji_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
            ),
            foreign_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test [np the n man] [infinitive vp conjugated]] [modifier test np stock-modifier]',
                default_tree = 'clause [finite speaker [vp v figure]] [modifier np clause [test [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
            english_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test [np the n man] [vp conjugated]] [modifier np test stock-modifier]',
                default_tree = 'clause [finite speaker [np the n man] [vp v figure]] [modifier np clause [test [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
        ],
        defaults.override(
            ((tense_progress_mood_voice_verb_traversal 
                & nonfinite_tense_progress_whitelist) 
                - constant['imperative'])
            * conjugation_subject_defaults
            * constant['infinitive']
            * constant['personal']
        ) 
    ))

print('flashcards/latin/participle-declension.html')
write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle', 'cloze', 'v','verb'], ['modifier', 'np', 'participle', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        # defaults.override(
        #     ((tense_progress_mood_voice_verb_traversal 
        #         & nonfinite_tense_progress_whitelist) - constant['unfinished'])
        #     * constant['indicative']
        #     * constant['participle']
        #     * constant['common']
        # ),
        defaults.override(
            DictSpace(
                'traversal',
                DictTupleIndexing(
                        '''tense progress mood voice verb'''.split()),
                    {
                        **tag_defaults,
                        'verb':        verbs,
                        'tense':       tenses, 
                        'voice':       voices,
                        'progress':    ['atelic','finished'], 
                        'valency':     'transitive',
                        'subjectivity':'subject',
                        'motion':      'associated',
                        'role':        'agent',
                        'animacy':     'thing',
                        'verb-form':   'participle',
                    }) 
            & nonfinite_tense_progress_whitelist
        ),
        tag_templates ={
            'dummy'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',},
            'emoji'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common', 'person':'4'},
            'participle' : {'case':'nominative'},
        },
    ))

subjectivity_motion_role_traversal = (
    ((axis['subjectivity'] * axis['motion'] * axis['role']) 
        & subjectivity_motion_whitelist)
    - subjectivity_role_blacklist
)

print('flashcards/latin/adpositions.html')
write('flashcards/latin/adpositions.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', 'n', 'noun'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.override(subjectivity_motion_role_traversal & constant['modifier']),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))


print('flashcards/latin/common-noun-declension.html')
write('flashcards/latin/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.override(axis['number'] * subjectivity_motion_role_traversal * axis['noun']),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

print('flashcards/latin/pronoun-declension.html')
write('flashcards/latin/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.override(declension_pronoun_traversal * subjectivity_motion_role_traversal * constant['personal']),
        tag_templates ={
            'dummy'      : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

print('flashcards/latin/adjective-agreement.html')
write('flashcards/latin/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
        ) for demonstration in demonstrations], 
        defaults.override(axis['number'] * gender_agreement_whitelist * subjectivity_motion_role_traversal * axis['adjective']),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

print('flashcards/latin/pronoun-possessives.html')
write('flashcards/latin/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            ((axis['number'] * possession_traversal * subjectivity_motion_role_traversal * possessor_pronoun_whitelist) 
                & possessor_possession_whitelist) *
            constant['exclusive-possessor'] * 
            constant['familiar-possessor'] ),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal-possessive'},
            'emoji'      : {'person':'4'},
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')