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
progress = 'atelic started finished'.split()
moods = 'indicative subjunctive imperative'.split()
tenses = 'present past future'.split()
voices = 'active passive'.split()
subjectivity = 'addressee subject direct-object indirect-object modifier'.split()

subjectivity_role_blacklist = DictSet(
    'subjectivity role filter', 
    DictTupleIndexing('subjectivity  role'.split()),
    content = {
        ('subject',       'audience'),
        ('subject',       'patient'),
        ('direct-object', 'agent'),
    })

subjectivity_motion_whitelist = DictSet(
    'subjectivity motion filter', 
    DictTupleIndexing('subjectivity  motion'.split()),
    content = {
        ('subject',  'associated'),
        ('direct-object', 'associated'),
        ('addressee', 'associated'),
        ('modifier', 'departed'),
        ('modifier', 'associated'),
        ('modifier', 'approached'),
        ('modifier', 'acquired'),
        ('modifier', 'surpassed'),
        ('modifier', 'leveraged'),
    })

pronoun_whitelist = DictSet(
    'pronoun filter', 
    DictTupleIndexing('person number gender'.split()),
    content = {
        ('1', 'singular', 'neuter'),
        ('2', 'singular', 'feminine'),
        ('3', 'singular', 'masculine'),
        ('1', 'plural',   'neuter'),
        ('2', 'plural',   'feminine'),
        ('3', 'plural',   'masculine'),
    })

mood_tense_whitelist = DictSet(
    'mood tense filter', 
    DictTupleIndexing('mood tense'.split()),
    content = {
        ('indicative',  'present'),
        ('indicative',  'past'),
        ('indicative',  'future'),
        ('subjunctive', 'present'),
        ('subjunctive', 'past'),
        ('imperative',  'present'),
        ('imperative',  'future'),
    })


finite_tense_progress_whitelist = DictSet(
    'finite_tense_progress_whitelist', 
    DictTupleIndexing(['tense', 'progress']),
    content = {
        ('present', 'atelic'),
        ('present', 'finished'),
        ('future',  'atelic'),
        ('future',  'finished'),
        ('past',    'unfinished'),
        ('past',    'finished'),
    })

voice_progress_whitelist = DictSet(
    'voice progress', 
    DictTupleIndexing(['voice','progress']),
    content = {
        ('active',  'atelic'),
        ('active',  'unfinished'),
        ('active',  'finished'),
        ('passive', 'atelic'),
        ('passive', 'unfinished'),
    })

verb_progress_blacklist = DictSet(
    'verb_progress_blacklist', 
    DictTupleIndexing(['verb','progress']),
    content = {
        ('become', 'finished'),
    })

verb_mood_blacklist = DictSet(
    'verb_mood_blacklist', 
    DictTupleIndexing(['verb','mood']),
    content = {
        ('be-able', 'imperative'),
    })

verb_voice_blacklist = DictSet(
    'verb_voice_blacklist', 
    DictTupleIndexing('verb  voice'.split()),
    content = {
        ('be',      'passive'),
        ('be-able', 'passive'),
        ('want',    'passive'),
        ('become',  'passive'),
    })

declension_pronoun_whitelist = DictSet(
    'pronoun filter', 
    DictTupleIndexing(['noun', 'person', 'number', 'gender']),
    content = {
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
    })

gender_agreement_whitelist = DictSet(
    'adjective agreement noun filter', 
    DictTupleIndexing(['gender', 'noun']),
    content = {
        ('masculine', 'man'   ),
        ('feminine',  'woman' ),
        ('neuter',    'animal'),
    })

nonfinite_tense_progress_whitelist = DictSet(
    'nonfinite_tense_progress_whitelist', 
    DictTupleIndexing(['tense', 'progress']),
    content = {
        ('present', 'atelic'),
        ('future',  'atelic'),
        ('past',    'finished'),
    })

possession_whitelist = DictSet(
    'possession_whitelist', 
    DictTupleIndexing(['possessor-noun', 'gender', 'noun']),
    content = {
        ('man',   'masculine', 'son'      ),
        ('man',   'feminine',  'daughter' ),
        ('man',   'neuter',    'livestock'),
        ('woman', 'masculine', 'son'      ),
        ('woman', 'feminine',  'daughter' ),
        ('woman', 'neuter',    'livestock'),
        ('snake', 'masculine', 'son'      ),
        ('snake', 'feminine',  'daughter' ),
        ('snake', 'neuter',    'name'     ),
    })

possessor_pronoun_whitelist = DictSet(
    'possessor_pronoun_whitelist', 
    DictTupleIndexing(['possessor-noun', 'possessor-person', 'possessor-number', 'possessor-gender']),
    content = {
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
    })

write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = foreign_language.grammar.stock_modifier,
            # default_tree = 'clause test [np the n man] [vp conjugated] [modifier np test stock-modifier]',
            default_tree = 'clause [test [np the n man] [vp conjugated]] [test modifier np stock-modifier]',
        ) for demonstration in demonstrations],
        DictSpace(
            'traversal',
            DictTupleIndexing([
                # categories that are iterated over
                'gender','person','number','formality','clusivity','clitic',
                'tense', 'progress', 'mood', 'voice', 'verb', 'verb-form']),
            {
                **tag_defaults,
                'gender':      genders,
                'person':    ['1','2','3'],
                'number':      numbers,
                'progress':    progress,
                'mood':        moods,
                'tense':       tenses,
                'voice':       voices,
                'verb':        verbs,
                'subjectivity':'subject',
                'animacy':    'sapient',
                'noun-form':  'personal',
                'verb-form':  'finite',
            }),
        whitelists = [
            pronoun_whitelist,
            mood_tense_whitelist,
            finite_tense_progress_whitelist,
            voice_progress_whitelist
        ],
        blacklists = [verb_progress_blacklist, verb_mood_blacklist, verb_voice_blacklist],
    ))

write('flashcards/latin/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'subjectivity', 'motion', 'role', 'number', 'noun', 'gender',]),
                {
                    **tag_defaults,
                    'noun':        nouns,
                    'number':      numbers,
                    'role':        roles,
                    'motion':      motions,
                    'subjectivity':subjectivity,
                    'animacy':    'thing',
                    'noun-form':  'common',
                    'verb-form':  'finite',
                }),
        whitelists = [subjectivity_motion_whitelist],
        blacklists = [subjectivity_role_blacklist],
        tag_templates ={
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
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    'noun', 'gender', 'person', 'number', 'subjectivity', 'motion', 'role',]),
                {
                    **tag_defaults,
                    'noun':      ['man','woman','snake'],
                    'person':    ['1','2','3'],
                    'gender':      genders,
                    'role':        roles,
                    'motion':      motions,
                    'number':      numbers,
                    'subjectivity':subjectivity,
                    'animacy':    'animate',
                    'noun-form':  'personal',
                    'verb-form':  'finite',
                }),
        whitelists = [
            subjectivity_motion_whitelist,
            declension_pronoun_whitelist, 
        ],
        blacklists = [subjectivity_role_blacklist],
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
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'subjectivity', 'motion', 'role', 'number', 'noun', 'gender', ]),
                {
                    **tag_defaults,
                    'motion':      case_episemaxis_to_episemes['motion'],
                    'role':        case_episemaxis_to_episemes['role'],
                    'subjectivity':'modifier',
                    'animacy':    'thing',
                    'noun-form':  'common',
                    'verb-form':  'finite',
                }),
        tag_templates ={
            'dummy'      : {'noun-form':'personal', 'person':'3', 'number':'singular'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
        ) for demonstration in demonstrations], 
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'subjectivity', 'motion', 'role', 'number', 'noun', 'gender', 'adjective',]),
                {
                    **tag_defaults,
                    'noun':      ['man','woman','animal'] ,
                    'adjective':   adjectives,
                    'number':      numbers,
                    'gender':      genders,
                    'role':        roles,
                    'motion':      motions,
                    'subjectivity':subjectivity,
                    'animacy':    'thing',
                    'noun-form':  'common',
                    'verb-form':  'finite',
                }),
        whitelists = [
            subjectivity_motion_whitelist,
            gender_agreement_whitelist,
        ],
        blacklists = [subjectivity_role_blacklist],
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
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'subjectivity', 'motion', 'role', 'number', 'noun', 'gender', 
                    'possessor-gender', 'possessor-noun', 
                    'possessor-clusivity', 'possessor-formality', 
                    'possessor-person', 'possessor-number',]),
                {
                    **tag_defaults,
                    'possessor-noun':   ['man','woman','snake'],
                    'possessor-gender': ['masculine-possessor','feminine-possessor','neuter-possessor'],
                    'possessor-number': ['singular-possessor','plural-possessor'],
                    'possessor-person': ['1st-possessor','2nd-possessor','3rd-possessor'],
                    'possessor-clusivity': 'exclusive-possessor',
                    'possessor-formality': 'familiar-possessor',
                    'noun':      ['son','daughter','livestock'],
                    'number':      numbers,
                    'gender':      genders,
                    'role':        roles,
                    'motion':      motions,
                    'subjectivity':subjectivity,
                    'animacy':    'thing',
                    'noun-form':  'common',
                    'verb-form':  'finite',
                }),
        whitelists = [
            subjectivity_motion_whitelist,
            possession_whitelist,
            possessor_pronoun_whitelist,
        ],
        blacklists = [subjectivity_role_blacklist],
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
                # default_tree = 'clause [test [np the n man] [infinitive vp conjugated]] [modifier test np stock-modifier]',
                default_tree = 'clause [speaker [vp v figure]] [modifier np clause [test [np the n man] [infinitive vp conjugated]]] [test modifier np stock-modifier]',
            ),
            english_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test [np the n man] [vp conjugated]] [modifier np test stock-modifier]',
                default_tree = 'clause [speaker [np the n man] [vp v figure]] [modifier np clause [test [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
        ],
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'gender','person','number','formality','clusivity','clitic',
                    'tense', 'progress', 'mood', 'voice', 'verb', 'verb-form', ]),
                {
                    **tag_defaults,
                    'voice':       voices,
                    'progress':    progress,
                    'tense':       tenses,
                    'voice':       voices,
                    'verb':        verbs,
                    'subjectivity':'subject',
                    'animacy':    'sapient',
                    'noun-form':  'personal',
                    'verb-form':  'finite',
                }),
        whitelists = [
            pronoun_whitelist,
            mood_tense_whitelist,
            nonfinite_tense_progress_whitelist,
        ],
        blacklists = [verb_progress_blacklist, verb_mood_blacklist, verb_voice_blacklist],
    ))

write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle', 'cloze', 'v','verb'], ['modifier', 'np', 'participle', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        DictSpace(
            'traversal',
            DictTupleIndexing([
                    # categories that are iterated over
                    'tense', 'voice', 'progress', 'mood', 
                    'subjectivity', 'motion', 'role', 'number', 'noun', 'gender', 'verb',]),
                {
                    **tag_defaults,
                    'motion':      case_episemaxis_to_episemes['motion'],
                    'role':        'agent',
                    'valency':     'transitive',
                    'verb':        verbs,
                    'animacy':    'thing',
                    'tense':       tenses, 
                    'voice':       voices,
                    'subjectivity':subjectivity,
                    'progress':    ['atelic','finished'], 
                    'verb-form':  'participle',
                    'noun-form':  'common',
                }),
        whitelists = [
            subjectivity_motion_whitelist,
            nonfinite_tense_progress_whitelist,
        ],
        blacklists = [
            subjectivity_role_blacklist, 
            verb_progress_blacklist, 
            verb_mood_blacklist, 
            verb_voice_blacklist
        ],
        tag_templates ={
            'dummy'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',},
            'emoji'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common', 'person':'4'},
            'participle' : {'case':'nominative'},
        },
    ))
