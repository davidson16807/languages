This directory contains tsv files that expresses a system of predicate logic that describes concepts that occur in natural language. It is motivated by the need to have a broad enough understanding of the words in a language to allow the procedural generation of flashcard decks that feature meaningful sentences that demonstrate the declensions of nouns, avoiding repetitive, meaningless, or unlikely sample sentences like "The man directs the horse to the egg". To demonstrate the system, the above sentence could be avoided by introducing the following predicates:

```
can-domesticate(human)
can-be-domesticate(horse)
can-eat-grass(horse)

{domesticator} {direct} {can-be-domesticate & can-eat-grass} to {grass}
```

Predicates are organized in the file structure according to their position in a [animacy hierarchy](https://en.wikipedia.org/wiki/Animacy). Animacy hierarchies are studied in linguistics since they can have dramatic effect on the behavior of linguistic constructs, and in this context they are useful in grouping concepts in vocabulary by their capabilities. Capabilities are especially important in sentences demonstrating declension since they indicate when sentences can be meaningful. 

The animacy hierarchy used by the predicate system here is defined within `animacy-hierarchy.tsv`, along with defintions for classes within the hierarchy. Additional groups of classes within the hierarchy are further defined within `animacy-groups.tsv`, some of which form alternate hierarchies.

An alternate way to consider the high level design of a predicate system is to leverage concepts typically explored in video game development, especially within sand box video games. Sand box video games are typically confronted with the same problem of representing all things which can exist in the world, as well as all things that can occur within it. These systems are implemented gradually, using incremental software development, and there is a strong motive to simplify and clarify the software system in the process of refactoring code. The processes of implementation and refactoring can occur over many years, bringing with it the benefit of all the thought and attention paid towards it. As an example, the following table maps predicates in the system here to data structures from game files for the "Elder Scrolls" video games. 

```
sapient 	race, non-playing character
creature 	creature
static   	static
item    	item, weapon, shield, potion, food
location 	cell, interior, region, world
spoken   	dialog
```

Variables and data structure attributes, such as health, magic, disposition, time of day, etc. can further inform us of concepts that have no concrete form in the real world (things that the animacy hierarchy terms "abstract"). 