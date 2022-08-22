import collections

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
    def __init__(self, name=''):
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
        self.add(predicand)
    def add(self, predicand):
        if self in predicand:
            raise Exception(f'Circular reference detected between {self.name} and {predicand.name}')
        else:
            self.set_of_predicand_set_references.add(predicand)



class PredicateSystem:
    '''
    A `PredicateSystem` is meant represent a bipredicate within predicate logic
    (that is, a predicate that accepts two arguments, such that it has valency 2).
    Its implimentation is based around set logic, 
     where it could be thought of as a function that maps elements to sets 
     that each represent isolated "systems" of predicate logic,  
     with a special operation that can be used to establish subset relationships
     between the outputs of different systems.
    More formally, a `PredicateSystem` in set theory represents a function:
        P:𝕏→𝕐 = {(x,Y):x∈𝕏 ∧ Y⊆𝕐}
     such that 𝕏⊆𝕐 is an arbitrary set of elements representing the domain of P, 
     𝕐 is the set of all elements that are considered by the predicate system,
     and there is a special relation B~C defined for PredicateSystems B and C such that:
        ∀(x,B(x))∈B: B(x) ⊆ C(x)
    While the above is a lot to take in, we find it allows practical uses. Observe:
        be, can, part = PredicateSystem(), PredicateSystem()
        can(be)                    # if you already are something, then you know you have the ability to be it
        can('mortal','die')        # if you can be mortal, you can die
        part('mortal','soul')      # if there is a mortal, then there is a soul that's part of it
        be('man','mortal')         # if you are a man, you are mortal
        be('socrates','man')       # if you are socrates, you are a man
        ('socrates','die') in can  # if you are socrates, can you die?
    See "thoughts-on-predicate-system-design.md" for design docs,
     how it works, an explanation of this definition, and additional use cases. 
    '''
    def __init__(self):
        self.direct_predications = set()
        self.subsystems = set()
    def predications(self):
        for predication in self.direct_predications:
            yield predication
        for subsystem in self.subsystems:
            for predication in subsystem.predications():
                yield predication
    def __contains__(self, predications):
        if type(predications) not in {tuple,list}:
            pass # TODO: implement
        elif len(predications) == 2:
            system = collections.defaultdict(Predicate)
            for subset, superset in self.predications():
                system[superset](system[subset])
            subset, superset = predications
            return system[subset] in system[superset]
        else:
            raise InvalidArgumentException('Invalid number of predicands passed')
    def __call__(self, *predicands):
        self.add(*predicands)
    def add(self, *predicands):
        if len(predicands) == 1:
            self.subsystems.add(predicands[0])
        if len(predicands) == 2:
            self.direct_predications.add(tuple(predicands))


be, can = PredicateSystem(), PredicateSystem()
can(be)                    # if you already are something, then you know you have the ability to be it
can('mortal','die')        # if you can be mortal, then you can die
('mortal','die') in can    # if you are a mortal, can you die?
be('man','mortal')         # if you are a man, you are mortal
be('socrates','man')       # if you are socrates, you are a man
('socrates','die') in can  # if you are socrates, can you die?

