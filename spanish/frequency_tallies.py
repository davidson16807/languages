import re
import collections

import inflection

import csv_functions

standardize_tuples = csv_functions.tuples_from_csv('standardize.tsv')
standardize_lookup = csv_functions.setdict_from_tuples(standardize_tuples, ['variant','part-of-speech','standardized'], ['variant','part-of-speech'])
standardize = csv_functions.function_from_dict(standardize_lookup)

parts_of_speech_tuples = csv_functions.tuples_from_csv('part-of-speech.tsv')
parts_of_speech_lookup = csv_functions.setdict_from_tuples(parts_of_speech_tuples, ['word','part-of-speech'], ['word'])
parts_of_speech = csv_functions.function_from_dict(parts_of_speech_lookup)

word_frequency = csv_functions.tuples_from_csv('frequency-from-subtitles.tsv', delimeter=' ')
frequency_to_word = [word for (word, frequency) in word_frequency]
word_to_frequency = csv_functions.function_from_dict(
	{word:int(frequency) for (word, frequency) in word_frequency},
	sentinel=0)

uncommon_conjugations = {
	'nada','así','uno','una','para',
	'mano','sobre','hermano','visto','justo','serio','cerca','incluso','sangre','medio','calle',
	'casa','casas','caso',
	'cosa','cosas',
	'nombre','nombres',
	'tarde','tardes',
	'esposa','esposas','esposo',
	'idea','ideas',
}
uncommon_adjectives = {

}
uncommon_nouns = {
	'la','e','pasa','no','a','ni'
}

# traverse words, starting with the most frequent first
for word, frequency in word_frequency:
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

