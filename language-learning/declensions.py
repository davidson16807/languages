import parsing
import collections
from predicates import Predicate, Bipredicate

tsv_parsing = parsing.SeparatedValuesFileParsing()
rows = [
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal.tsv'),
  *tsv_parsing.rows('data/noun-declension/predicates/biotic/animal-anatomy.tsv'),
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

systems = collections.defaultdict(Predicate)
for (f,x),(g,y) in level0_subset_relations:
    systems[g,y](systems[f,x])
    if g == f:
        for f2 in level1_subset_relations[f]:
            systems[f2,y](systems[f2,x])

systems['be','mouse'] in systems['can','scurry']
systems['be','mouse'] in systems['can','hop']
systems['be','mouse'] in systems['has-part','heart']
systems['be','mouse'] in systems['has-part','gill']
systems['be','mouse'] in systems['has-part','organ']
