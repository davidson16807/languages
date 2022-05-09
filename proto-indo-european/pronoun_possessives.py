# built in
import re
import itertools
import collections

# 3rd party
import inflection

# in-house
from csv_functions import csv_dict, dict_function, curried_dict_function
from card import batch_replace, card


emoji_possessives_templates_lookup = csv_dict('../emoji/pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
emoji_possessives_templates = dict_function(emoji_possessives_templates_lookup)


en_possessives_templates_lookup = csv_dict('../english/pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
en_possessives_templates = dict_function(en_possessives_templates_lookup, sentinel=None)


ie_possessives_templates_lookup = csv_dict('pronoun-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
ie_possessives_templates = dict_function(ie_possessives_templates_lookup, sentinel=None)





emoji_reflexives_templates_lookup = csv_dict('../emoji/pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
emoji_reflexives_templates = dict_function(emoji_reflexives_templates_lookup)


en_reflexives_templates_lookup = csv_dict('../english/pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
en_reflexives_templates = dict_function(en_reflexives_templates_lookup, sentinel=None)


ie_reflexives_templates_lookup = csv_dict('pronoun-reflexive-possessives-template.tsv',  
	 ['possessed-case', 'possessed-gender', 'possessed-plurality', 'template'], 
	 ['possessed-case', 'possessed-gender', 'possessed-plurality'])
ie_reflexives_templates = dict_function(ie_reflexives_templates_lookup, sentinel=None)






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






emoji_style = "font-size:5em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
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
