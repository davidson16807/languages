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

def dict_function(dict_, sentinel=lambda x: ''):
	def result(*keys):
		keys_tuple = tuple(keys)
		return dict_[keys_tuple] if keys_tuple in dict_ else sentinel(*keys)
	return result

def curried_dict_function(dict_, sentinel=''):
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


en_declension_templates_lookup = csv_dict('../english/pronoun-declensions-template.tsv',  
	 ['case', 'template'], 
	 ['case'])
en_declension_templates = dict_function(en_declension_templates_lookup, sentinel=lambda *x:None)


emoji_declension_templates_lookup = csv_dict('../emoji/pronoun-declensions-template.tsv',  
	 ['case', 'template'], 
	 ['case'])
emoji_declension_templates = dict_function(emoji_declension_templates_lookup)


ie_declension_templates_lookup = csv_dict('pronoun-declensions-template.tsv',  
	 ['case', 'template'], 
	 ['case'])
ie_declension_templates = dict_function(ie_declension_templates_lookup, sentinel=lambda *x:None)


en_declension_lookup = csv_dict('../english/pronoun-declensions-source.tsv',  
	 ['case','person','gender','plurality','en'],
	 ['case','person','gender','plurality'])
en_declension = dict_function(en_declension_lookup)


emoji_declension_lookup = csv_dict('../emoji/pronoun-declensions-source.tsv',  
	 ['person','gender','plurality','emoji'], 
	 ['person','gender','plurality'])
emoji_declension = dict_function(emoji_declension_lookup)


ie_declension_lookup = csv_dict('pronoun-declensions-source.tsv',  
	 ['case','person','gender','plurality','clitic','pie'],
	 ['case','person','gender','plurality','clitic'])
ie_declension_fallback = dict_function(ie_declension_lookup, sentinel=lambda *x:None)
ie_declension = dict_function(ie_declension_lookup, 
	sentinel=lambda case,person,gender,plurality,clitic: ie_declension_fallback(case,person,gender,plurality,''))

plurality_representative = {'singular': 1, 'dual': 2, 'plural': 3}
combinations = itertools.product(
	['singular', 'dual', 'plural'],
	['1', '2', '3'],
	['neuter', 'masculine', 'feminine'],
	list(dict.fromkeys([case for case, person, gender, plurality, clitic in ie_declension_lookup])),
)
for plurality, person, gender, case in combinations:
	representative_count = plurality_representative[plurality]
	en = en_declension_templates(case)
	ie = ie_declension_templates(case)
	emoji = emoji_declension_templates(case)
	if not en or not ie: continue
	if not ie_declension(case, person, gender, plurality, "enclitic"): continue
	if not ie_declension('nominative', person, gender, plurality, ""): continue

	en = batch_replace(en, [
		('{{declined}}', en_declension(case, person, gender, plurality)),
		('{{direct}}', 'direct' if representative_count > 1 or person!='3' else 'directs'),
		('{{nominative}}', en_declension('nominative', person, gender, plurality)),
	])

	ie = batch_replace(ie, [
		('declined', f'c1::{ie_declension(case, person, gender, plurality, "enclitic")}'),
		('{{direct}}', {1:'déwkti',2:'duktés',3:'dukénti'}[representative_count]),
		('{{nominative}}', ie_declension('nominative', person, gender, plurality, "")),
		('mₒ', 'm̥'),
		('nₒ', 'n̥'),
		('rₒ', 'r̥'),
		('lₒ', 'l̥'),
		('(', ''),
		(')', ''),
	])

	emoji = batch_replace(emoji, [
		('{{declined}}', emoji_declension(person, gender, plurality)),
	])

	if '{{c1::}}' not in ie:
		emoji_style = "font-size:7em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
		print(f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>')
