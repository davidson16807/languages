See GLOSSARY.tsv for a summary of the terms introduced here.

The terms used in this project are based on a systemization that was first adopted by Leonard Bloomfield in his book, "Language" (1933) 
then later expanded by Kenneth Pike in his own book ("Language in Relation to a Unified Theory of the Structure of Human Behavior", 1965).
We will attempt to remain consistent with the definitions that were provided by Leonard Bloomfield,
however to prevent any ambiguity we will provide our own definitions here.
The definitions we provide are meant to be grounded on a foundation of set theory and category theory,
but though we may occassionally dive into these subjects, we will still provide definitions in terms that we expect most readers will understand.
We hope that in discussing definitions this way we will still at least offer clarity greater than what was seen while surveying the literature.

Our discussion of terminology begins by leveraging a set of preexisting terms from phonology: the terms "phone" and "phoneme". 
We will define a "phone" as *an indivisible unit of sound* that has been *attested to convey a distinction in meaning* within *any natural language*.
The phones are *initial objects* in categories where objects are *human utterances* and arrows map *how utterances compose from smaller utterances*.
The phones are *disjoint sets* of sound whose *union* is the infinitely subdivisible continuum of all sounds that have ever been made by humans during speech.
Another way to phrase this is to say the phones are *equivalence classes*, or the *fibers* of a *bundle* defined for some function mapping *sound→phone*.
More precisely, we define that any two sounds of the same phone can be interchanged 
in any statement of any attested natural language and still produce the same meaning.
This is to say that each phone is an *equalizer* of sounds for a given set of functions, which we will now attempt to define.
Suppose there is a function f:U→(S+1) that for any utterance maps to the semantic meaning (S) received by an audience in that language, or no meaning (1) if the utterance is unintelligible.
Suppose there is also a function: g:L→U that for any any attested natural language maps to the set of all meaningful utterances made in that language, such that the diagram L→U→S commutes. 
For every l∈L, and for every utterance u∈g(l), we say there is a function, h(l,u):P×P→U that replaces every instance of one sound in a phone P with another in the utterance u
The phone is then the following equalizer:
	Eq({f∘h(l,u) | l∈L, u∈g(l)})

Likewise, we will define a "phoneme" as *an indivisible unit of sound* that is *capable conveying a distinction in meaning* within *a given language*.
The phonemes of a language are disjoint sets of phones whose union is what is known as the *phoneme inventory* of that language.
The phonemes are defined such that any two phones of the same phoneme can be interchanged 
in any statement of the phonemes' language and still produce the same meaning.
Equivalently, the phonemes are equalizers of phones for a set of functions:
	Eq({f∘hₘ(u) | u∈g(l)})
where l∈L is a language, f and g match the definitions above, and hₘ(u):Pₘ×Pₘ→U replaces every instance of one sound in a phoneme Pₘ with another in the utterance u

To illustrate, in Japanese there is no distinction between the phones made by the letters "l" and "r",
so to Japanese speakers the English words "lap" and "rap" may sound indistinguishable despite being different words.
Meanwhile in English you can choose to roll the letter "r" without altering the meaning of words,
however doing so in Spanish might cause the word for "but" ("pero") to be mistaken for the word for "dog" ("perro").
We therefore say in Japanese the sounds conveyed by letters "l" and "r" correspond to the same phoneme,
whereas in English "l" and "r" correspond to different phonemes but not the sounds that correspond to the rolled and unrolled "r",
and in Spanish all three sounds correspond to different phonemes.
If Japanese, English, and Spanish were the only natural languages ever to have been attested,
we would then have to declare that the "rolled r", "unrolled r", and "l" were each instances of a phone.

The system of phonemes that are used by a language are known as that language's "phonemics",
whereas the study of phones across all languages is known as "phonetics". 
We therefore create a distinction between what are known as "-emic" and "-etic" units,
where "-etic" units (indicated here without a suffix) apply to all attested natural languages,
and "-emic" units (suffixed by "-eme") are specific to a given language.

Just as "-emic" and "-etic" units can be assigned precise mathematical definitions in phonology,
so too can can we create units that are *functorial* to these definitions in other categories.
We will broadly define any "-etic" unit as an equalizer for some set of functions that must be defined.
This set of functions can be partitioned into disjoint subsets, and to each disjoint subset there exists a set of "-emic" units.
Each "-emic" unit for a disjoint subset is an equalizer for that disjoint subject, whose members are "-etic" units.
Therefore to define any "-emic/-etic" pair, we first need to define the disjoint sets of functions that "-emic" units equalize, 
and then we must define -etic unit, typically being the equalizer of the union of these sets of functions.
In the context of linguistics, we will say that every natural language that has ever been attested 
maps to its own disjoint set of functions that an "-emic" unit equalizes,
and any "-etic" unit in linguistics always considers in some way all attested natural languages.

We will next enumerate the terms that have resulted from us applying this technique.

Just as a "phoneme" describes an indivisible unit of sound that is capable of *representing a distinction* in a language,
a "morpheme" is said to describe an indivisible unit of sound that is capable of *conveying a distinct meaning* in a language.
To illustrate, in Japanese the morpheme "ga" is a particle that follows a word to indicate the subject of a sentence,
and in English "-able" (in words such as "doable") is a suffix that is used to indicate when an action indicated by a verb can be performed.
By analogy a "morph" is an indivisible unit of sound capable of conveying *any meaning* in *any attested natural language*. 
Multiple morphs may correspond to the same morpheme, so for instance in English the "-ible" suffix in a word such as "feasible" 
is seen as equivalent in meaning as the "-able" suffix in a word such as "doable". Both are each recognized by English speakers 
as being part of the same morpheme, which broadly represents how some variant of "-[ia]ble" can be tacked onto a verb to indicate potentiality.
Examples of homomorphs in English include the "-s" suffix that indicates the plural of a noun ("the cats run")
and the "-'s" suffix (with appostrophe) that indicates the possessive of a noun ("the cat's ear")

We therefore say that a "morpheme" is the equalizer for a set of functions:
	Eq({f∘hₘ(u) | u∈g(l)})
where l∈L is a language, f and g match the definitions above, and hₘ(l,u):Mₘ×Mₘ→U replaces every instance of one sound in a phoneme Pₘ with another in the utterance u
such that for each pair of phoneme tuples in the same morpheme M of a given language, and for each utterance in that language u∈U(l),
we say there is a function, f(u):M×M→U→(R+1) that replaces every instance of one morpheme with the other in the utterance and maps the utterance 
either to a meaning R received by an audience in that language, or to no meaning if the utterance is unintelligible.
A morph is however not just the equalizer for the union of these sets of functions for all attested natural languages,
since it also is typically used to convey distinctions in sound that do not carry meaning, 
so we must say that the morph is the equalizer of functions g(u):M×M→U→R

Likewise, a "sememe" is said to be the equivalence class of meanings (or "semes") that are suggested by a morpheme, 
of which one of the "semes" represents what the speaker *intends* to communicate. 
During speech, the speaker must map the seme he intends to communicate to a "sememe" that can be conveyed by a morpheme. 
"Allosemes" are then distinct sememes that represent the same seme.
The concept of the seme and sememe is useful for conveying certain distinctions in meaning that may be present in one language but not another.
To illustrate, speakers of Ergative-Absolutive languages distinguish morphemes based upon whether a verb is transitive or intransitive,
whereas speakers of Nominative-Accusative languages are wholly unfamiliar with these distinctions and do not mark them in any way.
The concept of a "subject" in a Nominative-Accusative language is a sememe that refers to the semes of both the 
"solitary" and "agent" sememes of the Ergative-Absolutive languages.
If one were able to create a system that could represent any distinction present in the morphemes of any attested natural language,
such a system would consist of a set of "semes" that each correspond to multiple semes.

We will now make an observation: a "seme" is not strictly indivisible as a unit of meaning. 
A seme *can* be decomposed further into smaller units, and these units will still have meaning, 
however *these units will not correspond to any morpheme*, and this was an esstential property of a seme,
so these subdivided units cannot be called "semes", and they must be called by a different word.
To illustrate this point, in Spanish "-isteis" is a morpheme that indicates 
that an audience of several people has completed at some point in the past an action that is indicated by the verb being inflected.
The sememe that maps to this morpheme must therefore simultanesously represent the second person, plural number, past tense, and perfect aspect.
We could attempt to reanalyze the "-isteis" morpheme as a set of smaller morphemes in an effort to make its sememe indivisible,
for instance we could represent it as a combination of "-iste"+"-is", where "-iste" represents second person broadly, and "-is" indicates plurality,
however "-iste" still represents both the past tense and perfect aspect, so it can still be divided into smaller units of meaning,
but fluent speakers of the language will not be able to understand any such subdivision if we were to attempt representing it by sound.
We should therefore introduce a new term to describe these smaller, indivisible units of meaning that do not necesarrily correspond to a morpheme.
The only other term available in literature that describes another unit of meaning is the "episememe", which is a term introduced by Leonard Bloomfield (1933).
It is unfortunate Bloomfield defines "episememe" in only a vague way: he defines it simply as an indivisible unit of meaning that corresponds to grammar,
however there is no definition as to what grammar constitutes so we are no better off for having it.
We will nevertheless coopt this term in an attempt to rehabilitate it with what should be a stronger definition. 
Our stronger definition is as follows: in a manner analogous to semes, 
an "episeme" will be defined as an *indivisible unit of meaning* that is *intended by the speaker*,
and much like phonemes are an indivisible unit of sound that can represent distinctions in morphemes, 
we will define an "episememe" to be thean indivisible unit of meaning* that is capable of *representing a distinction in sememes* 
(and by extension, the morphemes) of a *given language*.
To illustrate again with the "-isteis" example, the Spanish morpheme "-isteis" indicates a plural audience in past tense and perfect aspect,
whereas the Spanish morpheme "-iste" indicates singular audience in past tense and perfect aspect,
so the sememes that correspond to the "-isteis" and "-iste" morphemes differ only in their grammatical number.
Singular and plural must therefore be distinct episememes in Spanish.
As it turns out, these are the only two episememes to indicate number in Spanish,
however many languages of the world also have a "dual" number that indicates when there is two of something,
and in principle the speaker might have some precise number in their head that they want to convey in a morpheme, such as 42 or 10⁹, 
so the precise number in the speaker's head is an example of an "episeme",
and were we to compile a full list of grammatical numbers available in all the world's attested natural languages, 
such a list could be said to consist of "episemes". 
"Alloepisemes" meanwhile would be in principle distinct episememes that correspond to the same episeme.

The last concept we wish to introduce relies upon an analogy between the concepts introduced thus far.
The episeme and seme constitute units of grammatical meaning that cannot be divided without sacraficing a certain constraint specific to a language.
Likewise, the morpheme is a unit of sound that that cannot be divided without sacraficing a certain constraint specific to a language.
The morpheme and the sememe are very closely related concepts, since a sememe maps directly to a morpheme in a given language,
however the two are in distinct in one way: two morphemes can represent the same sememe, differing only in the sounds they use to represent the sememe.
This could in principle be observed in a single language however it is especially noticeable when comparing morphemes across languages. 
An simple example of this can be seen by comparing the Spanish root verb "poner" with the English root verb "pose".
These two morphemes don't even share consonants of the same manner of articulation, 
yet the two share similar if not identical meaning and even share similar usage thanks to their shared etymology.
We see how the two can be used similarly by comparing Spanish "suponer" with English "suppose", Spanish "disponer" with English "dispose", etc.
In this case the morphemes "poner" and "pose" are undoubtedly distinct in sound, yet if their semmemes are comprised of the same set of semes,
then by the definition of a sememe there is nothing further that could be argued to distinguish them - the sememes would be equivalent up to the definition of a sememe.

This distinction between the meaning of something and its representation(s) in one or more languages can be useful,
so we must ask if we can make a similar distinction with regard to an episememe? 
Does any concept exist that could indicate the way an epsememe is represented in a language?
Such a concept could not possibly have sound associated to it, since the morpheme is by definition an indivisble unit of sound that carries any meaning,
however we could perhaps define a concept based around the way the episememe is represented in a language's *grammar*.
Such a concept will be termed the "tagmeme", again borrowing from Leonard Bloomfield, who defines the tagmeme as an indivisble meaningful unit of grammar.
We find Bloomfield's definition compatible with ours, however we provide our own definition here for clarity:
a "tagmeme" is *indivisible unit of grammatical representation* that is capable of *representing a difference between morphemes* in a language.
So to illustrate, two possible tagmemes in Spanish are the manner in which the episememes for singular and plural are represented through the use of inflection.

We will now pause for a while so we can discuss our extended analogy of "-emic/-etic" units in the abstract. 
Let us say we encounter a set of elements of the same data type. We will indicate this set with the letter "X". 
Members of X, denoted x∈X, are each considered distinct from one another in some way,
and it is up to the originators the concept to define this distinction if it is useful.

We will practice using our mathematical formalism above by using it to retroactively define the concepts surrounding a "phone". 
There is a set "phones" whose elements are human utterances distinct in the manner, place, and voice of their articulation,
without necessarily being distinct in their sound as perceived by humans. There exist a set of functorial subcategories that we will address as "attested natural languages",
and to each subcategory in the set of attested natural languages, we will introduce a product that describes how objects known as "morphs" are composed of objects known as "phonemes". 
There exist a subcategory of this subcategory that represents the set of phones, and a "phoneme" is the limit on this subcategory that captures the product describing morphs. 
Any possible phone in this subcategory will map to exactly one phoneme, and it through the composition of this map that the phone can perform all the behavior of its phoneme.
The function that maps each phone to its phoneme is then denoted phonemics:phone→phoneme. If we were to consider the entire category that represents all attested natural languages,
then a "phone" is the limit on the subcategory of phones that captures the product describing morphs in any language

If one is to adapt the "phoneme analogy" to their own topic of interest, they must therefore specify at minimum the following:
* the data type X
* the manner in which elements of X are distinct
* the set of functorial subcategories, C that distinguishes the -emic from the -etic unit
* a subcategory for each c∈C whose limit defines the -emic and -etic unit of the data type X

The table defined in classifications.tsv illustrates the extensions to this analogy that we have used in this project,
and the table in GLOSSARY.tsv condenses the terms that were introduced here.