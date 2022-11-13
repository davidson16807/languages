import collections

class Predicate:
    '''
    `Predicate` is a set-like object that is able to express predicate logic. 
    A `Predicate` consists of a set of references to other sets. 
    Values can be added to subsets and the added values will immediately
    reflect in supersets upon any checks for set inclusion.
    This allows us to easily and performantly perform predicate logic.
    As an example:
        mortals, men, socrates = [Predicate() for i in range(3)]
        mortals(men)
        men(socrates)
        print(socrates in mortals)
    '''
    def __init__(self, name=''):
        self.name = name
        self.set_of_subsets = set()
    def __contains__(self, predicand):
        return (predicand in self.set_of_subsets or
                any([predicand in subset 
                     for subset in self.set_of_subsets]))
    def __len__(self):
        evaluated_set = set()
        for subset in self.set_of_subsets:
            evaluated_set.add(subset)
            for content in subset:
                evaluated_set.add(content)
        return len(evaluated_set)
    def __iter__(self):
        evaluated_set = set()
        for subset in self.set_of_subsets:
            evaluated_set.add(subset)
            for content in subset:
                evaluated_set.add(content)
        for predicand in evaluated_set:
            yield predicand
    def __call__(self, predicand):
        self.add(predicand)
    def add(self, predicand):
        if self == predicand:
            raise Exception(f'Circular reference detected between {self.name} and {predicand.name}')
        if self in predicand:
            raise Exception(f'Circular reference detected between {self.name} and {predicand.name}')
        else:
            self.set_of_subsets.add(predicand)



class Bipredicate:
    '''
    A `Bipredicate` is meant to represent a predicate in predicate logic
    with a valency of 2 (that is, a predicate that accepts two arguments).
    It can be considered a independant system of unipredicates that
     has the ability to compose with other similarly independant systems.
    To illustrate its use:
       be, can, part = Bipredicate(), Bipredicate()
       can(be)                    # if you already are something, then you know you have the ability to be it
       can('mortal','die')        # if you can be mortal, you can die
       part('mortal','soul')      # if there is a mortal, then there is a soul that's part of it
       be('man','mortal')         # if you are a man, you are mortal
       be('socrates','man')       # if you are socrates, you are a man
       ('socrates','die') in can  # if you are socrates, can you die? (True)
       ('socrates','die') in be   # if you are socrates, are you dead? (False, it was never established)
    Its implementation is based around sets, such that a bipredicate
     can be considered a mapping from elements to sets 
     where sets each represent isolated systems of predicate logic, 
    There is then a special operation that can be used to establish subset 
     relationships between the outputs of different systems.
    More formally, a `Bipredicate` in set theory represents a function:
        P:𝕏→𝒫(𝕐) = {(x,Y):x∈𝕏 ∧ Y⊆𝕐}
     𝕏⊆𝕐 is an arbitrary set of elements representing the domain of P, 
     𝕐 is the set of all elements that are considered by the predicate system,
     𝒫(𝕐) is the powerset of 𝕐, and there is a special relation denoted B⊆¹C 
     defined for Bipredicates B and C such that:
        ∀(x,B(x))∈B: B(x) ⊆ B(x) ⟹ C(x) ⊆ C(x)
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


be, can = Bipredicate(), Bipredicate()
can(be)                    # if you already are something, then you know you have the ability to be it
can('mortal','die')        # if you can be mortal, then you can die
('mortal','die') in can    # if you are a mortal, can you die?
be('man','mortal')        # if you are a man, you are mortal
be('socrates','man')      # if you are socrates, you are a man
('socrates','die') in can  # if you are socrates, can you die?

# taxonomy(head) ⊆ taxonomy(human)
# taxonomy(human,head)

