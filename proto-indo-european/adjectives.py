# built in
import re
import itertools
import collections

# 3rd party
import inflection

# in-house
from csv_functions import csv_dict, dict_function, curried_dict_function
from card import batch_replace, card


en_declension_templates_lookup = csv_dict('../english/declensions-template.tsv',  
	 ['plurality', 'case', 'template'], 
	 ['plurality', 'case'])
en_declension_templates = dict_function(en_declension_templates_lookup, sentinel=None)


ie_declension_templates_lookup = csv_dict('declensions-template.tsv',  
	 ['plurality', 'case', 'template'], 
	 ['plurality', 'case'])
ie_declension_templates = dict_function(ie_declension_templates_lookup, sentinel=None)


emoji_declension_templates_lookup = csv_dict('../emoji/declensions-source.tsv',  
	 ['case', 'template'], 
	 ['case'])
emoji_declension_templates = dict_function(emoji_declension_templates_lookup)


ie_adjective_lookup = csv_dict('adjectives-source.tsv',  
	 ['case','gender','singular','dual','plural','en','emoji','emoji-property','type'],
	 ['type','case','gender'])
ie_adjective = curried_dict_function(ie_adjective_lookup)


ie_noun_lookup = csv_dict('adjectives-noun-source.tsv',  
	 ['case','gender','singular','dual','plural','en'],
	 ['case','gender'])
ie_noun = curried_dict_function(ie_noun_lookup)



plurality_representative = {'singular': 1, 'dual': 2, 'plural': 3}
combinations = itertools.product(
	list(dict.fromkeys([type_ for type_, case, gender in ie_adjective_lookup])),
	list(dict.fromkeys([case for type_, case, gender in ie_adjective_lookup])),
	['singular', 'dual', 'plural'],
	['masculine', 'feminine', 'neuter'],
)
for type_, case, plurality, gender in combinations:
	subject_count = plurality_representative[plurality]
	en = en_declension_templates(plurality, case)
	ie = ie_declension_templates(plurality, case)
	if not en or not ie: continue
	if (type_, case, gender) not in ie_adjective_lookup: continue
	ie_adjective_row = ie_adjective(type_, case, gender)
	en_noun = ie_noun(case, gender)('en')

	replacements = [
		('{{declined}}', f'{ie_adjective_row("en")} {en_noun if subject_count < 2 else inflection.pluralize(en_noun)}'),
		('{{preposition}}', 'near'),
		('{{direct}}', 'direct' if subject_count > 1 else 'directs'),
	]
	for replaced, replacement in replacements:
		en = en.replace(replaced, replacement)
	replacements = [
		('{{declined}}', '{{c1::'+ie_adjective_row(plurality)+'}} '+ie_noun(case, gender)(plurality)),
		('{{nominative}}', ie_noun('nominative', gender)(plurality)),
		('mₒ', 'm̥'),
		('nₒ', 'n̥'),
		('rₒ', 'r̥'),
		('lₒ', 'l̥'),
		('(', ''),
		(')', ''),
	]
	for replaced, replacement in replacements:
		ie = ie.replace(replaced, replacement)

	emoji = emoji_declension_templates(case)
	emoji_noun = ie_adjective_row('emoji')
	replacements = [
		('{{declined}}', subject_count*emoji_noun),
		('{{property}}', ie_adjective_row('emoji-property')),
	]
	for replaced, replacement in replacements:
		emoji = emoji.replace(replaced, replacement)

	if '{{c1::}}' not in ie:
		print(card(emoji,en,ie))
