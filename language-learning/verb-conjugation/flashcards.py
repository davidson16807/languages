import re
import copy
import collections
import itertools

category_to_grammemes = {
	# needed to tip off which key/lookup should be used to stored cell contents
	'lookup':     ['finite', 'infinitive', 
	               'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
	               'context', 'group', 'emoji'],

	# needed for context in a sentence
	'language':   ['english', 'translated'], 

	# needed for infinitives
	'completion': ['full', 'bare'],

	# needed for finite forms
	'person':     ['1','2','3'],
	'plurality':  ['singular', 'dual', 'plural'],
	'inclusivity':['inclusive', 'exclusive', 'voseo', 'formal'],
	'modifier':   ['familiar', 
	               'formal', 'voseo' # needed for Spanish
	              ],
	'mood':       ['indicative', 'subjunctive', 'conditional', 
	               'optative', 'benedictive', 'jussive', 'potential', 
	               'imperative', 'prohibitive', 'desiderative', 
	               'dubitative', 'hypothetical', 'presumptive', 'permissive', 
	               'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
	               'precative', 'volitive', 'involutive', 'inferential', 
	               'necessitative', 'interrogative', 'injunctive', 
	               'suggestive', 'comissive', 'deliberative', 
	               'propositive', 'dynamic', 
	               'conditional I', 'conditional II', # needed for German
	              ],

	# needed for Sanskrit
	'stem':       ['primary', 'causative', 'intensive',],

	# needed for gerunds, supines, participles, and gerundives
	'gender':     ['masculine', 'feminine', 'neuter'],
	'declension': ['nominative', 'accusative', 'dative', 'ablative', 
	               'genitive', 'locative', 'instrumental'],

    # needed for infinitive forms, finite forms, participles, context in sentences, and graphic depictions
	'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
	'tense':      ['present', 'past', 'future',], 
	'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes.items() 
    for instance in instances
}

class SeparatedValuesFileParsing:
	def __init__(self, comment=None, delimeter='\t', padding=' \t\r\n'):
		self.comment = comment
		self.delimeter = delimeter
		self.padding = padding
	def rows(self, filename):
		rows_ = []
		with open(filename) as file:
			for line in file.readlines():
				if self.comment is not None and line.startswith(self.comment):
					continue
				elif len(line.strip()) < 1:
					continue
				rows_.append([column.strip(self.padding) for column in line.split(self.delimeter)])
		return rows_

class TableAnnotation:
	'''
	`TableAnnotation` instances represent a system for storing tabular data 
	that comes up naturally in things like conjugation or declension tables.

	A table has a given number of header rows and header columns.
	When a predifined keyword occurs within the cell contents of a header row or column, 
	 the row or column associated with that header is marked as having that keyword 
	 for an associated attribute.
	Keywords are indicated by keys within `content_to_attribute`.
	Keywords that are not known at the time of execution may be 
	 indicated using `header_column_id_to_attribute`, 
	 which marks all cell contents of a given column as keywords for a given attribute.

	As an example, if a header row is marked "green", and "green" is a type of "color",
	 then `content_to_attribute` may store "green":"color" as a key:value pair.
	Anytime "green" is listed in a header row or column, 
	 all contents of the row or column associated with that header cell 
	 will be marked as having the color "green".

	`TableAnnotation` converts tables that are written in this manner between 
	two reprepresentations: 
	The first representation is a list of rows, where rows are lists of cell contents.
	The second representation is a list where each element is a tuple,
	 (cell, annotations), where "cell" is the contents of a cell within the table,
	 and "annotations" is a dict of attribute:keyword associated with a cell.
	'''
	def __init__(self, 
			content_to_attribute, header_row_id_to_attribute, header_column_id_to_attribute):
		self.content_to_attribute = content_to_attribute
		self.header_column_id_to_attribute = header_column_id_to_attribute
		self.header_row_id_to_attribute = header_row_id_to_attribute
	def annotate(self, rows, header_row_count=None, header_column_count=None):
		header_row_count = header_row_count if header_row_count is not None else len(self.header_row_id_to_attribute)
		header_column_count = header_column_count if header_column_count is not None else len(self.header_column_id_to_attribute)
		column_count = max([len(row) for row in rows])
		column_base_attributes = [{} for i in range(column_count)]
		header_rows = rows[:header_row_count]
		nonheader_rows = rows[header_row_count:]
		for i, row in enumerate(header_rows):
			for j, cell in enumerate(row):
				if i in self.header_row_id_to_attribute:
					column_base_attributes[j][self.header_row_id_to_attribute[i]] = cell
				if cell in self.content_to_attribute:
					column_base_attributes[j][self.content_to_attribute[cell]] = cell
		annotations = []
		for row in nonheader_rows:
			header_cells = row[:header_column_count]
			nonheader_cells = row[header_column_count:]
			row_base_attributes = {}
			for i in range(0,header_column_count):
				cell = row[i]
				if i in self.header_column_id_to_attribute:
					row_base_attributes[self.header_column_id_to_attribute[i]] = cell
				if cell in self.content_to_attribute:
					row_base_attributes[self.content_to_attribute[cell]] = cell
			for i in range(header_column_count,len(row)):
				cell = row[i]
				if cell and column_base_attributes[i]:
					annotation = {}
					annotation.update(row_base_attributes)
					annotation.update(column_base_attributes[i])
					annotations.append((cell, annotation))
		return annotations

class TableIndexing:
	'''
	`TableIndexing` converts a list of (cell, annotation) tuples
	(such as those output by `TableAnnotation`)
	to a representation where cells are stored in nested lookups.
	The cells are indexed by their annotations according to the indexing behavior 
	within a given `template_lookups`.
	'''
	def __init__(self, template_lookups):
		self.template_lookups = template_lookups
	def index(self, annotations):
		lookups = copy.deepcopy(self.template_lookups)
		for cell, annotation in annotations:
			lookups[annotation][annotation] = cell
		return lookups

class DictKeyHashing:
	def __init__(self, key, default=None):
		self.key = key
		self.default = default
	def encode(self, dict_):
		'''
		Converts an arbitrary dict object to a tuple 
		whose values are the values of the dict ordered by a given list of keys
		'''
		if isinstance(dict_, dict):
			return dict_[self.key] if self.key in dict_ else self.default
		elif isinstance(dict_, str):
			return dict_
	def decode(self, value):
		return {self.key:value}
	def iterate(self, keys_to_values):
		'''
		Returns a generator that iterates through 
		possible tuples whose keys are given by `keys_and_defaults`
		and whose values are given by a `keys_to_values` dict 
		that maps keys in `keys_and_defaults` to sets of possible values.
		'''
		return itertools.chain(
				[default] if default not in keys_to_values[self.key] else [], 
				keys_to_values[key])

class DictTupleHashing:
	def __init__(self, keys_and_defaults=None, keys=None):
		self.keys_and_defaults = (
			[(key,'') for key in keys] if keys_and_defaults is None 
			 else keys_and_defaults)
	def encode(self, dict_):
		'''
		Converts an arbitrary dict object to a tuple 
		whose values are the values of the dict ordered by a given list of keys
		'''
		return tuple([
			(dict_[key] if key in dict_ else default)
			for key, default in self.keys_and_defaults
		])
	def decode(self, values):
		return {key:values[i] for i, (key, default) in enumerate(self.keys_and_defaults)}
	def iterate(self, keys_to_values):
		'''
		Returns a generator that iterates through 
		possible tuples whose keys are given by `keys_and_defaults`
		and whose values are given by a `keys_to_values` dict 
		that maps keys in `keys_and_defaults` to sets of possible values.
		'''
		return itertools.product(
			*[itertools.chain(
				[default] if default not in keys_to_values[key] else [], 
				keys_to_values[key])
			  for key, default in self.keys_and_defaults])
'''
options:
* iterate through hashes and populate wildcard substitutions after lookup is constructed
* iterate through wildcard substitutions upon call to lookup's __setitem__()
* iterate through wildcard substitutions upon call to lookup's __getitem__()
'''

class DictLookup:
	def __init__(self, hashing, content=None):
		self.hashing = hashing
		self.content = {} if content is None else content
	def __getitem__(self, key):
		return self.content[self.hashing.encode(key)]
	def __setitem__(self, key, value):
		self.content[self.hashing.encode(key)] = value
	def __contains__(self, key):
		return self.hashing.encode(key) in self.content
	def __iter__(self):
		return self.content.__iter__()
	def __len__(self):
		return self.content.__len__()
	def values():
		return self.content.values()
	def keys(self, keys_to_values):
		for code in self.hashing.iterate(keys_to_values):
			if code in self.content:
				yield self.hashing.decode(code)
	def items(self, keys_to_values):
		for code in self.hashing.iterate(keys_to_values):
			if code in self.content:
				yield self.hashing.decode(code), self.content[code]

inflection_lookup_hashing = DictKeyHashing('lookup', 'finite')

inflection_template_lookups = DictLookup(
	inflection_lookup_hashing, 
	{
		# verbs that indicate a subject
		'finite': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('person',    'unspecified'),
				('plurality', 'unspecified'),
				('modifier',  'unspecified'), # needed for Spanish ("voseo")
				('mood',      'indicative' ),
				('voice',     'active'     ),
				('tense',     'present'    ),
				('aspect',    'aorist'     ),
			])),

		# verbs that do not indicate a subject
		'infinitive': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('completion','bare'       ), # needed for Old English
				('voice',     'active'     ), # needed for Latin, Swedish
				('tense',     'present'    ), # needed for German, Latin
				('aspect',    'aorist'     ), # needed for Greek
			])),

		# verbs used as adjectives, indicating that an action is done upon a noun at some point in time
		'participle': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('plurality', 'unspecified'), # needed for German
				('gender',    'unspecified'), # needed for Latin, German, Russian
				('declension','unspecified'), # needed for Latin
				('voice',     'active'     ), # needed for Russian
				('tense',     'present'    ), # needed for Greek, Russian, Spanish, Swedish, French
				('aspect',    'aorist'     ), # needed for Greek, Latin, German, Russian
			])),

		# verbs used as adjectives, indicating the purpose of something
		'gerundive': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('plurality', 'unspecified'), # needed in principle
				('gender',    'unspecified'), # needed in principle
				('declension','unspecified'), # needed in principle
			])),

		# verbs used as nouns
		'gerund': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('plurality', 'unspecified'), # needed for German
				('gender',    'unspecified'), # needed for Latin, German, Russian
				('declension','unspecified'), # needed for Latin
			])),

		# verbs used as nouns, indicating the objective of something
		'supine': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified'),
				('plurality', 'unspecified'), # needed for German
				('gender',    'unspecified'), # needed for Latin, German, Russian
				('declension','unspecified'), # needed for Latin
			])),

		# verbs used as adverbs
		'adverbial': DictLookup(
			DictKeyHashing('lemma', 'unspecified')),

		# a pattern in conjugation that the verb is meant to demonstrate
		'group': DictLookup(
			DictKeyHashing('lemma', 'unspecified' )),

		# text that follows a verb in a sentence that demonstrates the verb
		'context': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified' ),
				('language',  'unspecified' ),
				('voice',     'active'      ), # needed for Greek
				('gender',    'unspecified' ), # needed for Greek
				('plurality', 'unspecified' ), # needed for Russian
			])),

		# an emoji depiction of a sentence that demonstrates the verb
		'emoji': DictLookup(
			DictTupleHashing([
				('lemma',     'unspecified' ),
				('voice',     'active'      ), # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
			])),
	})

def constantdict(value):
	return collections.defaultdict(lambda: value)

tsv_parsing = SeparatedValuesFileParsing()
inflection_annotation  = TableAnnotation(grammeme_to_category, {}, {0:'lemma'})
mood_annotation        = TableAnnotation(grammeme_to_category, {0:'lookup'}, {})
verb_phrase_annotation = TableAnnotation(grammeme_to_category, {}, {})

inflection_indexing = TableIndexing(inflection_template_lookups)
mood_indexing = TableIndexing(
	DictLookup(DictKeyHashing('lookup','template'), 
		constantdict(DictLookup(DictKeyHashing('mood')))))
verb_phrase_indexing = TableIndexing(
	DictLookup(DictKeyHashing('lookup','template'),
		constantdict(DictLookup(DictTupleHashing(keys=['voice','tense','aspect'])))))

english_conjugation = \
	inflection_indexing.index(
		inflection_annotation.annotate(
			tsv_parsing.rows('english/conjugations.tsv'), 3, 2))
english_mood_templates = \
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('english/mood-templates.tsv'), 1, 1))
emoji_mood_templates = \
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('emoji/mood-templates.tsv'), 1, 1))
english_verb_phrase_templates = \
	verb_phrase_indexing.index(
		verb_phrase_annotation.annotate(
			tsv_parsing.rows('english/verb-phrase-templates.tsv'), 1, 4))

def english(grammemes, 
		pronoun_declensions, conjugations, 
		contexts, mood_templates, verb_phrase_templates):
	be_base = {
		'lemma':     'be',
		'person':    grammemes['person'], 
		'plurality': grammemes['plurality'], 
	}
	have_base = {
		'lemma':     'have',
		'person':    grammemes['person'], 
		'plurality': grammemes['plurality'], 
	}
	verb_base = {
		'lemma':     grammemes['lemma'],
		'person':    grammemes['person'], 
		'plurality': grammemes['plurality'], 
	}
	verb_phrase_replacements = [
		('{have|present}',    conjugations[{**have_base, 'tense':  'present'  }]),
		('{have|past}',       conjugations[{**have_base, 'tense':  'past'     }]),
		('{have|imperfect}',  conjugations[{**have_base, 'aspect': 'imperfect'}]),
		('{have|perfect}',    conjugations[{**have_base, 'aspect': 'perfect'  }]),
		('{be|present}',      conjugations[{**be_base,   'tense':  'present'  }]),
		('{be|past}',         conjugations[{**be_base,   'tense':  'past'     }]),
		('{be|imperfect}',    conjugations[{**be_base,   'aspect': 'imperfect'}]),
		('{be|perfect}',      conjugations[{**be_base,   'aspect': 'perfect'  }]),
		('{verb|present}',    conjugations[{**verb_base, 'tense':  'present'  }]),
		('{verb|past}',       conjugations[{**verb_base, 'tense':  'past'     }]),
		('{verb|imperfect}',  conjugations[{**verb_base, 'aspect': 'imperfect'}]),
		('{verb|perfect}',    conjugations[{**verb_base, 'aspect': 'perfect'  }]),
		('{verb|infinitive}', grammemes['lemma']),
	]
	verb_phrase_conjugated = verb_phrase_templates['finite'][grammemes]
	for replaced, replacement in replacements:
		verb_phrase_conjugated = verb_phrase_conjugated.replace(replaced, replacement)
	verb_phrase_infinitive = verb_phrase_templates['infinitive'][grammemes]
	for replaced, replacement in replacements:
		verb_phrase_infinitive = verb_phrase_infinitive.replace(replaced, replacement)
	context = contexts[{**grammemes, 'language':'english'}]
	mood_replacements = [
		#('{subject}',           pronoun_declensions[{**grammemes, 'case':'nominative'}]),
		('{phrase}',            ' '.join([verb_phrase_conjugated, *([context] if context else [])])),
		('{phrase|infinitive}', ' '.join([verb_phrase_infinitive, *([context] if context else [])])),
	]
	sentence = mood_templates['template'][grammemes]
	for replaced, replacement in replacements:
		sentence = sentence.replace(replaced, replacement)

def format(lookups, lemmas, category_to_grammemes):
	category_to_grammemes = {**category_to_grammemes, 'lemma':lemmas}
	for grammemes, conjugation in lookups['finite'].items(category_to_grammemes):
		print((grammemes, conjugation))

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('ancient-greek/finite-conjugations.tsv'), 3, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('ancient-greek/nonfinite-conjugations.tsv'), 3, 2)
])

grammemes = {
	'lemma': 'release', 
	'person': '3', 
	'plurality': 'plural', 
	'modifier': 'unspecified', 
	'mood': 'imperative', 
	'voice': 'passive', 
	'tense': 'past', 
	'aspect': 'aorist'
}

for grammemes, conjugation in conjugations.items(category_to_grammemes):
	print((grammemes, conjugation))

english(grammemes, {}, english_conjugation['finite'], 
	lookups['context'], english_mood_templates, english_verb_phrase_templates)


lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('french/finite-conjugations.tsv'), 4, 3),
	*inflection_annotation.annotate(
		tsv_parsing.rows('french/nonfinite-conjugations.tsv'), 3, 1),
])

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('german/finite-conjugations.tsv'), 2, 3),
	*inflection_annotation.annotate(
		tsv_parsing.rows('german/nonfinite-conjugations.tsv'), 4, 1),
])

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('latin/finite-conjugations.tsv'), 3, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('latin/nonfinite-conjugations.tsv'), 6, 2),
])

lookups = inflection_indexing.index(
	inflection_annotation.annotate(
		tsv_parsing.rows('old-english/conjugations.tsv'), 5, 1))

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('proto-indo-european/finite-conjugations.tsv'), 2, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('proto-indo-european/nonfinite-conjugations.tsv'), 2, 2),
])

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('russian/finite-conjugations.tsv'), 2, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('russian/nonfinite-conjugations.tsv'), 2, 2),
])

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('sanskrit/conjugations.tsv'), 2, 4),
])

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('spanish/finite-conjugations.tsv'), 2, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('spanish/nonfinite-conjugations.tsv'), 3, 1),
])

lookups = inflection_indexing.index(
	inflection_annotation.annotate(
		tsv_parsing.rows('swedish/conjugations.tsv'), 4, 2),
)

for lookup_id, lookup in lookups.items(): 
	print(lookup_id)
	for k,v in lookup.items():
		print(k,v)


def emoji(cell):
	fonts = "'sans-serif', 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji'"
	return f'<div style="font-size:3em; font-family: {fonts}">{cell}</div>'

def foreign_focus(cell):
	return f'<div style="font-size:3em">{cell}</div>'

def foreign_side_note(cell):
	return f'<div style="font-size:2em">{cell}</div>'

def english_word(cell):
	return f'<div>{cell}</div>'

def cloze(id):
	return lambda cell: '{{'+f'c{id}::{cell}'+'}}'

def require(cell):
	return cell if cell.strip() else None

def write(filename, columns):
	with open(filename, 'w') as file:
		for row in zip(*columns):
			if all(cell is not None for cell in row):
				file.write(''.join(row)+'\n')

write('flashcards/proto-indo-european.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 3, require, strip_asterisks, cloze(2), foreign_focus), 
])

