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
    RuleTools, RuleFormatting, RuleSyntax, 
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

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/slavic/russian/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/slavic/russian/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/slavic/russian/conjugations.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/slavic/russian/common-noun-declensions.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/slavic/russian/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/slavic/russian/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/slavic/russian/adjective-agreements.tsv')),
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
    substitutions = []
)

# breakpoint()

foreign_termaxis_to_terms = {
    **termaxis_to_terms,
    **parse_any.termaxis_to_terms('''
        gender :  masculine feminine neuter
        animacy:  animate inanimate
        number :  singular plural
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic
        tense  :  present past future
        voice  :  active
        mood   :  indicative imperative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object adnominal indirect-object adverbial
    '''),
    **parse_any.token_to_tokens('''
        adjective: new blue tall good big
        noun : job bathhouse line movie writer hero comment building place sea bone mouse man
        verb : give eat live call go write read return draw spit dance be-able 
            bake carry lead sweep row steal convey climb wash beat wind 
            pour drink sew swim pass-for speak love catch sink feed ask pay forgive
    '''),
}

foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    Orthography('cyrillic', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_focus,
    [('∅',''), ('-','')]
)

transliteration = parse_any.tokenpoints('''
    ае      aye
    ее      eye
    ёе      ёye
    ие      iye
    йе      yye
    ье      'ye
    ъе      "ye
    #^е     ye

    аё      ayё
    её      eyё
    ёё      ёyё
    иё      iyё
    йё      yyё
    ьё      'yё
    ъё      "yё
    #^ё     yё

    ай      аy·
    уй      уy·
    ый      ыy·
    эй      эy·

    аэ      ae
    еэ      ee
    ёэ      ёe
    иэ      ie
    йэ      ye
    ьэ      'e
    ъэ      "e

    ыа      y·а
    ыу      y·у
    ыы      y·ы
    ыэ      y·э

    аы      a·y
    еы      e·y
    ёы      ё·y
    иы      i·y
    йы      y·y
    ьы      '·y
    ъы      "·y

    а       a
    б       b
    в       v
    г       g
    д       d
    е       e
    ё       ё
    ж       zh
    з       z
    и       i
    й       y
    к       k
    л       l
    м       m
    н       n
    о       o
    п       p
    р       r
    с       s
    т       t
    у       u
    ф       f
    х       kh
    ц       ts
    ч       ch
    ш       sh
    щ       shch
    ъ       "
    ы       y
    ь       '
    э       ·e
    ю       yu
    я       ya
    тс      t·s
    шч      sh·ch

    ∅
    -
    ''')

transliterated_demonstration = LanguageSpecificTextDemonstration(
    Orthography('cyrillic', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_side_note,
    # [('∅',''), ('-','')]
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

mood_tense_whitelist = parse.termmask(
    'mood_tense_whitelist', 
    'mood tense',
    '''
    indicative   present
    indicative   past
    indicative   future
    imperative   present
    ''')

mood_person_whitelist = parse.termmask(
    'mood_person_whitelist', 
    'mood person',
    '''
    indicative   1
    indicative   2
    indicative   3
    imperative   2
    ''')

finite_tense_progress_traversal = parse.termpath(
    'finite_tense_progress_traversal', 
    'tense progress',
    '''
    present  atelic
    future   atelic
    #past     unfinished
    #past     finished
    ''')

pronoun_traversal = parse.tokenpath(
    'pronoun_traversal', 
    'noun person number gender',
    '''
    man    1 singular masculine   
    woman  1 singular feminine 
    snake  1 singular neuter 
    man    2 singular masculine   
    woman  2 singular feminine 
    snake  2 singular neuter 
    man    3 singular masculine
    woman  3 singular feminine 
    snake  3 singular neuter   
    man    1 plural masculine   
    woman  1 plural feminine 
    snake  1 plural neuter 
    man    2 plural masculine   
    woman  2 plural feminine 
    snake  2 plural neuter 
    man    3 plural masculine
    woman  3 plural feminine 
    snake  3 plural neuter   
    ''')

gender_agreement_traversal = parse.tokenpath(
    'gender_agreement_traversal', 
    'animacy gender noun',
    '''
    animate   masculine  man   
    animate   feminine   woman 
    animate   neuter     animal
    inanimate masculine  house   
    inanimate feminine   book
    inanimate neuter     building
    ''')

gender_noun_whitelist = parse.tokenmask(
    'gender_noun_whitelist', 
    'noun gender animacy',
    '''

    animal    neuter    animate
    attention neuter    inanimate
    bird      feminine  animate
    boat      feminine  inanimate
    book      feminine  inanimate
    brother   masculine animate
    bug       feminine  animate
    clothing  feminine  inanimate
    daughter  feminine  animate
    dog       feminine  animate
    door      feminine  inanimate
    drum      masculine inanimate
    enemy     masculine animate
    fire      masculine inanimate
    food      feminine  inanimate
    gift      masculine inanimate
    glass     neuter    inanimate
    guard     masculine animate
    horse     feminine  animate
    house     masculine inanimate
    livestock masculine inanimate
    love      feminine  inanimate
    idea      feminine  inanimate
    man       masculine animate
    money     feminine  inanimate
    monster   neuter    animate
    name      neuter    inanimate
    rock      masculine inanimate
    rope      masculine inanimate
    size      feminine  inanimate
    son       masculine animate
    sound     masculine inanimate
    warmth    neuter    inanimate
    water     feminine  inanimate
    way       masculine inanimate
    wind      masculine inanimate
    window    neuter    inanimate
    woman     feminine  animate
    work      feminine  inanimate

    job       feminine  inanimate
    bathhouse feminine  inanimate
    line      feminine  inanimate
    movie     masculine inanimate
    writer    masculine animate
    hero      masculine animate
    comment   masculine inanimate
    building  neuter    inanimate
    place     neuter    inanimate
    sea       neuter    inanimate
    bone      feminine  inanimate
    mouse     feminine  animate
    '''
)

possession_traversal = parse.tokenpath(
    'possession_traversal', 
    'animacy gender noun',
    '''
    animate   masculine  brother      
    animate   feminine   sister 
    animate   neuter     animal
    inanimate masculine  gift
    inanimate feminine   money
    inanimate neuter     name
    ''')

possessor_possession_whitelist = parse.tokenmask(
    'possessor_possession_whitelist', 
    'possessor-noun noun',
    '''
    man-possessor     brother
    man-possessor     sister
    man-possessor     animal
    man-possessor     gift
    man-possessor     size  
    man-possessor     name  
    woman-possessor   brother
    woman-possessor   sister
    woman-possessor   animal
    woman-possessor   gift
    woman-possessor   size  
    woman-possessor   name  
    animal-possessor  brother
    animal-possessor  sister
    animal-possessor  animal
    animal-possessor  gift
    animal-possessor  size  
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

#useful for debugging
def head(store):
    print(str(store)[:3000])

tense_progress_mood_voice_verb_traversal = (
    ((((
          axis['valency']
        * finite_tense_progress_traversal
        * axis['mood'])
        & mood_tense_whitelist)
        * axis['voice'])
        * axis['verb'])
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

write('flashcards/slavic/russian/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = UniformDictLookup(
                'clause [test [np n] [vp cloze v verb]] [dummy np [adposition] n]',)
        ) for demonstration in demonstrations],
        defaults.override(
              conjugation_subject_traversal 
            * conjugation_traversal
            & mood_person_whitelist
        ),
        tag_templates ={
            'test'    : parse.termaxis_to_term('personal associated agent subject'),
            'dummy'   : parse.termaxis_to_term('common 3 singular masculine'),
        },
    ))

"""
write('flashcards/slavic/russian/participle-declension.html', 
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

write('flashcards/slavic/russian/adpositions.html', 
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

write('flashcards/slavic/russian/common-noun-declension.html',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((declension_noun_traversal * axis['number'] * axis['noun'])
                & noun_template_whitelist)
                * axis['gender'] * axis['animacy'])
                & gender_noun_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))


write('flashcards/slavic/russian/pronoun-declension.html', 
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

write('flashcards/slavic/russian/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace([['cloze','adj','adjective'], ['n']])}],
        ) for demonstration in demonstrations], 
        defaults.override(
            ((  axis['number']
             * gender_agreement_traversal
             * declension_noun_traversal
             * axis['adjective'])
            & noun_template_whitelist) 
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))

write('flashcards/slavic/russian/pronoun-possessives.html', 
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
