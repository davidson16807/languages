# built in
import re
import inflection
import itertools
import collections

# in-house
from csv_functions import csv_dict, dict_function, curried_dict_function
from card import batch_replace, card


en_conjugation_templates_lookup = csv_dict('../english/conjugations-template.tsv',  
	 ['mood', 'voice', 'tense', 'template'], 
	 ['mood', 'voice', 'tense'])
en_conjugation_templates = dict_function(en_conjugation_templates_lookup, sentinel=None)


en_pronoun_declension_lookup = csv_dict('../english/pronoun-declensions-source.tsv',  
	 ['case', 'person', 'gender', 'plurality', 'declension'], 
	 ['case', 'person', 'gender', 'plurality'])
en_pronoun_declension = dict_function(en_pronoun_declension_lookup)


ie_conjugation_templates_lookup = csv_dict('conjugations-template.tsv',  
	 ['mood', 'tense', 'template'], 
	 ['mood', 'tense'])
ie_conjugation_templates = dict_function(ie_conjugation_templates_lookup, sentinel=None)


ie_conjugation_demo_lookup = csv_dict('conjugations-source.tsv',  
	 ['voice','person','plurality',
	  'ie-present-indicative','ie-past-indicative','ie-imperative','ie-subjunctive','ie-optative','ie-participle',
	  'en-infinitive','en-present','en-past','en-participle','en-object','ie-object', 'emoji-template'],
	 ['voice','person','plurality','en-infinitive'])
ie_conjugation_demo = curried_dict_function(ie_conjugation_demo_lookup)


ie_decline_pronoun_lookup = csv_dict('pronoun-declensions-source.tsv',  
	 ['case', 'person', 'gender', 'plurality', 'clitic', 'declension'], 
	 ['case', 'person', 'gender', 'plurality', 'clitic'])
def ie_decline_pronoun(case, person, gender, plurality, clitic):
	clitic_key = (case, person, gender, plurality, clitic)
	default_key = (case, person, gender, plurality, '')
	return (
		ie_decline_pronoun_lookup[clitic_key] if clitic_key in ie_decline_pronoun_lookup else 
		ie_decline_pronoun_lookup[default_key] if default_key in ie_decline_pronoun_lookup else 
		'')


emoji_decline_pronoun_lookup = csv_dict('../emoji/pronoun-declensions-source.tsv',  
	 ['person', 'gender', 'plurality', 'declension'],
	 ['person', 'gender', 'plurality'])
emoji_decline_pronoun = dict_function(emoji_decline_pronoun_lookup, sentinel='')


plurality_representative = {'singular': 1, 'dual': 2, 'plural': 3}
verbs = list(dict.fromkeys([verb for voice, person, plurality, verb in ie_conjugation_demo_lookup]))
combinations = itertools.product(
	verbs,
	['active', 'middle'], 
	['indicative', 'imperative', 'subjunctive', 'optative', 'nonfinite'],
	['present', 'perfect', 'participle'],
	['1','2','3'],
	['singular', 'plural', 'dual'],
)
for verb, voice, mood, tense, person, plurality in combinations:
	subject_count = plurality_representative[plurality]
	genders = (['masculine', 'feminine', 'neuter'] 
		if person == '3' and subject_count == 1 else ['neuter'])
	for gender in genders:
		en = en_conjugation_templates(mood,voice,tense)
		ie = ie_conjugation_templates(mood,tense)
		if not en or not ie: continue
		if (voice, person, plurality, verb) not in ie_conjugation_demo_lookup: continue
		target_voice_row = ie_conjugation_demo(voice, person, plurality, verb)
		middle_voice_row = ie_conjugation_demo('middle', person, plurality, verb)


		replacements = [
			('{{subject}}', en_pronoun_declension_lookup[('nominative', person, gender, plurality)]),
			('{{object}}', target_voice_row('en-object')),
			('{{is}}', 'are' if subject_count > 1 or person == '2' else 'am' if person == '1' else 'is'),
			('{{was}}', 'were' if subject_count > 1 or person == '2' else 'was'),
			('{{imperfect}}', target_voice_row('en-participle')),
			('{{infinitive}}', verb),
			('{{present}}', target_voice_row('en-present')),
			('{{perfect}}',target_voice_row('en-past')),
			('{{middle-imperfect}}', middle_voice_row('en-participle')),
			('{{middle-infinitive}}', verb),
			('{{middle-perfect}}', middle_voice_row('en-past')),
			('{{middle-present}}', middle_voice_row('en-present')),
		]
		for replaced, replacement in replacements:
			en = en.replace(replaced, replacement)

		replacements = [
			('{{subject}}', ie_decline_pronoun('nominative', person, gender, plurality, 'enclitic')),
			('{{object}}', target_voice_row('ie-object')),
			('imperative', f'c1::{target_voice_row("ie-imperative")}'),
			('optative', f'c1::{target_voice_row("ie-optative")}'),
			('participle', f'c1::{target_voice_row("ie-participle")}'),
			('past-indicative', f'c1::{target_voice_row("ie-past-indicative")}'),
			('present-indicative', f'c1::{target_voice_row("ie-present-indicative")}'),
			('subjunctive', f'c1::{target_voice_row("ie-subjunctive")}'),
			('mₒ', 'm̥'),
			('nₒ', 'n̥'),
			('rₒ', 'r̥'),
			('lₒ', 'l̥'),
			('(', ''),
			(')', ''),
		]
		for replaced, replacement in replacements:
			ie = ie.replace(replaced, replacement)

		emoji = target_voice_row('emoji-template')
		emoji = emoji.replace('{{subject}}', emoji_decline_pronoun(person, gender, plurality))

		if '{{c1::}}' not in ie:
			emoji_style = "font-size:3em; font-family: 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji', 'sans-serif'"
			print(f'<div style="{emoji_style}">{emoji}</div><div style="font-size:small">{en}</div><div style="font-size:large">{ie}</div>')
