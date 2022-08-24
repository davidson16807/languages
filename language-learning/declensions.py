import parsing
import collections
from predicates import Predicate, Bipredicate

tsv_parsing = parsing.SeparatedValuesFileParsing()
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
  # *tsv_parsing.rows('data/noun-declension/predicates/animacy-hierarchy.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/capability.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/property.tsv'),
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

