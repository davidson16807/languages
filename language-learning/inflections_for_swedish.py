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


def definiteness(machine, tree, memory):
    '''creates articles when necessary to express definiteness'''
    definiteness = memory['definiteness'] if 'definiteness' in memory else 'indefinite'
    subjectivity = memory['subjectivity']
    number = memory['number']
    nounform = memory['noun-form']
    if definiteness == 'definite' and subjectivity != 'addressee' and nounform != 'personal' and 'adjective' in memory: 
        return [['det','the'], tree]
    if (definiteness, number) == ('indefinite', 'singular') and subjectivity != 'addressee' and nounform != 'personal': 
        return [['det','a'], tree]
    if definiteness == 'adefinite': 
        return ['indefinite', tree]
    else:
        return tree

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/conjugations.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/common-noun-declensions.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/germanic/swedish/modern/adjective-agreements.tsv')),
            ])),
    ),
    RuleSyntax(
        parse_any.tokens('adposition det adj np n clause'),
        parse_any.terms('subject verb direct-object indirect-object adverbial'),
    ),
    # TODO: this should technically be SOV, but V2 ordering applies to main clauses which mainly produces SVO
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = [
        {'n': definiteness}, # needs annotations to simplify the definition of articles
    ]
)

foreign_termaxis_to_terms = {
    **termaxis_to_terms,
    **parse_any.termaxis_to_terms('''
        gender :  masculine feminine neuter
        number :  singular plural
        definiteness: definite indefinite
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic
        tense  :  present past
        voice  :  active passive
        mood   :  indicative subjunctive imperative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object adnominal indirect-object adverbial
    '''),
    **parse_any.token_to_tokens('''
        verb : be go call close read sew strike
        noun : girl rose dog mother evening enemy book bee eye animal man
        adjective: strong
    '''),
}

foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    Orthography('latin', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_focus,
    [('∅','')]
)

emoji_demonstration = LanguageSpecificEmojiDemonstration(
    emoji_casts[2],
    card_formatting.emoji_focus,
)

demonstrations = [
    emoji_demonstration,
    foreign_demonstration,
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
    intransitive  adverbial
    ''')

subjectivity_motion_traversal = parse.termpath(
    'subjectivity_motion_traversal', 
    'subjectivity motion',
    '''
    subject       associated
    direct-object associated
    adverbial     acquired
    adverbial     associated
    adverbial     departed
#    adverbial     surpassed
#    adverbial     leveraged
    ''')

# we assign each person a gender to make them easier to distinguish
conjugation_subject_traversal = parse.termpath(
    'conjugation_subject_traversal', 
    'person number gender',
    '''
    1  singular neuter
    2  singular feminine
    3  singular masculine
    1  plural   neuter
    2  plural   feminine
    3  plural   neuter
    ''')


mood_tense_polarity_whitelist = parse.termmask(
    'mood_tense_whitelist', 
    'mood tense polarity',
    '''
    indicative   present affirmative
    indicative   past    affirmative
    subjunctive  present affirmative
    subjunctive  past    affirmative
    imperative   present affirmative
    imperative   present negative
    ''')

finite_tense_progress_traversal = parse.termpath(
    'finite_tense_progress_traversal', 
    'tense progress',
    '''
    present  atelic
    past     atelic
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
    man    1 plural   neuter
    woman  2 plural   feminine
    man    3 plural   masculine
    man    3 plural   neuter   
    ''')

gender_agreement_traversal = parse.tokenpath(
    'gender_agreement_traversal', 
    'gender noun',
    '''
    masculine man
    feminine  woman
    neuter    animal
    ''')

gender_noun_whitelist = parse.tokenmask(
    'gender_noun_whitelist', 
    'noun gender',
    '''
    animal  neuter
    attention masculine
    bird    masculine
    boat    masculine
    book    masculine
    brother masculine
    bug     neuter
    clothing  neuter
    daughter  feminine
    dog masculine
    door    masculine
    drum    masculine
    enemy   masculine
    fire    masculine
    food    masculine
    gift    masculine
    glass   neuter
    guard   masculine
    horse   masculine
    house   neuter
    livestock neuter
    love    masculine
    idea    masculine
    man     masculine
    monster neuter
    name    neuter
    rock    masculine
    rope    neuter
    size    masculine
    son     masculine
    size    masculine
    sound   neuter
    warmth  masculine
    warmth  neuter
    water   neuter
    way     masculine
    wind    masculine
    window  neuter
    woman   masculine
    work    neuter

    girl    feminine
    rose    masculine
    mother  feminine
    evening masculine
    bee     neuter
    eye     neuter
    '''
)

possession_traversal = parse.tokenpath(
    'possession_traversal', 
    'gender noun',
    '''
    masculine brother
    neuter    house
    ''')

possessor_possession_whitelist = parse.tokenmask(
    'possessor_possession_whitelist', 
    'possessor-noun noun',
    '''
    man-possessor    brother
    man-possessor    house
    snake-possessor  brother
    snake-possessor  name
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
        man    1 plural   masculine
        woman  2 plural   feminine 
        man    3 plural   neuter   
        '''), 
    'possessor')

#useful for debugging
def head(store, n=3000):
    print(str(store)[:n])

tense_progress_mood_voice_verb_traversal = ((
    ((((
          axis['valency']
        * finite_tense_progress_traversal
        * axis['mood']
        * axis['polarity'])
        & mood_tense_polarity_whitelist)
        * axis['voice'])
        * axis['verb'])
) * constant['subject'])

conjugation_traversal = template_dummy_lookup(tense_progress_mood_voice_verb_traversal)

roles = parse_any.termspace('role', 'role', 
    'role: stimulus possessor location interior surface subsurface presence aid lack interest time company')

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

adposition_noun_traversal = (
    template_dummy_lookup(
        (demonstration_verbs
        * axis['template']
        * constant['active']
        * valency_subjectivity_motion_role_traversal)
        & template_verb_whitelist)
)

declension_noun_traversal = (
    adposition_noun_traversal
    & parse.termspace('declension-subjectivity', 'subjectivity', 
        'subjectivity: subject direct-object')
)


deck_path = 'flashcards/germanic/swedish'
deck_format = 'tsv'

write(f'{deck_path}/finite-conjugation.{deck_format}', 
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
write(f'{deck_path}/participle-declension.{deck_format}', 
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

write(f'{deck_path}/adpositions.{deck_format}', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [
                {'declined': list_tools.replace(['n'])},
                {'adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            (adposition_noun_traversal * constant['man'])
            & constant['adverbial']
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal definite'),
        },
    ))

write(f'{deck_path}/common-noun-{deck_format}.tsv',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (declension_noun_traversal * axis['definiteness'] * axis['number'] * axis['noun'])
                & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common'),
        },
    ))

write(f'{deck_path}/pronoun-declension.{deck_format}', 
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

write(f'{deck_path}/adjective-agreement.{deck_format}', 
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

write(f'{deck_path}/pronoun-possessives.{deck_format}', 
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
            'test'       : parse.termaxis_to_term('personal-possessive masculine'),
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')
 