import parsing
import collections
from predicates import Predicate, PredicateSystem

tsv_parsing = parsing.SeparatedValuesFileParsing()
rows = tsv_parsing.rows(
    'data/noun-declension/predicates/biotic/animal.tsv')

types = PredicateSystem()
types = PredicateSystem()
for row in rows:
    f, x, g, y = row[:4]
    types(x, y)

print(predicates.keys())


parts
types
skills
traits
