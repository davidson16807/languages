import time

start_time = time.time()

from tools.labels import TermLabelEditing
from tools.parsing import TermParsing
from tools.dictstores import DictSpace, UniformDictLookup, NestedDictLookup
from tools.indexing import DictTupleIndexing
from tools.languages import Language
from tools.orthography import Orthography
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleFormatting, RuleSyntax
)
from tools.cards import DeckGeneration
from tools.inflections import (
    dict_bundle_to_map,
    LanguageSpecificTextDemonstration, LanguageSpecificEmojiDemonstration,
    card_formatting,
    tsv_parsing,
    finite_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, 
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    termaxis_to_terms,
    tag_defaults, 
    parse_any,
    write, 
    emoji_casts,
    template_verb_whitelist,
    template_dummy_lookup,
    template_tree_lookup,
    noun_template_whitelist,
)
from languages.english import native_english_demonstration

label_editing = TermLabelEditing()
deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

def definiteness(machine, tree, memory):
    '''creates articles when necessary to express definiteness'''
    definiteness = memory['definiteness'] if 'definiteness' in memory else 'indefinite'
    subjectivity = memory['subjectivity']
    nounform = memory['noun-form']
    if definiteness == 'definite' and subjectivity != 'addressee' and nounform != 'personal': 
        return [['det','the'], tree]
    else:
        return tree

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/greek/attic/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/greek/attic/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/greek/attic/finite-conjugations.tsv')),
                # *nonfinite_annotation.annotate(
                #     tsv_parsing.rows('data/inflection/indo-european/greek/attic/nonfinite-conjugations.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/greek/attic/common-noun-declensions.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/greek/attic/adjective-agreements.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/greek/attic/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/greek/attic/pronoun-possessives.tsv')),
            ])),
    ),
    RuleSyntax(
        parse_any.tokens('adposition det adj n np clause'),
        parse_any.terms('subject verb direct-object indirect-object adverbial'), 
    ),
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = [
        {'n': definiteness}, # Greek needs annotations to simplify the definition of articles
    ]
)

foreign_termaxis_to_terms = {
    **termaxis_to_terms,
    **parse_any.termaxis_to_terms('''
        gender :  masculine feminine neuter
        number :  singular dual plural
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic unfinished finished
        tense  :  present past future
        voice  :  active middle passive
        mood   :  indicative subjunctive imperative optative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object adnominal indirect-object adverbial
    '''),
    **parse_any.token_to_tokens('''
        verb : release be go
        noun : young-man soldier polity village person street gift 
         circumnavigation bone hero fish oak city axe town 
         master cow old-woman echo Clio crow vulture rug
         giant tooth old-man property Greek winter Titan
         light-ray shepherd guide neighbor tipstaff ichor chaff
         orator father man Demeter Socrates Pericles arrow
         foundation shame Ares woman Thales Oedipus fire
         Apollo knee wood Zeus liver dog ship ear water hand
        # adjective:
    '''),
}

foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    Orthography('greek', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_focus,
    [('∅',''), ('-','')]
)

transliteration = parse_any.tokenpoints('''
    αι  ae
    αυ  au
    ευ  eu
    ηυ  iu
    ου  ou
    υι  ui
    ωυ  ou
    οι  oe
    υι  ui
    ει  ei
    γγ  ng
    γκ  nk
    γξ  nx
    γχ  nch
 #\\bρ  rh

    ά   á
    ὰ   à
    ᾶ   ã
    ἀ   a
    ἄ   á
    ἂ   à
    ἆ   ã
    ἁ   ha
    ἅ   há
    ἃ   hà
    ἇ   hã
    ᾱ   ā
    ᾰ   ă
    ᾳ   a
    ᾴ   á
    ᾲ   à
    ᾷ   ã
    ᾀ   a
    ᾄ   á
    ᾂ   à
    ᾆ   ã
    ᾁ   ha
    ᾅ   há
    ᾃ   hà
    ᾇ   hã
    έ   é
    ὲ   è
    ἐ   e
    ἔ   é
    ἒ   è
    ἑ   he
    ἕ   hé
    ἓ   hè
    ή   é
    ὴ   è
    ῆ   ẽ
    ἠ   e
    ἤ   é
    ἢ   è
    ἦ   ẽ
    ἡ   he
    ἥ   hé
    ἣ   hè
    ἧ   hẽ
    ῃ   e
    ῄ   é
    ῂ   è
    ῇ   ẽ
    ᾐ   e
    ᾔ   é
    ᾒ   è
    ᾖ   ẽ
    ᾑ   hē
    ᾕ   hé
    ᾓ   hè
    ᾗ   hẽ
    ί   í
    ὶ   ì
    ῖ   ĩ
    ἰ   i
    ἴ   í
    ἲ   ì
    ἶ   ĩ
    ἱ   hi
    ἵ   hí
    ἳ   hì
    ἷ   hĩ
    ϊ   i
    ΐ   í
    ῒ   ì
    ῗ   ĩ
    ῑ   ī
    ῐ   ĭ
    ό   ó
    ὸ   ò
    ὀ   o
    ὄ   ó
    ὂ   ò
    ὁ   o
    ὅ   ó
    ὃ   ò
    ῤ   r
    ῥ   rh
    ῠ̔   hy̆
    ῡ̔   hȳ
    ύ   ý
    ὺ   ỳ
    ῦ   ỹ
    ὐ   y
    ὔ   ý
    ὒ   ỳ
    ὖ   ỹ
    ὑ   hy
    ὕ   hý
    ὓ   hỳ
    ὗ   hỹ
    ϋ   y
    ΰ   ý
    ῢ   ỳ
    ῧ   ỹ
    ῡ   ȳ
    ῠ   y̆
    ώ   ó
    ὼ   ò
    ῶ   õ
    ὠ   o
    ὤ   ó
    ὢ   ò
    ὦ   õ
    ὡ   ho
    ὥ   hó
    ὣ   hò
    ὧ   hõ
    ῳ   o
    ῴ   ó
    ῲ   ò
    ῷ   õ
    ᾠ   o
    ᾤ   ó
    ᾢ   ò
    ᾦ   õ
    ᾡ   ho
    ᾥ   hó
    ᾣ   hò
    ᾧ   hõ

    α   a
    β   b
    γ   g
    δ   d
    ε   e
    ζ   z
    η   e
    θ   th
    ι   i
    κ   c
    λ   l
    μ   m
    ν   n
    ξ   x
    ο   o
    π   p
    ρ   r
    σ   s
    ς   s
    τ   t
    υ   y
    φ   ph
    χ   ch
    ψ   ps
    ω   o
    ∅
    -
    ''')

transliterated_demonstration = LanguageSpecificTextDemonstration(
    Orthography('greek', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_side_note,
    transliteration
)

emoji_demonstration = LanguageSpecificEmojiDemonstration(
    emoji_casts[2],
    card_formatting.emoji_focus,
)

demonstrations = [
    emoji_demonstration,
    foreign_demonstration,
    transliterated_demonstration,
    native_english_demonstration,
]

axis = {
    axis: DictSpace(axis, DictTupleIndexing([axis]), {axis: tags})
    for (axis, tags) in foreign_termaxis_to_terms.items()
}

constant = {
    tag: DictSpace(tag, DictTupleIndexing([axis]), {axis: tag})
    for (tag, axis) in foreign_term_to_termaxis.items()
}

defaults = DictSpace(
    'defaults',
    DictTupleIndexing([]),
    {
        **tag_defaults,
        'noun':'man',
    }
)

# stimuli are typically only subjects or direct-objects
subjectivity_role_blacklist = parse.termmask(
    'subjectivity_role_blacklist', 
    'subjectivity role',
    '''
    adverbial      stimulus
    ''')

subjectivity_valency_whitelist = parse.termmask(
    'subjectivity_valency_whitelist', 
    'valency subjectivity',
    '''
    intransitive  subject
    transitive    direct-object
    intransitive  addressee
    intransitive  adnominal
    intransitive  adverbial
    ''')

subjectivity_motion_traversal = parse.termpath(
    'subjectivity_motion_traversal', 
    'subjectivity motion',
    '''
    subject       associated
    addressee     associated
    direct-object associated
    adnominal     associated
    adverbial     acquired
    adverbial     associated
    adverbial     departed
#    adverbial     surpassed
#    adverbial     leveraged
    ''')

conjugation_subject_traversal = parse.termpath(
    'conjugation_subject_traversal', 
    'person number gender',
    '''
    1  singular neuter
    2  singular feminine
    3  singular masculine
    1  plural   neuter
    2  plural   feminine
    3  plural   masculine
    ''')

finite_tense_progress_traversal = parse.termpath(
    'finite_tense_progress_traversal', 
    'tense progress',
    '''
    present  atelic
    future   atelic
    past     unfinished
    past     finished
    ''')

pronoun_traversal = parse.tokenpath(
    'pronoun_traversal', 
    'noun person number gender',
    '''
    man    1 singular neuter   
    woman  2 singular feminine 
    man    3 singular masculine
    woman  3 singular feminine 
    snake  3 singular neuter   
    man    3 dual     masculine 
    woman  3 dual     feminine  
    man    3 dual     neuter    
    man    1 plural   neuter   
    woman  2 plural   feminine 
    man    3 plural   masculine
    woman  3 plural   feminine 
    man    3 plural   neuter   
    ''')

gender_agreement_traversal = parse.tokenpath(
    'gender_agreement_traversal', 
    'gender noun',
    '''
    masculine  man   
    feminine   woman 
    neuter     animal
    ''')

gender_noun_whitelist = parse.tokenmask(
    'gender_noun_whitelist', 
    'noun gender',
    '''
    animal     neuter
    attention  feminine
    bird       masculine
    bird       feminine
    boat       feminine
    book       neuter
    bug        neuter
    dog        masculine
    dog        feminine
    door       feminine
    clothing   feminine
    daughter   feminine
    drum       neuter
    enemy      masculine
    fire       neuter
    food       neuter
    gift       neuter
    glass      feminine
    guard      masculine
    horse      masculine
    horse      feminine
    house      masculine
    livestock  neuter
    love       feminine
    idea       feminine
    man        masculine
    money      neuter
    monster    neuter
    name       neuter
    name       feminine
    rock       masculine
    rock       feminine
    rock       neuter
    rope       feminine
    size       neuter
    son        masculine
    sound      masculine
    warmth     feminine
    water      neuter
    way        feminine
    wind       masculine
    window     feminine
    woman      feminine
    work       neuter

    young-man  neuter
    soldier    masculine
    polity     masculine
    village    feminine
    village    neuter
    person     feminine
    street     masculine
    street     feminine
    hero       neuter
    fish       masculine
    oak        masculine
    city       feminine
    axe        feminine
    town       masculine
    town       neuter
    master     neuter
    old-woman  masculine
    cow        feminine
    echo       masculine
    echo       feminine
    Clio       feminine
    Clio       masculine
    crow       feminine
    vulture    masculine
    rug        masculine
    giant      masculine
    tooth      masculine
    old-man    masculine
    property   masculine
    Greek      neuter
    winter     masculine
    Titan      masculine
    light-ray  masculine
    shepherd   feminine
    guide      masculine
    neighbor   masculine
    ichor      masculine
    ichor      feminine
    chaff      masculine
    orator     masculine
    father     masculine
    Demeter    masculine
    Socrates   feminine
    Socrates   masculine
    Socrates   neuter
    Pericles   masculine
    arrow      masculine
    shame      neuter
    Ares       feminine
    Thales     masculine
    Oedipus    masculine
    Apollo     masculine
    knee       masculine
    wood       neuter
    Zeus       neuter
    Zeus       feminine
    liver      masculine
    ship       neuter
    ear        feminine
    hand       neuter
    '''
)

possession_traversal = parse.tokenpath(
    'possession_traversal', 
    'gender noun',
    '''
    masculine  brother      
    feminine   sister 
    neuter     gift
    ''')

possessor_possession_whitelist = parse.tokenmask(
    'possessor_possession_whitelist', 
    'possessor-noun noun',
    '''
    man-possessor     brother
    man-possessor     sister
    man-possessor     gift
    woman-possessor   brother
    woman-possessor   sister
    woman-possessor   gift
    animal-possessor  brother
    animal-possessor  sister
    animal-possessor  name
    ''')

possessor_pronoun_traversal = label_editing.termpath(
    parse.tokenpath(
        'possessor_pronoun_traversal', 
        'noun person number gender',
        '''
        man    1 singular neuter   
        woman  2 singular feminine 
        man    3 singular masculine
        woman  3 singular feminine 
        snake  3 singular neuter   
        man    1 plural   neuter   
        woman  2 plural   feminine 
        man    3 plural   masculine
        woman  3 plural   feminine 
        man    3 plural   neuter   
        '''), 
    'possessor')

verb_voice_blacklist = parse.termmask(
    'verb_voice_blacklist', 
    'verb  voice',
    '''
    be       middle
    gone     middle
    ''')

#useful for debugging
def head(store):
    print(str(store)[:3000])

tense_progress_mood_voice_verb_traversal = (
    (((
          axis['valency']
        * finite_tense_progress_traversal
        * axis['mood'])
        * axis['voice'])
        * axis['verb'])
    - verb_voice_blacklist
) * constant['subject'] 

conjugation_traversal = template_dummy_lookup(tense_progress_mood_voice_verb_traversal)

roles = parse_any.termspace('role', 'role', 
    'role: stimulus possessor location interior surface presence aid lack interest time company')

subjectivity_motion_role_traversal = (
    (  subjectivity_motion_traversal
     * roles )
    - subjectivity_role_blacklist
)

valency_subjectivity_motion_role_traversal = (
      axis['valency'] 
    * subjectivity_motion_role_traversal
) & subjectivity_valency_whitelist

demonstration_verbs = parse_any.tokenspace('demonstration-verbs', 'verb',
    'verb: ∅ swim fly rest walk crawl flow direct work resemble eat endure warm ' +
        ' cool fall change occupy show see watch startle displease appear be')

declension_noun_traversal = (
    template_dummy_lookup(
        (demonstration_verbs
        * axis['template']
        * constant['active']
        * valency_subjectivity_motion_role_traversal)
        & template_verb_whitelist)
)

write('flashcards/ancient-greek/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = UniformDictLookup(
                'clause [test [np n] [vp cloze v verb]] [dummy np [adposition] n]',)
        ) for demonstration in demonstrations],
        defaults.override(
              conjugation_subject_traversal 
            * conjugation_traversal
        ),
        tag_templates ={
            'test'    : parse.termaxis_to_term('personal associated agent subject'),
            'dummy'   : parse.termaxis_to_term('common 3 singular masculine'),
        },
    ))

"""
write('flashcards/ancient-greek/participle-declension.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = UniformDictLookup(
                '''clause test [
                    [np participle clause [np n] parentheses [vp cloze v verb] [dummy np [adposition] n]]
                    [vp active present atelic v appear]
                ]'''),
        ) for demonstration in demonstrations],
        defaults.override(
            (   conjugation_traversal
              & constant['indicative']
              & constant['atelic'])
        ),
        tag_templates ={
            'test'    : parse.termaxis_to_term('common definite associated agent subject'),
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'participle' : parse.termaxis_to_term('common definite participle subject'),
        },
    ))
"""

write('flashcards/ancient-greek/adpositions.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [
                {'declined': list_tools.replace(['n'])},
                {'adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            (declension_noun_traversal * constant['man'])
            & constant['adverbial']
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal definite'),
        },
    ))

write('flashcards/ancient-greek/common-noun-declension.html',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((declension_noun_traversal * axis['number'] * axis['noun'])
                & noun_template_whitelist)
                * axis['gender'])
                & gender_noun_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))


write('flashcards/ancient-greek/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            ((pronoun_traversal * declension_noun_traversal * constant['personal'])
            & noun_template_whitelist)
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term(''),
        },
    ))

# write('flashcards/ancient-greek/adjective-agreement.html', 
#     deck_generation.generate(
#         [demonstration.generator(
#             tree_lookup = template_tree_lookup,
#             substitutions = [{'declined': list_tools.replace([['cloze','adj','adjective'], ['n']])}],
#         ) for demonstration in demonstrations], 
#         defaults.override(
#             ((  axis['number']
#              * gender_agreement_traversal
#              * declension_noun_traversal
#              * axis['adjective'])
#             & noun_template_whitelist) 
#         ),
#         tag_templates ={
#             'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
#             'test'       : parse.termaxis_to_term('common definite'),
#         },
#     ))

write('flashcards/ancient-greek/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace([['cloze','det'], ['common', 'n']])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((  axis['number'] 
               * possession_traversal 
               * declension_noun_traversal 
               * possessor_pronoun_traversal)
              & possessor_possession_whitelist)
             * constant['exclusive-possessor']  
             * constant['familiar-possessor']
            )
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal-possessive adefinite'),
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')
