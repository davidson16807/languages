import re
import collections
import sys
import yaml

import inflection

import csv_functions

foreign_language_config_filename = sys.argv[1]
foreign_language = yaml.load(open(foreign_language_config_filename, 'r'))

word_frequency = csv_functions.tuples_from_csv(foreign_language['frequency'], delimeter=foreign_language['frequency_delimeter'])
frequency_to_word = [columns[0] for columns in word_frequency if len(columns) == 2]
word_to_frequency = csv_functions.function_from_dict(
	{columns[0]:int(columns[1]) for columns in word_frequency if len(columns) == 2},
	sentinel=0)

standardize_tuples = csv_functions.tuples_from_csv(foreign_language['standardize'])
standardize_lookup = csv_functions.setdict_from_tuples(standardize_tuples, ['variant','part-of-speech','standardized'], ['variant','part-of-speech'])
standardize = csv_functions.function_from_dict(standardize_lookup)

parts_of_speech_tuples = csv_functions.tuples_from_csv(foreign_language['part_of_speech'])
parts_of_speech_lookup = csv_functions.setdict_from_tuples(parts_of_speech_tuples, ['word','part-of-speech'], ['word'])
parts_of_speech = csv_functions.function_from_dict(parts_of_speech_lookup)

uncommon_conjugations = (
	foreign_language['uncommon_conjugations'] 
	if 'uncommon_conjugations' in foreign_language else {}) 
uncommon_adjectives = (
	foreign_language['uncommon_adjectives'] 
	if 'uncommon_adjectives' in foreign_language else {})
uncommon_nouns = (
	foreign_language['uncommon_nouns'] 
	if 'uncommon_nouns' in foreign_language else {})

# traverse words, starting with the most frequent first
for columns in word_frequency:
	if len(columns) == 2:
		word = columns[0]
		frequency = columns[1]
		valid_parts_of_speech = parts_of_speech(word)
		for part_of_speech in valid_parts_of_speech:
			standardizations = {word}

			# set hard limit to number of times to reapply standardization to prevent infinite loops
			for i in range(0,5):
				restandardizations = {restandardized 
					for standardized in standardizations 
					for restandardized in standardize(standardized, part_of_speech)}
				standardizations = restandardizations if restandardizations else standardizations

			if (not ( part_of_speech == 'verb' and word in uncommon_conjugations) and
				not ( part_of_speech == 'adjective' and word in uncommon_adjectives) and
				not ( part_of_speech == 'noun' and word in uncommon_nouns)):
				for standard in standardizations:
					print(part_of_speech, '\t', standard.lower(), '\t', frequency)

