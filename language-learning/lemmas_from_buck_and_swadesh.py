import os
import re

'''
USAGE: python lemmas_from_buck_and_swadesh.py

Appends rows to data/inflection/**/{noun,verb,adjective}-lemmas.tsv
for concepts of the Swadesh and Buck lists that the lemma tables do not already have.

A concept is an english translation in lower-kebab-case, e.g. "you all" → "you-all".
Concepts are read from the lists whose english translations are standardized:
data/swadesh-tables/germanic-languages.tsv for Swadesh lists,
and data/buck-tables/indo-european/english.tsv for Buck lists,
and are matched by id to the lemmas of other lists.
Where a row has several english translations (delimited by commas or pipes),
each translation becomes a concept for the same lemma.
Where a row has several lemmas, only the first is used.
Where several sources give a lemma for the same concept, the first source listed below is used,
and lemmas that already exist in a table are never replaced.
Pronouns, demonstratives, and interrogatives are omitted,
since they are handled elsewhere in the tag system, as noun-forms.
'''

def rows(filename):
	with open(filename) as file:
		return [[cell.strip() for cell in line.rstrip('\n').split('\t')]
			for line in file.read().split('\n')
			if line.strip()]

def header_index(header, name):
	return [cell.strip().strip('#').strip() for cell in header].index(name)

def concepts(english):
	return [
		re.sub(r'\s+', '-', re.sub(r"['’]", '', translation.strip().lower()))
		for translation in re.split(r'[,|]', re.sub(r'\([^)]*\)', '', english))
		if translation.strip()
	]

def lemma(cell):
	'''
	Returns the first lemma of a cell, without the notes, gender markers,
	reconstruction markers, and IPA delimiters that accompany it, or None if there is none.
	'''
	cell = re.sub(r'[‎‏]', '', cell)
	cell = re.sub(r'\([^)]*\)', '', cell)
	cell = re.sub(r'[♂♀⚲"]', '', cell)
	first = next((alternative for alternative in re.split(r'[,|;~]| / ', cell) if alternative.strip()), '')
	first = re.sub(r'(\s+(m|f|n|rare))+$', '', first.strip())
	first = first.strip(' */')
	return first if re.search(r'\w', first) else None

class ConceptList:
	'''
	`ConceptList` stores the concepts and parts of speech of a list, by id,
	given the rows of a list whose english translations are standardized.
	'''
	def __init__(self, rows, id_column, english_column, part_of_speech_column):
		self.concepts_for_id = {row[id_column]: concepts(row[english_column]) for row in rows if len(row) > english_column}
		self.parts_of_speech_for_id = {row[id_column]: row[part_of_speech_column].split('|') for row in rows if len(row) > part_of_speech_column}
	def entries(self, rows, id_column, lemma_column, part_of_speech):
		'''
		Returns (concept, lemma) tuples of a given part of speech
		for the rows of another list that shares ids with this one.
		'''
		return [
			(concept, lemma(row[lemma_column]))
			for row in rows
			if len(row) > lemma_column
				and part_of_speech in self.parts_of_speech_for_id.get(row[id_column], [])
				and lemma(row[lemma_column])
			for concept in self.concepts_for_id[row[id_column]]
		]

def join_hyphens(lemma):
	'''
	Removes hyphens between letters, for lists that use hyphens to mark morpheme boundaries (sko-makare → skomakare),
	without writing a letter three times in a row (till-laga → tillaga).
	'''
	return re.sub(r'(\w)\1\1', r'\1\1', re.sub(r'(?<=\w)-(?=\w)', '', lemma))

def appended(existing_rows, entries):
	'''
	Returns the rows to append to a lemma table, given the rows it already has,
	such that each concept occurs only once.
	'''
	concepts = {row[0] for row in existing_rows}
	result = []
	for concept, lemma in entries:
		if concept not in concepts:
			concepts.add(concept)
			result.append((concept, lemma))
	return result

swadesh_concepts = rows('data/swadesh-tables/germanic-languages.tsv')
buck_concepts = rows('data/buck-tables/indo-european/english.tsv')
swadesh = ConceptList(swadesh_concepts, 0, 2, 1)
buck = ConceptList(buck_concepts[1:], 0, 1, 2)

swadesh_tables = {filename: rows(f'data/swadesh-tables/{filename}')
	for filename in 'germanic-languages.tsv romance-languages.tsv slavic-languages.tsv indo-european-branches.tsv'.split()}
buck_table = rows('data/buck-tables/indo-european/indo-european.tsv')

def formatted(entries, formatters):
	result = []
	for concept, lemma in entries:
		for formatter in formatters:
			lemma = formatter(lemma)
		result.append((concept, lemma))
	return result

def from_swadesh(filename, column_name, *formatters):
	table = swadesh_tables[filename]
	return lambda part_of_speech: formatted(swadesh.entries(table, 0, header_index(table[0], column_name), part_of_speech), formatters)

def from_buck(column_name, *formatters):
	return lambda part_of_speech: formatted(buck.entries(buck_table[1:], 0, header_index(buck_table[0], column_name), part_of_speech), formatters)

# concepts that are handled elsewhere in the tag system, as noun-forms
pronouns = 'i you he she it we you-all they'.split()
demonstratives = 'this that here there'.split()
interrogatives = 'who what which where when how why how-many how-much'.split()
omitted = {*pronouns, *demonstratives, *interrogatives}

def tables(directory, sources, parts_of_speech='noun verb adjective'.split()):
	return [(f'{directory}/{part_of_speech}-lemmas.tsv', part_of_speech, sources) for part_of_speech in parts_of_speech]

# sources of lemmas for each table, in order of precedence
# Latin verbs are omitted, since lemma tables use the first person singular for them (amō),
# while Swadesh and Buck lists use the infinitive (amāre).
# Russian lemmas are only drawn from Swadesh lists, since Buck lists transliterate them.
# Buck lists for Middle English and Swedish mark morpheme boundaries with hyphens, which are removed.
D = 'data/inflection/indo-european'
sources_for_tables = [
	*tables(f'{D}/germanic/english/old',        [from_swadesh('germanic-languages.tsv', 'Old English'), from_buck('Old English')]),
	*tables(f'{D}/germanic/english/middle',     [from_buck('Middle English', join_hyphens)]),
	*tables(f'{D}/germanic/swedish/modern',     [from_swadesh('germanic-languages.tsv', 'Swedish'), from_buck('Swedish', join_hyphens)]),
	*tables(f'{D}/romance/latin/classic',       [from_swadesh('romance-languages.tsv', 'Latin'), from_buck('Latin')], ['noun', 'adjective']),
	*tables(f'{D}/romance/spanish/modern',      [from_swadesh('romance-languages.tsv', 'Spanish'), from_buck('Spanish')]),
	*tables(f'{D}/romance/portugese/modern',    [from_swadesh('romance-languages.tsv', 'Portuguese'), from_buck('Portuguese')]),
	*tables(f'{D}/romance/italian/modern',      [from_swadesh('romance-languages.tsv', 'Italian'), from_buck('Italian')]),
	*tables(f'{D}/romance/french/modern',       [from_swadesh('romance-languages.tsv', 'French'), from_buck('French')]),
	(f'{D}/romance/french/modern/noun-ipa-lemmas.tsv', 'noun', [from_swadesh('romance-languages.tsv', 'French IPA')]),
	*tables(f'{D}/romance/romanian/modern',     [from_swadesh('romance-languages.tsv', 'Romanian')]),
	*tables(f'{D}/slavic/russian',              [from_swadesh('slavic-languages.tsv', 'Russian')]),
	*tables(f'{D}/proto-indo-european/sihler',  [from_swadesh('indo-european-branches.tsv', 'Proto-Indo-European'), from_buck('Proto Indo European')]),
]

for filepath, part_of_speech, sources in sources_for_tables:
	if os.path.exists(filepath):
		with open(filepath) as file:
			text = file.read()
		new = appended(rows(filepath), [(concept, lemma)
			for source in sources
			for concept, lemma in source(part_of_speech)
			if concept not in omitted])
		with open(filepath, 'a') as file:
			if text and not text.endswith('\n'):
				file.write('\n')
			file.write(''.join(f'{concept}\t{lemma}\n' for concept, lemma in new))
		print(f'{len(new):5} appended to {filepath}')
