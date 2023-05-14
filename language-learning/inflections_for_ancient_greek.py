from tools.lookup import DefaultDictLookup, DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.cards import DeckGeneration
from tools.shorthands import EmojiPerson
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
    tagaxis_to_tags,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    tag_defaults, nouns_to_depictions,
    write, replace,
)

deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

greek_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/greek/attic/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/greek/attic/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/greek/attic/aspect-usage.tsv'))),
    ),
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
    ),
    RuleSyntax('subject modifiers indirect-object direct-object verb'.split()),
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = [],
)

demonstrations = [
    LanguageSpecificEmojiDemonstration(
        card_formatting.emoji_focus,
        greek_language.grammar.conjugation_lookups['argument'], 
        [
            EmojiPerson('s','n',3),
            EmojiPerson('s','f',4),
            EmojiPerson('s','m',2),
            EmojiPerson('s','n',1),
            EmojiPerson('s','n',5),
        ]),
    LanguageSpecificTextDemonstration(
            card_formatting.foreign_focus,
            Orthography('greek', greek_language),
        ),
    # LanguageSpecificTextDemonstration(
    #         card_formatting.foreign_side_note,
    #         Orthography('latin', greek_language),
    #     ),
    english_demonstration,
]

genders = 'masculine feminine neuter'.split()
numbers = 'singular dual plural'.split()
verbs = 'be go release'.split()
nouns = '''young-man soldier polity village person street gift 
         circumnavigation bone hero fish oak city axe town 
         master cow old-woman echo Clio crow vulture rug
         giant tooth old-man property Greek winter Titan
         light-ray shepherd guide neighbor tipstaff ichor chaff
         orator father man Demeter Socrates Pericles arrow
         foundation shame Ares woman Thales Oedipus fire
         Apollo knee wood Zeus liver dog ship ear water hand'''.split()
progress = 'atelic started finished'.split()
moods = 'indicative subjunctive imperative optative'.split()
tenses = 'present past future'.split()
voices = 'active middle passive'.split()

write('flashcards/ancient-greek/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = greek_language.grammar.stock_modifier,
            default_tree = 'clause [test-seme [np the n man] [vp conjugated]] [modifier-seme np test-seme stock-modifier]'
        ) for demonstration in demonstrations],
        DictTupleIndexing([
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
                    ('2', 'dual', 'feminine'),
                    ('3', 'dual', 'masculine'),
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
                    ('past',    'atelic'),
                    ('past',    'finished'),
                    ('past',    'started'),
                }),
            DictLookup(
                'voice filter', 
                DictTupleIndexing(['verb', 'voice']),
                content = {
                    ('be',      'active'),
                    ('go',      'active'),
                    ('release', 'active'),
                    ('release', 'middle'),
                    ('release', 'passive'),
                }),
        ],
        blacklists = [
            DictLookup(
                'tense mood filter', 
                DictTupleIndexing(['tense', 'mood']),
                content = {
                    ('past',   'imperative'),
                    ('future', 'subjunctive'),
                    ('future', 'imperative'),
                }),
            DictLookup(
                'tense aspect mood filter', 
                DictTupleIndexing(['tense', 'progress', 'mood']),
                content = {
                    ('past', 'finished', 'subjunctive'),
                    ('past', 'finished', 'optative'),
                    ('past', 'started',  'subjunctive'),
                    ('past', 'started',  'optative'),
                }),
        ],
        tag_templates ={
            'test'       : {'noun-form': 'personal', 'role':'agent', 'motion':'associated'},
            'modifier'   : {'noun-form': 'common', 'role':'modifier', 'motion':'associated'},
        },
    ))

write('flashcards/ancient-greek/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = greek_language.grammar.stock_modifier,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
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
        blacklists = [
            DictLookup(
                'noun number filter', 
                DictTupleIndexing(['noun', 'number']),
                content = {
                    ('ear',     'dual'),
                    ('echo',    'dual'),
                    ('echo',    'plural'),
                    ('fire',    'dual'),
                    ('fire',    'plural'),
                    ('Clio',    'dual'),
                    ('Clio',    'plural'),
                    ('Demeter', 'dual'),
                    ('Demeter', 'plural'),
                    ('Socrates','dual'),
                    ('Socrates','plural'),
                    ('Pericles','dual'),
                    ('Pericles','plural'),
                    ('Ares',    'dual'),
                    ('Ares',    'plural'),
                    ('Apollo',  'dual'),
                    ('Apollo',  'plural'),
                    ('Thales',  'dual'),
                    ('Thales',  'plural'),
                    ('Oedipus', 'dual'),
                    ('Oedipus', 'plural'),
                    ('Zeus',    'dual'),
                    ('Zeus',    'plural'),
                }),
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

write('flashcards/ancient-greek/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = greek_language.grammar.stock_modifier,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
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
    ))


write('flashcards/ancient-greek/adpositions.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = greek_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', 'n', 'noun'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
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
    ))

write('flashcards/ancient-greek/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = greek_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])},
            ],
        ) for demonstration in demonstrations],
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

write('flashcards/ancient-greek/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            stock_modifier = greek_language.grammar.stock_modifier,
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'noun'], ['parentheses', ['participle-seme', 'cloze', 'v','verb'], ['modifier-seme', 'np', 'participle-seme', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        DictTupleIndexing([
            'tense', 'voice', 'progress', 'mood', 
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

