from tools.lookup import DictLookup
from tools.indexing import DictTupleIndexing
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
    RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
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
verbs = ['be', 'be able', 'want', 'become', 'go', 
         'carry', 'eat', 'love', 'advise', 
         'capture', 'hear']
nouns = ['man', 'day', 'hand', 'night', 'thing', 'name', 'son', 'war',
         'air', 'boy', 'animal', 'star', 'tower', 'horn', 'sailor', 'foundation',
         'echo', 'phenomenon', 'vine', 'myth', 'atom', 'nymph', 'comet']
adjectives = ['tall', 'holy', 'poor', 'mean', 'old', 'nimble', 'swift', 'jovial']
progress = 'atelic started finished'.split()
moods = 'indicative subjunctive imperative'.split()
tenses = 'present past future'.split()
voices = 'active passive'.split()

write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = foreign_language.grammar.stock_modifier,
            default_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]'
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            # categories that are iterated over
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'progress', 'mood', 'voice', 'verb', 'verb-form', ]),
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
            'animacy':    'sapient',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        whitelists = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'feminine'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'feminine'),
                    ('3', 'plural',   'masculine'),
                }),
            DictLookup(
                'tense aspect filter', 
                DictTupleIndexing(['tense', 'progress']),
                content = {
                    ('present', 'atelic'),
                    ('present', 'finished'),
                    ('future',  'atelic'),
                    ('future',  'finished'),
                    ('past',    'unfinished'),
                    ('past',    'finished'),
                }),
            DictLookup(
                'mood tense filter', 
                DictTupleIndexing(['mood','tense']),
                content = {
                    ('indicative',  'present'),
                    ('indicative',  'past'),
                    ('indicative',  'future'),
                    ('subjunctive', 'present'),
                    ('subjunctive', 'past'),
                    ('imperative',  'present'),
                    ('imperative',  'future'),
                }),
        ],
        blacklists = [
            DictLookup(
                'verb voice filter', 
                DictTupleIndexing(['verb','voice']),
                content = {
                    ('be', 'passive'),
                    ('be able', 'passive'),
                    ('become', 'passive'),
                    ('want', 'passive'),
                }),
            DictLookup(
                'verb aspect filter', 
                DictTupleIndexing(['verb','progress']),
                content = {
                    ('become', 'finished'),
                }),
            DictLookup(
                'verb mood filter', 
                DictTupleIndexing(['verb','mood']),
                content = {
                    ('be able', 'imperative'),
                }),
        ],
    ))

write('flashcards/latin/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'noun':        nouns,
            'number':      numbers,
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        tag_templates ={
            'agent'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            'noun', 'gender', 'person', 'number', 'motion', 'role',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'noun':      ['man','woman','snake'],
            'person':    ['1','2','3'],
            'gender':      genders,
            'number':      numbers,
            'animacy':    'animate',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        whitelists = [
            DictLookup(
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
            ],
        tag_templates ={
            'agent'      : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal'},
            'emoji'      : {'noun-form':'personal'},
        },
    ))


write('flashcards/latin/adpositions.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', 'n', 'noun'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', ]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'role': [
                # 'solitary', # the subject of an intransitive verb
                # 'agent',    # the subject of a transitive verb
                # 'patient',  # the direct object of an active verb
                # 'theme',    # the direct object of a stative verb
                # 'possessor', 
                'location', 'extent', 'vicinity', 'interior', 'surface', 
                'presence', 'aid', 'lack', 
                #'interest', 
                'purpose', 'possession', 
                'time', 'state of being', 'topic', 'company', 'resemblance'],
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        tag_templates ={
            'agent'      : {'noun-form':'personal', 'person':'3', 'number':'singular'},
            'solitary'   : {'noun-form':'personal', 'person':'3', 'number':'singular'},
            'patient'    : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
        ) for demonstration in demonstrations], 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'noun':      ['man','woman','animal'] ,
            'adjective':   adjectives,
            'number':      numbers,
            'gender':      genders,
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        whitelists = [
            DictLookup(
                'adjective agreement noun filter', 
                DictTupleIndexing(['gender', 'noun']),
                content = {
                    ('masculine', 'man'   ),
                    ('feminine',  'woman' ),
                    ('neuter',    'animal'),
                })
            ],
        tag_templates ={
            'agent'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
    ))

write('flashcards/latin/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])},
            ],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            'possessor-gender', 'possessor-noun', 
            'possessor-clusivity', 'possessor-formality', 
            'possessor-person', 'possessor-number',]),
        {
            **case_episemaxis_to_episemes,
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
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        whitelists = [
            DictLookup(
                'possessive pronoun possession filter', 
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
                }),
            DictLookup(
                'pronoun filter', 
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
                }),
            ],
        tag_templates ={
            'agent'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
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
                default_tree = 'clause [speaker-seme [vp v figure]] [modifier-seme np clause [test-seme [theme np the n man] [infinitive vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
            ),
            english_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                default_tree = 'clause [speaker-seme [np the n man] [vp v figure]] [modifier-seme np clause [test-seme [np the n man] [vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
            ),
        ],
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
            'animacy':    'sapient',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        whitelists = [
            DictLookup(
                'pronoun filter', 
                DictTupleIndexing(['person', 'number', 'gender']),
                content = {
                    ('1', 'singular', 'neuter'),
                    ('2', 'singular', 'feminine'),
                    ('3', 'singular', 'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'feminine'),
                    ('3', 'plural',   'masculine'),
                }),
            DictLookup(
                'tense aspect filter', 
                DictTupleIndexing(['tense', 'progress']),
                content = {
                    ('present', 'atelic'),
                    ('present', 'finished'),
                    ('future',  'atelic'),
                    ('future',  'finished'),
                    ('past',    'unfinished'),
                    ('past',    'finished'),
                }),
            DictLookup(
                'mood tense filter', 
                DictTupleIndexing(['mood','tense']),
                content = {
                    ('indicative',  'present'),
                    ('indicative',  'past'),
                    ('indicative',  'future'),
                    ('subjunctive', 'present'),
                    ('subjunctive', 'past'),
                    ('imperative',  'present'),
                    ('imperative',  'future'),
                }),
        ],
        blacklists = [
            DictLookup(
                'verb voice filter', 
                DictTupleIndexing(['verb','voice']),
                content = {
                    ('be', 'passive'),
                    ('be able', 'passive'),
                    ('become', 'passive'),
                    ('want', 'passive'),
                }),
        ],
    ))

write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = foreign_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle-seme', 'cloze', 'v','verb'], ['modifier-seme', 'np', 'participle-seme', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            # categories that are iterated over
            'tense', 'voice', 'progress', 'mood', 
            'motion', 'role', 'number', 'noun', 'gender', 'verb',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'role':        'agent',
            'valency':     'transitive',
            'verb':        verbs,
            'animacy':    'thing',
            'tense':       tenses, 
            'voice':       voices,
            'progress':    ['atelic','finished'], 
            'verb-form':  'participle',
            'noun-form':  'common',
        },
        whitelists = [
            DictLookup(
                'tense aspect filter', 
                DictTupleIndexing(['tense', 'progress']),
                content = {
                    ('present', 'atelic'),
                    ('future',  'atelic'),
                    ('past',    'finished'),
                }),
        ],
        blacklists = [
            DictLookup(
                'verb voice filter', 
                DictTupleIndexing(['verb', 'voice']),
                content = {
                    ('be',      'passive'),
                    ('be able', 'passive'),
                    ('want',    'passive'),
                    ('become',  'passive'),
                }),
        ],
        tag_templates ={
            'agent'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common',},
            'emoji'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'progress':'atelic', 'noun-form':'common', 'person':'4'},
            'participle' : {'case':'nominative'},
        },
    ))
