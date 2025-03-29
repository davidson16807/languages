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
from tools.nodes import Rule
from tools.cards import DeckGeneration
from inflections import (
    dict_bundle_to_map,
    LanguageSpecificTextDemonstration, LanguageSpecificEmojiDemonstration, 
    english_orthography, english_mood_context,
    card_formatting,
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
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
    if definiteness == 'indefinite' and subjectivity != 'addressee' and nounform != 'personal': 
        return [['det','a'], tree]
    else:
        return tree

class ModernRomanceRuleSyntax(RuleSyntax):
    def __init__(self, sentence_structure, noun_phrase_structure):
        super().__init__(sentence_structure, noun_phrase_structure)
    def order_clause(self, treemap, clause):
        rules = clause.content
        nouns = [phrase for phrase in rules if phrase.tag in {'np'}]
        # enclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'enclitic'}]
        # proclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'proclitic'}]
        noun_lookup = {
            subjectivity: [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == subjectivity]
            for subjectivity in 'subject adverbial adnominal'.split()
        }
        verbs = [phrase
            for phrase in rules 
            if phrase.tag in {'vp'}]
        phrase_lookup = {
            **noun_lookup,
            'personal-direct-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'direct-object'
                and noun.tags['noun-form'] == 'personal'],
            'common-direct-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'direct-object'
                and noun.tags['noun-form'] != 'personal'],
            'personal-indirect-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'indirect-object'
                and noun.tags['noun-form'] == 'personal'],
            'common-indirect-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'indirect-object'
                and noun.tags['noun-form'] != 'personal'],
            'verb': verbs,
        }
        ordered = Rule(clause.tag, 
            clause.tags,
            treemap.map([
                phrase
                for phrase_type in self.sentence_structure
                for phrase in phrase_lookup[phrase_type]
            ]))
        return ordered

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        NestedDictLookup(
            conjugation_population.index([
                *finite_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/finite-conjugations.tsv')),
                # *nonfinite_annotation.annotate(
                #     tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/nonfinite-conjugations.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/common-noun-declensions.tsv')),
                *pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/pronoun-declensions.tsv')),
            ])),
        NestedDictLookup(
            declension_population.index([
                *possessive_pronoun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/pronoun-possessives.tsv')),
                *common_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/indo-european/romance/spanish/modern/adjective-agreements.tsv')),
            ])),
    ),
    ModernRomanceRuleSyntax(
        'subject personal-indirect-object personal-direct-object verb common-direct-object common-indirect-object adverbial'.split(), 
        parse_any.tokens('adposition det adj n np clause')
    ),
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
        gender :  masculine feminine
        number :  singular plural
        formality: tuteo voseo formal
        motion :  approached acquired associated departed leveraged surpassed
        progress: atelic unfinished finished
        polarity: affirmative negative
        tense  :  present past future
        voice  :  active
        mood   :  indicative subjunctive imperative
        role   :  agent patient stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: subject addressee direct-object adnominal indirect-object adverbial adnominal
        degree :  positive superlative
    '''),
    **parse_any.token_to_tokens('''
        adjective: tall strong
        verb : be-inherently be-momentarily have go have-in-possession work eat drive hear
        noun : man woman
    '''),
}


foreign_term_to_termaxis = dict_bundle_to_map(foreign_termaxis_to_terms)

parse = TermParsing(foreign_term_to_termaxis)

foreign_demonstration = LanguageSpecificTextDemonstration(
    Orthography('latin', foreign_language),
    lambda tags, text: text,
    card_formatting.foreign_focus,
    [('∅',''), 
     ('-',''),
     ('con mi','conmigo'),
     ('con ti','contigo'),
     ('de el','del'),
     ('a el','al')]
)

english_demonstration = LanguageSpecificTextDemonstration(
    english_orthography,
    english_mood_context,
    card_formatting.native_word, 
    [('[the mass of]','')]
)

emoji_demonstration = LanguageSpecificEmojiDemonstration(
    emoji_casts[2],
    card_formatting.emoji_focus,
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
    'person number gender formality',
    '''
    1  singular masculine tuteo
    2  singular feminine  tuteo
    2  singular feminine  voseo
    2  singular feminine  formal
    3  singular masculine tuteo
    1  plural   masculine tuteo
    2  plural   feminine  tuteo
    2  plural   feminine  formal
    3  plural   masculine tuteo
    ''')

mood_tense_polarity_whitelist = parse.termmask(
    'mood_tense_whitelist', 
    'mood tense polarity',
    '''
    indicative   present affirmative
    indicative   past    affirmative
    indicative   future  affirmative
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
    future   atelic
    past     unfinished
    past     finished
    ''')

pronoun_traversal = parse.tokenpath(
    'pronoun_traversal', 
    'noun person number formality gender',
    '''
    man    1 singular tuteo  neuter   
    woman  2 singular tuteo  feminine 
    woman  2 singular voseo  feminine 
    man    2 singular formal masculine
    woman  2 singular formal feminine 
    man    3 singular tuteo  masculine
    woman  3 singular tuteo  feminine 
    man    1 plural   tuteo  masculine   
    woman  1 plural   tuteo  feminine
    man    2 plural   tuteo  masculine
    woman  2 plural   tuteo  feminine 
    man    3 plural   tuteo  masculine
    woman  3 plural   tuteo  feminine 
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
    animal    masculine
    #attention 
    bird      masculine
    #boat      
    book      masculine
    bug       feminine
    clothing  feminine
    daughter  feminine
    dog       masculine
    dog       feminine
    #door      
    drum      masculine
    #enemy     
    fire      masculine
    food      feminine
    gift      masculine
    gift      feminine
    #glass     
    guard     feminine
    horse     masculine
    house     feminine
    livestock masculine
    love      feminine
    idea      feminine
    man       masculine
    money     masculine
    monster   masculine
    name      masculine
    rock      feminine
    rope      feminine
    sister    feminine
    size      masculine
    son       masculine
    sound     masculine
    thought   feminine
    warmth    masculine
    water     feminine
    way       feminine
    wind      feminine
    window    feminine
    woman     feminine
    work      masculine
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
    '''
)

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
        '''), 
    'possessor')

agreement_roles = parse.termmask(
    'agreement_roles', 
    'role subjectivity',
    '''
    stimulus subject
    stimulus direct-object
    '''
)

#useful for debugging
def head(store):
    print(str(store)[:3000])

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

print('flashcards/romance/spanish/finite-conjugation.html')
write('flashcards/romance/spanish/finite-conjugation.html', 
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

print('flashcards/romance/spanish/adpositions.html')
write('flashcards/romance/spanish/adpositions.html', 
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
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine tuteo'),
            'test'       : parse.termaxis_to_term('personal definite tuteo'),
        },
    ))

print('flashcards/romance/spanish/pronoun-declension.html')
write('flashcards/romance/spanish/pronoun-declension.html', 
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
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine tuteo'),
            'test'       : parse.termaxis_to_term('tuteo'),
        },
    ))

print('flashcards/romance/spanish/adjective-agreement.html')
write('flashcards/romance/spanish/adjective-agreement.html', 
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
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine tuteo'),
            'test'       : parse.termaxis_to_term('common definite tuteo'),
        },
    ))

print('flashcards/romance/spanish/pronoun-possessives.html')
write('flashcards/romance/spanish/pronoun-possessives.html', 
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
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine tuteo'),
            'test'       : parse.termaxis_to_term('personal-possessive adefinite tuteo'),
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')
