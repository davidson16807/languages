from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.shorthands import EmojiPerson
from tools.languages import Language
from tools.writing import Writing
from tools.nodemaps import (
    ListTools, ListGrammar,
    RuleTools, RuleSyntax, RuleValidation, RuleFormatting, 
)
from inflections import (
    case_episemaxis_to_episemes,
    tagaxis_to_tags,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    card_generation, tag_defaults, nouns_to_depictions,
    write, replace
)

list_tools = ListTools()
rule_tools = RuleTools()

foreign_writing = Writing(
    'greek',
    Language(
        ListGrammar(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/finite-conjugations.tsv')),
                *nonfinite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/nonfinite-conjugations.tsv')),
                *filter(has_annotation('language','attic-greek'),
                    declension_verb_annotation.annotate(
                        tsv_parsing.rows(
                            'data/inflection/declension-template-verbs-minimal.tsv'))),
            ]),
            declension_population.index([
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/pronoun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/common-noun-declensions.tsv')),
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/pronoun-possessives.tsv')),
                *filter(has_annotation('language','attic-greek'),
                    declension_template_noun_annotation.annotate(
                        tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'))),
            ]),
            case_usage_population.index(
                case_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/case-usage.tsv'))),
            mood_usage_population.index(
                mood_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/mood-usage.tsv'))),
            aspect_usage_population.index(
                aspect_usage_annotation.annotate(
                    tsv_parsing.rows('data/inflection/greek/attic/aspect-usage.tsv'))),
            {'language-type':'foreign'},
        ),
        RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
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
verbs = 'be go release'.split()
nouns = ['young-man', 'soldier', 'polity', 'village', 'person', 'street', 'gift', 
         'circumnavigation', 'bone', 'hero', 'fish', 'oak', 'city', 'axe', 'town', 
         'master', 'cow', 'old-woman', 'echo', 'Clio', 'crow', 'vulture', 'rug',
         'giant', 'tooth', 'old-man', 'property', 'Greek', 'winter', 'Titan',
         'light-ray', 'shepherd', 'guide', 'neighbor', 'tipstaff', 'ichor', 'chaff',
         'orator', 'father', 'man', 'Demeter', 'Socrates', 'Pericles', 'arrow',
         'foundation', 'shame', 'Ares', 'woman', 'Thales', 'Oedipus', 'fire',
         'Apollo', 'knee', 'wood', 'Zeus', 'liver', 'dog', 'ship', 'ear', 'water', 'hand']
aspects = 'aorist imperfective perfective'.split()
moods = 'indicative subjunctive imperative optative'.split()
tenses = 'present past future'.split()
voices = 'active middle passive'.split()

write('flashcards/ancient-greek/finite-conjugation.html', 
    card_generation.conjugation(
        foreign_writing,
        DictTupleIndexing([
            'gender','person','number','formality','clusivity','clitic',
            'tense', 'aspect', 'mood', 'voice', 'verb', 'verb-form', ]),
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
        whitelist = [
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

write('flashcards/ancient-greek/common-noun-declension.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
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

write('flashcards/ancient-greek/pronoun-declension.html', 
    card_generation.declension(
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
        whitelist = [
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


write('flashcards/ancient-greek/adpositions.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
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
        persons = persons,
        substitutions = [
            {'declined':         list_tools.replace(['the', 'n', 'noun'])},
            {'stock-adposition': list_tools.wrap('cloze')},
        ],
    ))

write('flashcards/ancient-greek/pronoun-possessives.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
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
        whitelist = [
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


write('flashcards/ancient-greek/participle-declension.html', 
    card_generation.declension(
        foreign_writing, 
        DictTupleIndexing([
            'tense', 'voice', 'aspect', 'mood', 
            'motion', 'role', 'number', 'noun', 'gender', 'verb',]),
        {
            **case_episemaxis_to_episemes,
            **tag_defaults,
            'role':        'agent',
            'verb':         verbs,
            'valency':     'transitive',
            'animacy':     'thing',
            'tense':        tenses, 
            'voice':        voices,
            'verb-form':   'participle',
            'noun-form':   'common',
        },
        tag_templates ={
            'agent'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'solitary'   : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'patient'    : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'theme'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'personal', 'person':'3', 'number':'singular', 'gender':'masculine'},
            'possession' : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',   'person':'3', 'number':'singular', 'gender':'masculine'},
            'test'       : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common',},
            'emoji'      : {'verb-form':'finite','tense':'present', 'voice':'active', 'aspect':'aorist', 'noun-form':'common', 'person':'4'},
            'participle' : {'case':'nominative'},
        },
        persons = persons,
        substitutions = [{'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle-seme', 'cloze', 'v','verb'], ['modifier-seme', 'np', 'participle-seme', 'stock-modifier']]])}],
    ))

