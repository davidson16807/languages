
import collections

from parsing import SeparatedValuesFileParsing
from annotation import RowAnnotation
from predicates import Predicate, Bipredicate
from lookup import DefaultDictLookup, DictLookup
from indexing import DictTupleIndexing, DictKeyIndexing
from evaluation import KeyEvaluation
from population import ListLookupPopulation, FlatLookupPopulation

tsv_parsing = SeparatedValuesFileParsing()
rows = [
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal-anatomy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/deity.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/human.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/humanoid.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/mythical.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/plant-anatomy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/plant.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/sapient.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/animacy-hierarchy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/capability.tsv'),
]

level0_subset_relations = set()
level1_subset_relations = collections.defaultdict(
    set, {'be':{'can','has-trait','has-part'}})
level1_function_domains = collections.defaultdict(set)

for row in rows:
    f, x, g, y = row[:4]
    if all([f.strip(), x.strip(), g.strip(), y.strip()]):
        fxgy = (f,x),(g,y)
        level0_subset_relations.add(fxgy)

allthat = collections.defaultdict(Predicate)
for (f,x),(g,y) in level0_subset_relations:
    allthat[g,y](allthat[f,x])
    if g == f:
        for f2 in level1_subset_relations[f]:
            allthat[f2,y](allthat[f2,x])

allthat['be','mouse'] in allthat['can','scurry']
allthat['be','mouse'] in allthat['can','hop']
allthat['be','mouse'] in allthat['has-part','heart']
allthat['be','mouse'] in allthat['has-part','gill']
allthat['be','mouse'] in allthat['has-part','organ']

allthat['be','man'] in allthat['can','be-seen']
allthat['be','man'] in allthat['has-trait','size']
allthat['be','man'] in allthat['has-part','skin']

allthat['be','man']   in allthat['be','human']
allthat['be','human'] in allthat['be','primate']
allthat['be','human'] in allthat['be','primate']

header_columns = [
    'motion', 'attribute', 
    'subject-function', 'subject-argument', 
    'verb', 'direct-object', 'preposition', 
    'declined-noun-function', 'declined-noun-argument']
template_annotation = RowAnnotation(header_columns)
template_population = ListLookupPopulation(
    DefaultDictLookup('declension-template',
        DictTupleIndexing(['motion','attribute']), list))
templates = \
    template_population.index(
        template_annotation.annotate(
            tsv_parsing.rows(
                'data/noun-declension/declension-templates-minimal.tsv')))

class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, motion, attribute):
        def subject(template):
            return self.predicates[template['subject-function'], template['subject-argument']]
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        templates = sorted([template 
                            for template in (self.templates[motion, attribute] 
                                if (motion, attribute) in self.templates else [])
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: len(declined_noun(template)))
        return templates[0] if len(templates) > 0 else None

case_annotation = RowAnnotation(['motion','attribute','case'])
case_indexing = DictTupleIndexing(['motion','attribute'])
case_population = \
    FlatLookupPopulation(
        DictLookup('declension-use-case-to-grammatical-case', case_indexing),
        KeyEvaluation('case'))
use_case_to_grammatical_case = \
    case_population.index(
        case_annotation.annotate(
            tsv_parsing.rows('data/noun-declension/latin/declension-use-case-to-grammatical-case.tsv')))

case_category_to_grammemes = {
    'motion': ['departed', 'associated', 'acquired', 'leveraged'],
    'attribute': [
        'location', 'extent', 'vicinity', 'interior', 'surface', 
        'presence', 'aid', 'lack', 'interest', 'purpose', 'owner', 
        'time', 'state of being', 'topic', 'company', 'resemblance'],
    'voice':  'active',
    'tense':  'present',
    'aspect': 'aorist',
    'mood':   'indicative',
    'proform':'common',
    'person': ['1','2','3'],
    'number': ['singular','dual','plural'],
}



case_grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in case_category_to_grammemes.items() 
    for instance in instances
}

conjugation_annotation = CellAnnotation(
    case_grammeme_to_category, {0:'lemma'}, {0:'language'}, case_category_to_grammemes)

matching = DeclensionTemplateMatching(templates, allthat)

for lemma in ['fish']:
    for tuplekey in case_indexing.tuplekeys(case_category_to_grammemes):
        dictkey = {
            **case_category_to_grammemes,
            **case_indexing.dictkey(tuplekey), 
            'person': '3',
            'noun': lemma,
            'verb': match['verb'],
        }
        match = matching.match(lemma, dictkey['motion'], dictkey['attribute'])
        if match:
            argument = ' '.join([
                match['direct-object'],
                english.decline(dictkey)
            ])
            sentence = ' '.join([
                english.conjugate(, argument),
                match[''],
            ])

