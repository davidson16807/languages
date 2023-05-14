from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.cards import DeclensionTemplateMatching, CardFormatting, DeckGeneration
from tools.shorthands import EmojiPerson
from tools.languages import Language
from tools.orthography import Orthography
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleSyntax, RuleFormatting, 
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
                    tsv_parsing.rows('data/inflection/english/old/case-usage.tsv'))),
            mood_usage_population.index(
                mood_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/mood-usage.tsv'))),
            aspect_usage_population.index(
                aspect_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/aspect-usage.tsv'))),
        ),
        ListGrammar(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/conjugations.tsv')),
                *filter(has_annotation('language','old-english'),
                    declension_verb_annotation.annotate(
                        tsv_parsing.rows(
                            'data/inflection/declension-template-verbs-minimal.tsv'))),
            ]),
            declension_population.index([
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/pronoun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/common-noun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/adjective-agreement.tsv')),
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/english/old/pronoun-possessives.tsv')),
                *filter(has_annotation('language','old-english'),
                    declension_template_noun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'))),
            ]),
        ),
        RuleSyntax('subject verb direct-object indirect-object modifiers'.split()), 
        {'language-type':'foreign'},
        # TODO: this should technically be SOV, but V2 ordering applies to main clauses which mainly produces SVO
        list_tools,
        rule_tools,
        RuleFormatting(),
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
numbers = 'singular plural'.split()
verbs = ['be [momentarily]', 'be [by nature]', 'do', 'go', 'want', 
         'steal', 'share', 'tame', 'move', 'love', 'have', 'live', 'say', 'think',]
nouns = 'dog light house gift raid moon sun eye time English son hand person nut goose friend bystander father mother brother sister daughter lamb shoe piglet shadow meadow'.split(' ')
adjectives = 'good tall black red green'.split()
progress = 'atelic'
moods = 'indicative subjunctive imperative'.split()
tenses = 'present past'.split()
voices = 'active'

write('flashcards/old-english/finite-conjugation.html', 
    deck_generation.conjugation(
        foreign_writing,
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
                'pronoun filter', 
                DictTupleIndexing(['tense', 'mood']),
                content = {
                    ('present', 'indicative', ),
                    ('past',    'indicative', ),
                    ('present', 'subjunctive',),
                    ('past',    'subjunctive',),
                    ('present', 'imperative', ),
                }),
        ],
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        foreign_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
        native_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
    ))

write('flashcards/old-english/common-noun-declension.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', ]),
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
        persons = persons,
        nouns_to_depictions = nouns_to_depictions,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))

write('flashcards/old-english/pronoun-declension.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            'noun', 'gender', 'person', 'number', 'motion', 'role',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'noun':      ['man','woman','snake'],
            'gender':      genders,
            'number':     numbers,
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


write('flashcards/old-english/adpositions.html', 
    deck_generation.declension(
        foreign_writing, 
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
            'animacy':    'sapient',
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

write('flashcards/old-english/strong-adjective-agreement.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective']),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'adjective':  adjectives,
            'noun':      ['man','woman','animal'] ,
            'number':     numbers,
            'gender':     genders,
            'strength':   'strong',
            'animacy':    'animate',
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

write('flashcards/old-english/weak-adjective-agreement.html', 
    deck_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective']),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'adjective':  adjectives,
            'noun':      ['man','woman','animal'] ,
            'number':     numbers,
            'gender':     genders,
            'strength':   'weak',
            'animacy':    'animate',
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

write('flashcards/old-english/pronoun-possessives.html', 
    deck_generation.declension(
        foreign_writing, 
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
        persons = persons,
        substitutions = [
            {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])}
        ],
    ))


write('flashcards/old-english/participle-declension.html', 
    deck_generation.declension(
        foreign_writing, 
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



