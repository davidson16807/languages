import csv_functions

english_to_emoji_tuples = csv_functions.tuples_from_csv('../../emoji/vocabulary.tsv')
english_to_emoji = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english','part-of-speech']),
	sentinel = '') 
english_to_emoji_fallback = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english'],['emoji']),
	sentinel = '')

frequency_tally_tuples = csv_functions.tuples_from_csv('frequency_tallies.tsv')
for part_of_speech, word, frequency in frequency_tally_tuples:
	emojis = {
		*[english_to_emoji(word, part_of_speech)],
		*[english_to_emoji(word.lower(), part_of_speech)],
		*[english_to_emoji_fallback(word)],
		*[english_to_emoji_fallback(word.lower())],
	}
	emoji_text = ' '.join(emojis)
	print(f'{word}\t{part_of_speech}\t{emoji_text}')
