from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.shorthands import EmojiPerson
from tools.languages import Language
from tools.writing import Writing
from tools.nodemaps import (
    ListTools, ListGrammar,
    RuleValidation, RuleFormatting, RuleSyntax,
)
from inflections import (
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    case_annotation,
    conjugation_population, declension_population, case_population,
    card_generation, tag_defaults, nouns_to_depictions,
    write, replace
)

list_tools = ListTools()

foreign_writing = Writing(
    'latin',
    Language(
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
            case_population.index(
                case_annotation.annotate(
                    tsv_parsing.rows('data/inflection/latin/classic/usage-case-to-grammatical-case.tsv'))),
            {'language-type':'foreign'},
        ),
        RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
        list_tools,
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
numbers = 'singular plural'.split()
verbs = ['be', 'be able', 'want', 'become', 'go', 
         'carry', 'eat', 'love', 'advise', 
         'capture', 'hear']
nouns = ['man', 'day', 'hand', 'night', 'thing', 'name', 'son', 'war',
         'air', 'boy', 'animal', 'star', 'tower', 'horn', 'sailor', 'foundation',
         'echo', 'phenomenon', 'vine', 'myth', 'atom', 'nymph', 'comet']
adjectives = ['tall', 'holy', 'poor', 'mean', 'old', 'nimble', 'swift', 'jovial']
aspects = 'aorist imperfect perfect'.split()
moods = 'indicative subjunctive imperative'.split()
tenses = 'present past future'.split()
voices = 'active passive'.split()


write('flashcards/latin/finite-conjugation.html', 
    card_generation.conjugation(
        foreign_writing,
        DictTupleIndexing([
            # categories that are iterated over
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'aspect', 'mood', 'voice', 'verb', 'verb-form', 
            # categories that are constant since they are not relevant to conjugation
            'animacy', 'strength', 'noun-form']),
        {
            **tag_defaults,
            'gender':      genders,
            'person':    ['1','2','3'],
            'number':      numbers,
            'aspect':      aspects,
            'mood':        moods,
            'tense':       tenses,
            'voice':       voices,
            'verb':        verbs,
            'animacy':    'sapient',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        filter_lookups = [
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
                })
            ],
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        foreign_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
        native_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
    ))

write('flashcards/latin/common-noun-declension.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'strength', 'tense', 'voice', 'aspect', 'mood', 'noun-form']),
        {
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
            'patient'    : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
        persons = persons,
        nouns_to_depictions = nouns_to_depictions,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))

write('flashcards/latin/pronoun-declension.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            'noun', 'gender', 'person', 'number', 'motion', 'role',
            # categories that are constant since they do not affect pronouns in the language
            'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'strength', 'tense', 'voice', 'aspect', 'mood', 'noun-form']),
        {
            **tag_defaults,
            'noun':      ['man','woman','snake'],
            'person':    ['1','2','3'],
            'gender':      genders,
            'number':      numbers,
            'animacy':    'animate',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        filter_lookups = [
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
            'patient'    : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal'},
            'emoji'      : {'noun-form':'personal'},
        },
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))


write('flashcards/latin/adpositions.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'strength', 'tense', 'voice', 'aspect', 'mood', 'noun-form']),
        {
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
            'patient'    : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
        persons = persons,
        substitutions = [
            {'declined':         list_tools.replace(['the', 'n', 'noun'])},
            {'stock-adposition': list_tools.wrap('cloze')},
        ],
    ))

write('flashcards/latin/adjective-agreement.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective',
            # categories that are constant since they are not relevant to common noun declension
            'strength', 'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form']),
        {
            **tag_defaults,
            'noun':      ['man','woman','animal'] ,
            'adjective':   adjectives,
            'number':      numbers,
            'gender':      genders,
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        filter_lookups = [
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
            'patient'    : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'common'},
            'emoji'      : {'noun-form':'common', 'person':'4'},
        },
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
    ))

write('flashcards/latin/pronoun-possessives.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            'possessor-gender', 'possessor-noun', 
            'possessor-clusivity', 'possessor-formality', 
            'possessor-person', 'possessor-number',
            # categories that are constant since they are not relevant to common noun declension
            'strength', 'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form']),
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
            'animacy':    'thing',
            'noun-form':  'common',
            'verb-form':  'finite',
        },
        filter_lookups = [
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
            'patient'    : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'noun-form':'personal-possessive'},
            'emoji'      : {'person':'4'},
        },
        persons = persons,
        substitutions = [
            {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])}
        ],
    ))

write('flashcards/latin/nonfinite-conjugation.html', 
    card_generation.conjugation(
        foreign_writing,
        DictTupleIndexing([
            # categories that are iterated over
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'aspect', 'mood', 'voice', 'verb', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'strength', 'animacy','noun-form']),
        {
            **tag_defaults,
            'voice':       voices,
            'aspect':      aspects,
            'tense':       tenses,
            'voice':       voices,
            'verb':        verbs,
            'animacy':    'sapient',
            'noun-form':  'personal',
            'verb-form':  'finite',
        },
        filter_lookups = [
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
            ],
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        native_tree='clause [speaker-seme [np the n man] [vp v figure]] [modifier-seme np clause [test-seme [np the n man] [vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
        foreign_tree='clause [speaker-seme [vp v figure]] [modifier-seme np clause [test-seme [theme np the n man] [infinitive vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
    ))
'''
'''


write('flashcards/latin/participle-declension.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            # categories that are iterated over
            'tense', 'voice', 'aspect', 'mood', 
            'motion', 'role', 'number', 'noun', 'gender', 'verb',
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'strength', 'noun-form']),
        {
            **tag_defaults,
            'role':       'solitary',
            'verb':        verbs,
            'animacy':    'thing',
            'tense':       tenses, 
            'voice':       voices,
            'aspect':     ['aorist','perfect'], 
            'verb-form':  'participle',
            'noun-form':  'common',
        },
        tag_templates ={
            'agent'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',},
            'emoji'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common', 'person':'4'},
            'participle' : {'case':'nominative'},
        },
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle-seme', 'cloze', 'v','verb'], ['modifier-seme', 'np', 'participle-seme', 'stock-modifier']]])}],
    ))



