TL;DR: There are momentous events in language evolution where massive numbers of loanwords are installed into a language's vocabulary at roughly the same time, to the extent that they can be characterized in future language evolution as having gone through the same shared sequence of sound laws. Borrowing from software terminology, we call a collection of these loanwords a "package", and their creation event is an "installation". Loanword packages can present obstacles to modeling language evolution if one strictly considers only sound laws. However, the behavior of these package installations can be considered regular, to the extent that a representative model can be constructed that is satisfactory for world building. We document this representative model. 

There are several representative package installations that we will consider here. We will focus on two dramatically noncognate languages that are frequently cited as examples of heavy borrowing, English and Vietnamese. Package installation events that have influenced their development include the following:

1.) Latin words introduced to English during the Scientific Revolution ("television", "relation")
2.) French words introduced to English during the Norman invasion ("judge", "tie", "beef", "marry")
3.) Latin words introduced to English during the rise of Christianity ("bible", "virgin", "sacred")
4.) Greek words introduced to Latin to convey philosophical or religious terms ("amphiprostȳlos")
5.) Borrowed words introduced to Proto Indo European ("apple", "bull")
6.) English words introduced to Vietnamese in modern times ("meeting","T.V.","internet")
7.) French words introduced to Vietnamese during French Colonialism ("coupon", "butter")
8.) Chinese words introduced to Vietnamese during the Han dynasty ("kowtow", "law", "marry", "hat", "tea")
9.) proto-Tai words introduced to Vietnamese during the pre-Han dynasty ("duck", "canal")

We notice patterns in loanword package behavior. Loanword packages can be categorized based on what type of word they install, what other have called the "semantic field" (Alves 200X). The examples above can be mapped to the following semantic fields:

1.) technology, scholarship, clinical terms
2.) social strata, law, marriage, fashion, cuisine, literature, warfare
3.) religion
4.) philosophy, scholarship, religion, nautical terms
5.) agriculture, animal husbandry
6.) business, technology
7.) fashion, cuisine, technology
8.) social strata, law, marriage, fashion, cuisine, literature, warfare, technology
9.) agriculture, animal husbandry

Lists can be created to determine whether a word in English belongs to one of these semantic fields. Vocabularies can be constructed for artificial languages by mapping to these words in English. We simulate nations interacting within a world, and if a nation of a given artificial language gains influence over a substrate language in a predefined way (for instance, the expansion of a sphere of influence, or military conquest), then there will a set of semantic fields associated with that type of influence, and each word with that semantic field in the substrate language will be replaced by equivalent words in the influential language. A filter will be words within the influential language before their installation so that phonemes from the influential language will map to nearest approximations within the substrate, and so that phonemes will be omitted if they do not conform to the phonetic structure of the substrate language. Other filters will be applied to the conjugation and declension systems of the substrate language that will blur distinctions to make the language easier to aquire, as is hypothesized to have occurred in English. 

So what are these semantic fields? What are the types of influence? How do semantic fields correspond to types of influence? Based upon our examples of package installations above, we start with the following proposals:

military conquest:  	social strata, law, marriage fashion, cuisine, literature, warfare
scholastic prestige: 	philosophy, scholarship
religious expansion: 	religion
technological invention: technology, nautical, agriculture, animal husbandry

"Military conquest" is an influence which typically results in a sweeping installation of many semantic fields, often entirely replacing words. To simplify our modeling effort, we can simply state that if a military conquest occurs, then every word in a semantic field will be replaced by the word in the influential language.

Other kinds of influence are not so sweeping, and supplement the language without replacement. This is most clearly seen in "technological" invention, where languages are not likely to replace words for semantic fields that have already been installed. For instance, we only see semantic fields regarding agriculture during very early installation events. We can simply presume there is a set of all possible semantic fields that exist up to present that relate to technology, and these semantic fields only populate when no such semantic field has yet been installed in a language. We propose the following technological semantic fields, expanding on the above list:

* computing
* engineering
* nautical terms
* terms relating to the wheel
* agriculture
* animal husbandry

We see the same pattern in scholastic and religious borrowings, where languages are not likely to replace words for existing concepts (e.g. "god" in English can refer to both the Christian "God" and pagan "gods", distinguished only by capitalization). However this sort of "co-opting" of concepts does not seem to occur as frequently in religion or scholarship. Many religious and scholastic borrowings only express concepts specific to the religions or philosophies of the influential language. For instance, we notice that early religious loanwords in English ("church") differ from late religious loanwords in English ("mosque") despite the fact that they both describe places of worship to the same deity. If a word is assigned to describe a concept in one movement, it is typically reserved from then on to refer to the concept within that specific religion. While there may be vast movements in religion or scholarship that span several religions or philosophies, like the rise of monotheism, the concepts that are developed by these movements are not typically described using interchangeable words. For this reason, we may be limited to a very small set of interchangeable words for these semantic fields, and outside these words we can do no better than to copy a list of deities and concepts from the influential language. 

