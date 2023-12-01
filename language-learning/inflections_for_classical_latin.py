import time

start_time = time.time()

from tools.labels import TermLabelEditing
from tools.parsing import TokenParsing, TermParsing
from tools.dictstores import DictSpace, UniformDictLookup, NestedDictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.languages import Language
from tools.orthography import Orthography
from tools.nodemaps import (
    ListTools, ListGrammar, ListSemantics,
    RuleTools, RuleSyntax, RuleFormatting, 
)
from tools.cards import DeckGeneration
from inflections import (
    dict_bundle_to_map,
    LanguageSpecificTextDemonstration, LanguageSpecificEmojiDemonstration, english_demonstration,
    card_formatting,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
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

label_editing = TermLabelEditing()
deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/aspect-usage.tsv'))),
        debug=True,
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/finite-conjugations.tsv')),
                *nonfinite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/nonfinite-conjugations.tsv')),
                *filter(has_annotation('language','classical-latin'),
                    declension_verb_annotation.annotate(
                        tsv_parsing.rows(
                            'data/inflection/declension-template-verbs-minimal.tsv'))),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/common-noun-declensions.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/latin/classic/adjective-agreement.tsv')),
            ])),
        debug=True,
    ),
    RuleSyntax(parse_any.terms('subject modifier indirect-object direct-object verb')),
    {'language-type':'foreign'},
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = []
)

foreign_termaxis_to_terms = {
    **termaxis_to_terms,
    **parse_any.termaxis_to_terms('''
        gender :  masculine feminine neuter
        number :  singular plural
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic unfinished finished
        tense  :  present past future
        voice  :  active passive
        mood   :  indicative subjunctive imperative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object indirect-object modifier
    '''),
    **parse_any.token_to_tokens('''
        adjective:tall holy poor mean old nimble swift jovial
        verb   :  be be-able want become go carry eat love advise capture hear
        noun   :  man day hand night thing name son war air boy animal star tower horn sailor foundation echo phenomenon vine myth atom nymph comet 
    '''),
}

foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    card_formatting.foreign_focus,
    Orthography('latin', foreign_language),
)

emoji_demonstration = LanguageSpecificEmojiDemonstration(
    card_formatting.emoji_focus,
    emoji_casts[3]
)

demonstrations = [
    emoji_demonstration,
    foreign_demonstration,
    english_demonstration,
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

subjectivity_role_blacklist = parse.termmask(
    'subjectivity_role_blacklist', 
    'subjectivity role',
    '''
    modifier      stimulus
    ''')

subjectivity_valency_whitelist = parse.termmask(
    'subjectivity_valency_whitelist', 
    'valency subjectivity',
    '''
    intransitive  subject
    transitive    direct-object
    intransitive  addressee
    transitive    modifier
    intransitive  modifier
    ''')

subjectivity_motion_whitelist = parse.termmask(
    'subjectivity_motion_whitelist', 
    'subjectivity motion',
    '''
    addressee     associated
    subject       associated
    direct-object associated
    modifier      acquired
    modifier      associated
    modifier      departed
#    modifier      surpassed
#    modifier      leveraged
    ''')

subjectivity_person_blacklist = parse.termmask(
    'subjectivity_person_blacklist', 
    'subjectivity person',
    '''
    addressee  3
    ''')

role_motion_blacklist = parse.termmask(
    'role_motion_blacklist', 
    'role motion',
    '''
    acquired      company
    approached    company
    departed      company
    surpassed     company
    leveraged     company
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
    subjunctive  present
    subjunctive  past
    imperative   present
    imperative   future
    ''')

finite_tense_progress_traversal = parse.termpath(
    'finite_tense_progress_traversal', 
    'tense progress',
    '''
    present  atelic
    future   atelic
    past     unfinished
    past     finished
    present  finished
    future   finished
    ''')

nonfinite_tense_progress_whitelist = parse.termmask(
    'nonfinite_tense_progress_whitelist', 
    'tense progress',
    '''
    present  atelic
    past     finished
    future   atelic
    ''')

voice_progress_whitelist = parse.termmask(
    'voice_progress_whitelist', 
    'voice progress',
    '''
    active   atelic
    active   unfinished
    active   finished
    passive  atelic
    passive  unfinished
    ''')

verb_progress_blacklist = parse.termmask(
    'verb_progress_blacklist', 
    'verb progress',
    '''
    become  finished
    ''')

verb_mood_blacklist = parse.termmask(
    'verb_mood_blacklist', 
    'verb mood',
    '''
    be-able  imperative
    ''')

verb_voice_blacklist = parse.termmask(
    'verb_voice_blacklist', 
    'verb  voice',
    '''
    be       passive
    be-able  passive
    want     passive
    become   passive
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
    man          masculine
    day          feminine
    hand         masculine
    night        feminine
    thing        feminine
    name         neuter
    son          masculine
    war          masculine
    air          masculine
    boy          masculine
    animal       neuter
    star         feminine
    tower        feminine
    horn         neuter
    sailor       masculine
    foundation   feminine
    echo         neuter
    phenomenon   neuter
    vine         feminine
    myth         masculine
    atom         feminine
    nymph        feminine
    comet        masculine
    woman        feminine
    son          masculine
    daughter     feminine
    livestock    neuter
    sound        masculine
    size         feminine
    thought      feminine
    place        masculine
    attention    feminine
    wind         masculine
    enemy        masculine
    monster      feminine
    rock         neuter
    book         masculine
    water        feminine
    horse        masculine
    food         masculine
    work         masculine
    gift         neuter
    house        feminine
    ghost        neuter
    guard        masculine
    dog          masculine
    dog          feminine
    boat         feminine
    shirt        feminine
    rope         masculine
    window       feminine
    drum         neuter
    picture      feminine
    car          masculine
    cart         masculine
    oath         neuter
    idea         feminine
    '''
)

possession_traversal = parse.tokenpath(
    'possession_traversal', 
    'gender noun',
    '''
    masculine  son      
    feminine   daughter 
    neuter     livestock
    neuter     name     
    ''')

possessor_possession_whitelist = parse.tokenmask(
    'possessor_possession_whitelist', 
    'possessor-noun noun',
    '''
    man-possessor    son
    man-possessor    daughter
    man-possessor    livestock
    woman-possessor  son
    woman-possessor  daughter
    woman-possessor  livestock
    animal-possessor son
    animal-possessor daughter
    animal-possessor name
    ''')

possessor_pronoun_traversal = parse.tokenpath(
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
    ''')

#useful for debugging
def head(store):
    print(str(store)[:3000])

tense_progress_mood_voice_verb_traversal = (
    (((((
          axis['valency']
        * finite_tense_progress_traversal
        * axis['mood'])
        & mood_tense_whitelist) 
        * axis['voice'])
        & voice_progress_whitelist)
        * axis['verb'])
    - verb_progress_blacklist
    - verb_mood_blacklist
    - verb_voice_blacklist
) * constant['subject'] 

conjugation_traversal =(
    template_dummy_lookup(tense_progress_mood_voice_verb_traversal)
)

roles = parse_any.termspace('role', 'role', 
    'role: stimulus location possessor interior surface presence aid lack interest time company')

subjectivity_motion_role_traversal = (
    (((axis['subjectivity']
     * axis['motion'] )
     & subjectivity_motion_whitelist)
     * roles )
    - subjectivity_role_blacklist
    - role_motion_blacklist
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

"""

"""

print('flashcards/latin/finite-conjugation.html')
write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = UniformDictLookup(
                'clause [test [np n] [vp cloze v verb]] [dummy np [stock-adposition] n]',)
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

print('flashcards/latin/nonfinite-conjugation.html')
write('flashcards/latin/nonfinite-conjugation.html', 
    deck_generation.generate(
        [
            emoji_demonstration.generator(),
            foreign_demonstration.generator(
                tree_lookup = UniformDictLookup(
                    'clause [speaker finite [vp v figure]] [modifier np clause [test infinitive [np n] [vp cloze v verb]] [dummy np [stock-adposition] n]]',)
            ),
            english_demonstration.generator(
                tree_lookup = UniformDictLookup(
                    'modifier clause [speaker finite [np n] [vp v figure]] [modifier np clause [test [np n] [vp cloze v verb]] [dummy np [stock-adposition] n]] ',)
            ),
        ],
        defaults.override(
            ((  conjugation_traversal 
              & nonfinite_tense_progress_whitelist) 
              - constant['imperative'])
        ),
        tag_templates ={
            'test'    : parse.termaxis_to_term('personal associated agent subject'),
            'dummy'   : parse.termaxis_to_term('common 3 singular masculine'),
            'speaker' : parse.termaxis_to_term('personal associated agent subject 1 singular masculine sapient man familiar present simple active atelic indicative'),
        },
    ))

print('flashcards/latin/participle-declension.html')
write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = UniformDictLookup(
                '''clause test [
                    [np participle clause [np n] parentheses [vp cloze v verb] [dummy np [stock-adposition] n]]
                    [vp active present atelic v appear]
                ]'''),
        ) for demonstration in demonstrations],
        defaults.override(
            (   conjugation_traversal
              & nonfinite_tense_progress_whitelist
              & constant['indicative']
              & constant['atelic'])
        ),
        tag_templates ={
            'test'    : parse.termaxis_to_term('common definite associated agent subject'),
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'participle' : parse.termaxis_to_term('common definite participle subject'),
        },
    ))

print('flashcards/latin/adpositions.html')
write('flashcards/latin/adpositions.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [
                {'declined': list_tools.replace(['n'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            (declension_noun_traversal * constant['man'])
            & constant['modifier']
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal definite'),
        },
    ))

print('flashcards/latin/common-noun-declension.html')
write('flashcards/latin/common-noun-declension.html',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((declension_noun_traversal * axis['noun'])
                & noun_template_whitelist)
                * axis['gender'])
                & gender_noun_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))


print('flashcards/latin/pronoun-declension.html')
write('flashcards/latin/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            ((pronoun_traversal * declension_noun_traversal)
            & noun_template_whitelist)
            - subjectivity_person_blacklist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal'),
        },
    ))

print('flashcards/latin/adjective-agreement.html')
write('flashcards/latin/adjective-agreement.html', 
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

print('flashcards/latin/pronoun-possessives.html')
write('flashcards/latin/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace([['cloze','adj'], ['common', 'n']])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (((  axis['number'] 
               * possession_traversal 
               * declension_noun_traversal 
               * label_editing.termpath(possessor_pronoun_traversal, 'possessor'))
              & possessor_possession_whitelist)
             * constant['exclusive-possessor']  
             * constant['familiar-possessor']
            )
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal-possessive'),
        },
    ))

"""

"""

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')
