
import csv_functions
import re

def foreign_to_english_card(emoji, part_of_speech, foreign, english):
	emoji_style = "font-size:3em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
	return f'''<br/>
<div style="font-size:3em">{foreign}</div>
\t
<div style="{emoji_style}">{emoji}</div>
<div style="font-size:small">{part_of_speech}</div>
<div style="font-size:large">{english}</div><br/>'''.replace('\n','')

def english_to_foreign_card(emoji, part_of_speech, english, foreign):
	emoji_style = "font-size:3em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
	return f'''<br/>
<div style="{emoji_style}">{emoji}</div>
<div style="font-size:large">{english}</div>
<div style="font-size:small">{part_of_speech}</div>
\t
<div style="font-size:3em">{foreign}</div>'''.replace('\n','')

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
	formatted_english = f'to {english}' if part_of_speech == 'verb' else english
	emojis = [
		english_to_emoji(lemma, part_of_speech),
		english_to_emoji(lemma.lower(), part_of_speech),
		*english_to_emoji_fallback(lemma),
		*english_to_emoji_fallback(lemma.lower()),
	]
	emoji = [emoji for emoji in emojis if emoji]
	emoji = emoji[0] if emoji else ''
	print(english_to_foreign_card(emoji, part_of_speech, english, foreign))
	print(foreign_to_english_card(emoji, part_of_speech, foreign, english))
