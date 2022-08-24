import parsing
import collections
from predicates import Predicate, Bipredicate

tsv_parsing = parsing.SeparatedValuesFileParsing()
rows = tsv_parsing.rows(
    'data/noun-declension/predicates/biotic/animal.tsv')

level1_functions = ['be','can','bear','attribute']

level0_subset_relations = set()
level1_subset_relations = set(('be','can'),('be','bear'))
level1_function_domains = collections.defaultdict(set)

for row in rows:
    f, x, g, y = row[:4]
    if all([f.strip(), x.strip(), g.strip(), y.strip()]):
        level0_subset_relations.add(((f,x)(g,y)))
        level1_function_domains[f].add(x)
        level1_function_domains[g].add(y)

systems = collections.defaultdict(Predicate)
for fx, gx in level0_subset_relations:
    systems[gx](systems[fx])

for f, g in level1_subset_relations:
    for x in level1_function_domains[f]:
        systems[g,x](systems[f,x])
