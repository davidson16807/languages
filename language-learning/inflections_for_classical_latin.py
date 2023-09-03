import time

start_time = time.time()

from tools.shorthands import TermParsing
from tools.dictstores import DictSet, DictList, DictSpace
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
    template_tree_whitelist,
    noun_template_whitelist,
)

deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/latin/classic/aspect-usage.tsv'))),
    ),
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
        motion :  associated departed acquired approached surpassed leveraged
        progress: atelic unfinished finished
        tense  :  present past future
        voice  :  active passive
        mood   :  indicative subjunctive imperative
        role   :  stimulus location possessor interior surface presence aid lack interest time company
        subjectivity: addressee subject direct-object indirect-object modifier
    '''),
    **parse_any.token_to_tokens('''
        adjective:tall holy poor mean old nimble swift jovial
        verb   :  be be-able want become go carry eat love advise capture hear
        noun   :  man day hand night thing name son war air boy animal star tower horn sailor foundation echo phenomenon vine myth atom nymph comet 
        possessor-noun :  man-possessor woman-possessor animal-possessor
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
    foreign_language.grammar.conjugation_lookups['argument'], 
    emoji_casts[3])

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

subjectivity_role_blacklist = DictSet(
    'subjectivity_role_blacklist', 
    DictTupleIndexing(parse.termaxes('subjectivity role')),
    content = parse.term_table('''
        modifier      stimulus
    '''))

subjectivity_valency_whitelist = DictSet(
    'subjectivity_valency_whitelist', 
    DictTupleIndexing(parse.termaxes('valency subjectivity')),
    content = parse.term_table('''
        intransitive  subject
        transitive    direct-object
        transitive    modifier
        intransitive  modifier
    '''))

subjectivity_motion_whitelist = DictSet(
    'subjectivity_motion_whitelist', 
    DictTupleIndexing(parse.termaxes('subjectivity motion')),
    content = parse.term_table('''
        subject       associated
        direct-object associated
        addressee     associated
        modifier      departed
        modifier      associated
        modifier      approached
        modifier      acquired
        modifier      surpassed
        modifier      leveraged
    '''))

conjugation_subject_traversal = DictList(
    'conjugation_subject_traversal', 
    DictTupleIndexing(parse.termaxes('person number gender')),
    sequence = parse.term_table('''
        1  singular neuter
        2  singular feminine
        3  singular masculine
        1  plural   neuter
        2  plural   feminine
        3  plural   masculine
    '''))

mood_tense_whitelist = DictSet(
    'mood_tense_whitelist', 
    DictTupleIndexing(parse.termaxes('mood tense')),
    content = parse.term_table('''
        indicative   present
        indicative   past
        indicative   future
        subjunctive  present
        subjunctive  past
        imperative   present
        imperative   future
    '''))

finite_tense_progress_traversal = DictList(
    'finite_tense_progress_traversal', 
    DictTupleIndexing(parse.termaxes('tense progress')),
    sequence = parse.term_table('''
        present  atelic
        future   atelic
        past     unfinished
        past     finished
        present  finished
        future   finished
    '''))

nonfinite_tense_progress_whitelist = DictSet(
    'nonfinite_tense_progress_whitelist', 
    DictTupleIndexing(parse.termaxes('tense progress')),
    content = parse.term_table('''
        present  atelic
        past     finished
        future   atelic
    '''))

voice_progress_whitelist = DictSet(
    'voice_progress_whitelist', 
    DictTupleIndexing(parse.termaxes('voice progress')),
    content = parse.term_table('''
        active   atelic
        active   unfinished
        active   finished
        passive  atelic
        passive  unfinished
    '''))

verb_progress_blacklist = DictSet(
    'verb_progress_blacklist', 
    DictTupleIndexing(parse.termaxes('verb progress')),
    content = parse.term_table('''
        become  finished
    '''))

verb_mood_blacklist = DictSet(
    'verb_mood_blacklist', 
    DictTupleIndexing(parse.termaxes('verb mood')),
    content = parse.term_table('''
        be-able  imperative
    '''))

verb_voice_blacklist = DictSet(
    'verb_voice_blacklist', 
    DictTupleIndexing(parse.termaxes('verb  voice')),
    content = parse.term_table('''
        be       passive
        be-able  passive
        want     passive
        become   passive
    '''))

pronoun_traversal = DictList(
    'pronoun_traversal', 
    DictTupleIndexing(parse.termaxes('noun person number gender')),
    sequence = parse.token_table('''
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
    '''))

gender_agreement_traversal = DictList(
    'gender_agreement_traversal', 
    DictTupleIndexing(parse.termaxes('gender noun')),
    sequence = parse.token_table('''
        masculine  man   
        feminine   woman 
        neuter     animal
    '''))

possession_traversal = DictList(
    'possession_traversal', 
    DictTupleIndexing(parse.termaxes('gender noun')),
    sequence = parse.token_table('''
        masculine  son      
        feminine   daughter 
        neuter     livestock
        neuter     name     
    '''))

possessor_possession_whitelist = DictSet(
    'possessor_possession_whitelist', 
    DictTupleIndexing(parse.termaxes('possessor-noun noun')),
    content = parse.token_table('''
        man-possessor    son
        man-possessor    daughter
        man-possessor    livestock
        woman-possessor  son
        woman-possessor  daughter
        woman-possessor  livestock
        animal-possessor son
        animal-possessor daughter
        animal-possessor name
    '''))

possessor_pronoun_traversal = DictList(
    'possessor_pronoun_traversal', 
    DictTupleIndexing(parse.termaxes('possessor-noun possessor-person possessor-number possessor-gender')),
    sequence = parse.token_table('''
        man-possessor    1st-possessor singular-possessor neuter-possessor   
        woman-possessor  2nd-possessor singular-possessor feminine-possessor 
        man-possessor    3rd-possessor singular-possessor masculine-possessor
        woman-possessor  3rd-possessor singular-possessor feminine-possessor 
        snake-possessor  3rd-possessor singular-possessor neuter-possessor   
        man-possessor    1st-possessor plural-possessor   neuter-possessor   
        woman-possessor  2nd-possessor plural-possessor   feminine-possessor 
        man-possessor    3rd-possessor plural-possessor   masculine-possessor
        woman-possessor  3rd-possessor plural-possessor   feminine-possessor 
        man-possessor    3rd-possessor plural-possessor   neuter-possessor   
    '''))

tense_progress_mood_voice_verb_traversal = (
    (((((finite_tense_progress_traversal
        * axis['mood'])
        & mood_tense_whitelist) 
        * axis['voice'])
        & voice_progress_whitelist) 
        * axis['verb'])
    - verb_progress_blacklist
    - verb_mood_blacklist
    - verb_voice_blacklist
)

conjugation_subject_defaults = (
    constant['subject'] * 
    constant['stimulus'] * 
    constant['associated'] * 
    constant['transitive']
)

subjectivity_motion_role_traversal = (
    ((  axis['subjectivity'] 
      * axis['motion'] 
      * axis['role']) 
     & subjectivity_motion_whitelist)
    - subjectivity_role_blacklist
)

verb_direct_object = DictSet('verb_direct_object', 
    DictTupleIndexing(parse.tokens('verb direct-object')),
    parse.token_table('''
        swim      ∅
        fly       ∅
        rest      ∅
        walk      ∅
        rest      ∅
        rest      ∅
        direct    attention
        work      ∅
        resemble  ∅
        eat       food
        endure    fire
        warm      man
        cool      man
        fall      ∅
        change    ∅
        occupy    place
        show      ∅
        see       ∅
        watch     ∅
        startle   ∅
        displease ∅
        appear    ∅
    '''),
)

demonstration_verbs = DictSpace('demonstration-verbs', 
    DictTupleIndexing(['verb']),
    {'verb': parse.tokens('''
        swim fly rest walk direct work resemble eat endure 
        warm cool fall change occupy show see watch startle displease appear be''')},
)

declension_noun_traversal = (
      demonstration_verbs
    * axis['valency'] 
    * axis['template']
    * subjectivity_motion_role_traversal
)

'''
print('flashcards/latin/finite-conjugation.html')
write('flashcards/latin/finite-conjugation.html', 
    deck_generation.generate(
        [demonstration.verb(
            substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
            stock_modifier = foreign_language.grammar.stock_modifier,
            # default_tree = 'clause test [np the n man] [vp conjugated] [modifier np test stock-modifier]',
            default_tree = 'clause [test [np the n man] [vp conjugated]] [test modifier np stock-modifier]',
        ) for demonstration in demonstrations],
        defaults.override(
              conjugation_subject_traversal 
            * tense_progress_mood_voice_verb_traversal 
            * conjugation_subject_defaults 
            * constant['personal']
        ),
    ))

print('flashcards/latin/nonfinite-conjugation.html')
write('flashcards/latin/nonfinite-conjugation.html', 
    deck_generation.generate(
        [
            emoji_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
            ),
            foreign_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test [np the n man] [infinitive vp conjugated]] [modifier test np stock-modifier]',
                default_tree = 'clause [finite speaker [vp v figure]] [modifier np clause [test [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
            english_demonstration.verb(
                substitutions = [{'conjugated': list_tools.replace(['cloze', 'v', 'verb'])}],
                stock_modifier = foreign_language.grammar.stock_modifier,
                # default_tree = 'clause [test [np the n man] [vp conjugated]] [modifier np test stock-modifier]',
                default_tree = 'clause [finite speaker [np the n man] [vp v figure]] [modifier np clause [test [np the n man] [vp conjugated]]] [test modifier np stock-modifier]',
            ),
        ],
        defaults.override(
            ((  tense_progress_mood_voice_verb_traversal 
              & nonfinite_tense_progress_whitelist) 
              - constant['imperative'])
            * conjugation_subject_defaults
            * constant['infinitive']
            * constant['personal']
        ) 
    ))
print('flashcards/latin/participle-declension.html')
write('flashcards/latin/participle-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [
                {'declined': list_tools.replace(['the', ['n', 'man'], ['parentheses', ['participle', 'cloze', 'v','verb'], ['modifier', 'np', 'participle', 'stock-modifier']]])},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            ((  tense_progress_mood_voice_verb_traversal 
              & nonfinite_tense_progress_whitelist
              & constant['indicative'])
             - constant['unfinished'])
            * conjugation_subject_defaults
            * constant['participle']
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('finite present active atelic personal 3 singular masculine'),
            'possession' : parse.termaxis_to_term('finite present active atelic common   3 singular masculine'),
            'test'       : parse.termaxis_to_term('finite present active atelic common'),
            'emoji'      : parse.termaxis_to_term('finite present active atelic common 4'),
            'participle' : parse.termaxis_to_term('nominative'),
        },
    ))
'''

print('flashcards/latin/adpositions.html')
write('flashcards/latin/adpositions.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [
                {'declined': list_tools.replace(['the', 'n', 'man'])},
                {'stock-adposition': list_tools.wrap('cloze')},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
              subjectivity_motion_role_traversal 
            & constant['modifier']),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('personal 3 singular'),
            'test'       : parse.termaxis_to_term('common'),
            'emoji'      : parse.termaxis_to_term('common 4'),
        },
    ))


declension_common_noun_traversal = (
    (declension_noun_traversal * axis['noun'] * constant['common'])
    & subjectivity_valency_whitelist
    & noun_template_whitelist
    & template_verb_whitelist
)
print('flashcards/latin/common-noun-declension.html')
write('flashcards/latin/common-noun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.override(declension_common_noun_traversal),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('personal 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common'),
            'emoji'      : parse.termaxis_to_term('common 4'),
        },
    ))


declension_pronoun_traversal = (
    (pronoun_traversal * declension_noun_traversal * constant['personal'])
    & subjectivity_valency_whitelist
    & noun_template_whitelist
    & template_verb_whitelist
)
print('flashcards/latin/pronoun-declension.html')
write('flashcards/latin/pronoun-declension.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [{'declined': list_tools.replace(['the', 'cloze', 'n', 'noun'])}],
        ) for demonstration in demonstrations],
        defaults.override(declension_pronoun_traversal),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal'),
            'emoji'      : parse.termaxis_to_term('common 4'),
        },
    ))

adjective_agreement_traversal = (
    (  axis['number']
     * gender_agreement_traversal
     * declension_noun_traversal
     * axis['adjective'])
    & subjectivity_valency_whitelist
    & noun_template_whitelist
    & template_verb_whitelist
)

print('flashcards/latin/adjective-agreement.html')
write('flashcards/latin/adjective-agreement.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [{'declined': list_tools.replace(['the', ['cloze','adj','adjective'], ['n', 'noun']])}],
        ) for demonstration in demonstrations], 
        defaults.override(adjective_agreement_traversal),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('personal 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common'),
            'emoji'      : parse.termaxis_to_term('common 4'),
        },
    ))

print('flashcards/latin/pronoun-possessives.html')
write('flashcards/latin/pronoun-possessives.html', 
    deck_generation.generate(
        [demonstration.case(
            tree_lookup = template_tree_whitelist,
            substitutions = [
                {'declined': list_tools.replace(['the', ['cloze','adj'], ['common', 'n', 'noun']])},
            ],
        ) for demonstration in demonstrations],
        defaults.override(
            (((  axis['number'] 
               * possession_traversal 
               * declension_noun_traversal 
               * possessor_pronoun_traversal)
              & possessor_possession_whitelist)
             * constant['exclusive-possessor']  
             * constant['familiar-possessor'] )
            & subjectivity_valency_whitelist
            & noun_template_whitelist
            & template_verb_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('personal 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal-possessive'),
            'emoji'      : parse.termaxis_to_term('4'),
        },
    ))

end_time = time.time()
duration = end_time-start_time
print(f'runtime: {int(duration//60)}:{int(duration%60):02}')