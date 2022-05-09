import sys
import yaml

import csv_functions

foreign_language_config_filename = sys.argv[1]
foreign_language = yaml.load(open(foreign_language_config_filename, 'r'))

def format_foreign(foreign):
	return conjugated_to_infinitives[foreign] if foreign in conjugated_to_infinitives else foreign

def format_english(english, foreign):
	return f'{english_to_frequency(english.strip())} to {english}' if foreign in conjugated_to_infinitives else f'{english_to_frequency(english.strip())} {english}'

def foreign_to_english_card(emoji, part_of_speech, english, foreign):
	emoji_style = "font-size:5em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
	return f'''<br/>
	<div style="font-size:5em">{english}</div>
	<div style="font-size:small">{part_of_speech}</div>
	\t
	<div style="{emoji_style}">{emoji}</div>
	<div style="font-size:large">{foreign}</div><br/>'''.replace('\n','')

def english_to_foreign_card(emoji, part_of_speech, foreign, english):
	emoji_style = "font-size:5em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
	return f'''<br/>
	<div style="{emoji_style}">{emoji}</div>
	<div style="font-size:large">{foreign}</div>
	<div style="font-size:small">{part_of_speech}</div>
	\t
	<div style="font-size:5em">{english}</div>'''.replace('\n','')

vocabulary = csv_functions.tuples_from_csv(foreign_language['sequence'])
english_to_foreign_lookup = csv_functions.setdict_from_tuples(vocabulary, 
	['emoji','part-of-speech','foreign','frequency','english'], ['english','part-of-speech'],['foreign'])
foreign_to_english_lookup = csv_functions.setdict_from_tuples(vocabulary, 
	['emoji','part-of-speech','foreign','frequency','english'], ['foreign','part-of-speech'],['english'])

english_prompts = set()
foreign_prompts = set()
for i, (emoji, part_of_speech, foreign, frequency, english) in enumerate(vocabulary):
	if i > 1000:
		break
	# print(emoji, part_of_speech, foreign, english) 
	if english not in english_prompts:
		english_prompts.add(english)
		print(english_to_foreign_card(emoji, part_of_speech, english, '; '.join(english_to_foreign_lookup[(english, part_of_speech)])))
	if foreign not in foreign_prompts:
		foreign_prompts.add(foreign)
		print(foreign_to_english_card(emoji, part_of_speech, foreign, '; '.join(foreign_to_english_lookup[(foreign, part_of_speech)])))
