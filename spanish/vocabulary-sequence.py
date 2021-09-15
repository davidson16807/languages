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

interjection_vocabulary_tuples = [(part_of_speech, spanish.strip(' !?'), spanish, key, english)
	for (part_of_speech, spanish, key, english) in csv_functions.tuples_from_csv('manually_translated_interjections.tsv')]
interjection_vocabulary_lookup = csv_functions.dict_from_tuples(
	interjection_vocabulary_tuples,
	['part-of-speech', 'spanish-key', 'spanish', 'english-key', 'english'], ['spanish-key', 'part-of-speech']
)

exceptional_vocabulary_tuples = [
	*csv_functions.tuples_from_csv('manually_translated_articles.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_conjunctions.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_determiners.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_particles.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_prepositions.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_pronouns.tsv'),
	*csv_functions.tuples_from_csv('manually_translated_exceptions.tsv'),
]
exceptional_vocabulary_lookup = csv_functions.dict_from_tuples(exceptional_vocabulary_tuples, 
	['part-of-speech', 'spanish', 'key', 'text'], ['spanish', 'part-of-speech'],['key','text'])
exceptional_vocabulary_set = {
	*[row[1] for row in  exceptional_vocabulary_tuples], 
	# *[row[1] for row in  interjection_vocabulary_tuples]
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
	if (word, part_of_speech) in exceptional_vocabulary_lookup:
		key = exceptional_vocabulary_lookup[word, part_of_speech]['key']
		translation = exceptional_vocabulary_lookup[word, part_of_speech]['text']
		frequency = word_to_frequency_lookup[(part_of_speech, word)]
		emoji = english_to_emoji(key, part_of_speech)
		emoji = emoji if emoji else english_to_emoji_fallback(key)
		print(f'{emoji}\t{part_of_speech}\t{word}\t{frequency}\t{translation}')
	# if (word, part_of_speech) in interjection_vocabulary_lookup:
	# 	interjection = interjection_vocabulary_lookup[word, part_of_speech]
	# 	spanish = interjection['spanish']
	# 	translation = interjection['text']
	# 	frequency = word_to_frequency_lookup[(part_of_speech, word)]
	# 	print(f'interjection\t{spanish}\t{frequency}\t{translation}')
	# 	print(f'interjection\t{spanish}\t{frequency}\t{translation}')
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
		finalized_translation = definition if 0 < len(definition) and len(definition) < len(formatted_translations) else formatted_translations
		emojis = [
			*[english_to_emoji(definition, part_of_speech)],
			*[english_to_emoji(translation, part_of_speech) for translation in truncated_translations],
			*[english_to_emoji(definition.lower(), part_of_speech)],
			*[english_to_emoji(translation.lower(), part_of_speech) for translation in truncated_translations],
			*[english_to_emoji_fallback(definition, part_of_speech)],
			*[english_to_emoji_fallback(translation) for translation in truncated_translations],
			*[english_to_emoji_fallback(definition.lower(), part_of_speech)],
			*[english_to_emoji_fallback(translation.lower()) for translation in truncated_translations]
		]
		emoji = [emoji for emoji in emojis if emoji]
		emoji = emoji[0] if emoji else ''
		# emoji = ('true' if emoji else 'false')
		# emoji = list(itertools.chain([english_to_emoji(translation, part_of_speech) for translation in common_translations]))
		# emojis = list(itertools.chain())
		# emoji = ''
		if finalized_translation:
			print(f'{emoji}\t{part_of_speech}\t{word}\t{word_to_frequency_lookup[(part_of_speech, word)]}\t{finalized_translation}')
