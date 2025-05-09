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
    RuleTools, RuleFormatting, 
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
from languages.romance import ModernRomanceRuleSyntax
from languages.english import native_english_demonstration

label_editing = TermLabelEditing()
deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/finite-conjugations.tsv')),
                # *nonfinite_annotation.annotate(
                #     tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/nonfinite-conjugations.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/common-noun-declensions.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/romanian/modern/adjective-agreements.tsv')),
            ])),
    ),
    ModernRomanceRuleSyntax(
        parse_any.tokens('adposition det adj n np clause'),
        'subject personal-indirect-object personal-direct-object verb common-direct-object common-indirect-object adverbial'.split(), 
    ),
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = [
    ]
)

foreign_termaxis_to_terms = {
    **termaxis_to_terms,
    **parse_any.termaxis_to_terms('''
        gender :  masculine feminine neuter
        number :  singular plural
        definiteness: definite indefinite
        formality: informal
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic finished unfinished
        polarity: affirmative negative
        tense  :  present past
        voice  :  active
        mood   :  indicative subjunctive imperative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object adnominal indirect-object adverbial adnominal
        degree :  positive
    '''),
    **parse_any.token_to_tokens('''
        adjective: good bad
        verb : give see choose know have be want sit throw take drink dry continue eat
        noun : man woman name brother book # father ox uncle aunt tea
    '''),
}

foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    Orthography('latin', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_focus,
    [('∅',''), 
     ('-',''),]
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

# vocatives for pronouns are not known
subjectivity_nounform_blacklist = parse.termmask(
    'subjectivity_nounform_blacklist', 
    'subjectivity noun-form',
    '''
    addressee  personal
    addressee  demonstrative
    ''')

conjugation_subject_traversal = parse.termpath(
    'conjugation_subject_traversal', 
    'person number gender',
    '''
    1  singular masculine 
    2  singular feminine  
    3  singular masculine 
    1  plural   masculine 
    2  plural   feminine  
    3  plural   masculine 
    ''')


mood_tense_polarity_whitelist = parse.termmask(
    'mood_tense_whitelist', 
    'mood tense polarity progress',
    '''
    indicative  present affirmative atelic
    indicative  present affirmative finished
    indicative  past    affirmative unfinished
    indicative  past    affirmative finished
    subjunctive present affirmative atelic
    imperative  present affirmative atelic
    imperative  present negative    atelic
    ''')

finite_tense_aspect_traversal = parse.termpath(
    'finite_tense_aspect_traversal', 
    'tense progress',
    '''
    present atelic
    present finished
    past    unfinished
    past    finished
    ''')

pronoun_traversal = parse_any.tokenpath(
    'pronoun_traversal', 
    'noun person number gender',
    '''
    man    1 singular neuter   
    woman  2 singular feminine 
    man    3 singular masculine
    woman  3 singular feminine 
    man    1 plural   neuter   
    woman  2 plural   feminine 
    man    3 plural   masculine
    woman  3 plural   feminine 
    ''')

gender_agreement_traversal = parse.tokenpath(
    'gender_agreement_traversal', 
    'gender noun',
    '''
    masculine  man   
    feminine   woman 
    ''')

gender_noun_whitelist = parse.tokenmask(
    'gender_noun_whitelist', 
    'noun gender',
    '''
    animal  masculine
    animal  neuter
    attention   feminine
    bird    feminine
    boat    feminine
    book    feminine
    brother masculine
    bug feminine
    clothing    feminine
    daughter    feminine
    dog masculine
    door    feminine
    drum    feminine
    enemy   masculine
    fire    neuter
    food    neuter
    gift    neuter
    glass   feminine
    guard   feminine
    horse   masculine
    house   feminine
    livestock   neuter
    love    feminine
    idea    feminine
    man masculine
    money   masculine
    monster masculine
    name    neuter
    rock    feminine
    rope    feminine
    size    feminine
    sister  feminine
    son masculine
    sound   neuter
    warmth  feminine
    water   feminine
    way feminine
    wind    neuter
    window  feminine
    woman   feminine
    work    feminine
    ''')

possession_traversal = parse.tokenpath(
    'possession_traversal', 
    'gender noun',
    '''
    masculine  brother      
    feminine   sister 
    ''')

possessor_possession_whitelist = parse.tokenmask(
    'possessor_possession_whitelist', 
    'possessor-noun noun',
    '''
    man-possessor    brother
    man-possessor    sister
    woman-possessor  brother
    woman-possessor  sister
    ''')

possessor_pronoun_traversal = label_editing.termpath(
    parse_any.tokenpath(
        'possessor_pronoun_traversal', 
        'noun person number gender',
        '''
        man    1 singular neuter   
        woman  2 singular feminine 
        man    3 singular masculine
        woman  3 singular feminine 
        man    1 plural   neuter   
        woman  2 plural   feminine 
        man    3 plural   masculine
        woman  3 plural   feminine 
        '''), 
    'possessor')

agreement_roles = parse.termmask(
    'agreement_roles', 
    'role subjectivity',
    '''
    stimulus subject
    stimulus direct-object
    ''')

#useful for debugging
def head(store):
    print(str(store)[:3000])

tense_progress_mood_voice_verb_traversal = ((
    ((((
          axis['valency']
        * finite_tense_aspect_traversal
        * axis['mood']
        * axis['polarity'])
        & mood_tense_polarity_whitelist)
        * axis['voice'])
        * axis['verb'])
) * constant['subject'])

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

write('flashcards/romance/romanian/finite-conjugation.html', 
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

write('flashcards/romance/romanian/adpositions.html', 
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

write('flashcards/romance/romanian/common-noun-declension.html',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((declension_noun_traversal * axis['definiteness'] * axis['number'] * axis['noun'])
                & noun_template_whitelist)
                * axis['gender'])
                & gender_noun_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common'),
        },
    ))

write('flashcards/romance/romanian/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            ((pronoun_traversal * declension_noun_traversal * constant['personal'])
            & noun_template_whitelist)
            - subjectivity_nounform_blacklist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term(''),
        },
    ))

write('flashcards/romance/romanian/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace([['cloze','adj','adjective'], ['n']])}],
        ) for demonstration in demonstrations], 
        defaults.override(
            ((  axis['number']
             * gender_agreement_traversal
             * declension_noun_traversal
             * axis['degree']
             * axis['adjective'])
            & noun_template_whitelist
            & agreement_roles) 
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))

write('flashcards/romance/romanian/pronoun-possessives.html', 
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
            'test'       : parse.termaxis_to_term('personal-possessive definite'),
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')
