import re
import collections
import sys
import yaml

import inflection

import csv_functions

foreign_language_config_filename = sys.argv[1]
foreign_language = yaml.load(open(foreign_language_config_filename, 'r'))

english_frequency = csv_functions.tuples_from_csv(foreign_language['frequency'], 
	delimeter=foreign_language['frequency_delimeter'])
frequency_to_english = [columns[0] for columns in english_frequency if len(columns) == 2]
english_to_frequency = csv_functions.function_from_dict(
	{columns[0]:int(columns[1]) for columns in english_frequency if len(columns) == 2},
	sentinel=0)

frequency_tally_tuples = csv_functions.tuples_from_csv(foreign_language['frequency_tallies'])
world_to_frequency_lookup = collections.defaultdict(lambda: 0)
for part_of_speech, word, frequency in frequency_tally_tuples:
	world_to_frequency_lookup[part_of_speech, word] += int(frequency)
word_to_frequency = csv_functions.function_from_dict(world_to_frequency_lookup)

spanish_english = csv_functions.tuples_from_csv(foreign_language['definition'])
spanish_to_english_by_definition_lookup = csv_functions.dict_from_tuples(spanish_english, ['spanish','part-of-speech','lemma','text'], ['spanish','part-of-speech'], ['text'])
spanish_to_english_by_definition = csv_functions.function_from_dict(spanish_to_english_by_definition_lookup)

english_spanish = csv_functions.tuples_from_csv(foreign_language['translation'])
spanish_to_english_by_translation_lookup = csv_functions.setdict_from_tuples(english_spanish, ['english','part-of-speech','spanish'], ['spanish','part-of-speech'])
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

words = [(part_of_speech, word) for (part_of_speech, word) in world_to_frequency_lookup]
words = sorted(words, key=lambda pair: -word_to_frequency(*pair))
for part_of_speech, word in words:
	translations = spanish_to_english_by_translation(word, part_of_speech)
	sorted_translations = sorted(get_common_translations(translations, english_to_frequency, 30), key=english_to_frequency)
	formatted_translations = '; '.join([english
			for i, english in enumerate(sorted_translations) 
			if i < 3])
	definition = spanish_to_english_by_definition(word, part_of_speech)
	if part_of_speech in ['article', 'conjunction', 'determiner', 'interjection', 'particle', 'preposition', 'pronoun']:
		finalized_translation = definition if 0 < len(definition) and len(definition) < len(formatted_translations) else formatted_translations
		suggested_key = sorted_translations[0] if len(sorted_translations) > 1 else finalized_translation
		print(part_of_speech, '\t', word, '\t', suggested_key, '\t', finalized_translation, '\t', definition, '\t', '; '.join(translations))

