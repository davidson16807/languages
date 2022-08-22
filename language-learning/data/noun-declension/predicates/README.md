This directory contains tsv files that expresses a system of predicate logic that describes concepts occuring in natural language. It is motivated by the need to have a broad enough understanding of the words in a language to allow the procedural generation of flashcard decks that feature meaningful sentences that demonstrate the declensions of nouns, avoiding repetitive, meaningless, or unlikely sample sentences like "The man directs the horse to the egg". To demonstrate the system, the above sentence could be avoided by introducing the following predicates:

```
can-domesticate(human)
can-be-domesticate(horse)
can-eat-grass(horse)

{domesticator} {direct} {can-be-domesticate & can-eat-grass} to {grass}
```

Predicates are organized in the file structure according to their position in a rudimentary [animacy hierarchy](https://en.wikipedia.org/wiki/Animacy). Animacy hierarchies are studied in linguistics since they can have dramatic effect on the behavior of linguistic constructs, and in this context they are useful in grouping concepts in vocabulary by their capabilities. Capabilities are especially important in sentences demonstrating declension since they indicate when sentences can be meaningful. 

The animacy hierarchy used by the predicate system here is defined within `animacy-hierarchy.tsv`, along with several competing concepts that could be used to further subdivide the hierarchy. The `.tsv` files of other predicates share the same name of the predicate that describes their contents. Files are ordered into folders according to a biotic/abiotic/abstract distinction, which is opted for over a living/nonliving/abstract distinction since it helps to group plant and animal anatomy together with the plants and animals they describe.

Subdivisions within the animacy hierarchies of real world languages are often conflicting, vague, and subject to interpretation. A project such as this cannot rest on systemizations that are subject to change. The animacy hierarchy that we use for this project must be divided strictly around crisp, intuitive, and relatively unopinionated definitions that easily correspond to formal scientific definitions while being linguistically useful and unequivocally nested. Those we can state with confidence are:

 * whether something is considered able to manifest in a physical form ("physical" or "abstract")
 * whether something is alive ("living" or "nonliving"), as defined in biology
 * whether something is motile ("motile" or "sessile"), as defined in biology
 * whether something is self aware and has the capacity to speak a language 
   that is spoken by humans ("sapient" or "nonsapient")
 * whether something is biologially human ("human" or "nonhuman")

When it is is not already stated above, the above definitions exclude circumstances that involve mythology, death, or physical and mental disability.

An alternate way to consider the high level design of a predicate system is to leverage concepts typically explored in video game development, especially within sand box video games. Sand box video games are typically confronted with the same problem of representing all things which can be considered or all things which could occur. These systems are implemented gradually, using incremental software development, and there is a strong motive to simplify and clarify the software system through refactoring. The processes of implementation and refactoring can occur over many years, offering many years of thought and attention to the subject. As the predicate system here was developed, there were noticed strikingly unintentional correspondences between the important predicates of the system and data structures for game files from the "Elder Scrolls" video games. To illustrate:

```
proper-noun	non-playing character
sapient 	race
creature 	creature
static   	static
item    	item, weapon, shield, potion, food
location 	cell, interior, region, world
spoken   	dialog
```

Variables and data structure attributes, such as health, magic, disposition, time of day, etc. can further inform us of concepts that have no concrete form in the real world (things that the animacy hierarchy terms "abstract"). 
