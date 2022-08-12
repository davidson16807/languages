If you look through the output of "manual_review.py" you might notice the most frequent words tend to be problematic.
The most common words can typically be used in several contexts, including some very obscure usages.
They can also be inflected, as with pronouns, or used as slang or interjection.
This is unfortunate, since these are the words that a language learner should be first introduced to,
and their translations should ideally be kept simple and to the point.

Our only solution is to provide manual translations for these words,
however it is unsatisfactory to traverse some arbitrary number of most frequent words
and create a list of exceptions with substitutions to apply.
Doing so from experience tends to be tedious, error prone, arbitrary, 
and liable to wasted wasted effort, especially if translations are regenerated.

Our workaround is to provide manual translations only for well defined parts of speech that tend to be used frequently.
Doing so allow us to interate over smaller lists of words that are less arbitrary and more comprehensive.
Full lists of these "exceptional" parts of speech can be generated using the same scripts we use to generate regular words.
The deck builder can use these lists as an aid to create tables of manually generated translations.
If the behavior of the script changes, the manual generated translations are still every bit as valid and authoritative as they were before,
so the manual translations can be reused in this case, unlike with lists of exceptions.
For this reason, the manual generated translations are stored separately from files that are automatically generated,
so that they are not overwritten by automated processes.
Files for manually generated tables are separated by parts of speech, 
so if one table needs to be redone for whatever reason, the rest can be reused.

The following parts of speech require manual translation in order to be included in the vocabulary deck:

articles
prepositions
pronouns
conjunctions
interjections
particles
determiners

Personal pronouns are already represented comprehensively within a table for a separate deck. 
We still provide a "pronoun" table for this deck, however this table is specialized for storing nonpersonal pronouns, 
such as interrogatives and determinatives.

Some words that can be used in exceptional parts of speech can be used as other parts of speech.
For instance, "que" in Spanish can be used as a particle, a pronoun, an interjection, an adverb, and an adjective.
In this case, we would provide manual translations for the particle, pronoun, and/or interjection, as we prefer,
but the adverb and adjective would have no manually generated translation.
However, since manual translation is always guaranteed to be provided for these exceptional parts of speech,
the translations we provide are presumably suitable regardless of what part of speech they were initiated for.
So in this case que would be replaced by whatever translations we provide in the manually generated tables.

So to summarize, we need to create special lists for words that belong to exceptional parts of speech.
If any word in our target language matches a word from these lists, 
then we need to teach as if that is the only possible interpretation there could be, 
and ignore nonexceptional parts of speech.
Fortunately, making lists for these things is relatively easy compared to creating exceptions to most common words,
and the process can be aided by the scripts that generate the nonexceptional words
