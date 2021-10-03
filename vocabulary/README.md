This folder contains a comprehensive collection of scripts that are needed to generate Anki decks that cover the vocabulary of foreign languages. 

The user may specify the foreign language within a yaml file. The name of the yaml file is the first and only argument to these scripts. 

Our approach in generating vocabulary decks is to forego considering individual words and to treat an entire vocabulary table as an object. Such an object can be passed as input to a function, producing new objects, representing new vocabulary tables. Another viewpoint is to consider each of these table objects as their own function. Each of these functions accepts a tuple of text values as input and returns a tuple of text values as output.

This approach can be seen in the commutative diagram under "CATEGORY.png", which depicts the way in which Anki decks are generated (this is also stored using LaTeX with tikcd, under "CATEGORY.latex"). Nodes within the commutative diagram represent vocabulary tables functions that map to and from text. All but a few of these functions in this diagram are stored within .tsv files as tab-separated columns that represent the input and output of the function. The remaining functions are represented procedurally (for instance, the `inflection` function, which is provided by a 3rd party python library). Arrows within the commutative diagram represent python scripts that generate these .tsv files using one or more files on disk. Although we would like to consolidate deck generation into a single python file, the time needed to run that file would be restrict turn around time, and the script would make it difficult to evaluate and troubleshoot output.

The first step of our deck generation process generates mapping functions from the English Wiktionary. These functions will be needed later in the process. They perform tasks such as mapping inflections to their root words, and identifying the parts of speech by which a word in a language may be used. 

Next, the process traverses through a list of words matched with their frequency. It is expected the user provides this list. 

I highly recommend using the frequencies compiled by this man from OpenSubtitles:

https://github.com/hermitdave/FrequencyWords/tree/master/content/2016

Subtitles generally provide the best frequency lists if the language learner wants to converse in the language. However, if the language is being learned to read classical texts, then it may be better to use a frequency list based around a corpus of classic texts, such as from project Gutenberg, or this man's work:

http://kyle-p-johnson.com/blog/2015/04/23/most-common-greek-latin-words.html

Wiktionary also provides nonstandardized frequency lists for many languages: 

https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists

Words within the frequency list are standardized and coupled to their parts of speech, then consolidated to create `frequency-tallies`, which indicates a proposed frequency for the number of times that a word is used in a language as a given part of speech, regardless of whether it is inflected.

Translations are themselves generated from the English wiktionary. This can be done in two ways: either by looking up translations for the English word (`vocabulary-translation-source`), or by looking up the foreign language word and reading its definition in English (`vocabulary-definition-source`). We generally prefer the former method, unless the latter method provides a more succinct definition, where "succinctness" is defined by character count.

Once the list of translations are generated, we iterate through the words in `frequency-tallies`, starting with the most common, and use their translations to create flashcards for Anki. Additional files outside this folder are used to order English translations by frequency, eliminate offensive translations, and display emoji depictions where applicable.

