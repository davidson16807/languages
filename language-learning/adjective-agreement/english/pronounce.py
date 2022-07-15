import csv_functions

# standardize_tuples = csv_functions.tuples_from_csv(foreign_language['standardize'])
# standardize_lookup = csv_functions.setdict_from_tuples(standardize_tuples, ['variant','part-of-speech','standardized'], ['variant','part-of-speech'])
# standardize = csv_functions.function_from_dict(standardize_lookup)

parts_of_speech_tuples = csv_functions.tuples_from_csv('part_of_speech.tsv')
parts_of_speech_lookup = csv_functions.setdict_from_tuples(parts_of_speech_tuples, ['word','part-of-speech'], ['word'])
parts_of_speech = csv_functions.function_from_dict(parts_of_speech_lookup)

text = 'the quick brown fox jumps over the lazy dog'
text = 'our father who art in heaven, hallowed be thy name'

for word in text.split(' '):
	print(word, parts_of_speech(word))

