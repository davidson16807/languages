from tools.lookup import DictLookup
from tools.indexing import DictTupleIndexing, DictKeyIndexing
from tools.cards import DeckGeneration
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
    tsv_parsing,
    has_annotation,
    finite_annotation, nonfinite_annotation, declension_verb_annotation, 
    pronoun_annotation, common_noun_annotation, possessive_pronoun_annotation, declension_template_noun_annotation,
    conjugation_population, declension_population, 
    case_usage_annotation, mood_usage_annotation, aspect_usage_annotation,
    case_usage_population, mood_usage_population, aspect_usage_population,
    tag_defaults, write, 
    emoji_casts
)

deck_generation = DeckGeneration()
list_tools = ListTools()
rule_tools = RuleTools()

foreign_language = Language(
    ListSemantics(
        case_usage_population.index(
            case_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/case-usage.tsv'))),
        mood_usage_population.index(
            mood_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/mood-usage.tsv'))),
        aspect_usage_population.index(
            aspect_usage_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/aspect-usage.tsv'))),
    ),
    ListGrammar(
        conjugation_population.index([
            *finite_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/conjugations.tsv')),
        ]),
        declension_population.index([
            *pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/pronoun-declensions.tsv')),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/common-noun-declensions.tsv')),
            *common_noun_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/adjective-agreements.tsv')),
            *possessive_pronoun_annotation.annotate(
                tsv_parsing.rows('data/inflection/indo-european/germanic/english/old/pronoun-possessives.tsv')),
            *filter(has_annotation('language','old-english'),
                declension_template_noun_annotation.annotate(
                    tsv_parsing.rows('data/inflection/declension-template-nouns-minimal.tsv'))),
        ]),
    ),
    RuleSyntax('subject verb direct-object indirect-object modifier'.split()), 
    {'language-type':'foreign'},
    # TODO: this should technically be SOV, but V2 ordering applies to main clauses which mainly produces SVO
    list_tools,
    rule_tools,
    RuleFormatting(),
    substitutions = []
)

demonstrations = [
    LanguageSpecificEmojiDemonstration(
        card_formatting.emoji_focus,
        foreign_language.grammar.conjugation_lookups['argument'], 
        emoji_casts[2]),
    LanguageSpecificTextDemonstration(
            card_formatting.foreign_focus,
            Orthography('latin', foreign_language),
        ),
    english_demonstration,
]

nouns = 'dog light house gift raid moon sun eye time English son hand person nut goose friend bystander father mother brother sister daughter lamb shoe piglet shadow meadow'.split(' ')
roles = 'solitary audience patient location possessor'.split()
motions = 'associated'.split()
genders = 'masculine feminine neuter'.split()
numbers = 'singular plural'.split()

verbs = ['be [momentarily]', 'be [by nature]', 'do', 'go', 'want', 
         'steal', 'share', 'tame', 'move', 'love', 'have', 'live', 'say', 'think']
tenses = 'present past'.split()
progress = 'atelic'
moods = 'indicative subjunctive imperative'.split()
voices = 'active'

adjectives = 'good tall black red green'.split()



print('flashcards/old-english/finite-conjugation.html')
write('flashcards/old-english/finite-conjugation.html', 
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

"""
print('flashcards/old-english/participle-declension.html')
write('flashcards/old-english/participle-declension.html', 
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

print('flashcards/old-english/adpositions.html')
write('flashcards/old-english/adpositions.html', 
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
            & constant['adverbial']
            & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('personal definite'),
        },
    ))

print('flashcards/old-english/common-noun-declension.html')
write('flashcards/old-english/common-noun-declension.html',
    deck_generation.generate(
        [demonstration.generator(
            tree_lookup = template_tree_lookup,
            substitutions = [{'declined': list_tools.replace(['cloze', 'n'])}],
        ) for demonstration in demonstrations],
        defaults.override(
            (declension_noun_traversal * axis['number'] * axis['noun'])
                & noun_template_whitelist
        ),
        tag_templates ={
            'dummy'      : parse.termaxis_to_term('common 3 singular masculine'),
            'test'       : parse.termaxis_to_term('common definite'),
        },
    ))

print('flashcards/old-english/pronoun-declension.html')
write('flashcards/old-english/pronoun-declension.html', 
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

print('flashcards/old-english/adjective-agreement.html')
write('flashcards/old-english/adjective-agreement.html', 
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

print('flashcards/old-english/pronoun-possessives.html')
write('flashcards/old-english/pronoun-possessives.html', 
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
 