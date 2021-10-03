import re
import collections
import itertools

import inflection

import csv_functions

english_to_emoji_tuples = csv_functions.tuples_from_csv('../emoji/vocabulary.tsv')
english_to_emoji = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english','part-of-speech']),
	sentinel = '') 
english_to_emoji_fallback = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english'],['emoji']),
	sentinel = '')

english_banned_words = set(csv_functions.lines_from_file('../english/banned-words.tsv'))

english_frequency = csv_functions.tuples_from_csv('../english/frequency-from-subtitles.tsv', delimeter=' ')
frequency_to_english = [english for (english, frequency) in english_frequency]
english_to_frequency = csv_functions.function_from_dict(
	{english:int(frequency) for (english, frequency) in english_frequency},
	sentinel=0)

frequency_tally_tuples = csv_functions.tuples_from_csv('frequency-tallies.tsv')
word_to_frequency_lookup = collections.defaultdict(lambda: 0)
for part_of_speech, word, frequency in frequency_tally_tuples:
	word_to_frequency_lookup[part_of_speech, word] += int(frequency)
word_to_frequency = csv_functions.function_from_dict(word_to_frequency_lookup)

exceptional_vocabulary_tuples = [
	*csv_functions.tuples_from_csv('manually_translated_parts_of_speech.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_exceptions.tsv'),
]
exceptional_vocabulary_lookup = csv_functions.dict_from_tuples(exceptional_vocabulary_tuples, 
	['part-of-speech', 'spanish', 'key', 'text'], ['spanish', 'part-of-speech'],['key','text'])
exceptional_vocabulary_set = {
	*[row[1] for row in  exceptional_vocabulary_tuples], 
}

spanish_english = csv_functions.tuples_from_csv('vocabulary-definition-source.tsv')
spanish_to_english_by_definition_lookup = csv_functions.dict_from_tuples(spanish_english, 
	['spanish','part-of-speech','lemma','text'], ['spanish','part-of-speech'], ['text'])
spanish_to_english_by_definition = csv_functions.function_from_dict(spanish_to_english_by_definition_lookup)

english_spanish = csv_functions.tuples_from_csv('vocabulary-translation-source.tsv')
spanish_to_english_by_translation_lookup = csv_functions.setdict_from_tuples(english_spanish, [
	'english','part-of-speech','spanish'], ['spanish','part-of-speech'])
spanish_to_english_by_translation = csv_functions.function_from_dict(spanish_to_english_by_translation_lookup)

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
		print(f'{word}\t{part_of_speech}\t{emoji}\t{translation}')
	if (word not in exceptional_vocabulary_set and 
		part_of_speech not in exceptional_parts_of_speech):
	
		translations = spanish_to_english_by_translation(word, part_of_speech)
		translations = [translation for translation in translations if translation not in english_banned_words]
		common_translations = get_common_translations(translations, english_to_frequency, 30)
		truncated_translations = [english 
			for i, english in enumerate(sorted(common_translations, key=english_to_frequency)) if i < 3]
		formatted_translations = '; '.join([
			f'to {english}' if part_of_speech == 'verb' else english 
			for english in truncated_translations])

		definition = spanish_to_english_by_definition(word, part_of_speech)
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
		if finalized_translation:
			emoji_text = ' '.join(emojis)
			print(f'{word}\t{part_of_speech}\t{emoji_text} {finalized_translation}')
