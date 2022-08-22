import parsing
import collections
from predicates import Predicate, PredicateSystem

tsv_parsing = parsing.SeparatedValuesFileParsing()
rows = tsv_parsing.rows(
    'data/noun-declension/predicates/biotic/animal.tsv')

system = PredicateSystem()
for row in rows:
    predicand_key, predicate_key = row[:2]
    system(predicand_key, predicate_key)

print(predicates.keys())
