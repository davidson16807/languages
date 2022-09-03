
import collections

from parsing import SeparatedValuesFileParsing
from annotation import RowAnnotation
from predicates import Predicate, Bipredicate
from lookup import DefaultDictLookup
from indexing import DictTupleIndexing, DictKeyIndexing
from population import ListLookupPopulation

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
    'case', 'PIE-case-name', 'motion', 'attribute', 
    'subject-function','subject-argument', 
    'verb', 'direct-object', 'preposition', 
    'declined-noun-function', 'declined-noun-argument']
rows = tsv_parsing.rows('data/noun-declension/declension-templates-minimal.tsv')
annotation = RowAnnotation(header_columns)
population = ListLookupPopulation(
    DefaultDictLookup('declension-template',
        DictKeyIndexing('case'), list))
templates = \
    population.index(
        annotation.annotate(
            tsv_parsing.rows(
                'data/noun-declension/declension-templates-minimal.tsv')))

relevant = sorted([template for template in templates['origin']], 
                  key=lambda template: len(allthat[template['declined-noun-function'],template['declined-noun-argument']]))

for template in relevant:
    f = template['declined-noun-function']
    x = template['declined-noun-argument']
    if allthat['be','horse'] in allthat[f,x]:
        print(f,x, len(allthat[f,x]), template)
