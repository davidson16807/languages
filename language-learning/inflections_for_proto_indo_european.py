from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.cards import DeclensionTemplateMatching, CardFormatting, DeckGeneration
from tools.shorthands import EmojiPerson
from tools.languages import Language
from tools.orthography import Orthography
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleSyntax, RuleValidation, RuleFormatting, 
)
from inflections import (
    case_episemaxis_to_episemes,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    deck_generation, tag_defaults, nouns_to_depictions,
    write, replace
)

list_tools = ListTools()
rule_tools = RuleTools()

foreign_writing = Orthography(
    'latin',
    Language(
        ListSemantics(
            case_usage_population.index(
                case_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/case-usage.tsv'))),
            mood_usage_population.index(
                mood_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/mood-usage.tsv'))),
            aspect_usage_population.index(
                aspect_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/aspect-usage.tsv'))),
        ),
        ListGrammar(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/finite-conjugations.tsv')),
                *nonfinite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/nonfinite-conjugations.tsv')),
                *filter(has_annotation('language','proto-indo-european'),
                    declension_verb_annotation.annotate(
                        tsv_parsing.rows(
                            'data/inflection/declension-template-verbs-minimal.tsv'))),
            ]),
            declension_population.index([
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/pronoun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/common-noun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/adjective-agreement.tsv')),
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/proto-indo-european/sihler/pronoun-possessives.tsv')),
                *filter(has_annotation('language','proto-indo-european'),
                    declension_template_noun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'))),
            ]),
        ),
        RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
        {'language-type':'foreign'},
        list_tools,
        rule_tools,
        RuleFormatting(),
        # RuleValidation(),
        RuleValidation(disabled=True),
        substitutions = []
    )
)

persons = [
    EmojiPerson('s','n',3),
    EmojiPerson('s','f',4),
    EmojiPerson('s','m',2),
    EmojiPerson('s','n',1),
    EmojiPerson('s','n',5),
]

genders = 'masculine feminine neuter'.split()
numbers = 'singular dual plural'.split()
verbs = ['be', 'become', 'carry', 'leave', 'work', 
         'do', 'ask', 'stretch', 'know', 
         'sit', 'protect', 'be red', 'set down', 'want to see',
         'renew', 'say', 'point out',]
nouns = 'wolf egg mare stranger seed father water cow pig sea fight cloud stone'.split()
adjectives = 'young old upset'.split()
progress = 'atelic'
moods = 'indicative subjunctive imperative optative'.split()
tenses = 'present past'.split()
voices = 'active middle'.split()

write('flashcards/proto-indo-european/finite-conjugation.html', 
    deck_generation.conjugation(
        foreign_writing,
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
                    ('2', 'dual',     'feminine'),
                    ('3', 'dual',     'masculine'),
                    ('1', 'plural',   'neuter'),
                    ('2', 'plural',   'feminine'),
                    ('3', 'plural',   'masculine'),
                })
            ],
        blacklists = [
            DictLookup(
                'voice filter', 
                DictTupleIndexing(['verb', 'voice']),
                content = {
                    ('be',     'middle'),
                    ('become', 'middle'),
                    ('know',   'middle'),
                    ('sit',    'middle'),
                    ('be red', 'middle'),
                    ('arrive', 'middle'),
                    ('thought','middle'),
                })
            ],
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        foreign_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
        native_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
    ))

write('flashcards/proto-indo-european/common-noun-declension.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender']),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
            'role':        case_episemaxis_to_episemes['role'],
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
        persons = persons,
        nouns_to_depictions = nouns_to_depictions,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))

write('flashcards/proto-indo-european/pronoun-declension.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            'noun', 'gender', 'person', 'number', 'motion', 'role']),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
            'role':        case_episemaxis_to_episemes['role'],
            'noun':      ['man','woman','snake'],
            'gender':      genders,
            'number':      numbers,
            'person':    ['1','2','3'],
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
            'agent'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal'},
            'emoji'      : {'noun-form':'personal'},
        },
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))


write('flashcards/proto-indo-european/adpositions.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender']),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
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
        persons = persons,
        substitutions = [
            {'declined':         list_tools.replace(['the', 'n', 'noun'])},
            {'stock-adposition': list_tools.wrap('cloze')},
        ],
    ))

write('flashcards/proto-indo-european/adjective-agreement.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective']),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
            'role':        case_episemaxis_to_episemes['role'],
            'adjective':  adjectives,
            'noun':      ['man','woman','animal'] ,
            'number':     numbers,
            'gender':     genders,
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
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
    ))

write('flashcards/proto-indo-european/pronoun-possessives.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender',
            'possessor-gender', 'possessor-noun', 
            'possessor-clusivity', 'possessor-formality', 
            'possessor-person', 'possessor-number',]),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
            'role':        case_episemaxis_to_episemes['role'],
            'possessor-noun':   ['man','woman','snake'],
            'possessor-gender': ['masculine-possessor','feminine-possessor','neuter-possessor'],
            'possessor-number': ['singular-possessor','plural-possessor'],
            'possessor-person': ['1st-possessor','2nd-possessor','3rd-possessor'],
            'possessor-clusivity': 'exclusive-possessor',
            'possessor-formality': 'familiar-possessor',
            'noun':      ['son','daughter','livestock'],
            'number':     numbers,
            'gender':     genders,
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
                    # ('man',   '3rd-possessor', 'singular-possessor', 'masculine-possessor'),
                    # ('woman', '3rd-possessor', 'singular-possessor', 'feminine-possessor' ),
                    # ('snake', '3rd-possessor', 'singular-possessor', 'neuter-possessor'   ),
                    ('man',   '1st-possessor', 'plural-possessor',   'neuter-possessor'   ),
                    ('woman', '2nd-possessor', 'plural-possessor',   'feminine-possessor' ),
                    # ('man',   '3rd-possessor', 'plural-possessor',   'masculine-possessor'),
                    # ('woman', '3rd-possessor', 'plural-possessor',   'feminine-possessor' ),
                    # ('man',   '3rd-possessor', 'plural-possessor',   'neuter-possessor'   ),
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
        persons = persons,
        substitutions = [
            {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])}
        ],
    ))


write('flashcards/proto-indo-european/participle-declension.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'tense', 'voice', 'progress', 'mood', 
            'motion', 'role', 'number', 'noun', 'gender', 'verb']),
        {
            **tag_defaults,
            'motion':      case_episemaxis_to_episemes['motion'],
            'verb':        verbs,
            'role':        'agent',
            'valency':     'transitive',
            'animacy':    'thing',
            'tense':       tenses, 
            'voice':       voices,
            'verb-form':  'participle',
            'noun-form':  'common',
        },
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
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle-seme', 'cloze', 'v','verb'], ['modifier-seme', 'np', 'participle-seme', 'stock-modifier']]])}],
    ))



