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
    case_episemaxis_to_episemes,
    tag_to_tagaxis,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    tag_defaults, write, 
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
        'progress': 'atelic started finished'.split(),
        'tense':    'present past future'.split(),
        'voice':    'active passive'.split(),
        'mood':     'indicative subjunctive imperative'.split(),
        'verb':     '''be be-able want become go
                    carry eat love advise
                    capture hear'''.split(),
        'role':     '''agent addressee patient 
                    location possessor interior surface presence 
                    aid lack interest time company'''.split(),
    }.items()
}

constant = {
    tag: DictSpace(tag, DictTupleIndexing([axis]), {axis: tag})
    for (tag, axis) in tag_to_tagaxis.items()
}

noun_gender_whitelist = DictSet(
    'noun_gender_whitelist', 
    DictTupleIndexing('noun gender'.split()),
    sequence = [
        ('man',        'masculine'),
        ('day',        'neuter'),
        ('hand',       'neuter'),
        ('night',      'feminine'),
        ('thing',      'feminine'),
        ('name',       'neuter'),
        ('son',        'masculine'),
        ('war',        'masculine'),
        ('air',        'masculine'),
        ('boy',        'masculine'),
        ('animal',     'neuter'),
        ('star',       'feminine'),
        ('tower',      'feminine'),
        ('horn',       'neuter'),
        ('sailor',     'masculine'),
        ('foundation', 'feminine'),
        ('echo',       'neuter'),
        ('phenomenon', 'neuter'),
        ('vine',       'feminine'),
        ('myth',       'masculine'),
        ('atom',       'feminine'),
        ('nymph',      'feminine'),
        ('comet',      'masculine'),
    ])

tense_mood_whitelist = DictSet(
    'tense_mood_whitelist', 
    DictTupleIndexing('tense mood'.split()),
    sequence = [
        ('present', 'indicative' ),
        ('past',    'indicative' ),
        ('future',  'indicative' ),
        ('present', 'subjunctive'),
        ('past',    'subjunctive'),
        ('present', 'imperative' ),
        ('future',  'imperative' ),
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

finite_tense_progress_whitelist = DictSet(
    'finite_tense_progress_whitelist', 
    DictTupleIndexing('tense progress'.split()),
    sequence = [
        ('present', 'atelic'),
        ('present', 'finished'),
        ('future',  'atelic'),
        ('future',  'finished'),
        ('past',    'unfinished'),
        ('past',    'finished'),
    ])

nonfinite_tense_progress_whitelist = DictSet(
    'nonfinite_tense_progress_whitelist', 
    DictTupleIndexing('tense progress'.split()),
    sequence = [
        ('present', 'atelic'),
        ('future',  'atelic'),
        ('past',    'finished'),
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
    DictTupleIndexing('verb voice'.split()),
    sequence = [
        ('be',      'passive'),
        ('be-able', 'passive'),
        ('want',    'passive'),
        ('become',  'passive'),
    ])

verb_default_whitelist = axis['progress'] | axis['tense'] | axis['voice'] | axis['mood'] | axis['verb']

conjugation_whitelist = (
    (verb_default_whitelist & tense_mood_whitelist & voice_progress_whitelist) 
    - verb_progress_blacklist - verb_mood_blacklist - verb_voice_blacklist)

subjectivity_role_blacklist = DictSet(
    'subjectivity_role_blacklist', 
    DictTupleIndexing('subjectivity role'.split()),
    sequence = [
        ('direct-object', 'addressee'),
        ('direct-object', 'agent'),
        ('direct-object', 'force'),
        ('subject', 'patient'),
        ('subject', 'theme'),
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

default_conjugation = DictSpace(
    'default_conjugation',
    DictTupleIndexing([]),
    {
        'duration':     'brief',
        'progress':     'atelic',
        'consistency':  'momentary',
        'ordinality':   'nonordinal',
        'persistence':  'static',
        'recency':      'arecent',
        'trajectory':   'directionless',
        'distribution': 'undistributed',

        'evidentiality':'presumed',
        'confidence':   'confident',
        'polarity':     'positive',
        'mood':         'indicative',

        'tense':        'present', 
        'voice':        'active',
        'completion':   'bare',
    }
)

default_declension = DictSpace(
    'default_declension',
    DictTupleIndexing([]),
    {
        'valency':      'transitive',
        'subjectivity': 'direct-object',
        
        'clitic':       'tonic',
        'clusivity':    'exclusive',
        'formality':    'familiar',
        'gender':       'masculine',
        'noun':         'man',
        'number':       'singular',
        'partitivity':  'nonpartitive',
        'person':       '3',
        'strength':     'strong',
    }
)

defaults = DictSpace(
    'defaults',
    DictTupleIndexing([]),
    tag_defaults
)


declension_whitelist = (subjectivity_motion_whitelist | axis['role'] | default_conjugation) - subjectivity_role_blacklist

adposition_whitelist = DictSpace('adposition_whitelist', DictTupleIndexing(['subjectivity']), {'subjectivity': 'modifier',})

gender_whitelist = DictSet(
    'gender_whitelist', 
    DictTupleIndexing('gender noun'.split()),
    sequence = [
        ('masculine', 'man'   ),
        ('feminine',  'woman' ),
        ('neuter',    'animal'),
        ('neuter',    'snake' ),
    ])

finite_conjugation_pronoun_whitelist = DictSet(
    'finite_conjugation_pronoun_whitelist', 
    DictTupleIndexing('noun person number gender'.split()),
    sequence = [
        ('man', '1', 'singular', 'neuter'),
        ('woman', '2', 'singular', 'feminine'),
        ('man', '3', 'singular', 'masculine'),
        ('man', '1', 'plural',   'neuter'),
        ('woman', '2', 'plural',   'feminine'),
        ('man', '3', 'plural',   'masculine'),
    ])

nonfinite_pronoun_whitelist = DictSet(
    'nonfinite_pronoun_whitelist', 
    DictTupleIndexing('noun person number gender'.split()),
    sequence = [
        ('man', '3', 'singular', 'masculine'),
    ])

declension_pronoun_whitelist = DictSet(
    'declension_pronoun_whitelist', 
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

possession_whitelist = DictSet(
    'possession_whitelist', 
    DictTupleIndexing(['possessor-noun', 'gender', 'noun']),
    sequence = [
        ('man',   'masculine', 'son'      ),
        ('man',   'feminine',  'daughter' ),
        ('man',   'neuter',    'livestock'),
        ('woman', 'masculine', 'son'      ),
        ('woman', 'feminine',  'daughter' ),
        ('woman', 'neuter',    'livestock'),
        ('snake', 'masculine', 'son'      ),
        ('snake', 'feminine',  'daughter' ),
        ('snake', 'neuter',    'name'     ),
    ])

possessor_pronoun_whitelist = DictSet(
    'possesor_pronoun_whitelist', 
    DictTupleIndexing(['possessor-noun', 'possessor-person', 'possessor-number', 'possessor-gender']),
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

# breakpoint()

write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = foreign_language.grammar.stock_modifier,
            # default_tree = 'clause test [np the n man] [vp conjugated] [modifier np test stock-modifier]',
            default_tree = 'clause [test subject [np the n man] [vp conjugated]] [test modifier np stock-modifier]',
        ) for demonstration in demonstrations],
        defaults.update(
            finite_conjugation_pronoun_whitelist & 
            conjugation_whitelist & 
            finite_tense_progress_whitelist &
            constant['finite']
        ),
    ))

write('flashcards/latin/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.update(
            noun_gender_whitelist &
            declension_whitelist &
            axis['number'] &
            constant['finite']
        ),
        tag_templates = {
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.update(
            declension_whitelist & 
            declension_pronoun_whitelist &
            constant['finite']
        ),
        tag_templates ={
            'dummy'      : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/adpositions.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', 'n', 'noun'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.update(
            declension_whitelist & 
            adposition_whitelist & 
            constant['finite']
        ),
        tag_templates ={
            'dummy'      : {'noun':'man', 'noun-form':'personal', 'person':'3', 'number':'singular'},
            'test'       : {'noun':'man', 'noun-form':'common'},
            'emoji'      : {'noun':'man', 'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
        ) for demonstration in demonstrations], 
        defaults.update(
            declension_whitelist & 
            gender_whitelist & 
            axis['adjective'] & 
            axis['number'] & 
            constant['finite']
        ),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])},
            ],
        ) for demonstration in demonstrations],
        defaults.update(
            declension_whitelist & 
            possession_whitelist & 
            possessor_pronoun_whitelist & 
            axis['number'] & 
            constant['finite']
        ),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal-possessive'},
            'emoji'      : {'person':'4'},
        },
    ))

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
                # default_tree = 'clause [test subject [np the n man] [infinitive vp conjugated]] [modifier test np stock-modifier]',
                default_tree = 'clause [speaker subject [vp v figure]] [modifier np clause [test subject [np the n man] [infinitive vp conjugated]]] [test modifier np stock-modifier]',
            ),
            english_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test subject [np the n man] [vp conjugated]] [modifier np test stock-modifier]',
                default_tree = 'clause [speaker subject [np the n man] [vp v figure]] [modifier np clause [test subject [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
        ],
        defaults.update(
            nonfinite_pronoun_whitelist & 
            conjugation_whitelist & 
            nonfinite_tense_progress_whitelist &
            constant['infinitive']
        ),
    ))


write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle', 'cloze', 'v','verb'], ['modifier', 'np', 'participle', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        defaults.update(
            conjugation_whitelist & 
            declension_whitelist & 
            nonfinite_tense_progress_whitelist &
            constant['participle']
        ),
        tag_templates ={
            'dummy'      : {'noun':'man', 'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun':'man', 'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun':'man', 'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',},
            'emoji'      : {'noun':'man', 'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common', 'person':'4'},
            'participle' : {'noun':'man', 'case':'nominative'},
        },
    ))
