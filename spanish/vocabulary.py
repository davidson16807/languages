import csv_functions

def format_spanish(spanish):
	return conjugated_to_infinitives[spanish] if spanish in conjugated_to_infinitives else spanish

def format_english(english, spanish):
	return f'{english_to_frequency(english.strip())} to {english}' if spanish in conjugated_to_infinitives else f'{english_to_frequency(english.strip())} {english}'

def spanish_to_english_card(emoji, part_of_speech, english, spanish):
	emoji_style = "font-size:5em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
	return f'''<br/>
	<div style="font-size:5em">{english}</div>
	<div style="font-size:small">{part_of_speech}</div>
	\t
	<div style="{emoji_style}">{emoji}</div>
	<div style="font-size:large">{spanish}</div><br/>'''.replace('\n','')

def english_to_spanish_card(emoji, part_of_speech, spanish, english):
	emoji_style = "font-size:5em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
	return f'''<br/>
	<div style="{emoji_style}">{emoji}</div>
	<div style="font-size:large">{spanish}</div>
	<div style="font-size:small">{part_of_speech}</div>
	\t
	<div style="font-size:5em">{english}</div>'''.replace('\n','')

vocabulary = csv_functions.tuples_from_csv('vocabulary-sequence.tsv')
english_to_spanish_lookup = csv_functions.setdict_from_tuples(vocabulary, 
	['emoji','part-of-speech','spanish','frequency','english'], ['english','part-of-speech'],['spanish'])
spanish_to_english_lookup = csv_functions.setdict_from_tuples(vocabulary, 
	['emoji','part-of-speech','spanish','frequency','english'], ['spanish','part-of-speech'],['english'])

english_prompts = set()
spanish_prompts = set()
for i, (emoji, part_of_speech, spanish, frequency, english) in enumerate(vocabulary):
	if i > 1000:
		break
	# print(emoji, part_of_speech, spanish, english) 
	if english not in english_prompts:
		english_prompts.add(english)
		print(english_to_spanish_card(emoji, part_of_speech, english, '; '.join(english_to_spanish_lookup[(english, part_of_speech)])))
	if spanish not in spanish_prompts:
		spanish_prompts.add(spanish)
		print(spanish_to_english_card(emoji, part_of_speech, spanish, '; '.join(spanish_to_english_lookup[(spanish, part_of_speech)])))
