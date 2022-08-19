
class Predicate:
    '''
    `Predicate` is a set-like object that is able to express predicate logic. 
    A `Predicate` consists of a set of references to other sets. 
    Values can be added to these sets and the added values will immediately
    be considered in any subsequent checks for set inclusion.
    This allows us to easily perform predicate logic.
    As an example:
        mortals = Predicate('mortals')
        men = Predicate('men')
        socrates = Predicate('socrates')
        mortals.add(men)
        men.add(socrates)
        print(socrates in mortals)
    '''
    def __init__(self, name):
        self.name = name
        self.set_of_predicand_set_references = set()
    def __contains__(self, predicand):
        return (predicand in self.set_of_predicand_set_references or
                any([predicand in set_reference 
                     for set_reference in self.set_of_predicand_set_references]))
    def __iter__(self):
        evaluated_set = set()
        for set_reference in self.set_of_predicand_set_references:
            evaluated_set.add(set_reference)
            for set_reference_content in set_reference:
                evaluated_set.add(set_reference_content)
        for predicand in evaluated_set:
            yield predicand
    def __call__(self, predicand):
        if self in predicand:
            raise f'Circular reference detected between {self.name} and {predicand.name}'
        else:
            self.set_of_predicand_set_references.add(predicand)

mortals = Predicate('mortals')
men = Predicate('men')
socrates = Predicate('socrates')
mortals(men)
men(socrates)
print(socrates in mortals)

