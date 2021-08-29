# built in
import re
import itertools
import collections

# 3rd party
import inflection

def csv_dict(filename, columns, keys):
	result = {}
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				cells = [column.strip() for column in line.split('\t') ]
				row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
				value = {column:row[column] for column in row if column not in keys}
				result[tuple(row[key] for key in keys)] = value if len(value) > 1 else list(value.values())[0]
	return result

def dict_function(dict_, sentinel=''):
	def result(*keys):
		keys_tuple = tuple(keys)
		return dict_[keys_tuple] if keys_tuple in dict_ else sentinel
	return result

def curried_dict_function(dict_, sentinel=''):
	def result(*keys):
		keys_tuple = tuple(keys)
		result = lambda attribute: dict_[keys_tuple][attribute]
		fallback = lambda attribute: sentinel
		return (result if keys_tuple in dict_ else fallback)
	return result


en_declension_templates_lookup = csv_dict('../english/declensions-template.tsv',  
	 ['plurality', 'case', 'template'], 
	 ['plurality', 'case'])
en_declension_templates = dict_function(en_declension_templates_lookup, sentinel=None)


ie_declension_templates_lookup = csv_dict('declensions-template.tsv',  
	 ['plurality', 'case', 'template'], 
	 ['plurality', 'case'])
ie_declension_templates = dict_function(ie_declension_templates_lookup, sentinel=None)


ie_declension_demo_lookup = csv_dict('declensions-source.tsv',  
	 ['case','singular','dual','plural','collective','emoji','emoji-property','noun','preposition','gender','stem','class'],
	 ['noun','case'])
ie_declension_demo = curried_dict_function(ie_declension_demo_lookup)


emoji_declension_templates_lookup = csv_dict('../emoji/declensions-source.tsv',  
	 ['case', 'template'], 
	 ['case'])
emoji_declension_templates = dict_function(emoji_declension_templates_lookup)

plurality_representative = {'singular': 1, 'dual': 2, 'plural': 3}
combinations = itertools.product(
	list(dict.fromkeys([noun for noun,case in ie_declension_demo_lookup])),
	['singular', 'dual', 'plural'],
	list(dict.fromkeys([case for noun,case in ie_declension_demo_lookup])),
)
for noun, plurality, case in combinations:
	subject_count = plurality_representative[plurality]
	en = en_declension_templates(plurality, case)
	ie = ie_declension_templates(plurality, case)
	if not en or not ie: continue
	if (noun, case) not in ie_declension_demo_lookup: continue
	ie_declension_row = ie_declension_demo(noun, case)

	replacements = [
		('{{declined}}', noun if subject_count < 2 else inflection.pluralize(noun)),
		('{{preposition}}', ie_declension_row('preposition')),
		('{{direct}}', 'direct' if subject_count > 1 else 'directs'),
	]
	for replaced, replacement in replacements:
		en = en.replace(replaced, replacement)

	replacements = [
		('declined', f'c1::{ie_declension_row(plurality)}'),
		('{{nominative}}', ie_declension_demo(noun, 'nominative')(plurality)),
		('mₒ', 'm̥'),
		('nₒ', 'n̥'),
		('rₒ', 'r̥'),
		('lₒ', 'l̥'),
	]
	for replaced, replacement in replacements:
		ie = ie.replace(replaced, replacement)

	emoji = emoji_declension_templates(case)
	emoji_noun = ie_declension_row('emoji')
	replacements = [
		('{{declined}}', subject_count*emoji_noun),
		('{{property}}', ie_declension_row('emoji-property')),
	]
	for replaced, replacement in replacements:
		emoji = emoji.replace(replaced, replacement)

	if '{{c1::}}' not in ie:
		emoji_style = "font-size:7em; font-family: 'DejaVu Sans', 'sans-serif', Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
		print(f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>')
