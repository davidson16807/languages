
import csv_functions
import re

foreign_language = {
	'emoji': '../../emoji/vocabulary.tsv',
}

english_to_emoji_tuples = csv_functions.tuples_from_csv(foreign_language['emoji'])
english_to_emoji = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english','part-of-speech']),
	sentinel = '') 
english_to_emoji_fallback = csv_functions.function_from_dict(
	csv_functions.dict_from_tuples(english_to_emoji_tuples, ['emoji','part-of-speech','english'], ['english'],['emoji']),
	sentinel = '')

english_foreign_tuples = csv_functions.tuples_from_csv('vocabulary-source-swadesh.tsv')

for english, lemma, part_of_speech, foreign in english_foreign_tuples:
	if foreign:	
		formatted_english = f'to {english}' if part_of_speech == 'verb' else english
		emojis = [
			english_to_emoji(lemma, part_of_speech),
			english_to_emoji(lemma.lower(), part_of_speech),
			*english_to_emoji_fallback(lemma),
			*english_to_emoji_fallback(lemma.lower()),
		]
		emoji = emojis[0] if emojis else ''
		print(f'{emoji}\t{part_of_speech}\t{english}\t{foreign}')
