from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.shorthands import EmojiPerson
from tools.languages import Language
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
    card_generation, tagaxis_to_tags, nouns_to_depictions,
    write, replace
)

list_tools = ListTools()

latin = Language(
    ListGrammar(
        conjugation_population.index([
            *finite_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/finite-conjugation.tsv'), 2, 5),
            *nonfinite_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/nonfinite-conjugations.tsv'), 6, 2),
            *filter(has_annotation('language','classical-latin'),
                declension_verb_annotation.annotate(
                    tsv_parsing.rows(
                        'data/inflection/declension-template-verbs-minimal.tsv'), 2, 9)),
        ]),
        declension_population.index([
            *pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/pronoun-declensions.tsv'), 1, 4),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/declensions.tsv'), 1, 2),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/adjective-agreement.tsv'), 1, 3),
            *possessive_pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/pronoun-possessives.tsv'), 1, 4),
            *filter(has_annotation('language','classical-latin'),
                declension_template_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'), 2, 7)),
        ]),
        case_population.index(
            case_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/declension-use-case-to-grammatical-case.tsv'))),
        {'language-type':'foreign'},
    ),
    RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
    list_tools,
    RuleFormatting(),
    RuleValidation(),
    substitutions = []
)

persons = [
    EmojiPerson('s','n',3),
    EmojiPerson('s','f',4),
    EmojiPerson('s','m',2),
    EmojiPerson('s','n',1),
    EmojiPerson('s','n',5),
]

write('flashcards/latin/finite-conjugation.html', 
    card_generation.conjugation(
        latin,
        DictTupleIndexing([
            # categories that are iterated over
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'aspect', 'mood', 'voice', 'verb', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'animacy','noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'gender':    ['neuter', 'feminine', 'masculine'],
            'person':    ['1','2','3'],
            'number':    ['singular','plural'],
            'formality':  'familiar',
            'clusivity':  'exclusive',
            'clitic':     'tonic',
            'mood':      ['indicative','subjunctive','imperative',],
            'voice':     ['active', 'passive'],
            'verb':      ['be', 'be able', 'want', 'become', 'go', 
                          'carry', 'eat', 'love', 'advise', 
                          'capture', 'hear'],
            'animacy':    'sapient',
            'noun-form':  'personal',
            'script':     'latin',
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
        native_map=replace([('♂',''),('♀','')]), 
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        foreign_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
        native_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]',
    ))

write('flashcards/latin/noun-declension.html', 
    card_generation.declension(
        latin, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'noun':      ['man', 'day', 'hand', 'night', 'thing', 'name', 'son', 'war',
                          'air', 'boy', 'animal', 'star', 'tower', 'horn', 'sailor', 'foundation',
                          'echo', 'phenomenon', 'vine', 'myth', 'atom', 'nymph', 'comet'],
            'number':    ['singular','plural'],
            'gender':     'masculine',
            'person':     '3',
            'clusivity':  'exclusive',
            'animacy':    'thing',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      'present', 
            'voice':      'active',
            'aspect':     'aorist', 
            'mood':       'indicative',
            'noun-form':  'common',
            'script':     'latin',
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
        latin, 
        DictTupleIndexing([
            'noun', 'gender', 'person', 'number', 'motion', 'role',
            # categories that are constant since they do not affect pronouns in the language
            'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'noun':      ['man','woman','snake'],
            'gender':    ['neuter', 'feminine', 'masculine'],
            'number':    ['singular','plural'],
            'person':    ['1','2','3'],
            'clusivity':  'exclusive',
            'animacy':    'animate',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      'present', 
            'voice':      'active',
            'aspect':     'aorist', 
            'mood':       'indicative',
            'noun-form':  'personal',
            'script':     'latin',
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
        native_map=replace([('you♀','you'),('you all♀','you all')]), 
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
    ))


write('flashcards/latin/adpositions.html', 
    card_generation.declension(
        latin, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form', 'script']),
        {
            **tagaxis_to_tags,
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
            'noun':       'man',
            'number':     'singular',
            'gender':     'masculine',
            'person':     '3',
            'clusivity':  'exclusive',
            'animacy':    'thing',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      'present', 
            'voice':      'active',
            'aspect':     'aorist', 
            'mood':       'indicative',
            'noun-form':  'common',
            'script':     'latin',
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
        latin, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 'adjective',
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'adjective': ['tall', 'holy', 'poor', 'mean', 'old', 'nimble', 'swift', 'jovial'],
            'noun':      ['man','woman','animal'] ,
            'number':    ['singular','plural'],
            'gender':    ['masculine','feminine','neuter'],
            'person':     '3',
            'clusivity':  'exclusive',
            'animacy':    'thing',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      'present', 
            'voice':      'active',
            'aspect':     'aorist', 
            'mood':       'indicative',
            'noun-form':  'common',
            'script':     'latin',
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
        latin, 
        DictTupleIndexing([
            # categories that are iterated over
            'motion', 'role', 'number', 'noun', 'gender', 
            'possessor-gender', 'possessor-noun', 
            'possessor-clusivity', 'possessor-formality', 
            'possessor-person', 'possessor-number',
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'tense', 'voice', 'aspect', 'mood', 'noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'possessor-noun':   ['man','woman','snake'],
            'possessor-gender': ['masculine-possessor','feminine-possessor','neuter-possessor'],
            'possessor-number': ['singular-possessor','plural-possessor'],
            'possessor-person': ['1st-possessor','2nd-possessor','3rd-possessor'],
            'possessor-clusivity': 'exclusive-possessor',
            'possessor-formality': 'familiar-possessor',
            'noun':      ['son','daughter','livestock'],
            'number':    ['singular','plural'],
            'gender':    ['masculine','feminine','neuter'],
            'person':     '3',
            'clusivity':  'exclusive',
            'animacy':    'thing',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      'present', 
            'voice':      'active',
            'aspect':     'aorist', 
            'mood':       'indicative',
            'noun-form':  'common',
            'script':     'latin',
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
        native_map=replace([('your♀','your'),('you all♀','you all')]), 
        substitutions = [
            {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])}
        ],
    ))

write('flashcards/latin/nonfinite-conjugation.html', 
    card_generation.conjugation(
        latin,
        DictTupleIndexing([
            # categories that are iterated over
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'aspect', 'mood', 'voice', 'verb', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'animacy','noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'gender':     'masculine',
            'person':     '3',
            'number':     'singular',
            'formality':  'familiar',
            'clusivity':  'exclusive',
            'clitic':     'tonic',
            'mood':       'indicative',
            'voice':     ['active', 'passive'],
            'verb':      ['be', 'be able', 'want', 'become', 'go', 
                          'carry', 'eat', 'love', 'advise', 
                          'capture', 'hear'],
            'animacy':    'sapient',
            'noun-form':  'personal',
            'script':     'latin',
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
        native_map=replace([('♂',''),('♀','')]), 
        persons = persons,
        substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
        native_tree='clause [speaker-seme [np the n man] [vp v figure]] [modifier-seme np clause [test-seme [np the n man] [vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
        foreign_tree='clause [speaker-seme [vp v figure]] [modifier-seme np clause [test-seme [theme np the n man] [infinitive vp conjugated]]] [modifier-seme np test-seme stock-modifier]',
    ))
'''
'''


write('flashcards/latin/participle-declension.html', 
    card_generation.declension(
        latin, 
        DictTupleIndexing([
            # categories that are iterated over
            'tense', 'voice', 'aspect', 'mood', 
            'motion', 'role', 'number', 'noun', 'gender', 'verb',
            # categories that are constant since they are not relevant to common noun declension
            'person', 'clusivity', 'animacy', 'clitic', 'partitivity', 'formality', 'verb-form', 
            # categories that are constant since they are not relevant to declension
            'noun-form', 'script']),
        {
            **tagaxis_to_tags,
            'role':      ['solitary'],
            'verb':      ['be', 'be able', 'want', 'become', 'go', 
                          'carry', 'eat', 'love', 'advise', 
                          'capture', 'hear'],
            'noun':       'man' ,
            'number':     'singular',
            'gender':     'masculine',
            'person':     '3',
            'clusivity':  'exclusive',
            'animacy':    'thing',
            'clitic':     'tonic',
            'partitivity':'nonpartitive',
            'formality':  'familiar',
            'tense':      ['present','past','future'], 
            'voice':      ['active','passive'],
            'aspect':     ['aorist','perfect'], 
            'mood':       'indicative',
            'verb-form':  'participle',
            'noun-form':  'common',
            'script':     'latin',
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


