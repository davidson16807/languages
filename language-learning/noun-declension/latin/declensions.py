import re
import inflection

def split(elements, trigger):
	result = [[]]
	for element in elements:
		if trigger(element):
			result.append([])
		else:
			result[-1].append(element)
	return result

def whitespace(text):
	return len(text.strip()) < 1

def pairwise(elements):
	last = elements[0]
	for current in elements[1:]:
		yield last, current
		last = current

with open('declensions-template.tsv') as file:
	template = file.read() 

with open('declensions-source.tsv') as file:
	table = [
		[ column.strip() for column in line.split('\t') ] 
		for line in file.readlines() 
		if not line.strip().startswith('#') and len(line.strip()) > 0
	]
	declensions = {}
	for row in table:
		case,singular,plural,translation,declension,gender,ending,etymology = row
		if translation in declensions:
			declensions[translation].append(row)
		else:
			declensions[translation] = [row]

replacements = [
	('singular',translation),
	('plural',inflection.pluralize(translation)),
]

prepositions = {
	'man': 'by',
	'night': 'in',
	'war': 'in',
	'air': 'in',
	'animal': 'by',
	'tower': 'in',
}

for word in declensions:
	notes = template
	notes = notes.replace('{{singular}}',word)
	notes = notes.replace('{{plural}}',inflection.pluralize(word))
	notes = notes.replace('{{preposition}}',
		prepositions[word] if word in prepositions else 'around')
	for declension in declensions[word]:
		case,singular,plural,translation,declension,gender,ending,etymology = declension
		notes = notes.replace('{{case-singular}}'.replace('case', case),singular)
		notes = notes.replace('{{case-plural}}'.replace('case', case),plural)
	compacted = ['\t'.join(column.strip() for column in note.split('\t')) for note in notes.split('\n')] 
	for line in compacted:
		if '{{' not in line: print(line)

