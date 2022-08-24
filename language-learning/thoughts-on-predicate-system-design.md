
In the beginning, there was `Predicate`.
`Predicate` is class designed to express predicate logic,
the kind you might see in a class on philosophy at school:

    mortal(man)
    man(socrates)
    ∴ socrates(mortal)

`Predicate` uses magic methods to represent this notation idiomatically,
so you can process logic without having to think in a different notation.
It's the poor man's Pythonic implementation of [prolog](https://en.wikipedia.org/wiki/Prolog).

```python
socrates, men, mortals = Predicate(), Predicate(), Predicate()
mortals(men)
men(socrates)
print(socrates in mortals)
```

`Predicate` can be implemented easily in terms of set logic,
i.e. socrates is in the set of men, and the set of men is a subset of the set of mortals,
and since subset relations are transitive, it plain to see that socrates is in the set of mortals.
However special consideration needs to be given to avoid the costly recalculation of set contents 
everytime you specify that one set is subset to another. We accomplish this using references.
`Predicate` is effectly a `set` that points to other `set`s by reference to indicate subset inclusion.
This way, values can be added to a subset and the added values will immediately
recognize it as part of its parent set upon any subsequent checks for set inclusion.
The heavy calculation is only performed upon checks for set inclusion.

Though I usually avoid solutions that use refence management, 
I found that it really was the best way to accomplish the task here.
The alternative value based approach would require
heavier state management logic that run checks for set inclusion, 
e.g. plain old data structures in a blackboard system.
It is not as plain to see what this state management logic looks like,
and as much as I like value based logic, 
blackboards smell heavily of an anti-pattern to me, 
they are typically resorted to when you don't know what you are doing 
and would just like to kindly ask the computer to think for you.
Failure to think prohibits you from debugging your solution,
you quickly wind up in states of chaos where "shit just happens"
and you are unable to put any confidence in the code you have written,
let alone the assurance needed for other software to rest upon it productively.
They are good for research projects, but not for production systems.
Painful reference management is avoided in this case,
simply because we impose the requirement that no other 
state modifications occur to predicates aside from adding predicands.

Here is `Predicate` its simplest form, when it was originally implemented:

```python
class Predicate:
    def __init__(self):
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
        self.set_of_predicand_set_references.add(predicand)
```

My typical use case for `Predicate`s was to store them in a `defaultdict` indexed by strings. 
The strings were read in from a .csv file, which also indicated predicate relationships, such as:

```
socrates,man
man,mortal
```

This turned out surprisingly well, I found I could handle a large number of predicates this way.
It was surprisingly intuitive too, I found I never experienced any serious bugs during 
the import of my .csv file. 

However it was inconvenient to query predicates in the `defaultdict`:

```python
predicates['men'](predicates['mortal'])
predicates['socrates'](predicates['man'])
predicates['mortal'] in predicates['socrates']
```

So I created a convenience wrapper to handle them,
which I termed `PredicateSystem`:

```python
class PredicateSystem:
    def __init__(self):
        self.predicates = collections.defaultdict(Predicate)
    def __contains__(self, predicate_predicand):
        predicate, predicand = predicate_predicand
        return self.predicates[predicand] in self.predicates[predicate]
    def __call__(self, predicate, predicand):
        self.add(predicate, predicand)
    def add(self, predicate, predicand):
        self.predicates[predicate](self.predicates[predicand])
```

This allowed statements such as:

```python
system = PredicateSystem()
system('socrates','men')
system('men','mortal')
('socrates','mortal') in system
```

However during development I quickly discovered it was more than that.
`PredicateSystem` could be used in some contexts as a bipredicate 
(that is, a predicate of valency 2):

```python
is_ancestor = PredicateSystem()
is_ancestor(parent, child)
(parent, child) in is_ancestor
```

That brings us up to the present, so we will now discuss how to continue.

Subsequent changes to `PredicateSystem` stood to distance itself
from the resemblance since `PredicateSystem` is architected strictly 
as a convenience wrapper, so we will rename it `InchoateBipredicate`.

We say it is "Inchoate" because it is not strictly a bipredicate:
at the very least, its `__call__()` and `__contains__()` methods 
operate on strings rather than predicates, so there is no transferrence
of properties that can occur when we use references, as we see with `Predicate`.

However, we retain it because it may be used in the future as a base
to implement a real bipredicate.

Example usage:

```python
be = IncoateBipredicate()
be('men','mortal')          # if you are a man, you are mortal
be('socrates','men')        # if you are socrates, you are a man
('socrates','mortal') in be # if you are socrates, are you mortal?
```

Or:

```python
can = IncoateBipredicate()
can('mortal','die')         # if you can be mortal, you can die
can('man','mortal')         # if you can be a man, you can be mortal
('socrates','die') in can   # if you can be socrates, can you die?
```

Or:

```python
can = IncoateBipredicate()
can_have('fingers', 'finger')# if you can have fingers, you can have a finger
can_have('hand', 'fingers')  # if you can have a hand, you can have a finger
can_have('man', 'hand')      # if you can have a man, you can have a hand
can_have('men', 'man')       # if you can have men, you can have a man
('man','finger') in can_have # if you can have a man, do you can have a finger?
```

But it would be ideal to merge these systems together, 
so that the above is modified to operate on references instead of strings.
After some modification to the above to account for this, 
the above could potentially be used to make queries that combine the systems,
for instance:

```python
(socrates, finger) in has
```

would return `True`.

This is how we would like `InchoateBipredicate` to behave.

We note the latter "has" system might be better stated using two systems, 
which differ only in potentiality:

```python
has(fingers, finger)    # if you have fingers, you always have a finger
has(men, man)           # if you have men, you always have a man
can_have(hand, fingers) # if you can have a hand, you can have a finger
can_have(man, hand)     # if you can have a man, you can have a hand
```

We also notice a fascinating orthogonality in the system names here:

                          "potentiality"
                        certain  potential
    "relation"  is-a    be       can
                has-a   have     can_have

and there are properties that characterize how the systems interrelate.

We'll call this cartesian product our "relation × potentiality" system from now on.

Obviously we cannot naïvely combine all component systems of "relation × potentiality" 
into a single system (let's call it "foo") and expect it to work, 
otherwise we wind up with ridiculous statements like:
```python
foo(man, hand)              # if you can have a man, you can have a hand
foo(socrates,man)           # if you are socrates, you are a man
(socrates, hand) in foo     # socrates is a hand
```

However if we reinterpret "foo" as equivalent to "can_have" the results do make sense:

```python
can_have(man, hand)          # if you can have a man, you can have a hand
can_have(socrates,man)       # if you can have socrates, you can have a man
(socrates, hand) in can_have # socrates can have a hand
```

In other words, "can_have" absorbs meaning from all other systems 
in the "relation × potentiality" product shown above.

However it is not satisfactory to accept this system as the final iteration, 
since it only allows us to understand when a sentence is meaningful 
if it contains the phrase "can have".

In the ideal, we want to be able to construct meaningful sentences 
that capture all aspects of spoken language, 
and while we may not be able to achieve all aspects of that ideal,
we would at least like to come up with meaningful and 
somewhat natural sentences like "the hand of socrates".

We will now make some observations:

 * just because you have something doesn't mean you are that thing
 * just because you can be something doesn't mean you are that thing

However:

 * if you are an x, and x always is a y, then you always are a y
 * if you have an x, and x always has a y, then you always have a y
 * if you are an x, and x always has a y, then you always have a y
 * if you have an x, and x always is a y, then you always have a y

This covers all possible behavior that can be assumed when composing "have" and "be" statements,
it is the "totality" of things that could be considered between them.

One way to summarize this list is to say that the inclusion 
of a "has" statement in a premise always "rachets" 
up the conclusion to another "has" statement.
We say it "rachets" since the operation has idempotence: 
once a "has" statment appears in a sequence of conclusions,
there is nothing in the system that allows conclusions to return to a "be" statement.

If we interpret a predicate as a set, then predication can be represented through 
set membership and subset inclusion. In this context, a bivariate such as "has" 
can be represented by saying that for each element considered by the predicate system,
there exists a set for each thing that belongs to it. 
We will call the set of things that are the parts of something its "anatomy". 
As an example:

    anatomy(finger) ⊆ anatomy(hand)
    anatomy(hand) ⊆ anatomy(socrates)

This presents a dramatic reinterpretation of a predicate system,
not as a bipredicate, but as a function that returns uniprediates (that is, of valency 1).
The approach is analogous to the currying of a function.

But a bivariate such as "be" can also be represented in set notation the same way.
We will call the set of categories that a thing belongs to its "taxonomy":

    taxonomy(man) ⊆ taxonomy(mortal) 
    taxonomy(socrates) ⊆ taxonomy(man)

Now that "be" is represented by its own system there is 
little need to ever make statements on "naked" sets, such as "mortal ⊆ man".
Indeed, predicates such as 'man' or 'mortal' now become little better than labels 
that are attached to real predicates like "taxonomy(man)" or "anatomy(man)",
and we seem to have been justified all along by implementing them using strings.
Predicates like "mortal" may help us to index them in dictionaries but do little else.
We will nevertheless see a little later why a function like "taxonomy()" is still useful.

Another thing to note here is that predicates in our set interpretation 
can be treated as both elements and subsets.
Fortunately this distinction is already captured in an adequate way 
by our implementation of `Predicate` without losing our ability to consider it as a set.
We will (hopefully) avoid the abuse of set notation this could cause in coming paragraphs
by simply addressing the form of predicate inclusion that can be considered set inclusion.
This should be easily done without loss of generality.

To return to our original subject (discussing composition between "has" and "be" predicates) 
we note that the statements we've outlined above can also be considered using set notation, 
by saying that a thing's anatomy includes all things that are in the anatomy of its parts
if we use "A(x)" to indicate "anatomy(x)", then:

      ⋃   A(x) ⊆ A(s)                                                           1
    x∈A(s)

Likewise, a thing's anatomy also includes the taxonomies for all parts in its anatomy. 
If we use "T(x)" to indicate "taxonomy(x)", then:

      ⋃   T(x) ⊆ A(s)                                                           2
    x∈A(s)

And a thing's anatomy also includes anatomy for the categories that fit in its taxonomy:

      ⋃   A(x) ⊆ A(s)                                                           3
    x∈T(s)

These can all be converted in a fairly straight forward way to a Python implementation.
Within Python, the function A is represented as a `defaultdict`, denoted `A`, that maps 
the hash of a predicate x to a `Predicate` that represents A(x), denoted `A[x]`.
The same statements can be made for the function T, denoted `T`.
The check shown in equation 1 is accomplished by checking `y in A[x]` given the predicand `y`, 
which will recursively call the `A[x].__contains__(y)` that is here being defined.
If it is unable to demonstrate inclusion in `y in A[x]`, 
then it continues to check for inclusion in `y in T[x]`.
This fallback accomplishes the behavior described in equation 2.
Since checking `y in A[x]` requires a recursive call, 
the recursive call will also check for `y in T[x]` in its fallback,
thereby also fulfilling the behavior required by equation 3.

So now we have illuminated how to implement the behavior described by "has",
however as it has been currently described we could only implement 
this as a specialized class, since as mentioned above we know there are predicates
which do not exhibit this behavior, e.g the "be" predicate. 
We would now like to implement this behavior in such a way that 
allows it to be easily described for any bipredicate without class specialization. 
The reason we would like this is because a "can" predicate
also shares the same behavior that "has" possesses: any instance of a "can" predicate in the 
premise will result in a "can" statement in the conclusion. To demonstrate:

 * if you are an x, and x always is a y, then you always are a y
 * if you can be a x, and x can be a y, then you can be a y
 * if you are an x, and x can be a y, then you can be a y
 * if you can be an x, and x always is a y, then you can be a y

The above list describes all possible compositions between "can" and "be",
and since it matches equivalently to the complete description of composition 
between "has" and "be" (shown earlier), we say that "can" and "have" behave equivalently 
with respect to "be".

We said earlier that a "can" predicate rachets the conclusion to a "can" statement.
This can be restated in another way: any instance of a "be" predicate 
is always an instance of a "can" predicate. A "be" predicate is a "can" predicate, 
which can be represented in the notation of predicate logic as:

    can(be)

And obviously if this is the case then the same applies to "has" and "can_have":

    can_have(have)

This makes intuitive sense: in order to do something you first must have the potential to do it,
which is to to say that doing it necessarily implies you have the ability to do it. 

Likewise, every instance of a "has" predicate is an instance of a "can_have" predicate:

    can_have(has)

and, since "has" has ratcheting behavior that is equivalent to "can", 
we can capture this fact by saying that every instance of a "be" predicate 
is an instance of a "has" predicate:

    has(be)

While this last statement is  not as apparent, 
it must necessarily be true under our definition of "has",
since both "can" and "have" behave equivalently with respect to "be", 
as our full traversal through possibilities reveals.
It also makes an intuitive sense on further reflection:
the "has" system must capture all aspects of the "be" system if it were to exist in isolation.
If the "be" system was never encoded, you would need to reintroduce 
all of the same predicates of "be" to "has" in order to capture 
statements such as "if you have a socrates, you always have a man".

# Conclusion
We conclude this section with a summary for the definition of a `PredicateSystem`:

A `PredicateSystem` is meant represent a bipredicate within predicate logic
(that is, a predicate that accepts two arguments, such that it has valency 2).

It can be considered a function that returns for any predicate label "x" 
an isolated "system" of predicates that behave according to the rules of predicate logic.

In set theory, it could be considered a function that maps elements to sets, 
with a special operation that can be used to
establish subset relationships between the outputs of different systems.

More formally, a `PredicateSystem` in set theory represents a function:

    P:𝕏→𝕐 = {(x,Y):x∈𝕏 ∧ Y⊆𝕐}

such that 𝕏⊆𝕐 is an arbitrary set of elements representing the domain of P, 
𝕐 is the set of all elements that are considered by the predicate system,
and there is a special relation B~C defined for PredicateSystems B and C such that:

    ∀(x,B(x))∈B: B(x) ⊆ B(x) ⟹ C(x) ⊆ C(x)

While the above is a lot to take in, we find it allows practical uses. Observe:

```python
    be, can = PredicateSystem(), PredicateSystem()
    can(be)                     # if you already are something, then you know you have the ability to be it
    can('mortal','die')        # if you can be mortal, you can die
    be('men','mortal')         # if you are a man, you are mortal
    be('socrates','man')       # if you are socrates, you are a man
    ('socrates','die') in can   # if you are socrates, can you die?
```

# Footnote on linguistic overloading

There is one catch we've noticed in our implementation, which is a linguistic one: 
within natural language, "has" has overloaded meaning. 

In natural language, "has" could mean not only that one has something as part of their anatomy,
but that one has something as an attribute (they "have" a certain mass, or a certain volume),
or one has something in their possession (they "own" it). 

These competing interpretations do not compose well, 
we wind up with silly results when we try to do so. Observe:

```python
    can_have(cat, tail)          # cats can have tails
    has(socrates, cat)           # socrates has a cat
    (socrates, tail) in can_have # therefore socrates can have a tail
```

We could try to interpret this in a way that is correct. 
For instance, it is technically true that the tail 
is a subset of the set of points in space that highlight the possesions of Socrates,
however the tail is currently attached to the cat, and the cat won't let him hold on to it,
so he really doesn't seem to have ownership over it in the sense that we usually understand.

As we soon discover, ownership does not behave by the same rules.
Saying "you own an x, and x owns a y" does not strictly imply that you own a y,
Here are possible combinations between "own" and "has" predicates:

 * If you own an x, and x has a y as part of it, 
   then transitivity would imply misleading statements such as "the tail of socrates",
   when it is in fact that cat that has the tail.
 * If you own an x, and x owns a y, 
   then transitivity would imply misleading statements such as "the mouse of socrates",
   when it is in fact the cat that owns the mouse.
 * If you have an x as part of you, and x owns a y, 
   then transitivity would permit misleading statements such as "the ring of athens",
   since socrates could be considered a component of athens, 
   despite the fact that socrates owns the ring.

The last item in this list demonstrates other peculiarities that cause trepidation
when considering transitivity of part composition, 
but these are more problems with producing idiomatic phrasing
rather than producing false or misleading statements.
Athens has a market, and that market has a barrel, 
so do we say this barrel is "the barrel of athens", or "Athen's barrel"? 
No, but we do say that it is "a barrel of athens", 
or perhaps more idiomatically an "Athenian barrel".
This distinction could in principle be resolved elsewhere in the system
by checking for membership in some region of an animacy hierarchy, 
but this is beyond the scope of this discussion.

We can also create exhaustive lists for composition with other interpretations for the word "has",
such as to indicate when something is an attribute of something else (the "mass" of an object):

 * If you have x as an attribute, and x has y as an attribute, 
   transitivity implies statements such as "the weight of socrates" 
   on the grounds that "weight is a property of things that have mass".
   By the same reasoning it could also permit statements such as 
   the "gravity of socrates", or the "mass-energy of socrates" 
   which are less common, but are still permitted in the context of physics.
 * If you have x as an attribute, then x cannot have a y as part of it,
   since attributes are nonphysical and are not have parts, 
   though we could interpret parts as including statements like 
   "a vector has an x-component", and since "socrates has a position vector".
   This could permit statements such as "the x-component of socrates"
   but this could also be permitted if the right context was established.
 * if x is part of you, and x has a property y, 
   transitivity implies misleading statements such as "the position of socrates",
   where the position refers not to the position of his body but 
   to the position of his hand.

We find results are more subject to interpretation but still permit 
unequivocally misleading statements. It may be possible to allow transitivity in some cases,
but since we see no compelling reason to represent their transitivity,
it seems safe to ignore it for now.

On examining the alternate definitions of "has" in natural language, 
we find there is clear need to create distinct predicates for them,
however there is no clear need to articulate rules for composition, 
other than to state it does not exist.
For brevity we'll call these predicates "owns" for ownership, 
"has_part" for anatomy, and "has_trait" for attributes.
Each of these will have respective can_own, can_have_part, and can_have_trait, 
to indicate where only potential exists.

