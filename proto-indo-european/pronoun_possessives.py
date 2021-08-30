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
				cells = [column.strip(' \t\r\n*?') for column in line.split('\t') ]
				row = {columns[i]:cells[i] for i, cell in enumerate(cells) if i < len(columns)}
				value = {column:row[column] for column in row if column not in keys}
				result[tuple(row[key] for key in keys)] = value if len(value) > 1 else list(value.values())[0]
	return result

def dict_function(dict_, sentinel=lambda *x: ''):
	def result(*keys):
		keys_tuple = tuple(keys)
		return dict_[keys_tuple] if keys_tuple in dict_ else sentinel(*keys)
	return result

def curried_dict_function(dict_, sentinel=lambda attribute: ''):
	def result(*keys):
		keys_tuple = tuple(keys)
		result = lambda attribute: dict_[keys_tuple][attribute]
		return (result if keys_tuple in dict_ else sentinel)
	return result


def batch_replace(string, replacements):
	result = string
	for replaced, replacement in replacements:
		result = result.replace(replaced, replacement) 
	return result


emoji_possessives_templates_lookup = csv_dict('../emoji/pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
emoji_possessives_templates = dict_function(emoji_possessives_templates_lookup)


en_possessives_templates_lookup = csv_dict('../english/pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
en_possessives_templates = dict_function(en_possessives_templates_lookup, sentinel=lambda *x:None)


ie_possessives_templates_lookup = csv_dict('pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
ie_possessives_templates = dict_function(ie_possessives_templates_lookup, sentinel=lambda *x:None)





emoji_reflexives_templates_lookup = csv_dict('../emoji/pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
emoji_reflexives_templates = dict_function(emoji_reflexives_templates_lookup)


en_reflexives_templates_lookup = csv_dict('../english/pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
en_reflexives_templates = dict_function(en_reflexives_templates_lookup, sentinel=lambda *x:None)


ie_reflexives_templates_lookup = csv_dict('pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
ie_reflexives_templates = dict_function(ie_reflexives_templates_lookup, sentinel=lambda *x:None)






emoji_possessives_lookup = csv_dict('../emoji/pronoun-declensions-source.tsv',  
	 ['person','gender','plurality','emoji'],
	 ['person','gender','plurality'])
emoji_possessives = dict_function(emoji_possessives_lookup)


en_possessives_lookup = csv_dict('../english/pronoun-possessives-source.tsv',  
	 ['possessor-person', 'possessor-gender', 'possessor-plurality', 'en-possessive', 'en-audience-address'],
	 ['possessor-person', 'possessor-gender', 'possessor-plurality'])
en_possessives = curried_dict_function(en_possessives_lookup)


ie_possessives_lookup = csv_dict('pronoun-possessives-source.tsv',  
	 ['possessor-person', 'possessor-gender', 'possessor-plurality', 'possessed-gender', 'possessed-case', 'singular', 'dual', 'plural'],
	 ['possessor-person', 'possessor-gender', 'possessor-plurality', 'possessed-gender', 'possessed-case'])
ie_possessives = curried_dict_function(ie_possessives_lookup)






emoji_style = "font-size:7em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
plurality_representative = {'singular': 1, 'dual': 2, 'plural': 3}
combinations = itertools.product(
	list(dict.fromkeys([case for person, gender1, plurality, gender2, case in ie_possessives_lookup])), #possessed case
	['singular', 'dual', 'plural'],      # possessor plurality
	['1', '2', '3'],                     # possessor person
	['neuter', 'masculine', 'feminine'], # possessor gender
	['neuter', 'masculine', 'feminine'], # possessed gender
	['singular', 'dual', 'plural'],      # possessed plurality
)
for possessed_case, possessor_plurality, possessor_person, possessor_gender, possessed_gender, possessed_plurality in combinations:
	possessor_representative_count = plurality_representative[possessor_plurality]
	possessed_representative_count = plurality_representative[possessed_plurality]
	en = en_possessives_templates(possessed_case, possessed_gender, possessed_plurality)
	ie = ie_possessives_templates(possessed_case, possessed_gender, possessed_plurality)
	emoji = emoji_possessives_templates(possessed_case, possessed_gender, possessed_plurality)
	if not en or not ie: continue

	en_possessive_row = en_possessives(possessor_person, possessor_gender, possessor_plurality)
	en = batch_replace(en, [
		('{{possessive}}', en_possessive_row('en-possessive')),
		('{{audience-address}}', en_possessive_row('en-audience-address')),
	])

	ie_possessive_row = ie_possessives(possessor_person, possessor_gender, possessor_plurality, possessed_gender, possessed_case)
	# print(possessor_person, possessor_gender, possessor_plurality, possessed_gender, possessed_case, ie_possessive_row(possessed_plurality))
	ie = batch_replace(ie, [
		('possessive', f'c1::{ie_possessive_row(possessed_plurality)}'),
	])

	emoji = batch_replace(emoji, [
		('{{possessive}}', emoji_possessives(possessor_person, possessor_gender, possessor_plurality)),
	])

	if '{{c1::}}' not in ie:
		print(f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>')







reflexives = itertools.product(
	list(dict.fromkeys([case for person, gender1, plurality, gender2, case in ie_possessives_lookup])), #possessed case
	['singular'],  # possessor plurality
	['masculine'], # possessor gender
	['neuter', 'masculine', 'feminine'], # possessed gender
	['singular', 'dual', 'plural'],      # possessed plurality
)
for possessed_case, possessor_plurality, possessor_gender, possessed_gender, possessed_plurality in reflexives:
	possessor_representative_count = plurality_representative[possessor_plurality]
	possessed_representative_count = plurality_representative[possessed_plurality]
	en = en_reflexives_templates(possessed_case, possessed_gender, possessed_plurality)
	ie = ie_reflexives_templates(possessed_case, possessed_gender, possessed_plurality)
	emoji = emoji_reflexives_templates(possessed_case, possessed_gender, possessed_plurality)
	if not en or not ie: continue

	en_possessive_row = en_possessives('3', possessed_gender, possessed_plurality)
	en = batch_replace(en, [
		('{{possessive}}', en_possessive_row('en-possessive')),
		('{{audience-address}}', en_possessive_row('en-audience-address')),
	])

	ie_possessive_row = ie_possessives('reflexive', 'neuter', possessor_plurality, possessed_gender, possessed_case)
	# print(possessor_person, possessor_gender, possessor_plurality, possessed_gender, possessed_case, ie_possessive_row(possessed_plurality))
	ie = batch_replace(ie, [
		('possessive', f'c1::{ie_possessive_row(possessed_plurality)}'),
		('mₒ', 'm̥'),
		('nₒ', 'n̥'),
		('rₒ', 'r̥'),
		('lₒ', 'l̥'),
		('(', ''),
		(')', ''),
	])

	emoji = batch_replace(emoji, [
		('{{possessive}}', emoji_possessives('3', possessor_gender, possessor_plurality)),
	])

	if '{{c1::}}' not in ie:
		print(f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>')
