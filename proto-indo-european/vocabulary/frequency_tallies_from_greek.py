import re
import collections
import itertools
import sys

import csv_functions

'''
Proto-Indo-European is a reconstructed language so it has no attested word frequencies.
There are however enough reconstructed words of its vocabulary 
that it is likely the language learner may not want to learn them all.
So there does need to be some way to convey the most important words of the language first.
We obviously have the Swadesh list to indicate words that are most conserved are therefore likely the most common,
however there are only 200 words on this list. What about the rest?

We had previously used English language word frequencies from the project Gutenberg.
Project Gutenberg covers historical texts, 
so we found it provided better frequency lists than from English language subtitles,
but we found many English words could trace back to PIE words of different frequency,
many English words in wiktionary lacked etymology altogether,
and many English words could be translated to up to several PIE words.
This caused our deck to often introduce many PIE words in a clearly suboptimal order, 
or to introduce many PIE synonyms at the same time.
Both these tendencies caused frustration when reviewing the deck.

So we now revise our deck to instead use word frequencies from other attested ancient languages.
Among the oldest candidates are Hittite, Greek, Sanskrit, and Latin.
Hittite is the oldest (first written around 1800 BCE) 
but it is only attested in cuneiform and samples of it are much less common.
Sanskrit and Latin are attested much later (around 700 BCE to 1500 CE).
Ancient Greek, however, is attested 1500 BCE to 300 BCE, 
and therefore provides the largest corpus that is most consistently composed 
closest in time to when PIE would have been spoken.
Therefore, after reviewing the Swadesh list, we choose to learn vocabulary
in the order determined by attested word frequencies in Ancient Greek.

We may eventually augment this process in the future to include frequencies from other ancient languages,
but for right now even just using Ancient Greek offers a major improvement to our deck generation.
'''

frequency_tally_tuples = csv_functions.tuples_from_csv('../../ancient-greek/vocabulary/frequency_from_classical_corpus.txt', delimeter=' ')
word_to_frequency_lookup = collections.defaultdict(lambda: 0)
for part_of_speech, word, frequency in frequency_tally_tuples:
	word_to_frequency_lookup[part_of_speech, word] += int(frequency)
word_to_frequency = csv_functions.function_from_dict(word_to_frequency_lookup)

exceptional_vocabulary_tuples = [
	*csv_functions.tuples_from_csv(foreign_language['manually_translated_exceptions']),
	*csv_functions.tuples_from_csv(foreign_language['manually_translated_parts_of_speech']),
]
exceptional_vocabulary_lookup = csv_functions.dict_from_tuples(exceptional_vocabulary_tuples, 
	['part-of-speech', 'foreign', 'key', 'text'], ['foreign', 'part-of-speech'],['key','text'])
exceptional_vocabulary_set = {
	*[row[1] for row in  exceptional_vocabulary_tuples], 
}

foreign_english = csv_functions.tuples_from_csv(foreign_language['definition'])
foreign_to_english_by_definition_lookup = csv_functions.dict_from_tuples(foreign_english, 
	['foreign','part-of-speech','lemma','text'], ['foreign','part-of-speech'], ['text'])
foreign_to_english_by_definition = csv_functions.function_from_dict(foreign_to_english_by_definition_lookup)

english_foreign = csv_functions.tuples_from_csv(foreign_language['translation'])
foreign_to_english_by_translation_lookup = csv_functions.setdict_from_tuples(english_foreign, [
	'english','part-of-speech','foreign'], ['foreign','part-of-speech'])
foreign_to_english_by_translation = csv_functions.function_from_dict(foreign_to_english_by_translation_lookup)

def get_common_translations(valid_translations, frequency_function, frequency_range_factor):
	if not valid_translations:
		return valid_translations
	else:
		sorted_translations = sorted(valid_translations, key=lambda translation:-frequency_function(translation.strip()))
		sorted_translation_frequencies = [frequency_function(translation.strip()) for translation in sorted_translations]
		return [translation 
			for (i, translation) in enumerate(sorted_translations) 
			if i == 0 or sorted_translation_frequencies[i] > sorted_translation_frequencies[0]/frequency_range_factor]

exceptional_parts_of_speech = {'article', 'preposition', 'pronoun', 'conjunction', 'interjection', 'particle', 'determiner'}

words = [(part_of_speech, word) for (part_of_speech, word) in word_to_frequency_lookup]
words = sorted(words, key=lambda pair: -word_to_frequency(*pair))
for part_of_speech, word in words:
	if ((word, part_of_speech) in exceptional_vocabulary_lookup and
		part_of_speech not in {'interjection'}):
		key = exceptional_vocabulary_lookup[word, part_of_speech]['key']
		translation = exceptional_vocabulary_lookup[word, part_of_speech]['text']
		frequency = word_to_frequency_lookup[(part_of_speech, word)]
		emoji = english_to_emoji(key, part_of_speech)
		emoji = emoji if emoji else english_to_emoji_fallback(key)
		print(f'{emoji}\t{part_of_speech}\t{word}\t{frequency}\t{translation}')
	if (word not in exceptional_vocabulary_set and 
		part_of_speech not in exceptional_parts_of_speech):
	
		translations = foreign_to_english_by_translation(word, part_of_speech)
		translations = [translation for translation in translations if translation not in english_banned_words]
		common_translations = get_common_translations(translations, english_to_frequency, 30)
		truncated_translations = [english 
			for i, english in enumerate(sorted(common_translations, key=english_to_frequency)) if i < 3]
		formatted_translations = '; '.join([
			f'to {english}' if part_of_speech == 'verb' else english 
			for english in truncated_translations])

		definition = foreign_to_english_by_definition(word, part_of_speech)
		subdefinitions = [subdefinition for subdefinition in re.split(',|\bor\b', definition)]
		split_subdefinitions = [subdefinition.strip() for subdefinition in subdefinitions]
		
		terse_subdefinitions = [re.sub('^(to|a)\b', '', subdefinition) for subdefinition in split_subdefinitions]
		reformatted_definition = '; '.join(split_subdefinitions)
		finalized_translation, finalized_emoji_tags = (
			(reformatted_definition, terse_subdefinitions)
			if 0 < len(reformatted_definition) and len(reformatted_definition) < len(formatted_translations) 
			else (formatted_translations, truncated_translations)
		)
		emojis = [
			*[english_to_emoji(tag, part_of_speech) for tag in finalized_emoji_tags],
			*[english_to_emoji(tag.lower(), part_of_speech) for tag in finalized_emoji_tags],
			*[english_to_emoji_fallback(tag) for tag in finalized_emoji_tags],
			*[english_to_emoji_fallback(tag.lower()) for tag in finalized_emoji_tags],
		]
		emoji = [emoji for emoji in emojis if emoji]
		emoji = emoji[0] if emoji else ''
		# emoji = ('true' if emoji else 'false')
		# emoji = list(itertools.chain([english_to_emoji(translation, part_of_speech) for translation in common_translations]))
		# emojis = list(itertools.chain())
		# emoji = ''
		if finalized_translation:
			print(f'{emoji}\t{part_of_speech}\t{word}\t{word_to_frequency_lookup[(part_of_speech, word)]}\t{finalized_translation}')
