import re
import copy
import collections
import itertools

category_to_grammemes = {

	# needed for context in a sentence
	'language':   ['english', 'translated'], 

	# needed for infinitives
	'completion': ['full', 'bare'],

	# needed for finite forms
	'person':     ['1','2','3'],
	'plurality':  ['singular', 'dual', 'plural'],
	'inclusivity':['inclusive', 'exclusive', 'voseo', 'formal'],
	'modifier':   ['unmodified','familiar', 
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
	'case':       ['nominative', 'accusative', 'dative', 'ablative', 
	               'genitive', 'locative', 'instrumental'],

    # needed for infinitive forms, finite forms, participles, context in sentences, and graphic depictions
	'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
	'tense':      ['present', 'past', 'future',], 
	'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 
}


category_to_grammemes_with_lookups = {
	**category_to_grammemes,
	# needed to tip off which key/lookup should be used to stored cell contents
	'lookup':     ['finite', 'infinitive', 
	               'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
	               'context', 'group', 'emoji'],
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes_with_lookups.items() 
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
	Keywords are indicated by keys within `keyword_to_attribute`.
	Keywords that are not known at the time of execution may be 
	 indicated using `header_column_id_to_attribute`, 
	 which marks all cell contents of a given column as keywords for a given attribute.

	As an example, if a header row is marked "green", and "green" is a type of "color",
	 then `keyword_to_attribute` may store "green":"color" as a key:value pair.
	Anytime "green" is listed in a header row or column, 
	 all contents of the row or column associated with that header cell 
	 will be marked as having the color "green".

	`TableAnnotation` converts tables that are written in this manner between 
	two reprepresentations: 
	The first representation is a list of rows, where rows are lists of cell contents.
	The second representation is a list where each element is a tuple,
	 (annotation,cell), where "cell" is the contents of a cell within the table,
	 and "annotations" is a dict of attribute:keyword associated with a cell.
	'''
	def __init__(self, 
			keyword_to_attribute, 
			header_row_id_to_attribute, header_column_id_to_attribute,
			default_attributes):
		self.keyword_to_attribute = keyword_to_attribute
		self.header_column_id_to_attribute = header_column_id_to_attribute
		self.header_row_id_to_attribute = header_row_id_to_attribute
		self.default_attributes = default_attributes
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
				if cell in self.keyword_to_attribute:
					column_base_attributes[j][self.keyword_to_attribute[cell]] = cell
		annotations = []
		for row in nonheader_rows:
			row_base_attributes = {}
			for i in range(0,header_column_count):
				cell = row[i]
				if i in self.header_column_id_to_attribute:
					row_base_attributes[self.header_column_id_to_attribute[i]] = cell
				if cell in self.keyword_to_attribute:
					row_base_attributes[self.keyword_to_attribute[cell]] = cell
			for i in range(header_column_count,len(row)):
				cell = row[i]
				# if cell and column_base_attributes[i]:
				if cell:
					annotation = {}
					annotation.update(self.default_attributes)
					annotation.update(row_base_attributes)
					annotation.update(column_base_attributes[i])
					annotations.append((annotation,cell))
		return annotations

class FlatTableIndexing:
	'''
	`FlatTableIndexing` converts a list of (annotation,cell) tuples
	(such as those output by `TableAnnotation`)
	to a representation where cells are stored in a lookup.
	The cells are indexed by their annotations according to the indexing behavior 
	within a given `template_lookup`.
	'''
	def __init__(self, template_lookup):
		self.template_lookup = template_lookup
	def index(self, annotations):
		lookups = copy.deepcopy(self.template_lookup)
		for annotation,cell in annotations:
			lookups[annotation] = cell
		return lookups

class NestedTableIndexing:
	'''
	`NestedTableIndexing` converts a list of (annotation,cell) tuples
	(such as those output by `TableAnnotation`)
	to a representation where cells are stored in nested lookups.
	The cells are indexed by their annotations according to the indexing behavior 
	within a given `template_lookups`.
	'''
	def __init__(self, template_lookups):
		self.template_lookups = template_lookups
	def index(self, annotations):
		lookups = copy.deepcopy(self.template_lookups)
		for annotation,cell in annotations:
			lookups[annotation][annotation] = cell
		return lookups

class DictKeyHashing:
	'''
	`DictKeyHashing` represents a method for using dictionaries as hashable objects.
	It does so by converting between two domains, known as "dictkeys" and "tuplekeys".
	A "dictkey" is a dictionary that maps each key to either a value or a set of values.
	A "dictkey" is indexed by one or more "tuplekeys", which are ordinary tuples of values
	 that can be indexed natively in Python dictionaries.
	`DictKeyHashing` works by selecting a single key:value pair 
	 within a dictkey to serve as the tuplekey(s) to index by.
	It offers several conveniences to allow 
	 working with both dictkeys and the values they are indexed by
	'''
	def __init__(self, key, default=None):
		self.key = key
		self.default = default
	def dictkey(self, tuplekey):
		return {self.key:tuplekey}
	def tuplekeys(self, dictkey):
		'''
		Returns a generator that iterates through 
		possible tuples whose keys are given by `keys_and_defaults`
		and whose values are given by a `dictkey` dict 
		that maps a key from `keys_and_defaults` to either a value or a set of possible values.
		'''
		key = self.key
		default = self.default
		if type(dictkey) in {dict}:
			return itertools.chain(
					[default] if default is not None and default not in dictkey[key] else [], 
					dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]])
		elif type(dictkey) in {set,list}:
			return dictkey
		else:
			return [dictkey]


class DictTupleHashing:
	'''
	`DictTupleHashing` represents a method for using dictionaries as hashable objects.
	It does so by converting between two domains, known as "dictkeys" and "tuplekeys".
	A "dictkey" is a dictionary that maps each key to either a value or a set of values.
	A "dictkey" is indexed by one or more "tuplekeys", which are ordinary tuples of values
	 that can be indexed natively in Python dictionaries.
	`DictKeyHashing` works by ordering values in a dictkey 
	 into one or more tuplekeys according to a given list of `keys`.
	'''
	def __init__(self, keys=None, keys_and_defaults=None):
		self.keys_and_defaults = (
			[(key,None) for key in keys] if keys_and_defaults is None 
			 else keys_and_defaults)
	def dictkey(self, tuplekey):
		return {key:tuplekey[i] for i, (key, default) in enumerate(self.keys_and_defaults)}
	def tuplekeys(self, dictkey):
		'''
		Returns a generator that iterates through 
		possible tuples whose keys are given by `keys_and_defaults`
		and whose values are given by a `dictkey` dict 
		that maps a key from `keys_and_defaults` to either a value or a set of possible values.
		'''
		return itertools.product(
			*[itertools.chain(
				[default] if default is not None and default not in dictkey[key] else [], 
				dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]])
			  for key, default in self.keys_and_defaults])

class DictLookup:
	'''
	`DictLookup` is a lookup that indexes "dictkeys" by a given `hashing` method,
	where `hashing` is of a class that shares the same iterface as `DictHashing`.
	A "dictkey" is a dictionary that maps each key to either a value or a set of values.
	A "dictkey" is indexed by one or more "tuplekeys", which are ordinary tuples of values.
	'''
	def __init__(self, hashing, content=None):
		self.hashing = hashing
		self.content = {} if content is None else content
	def __getitem__(self, key):
		'''
		Return the value that is indexed by `key` 
		if it is the only such value, otherwise return None.
		'''
		if isinstance(key, tuple):
			return self.content[key]
		else:
			tuplekeys = [tuplekey 
				for tuplekey in self.hashing.tuplekeys(key)
				if tuplekey in self.content]
			if len(tuplekeys) == 1:
				return self.content[tuplekeys[0]]
			elif len(tuplekeys) == 0:
				raise IndexError('\n'.join([
									'Key does not exist within the dictionary.',
									'Key:',
									  '\t'+str(key),
								]))
			else:
				raise IndexError('\n'.join([
									'Key is ambiguous.',
									'Key:',
									  '\t'+str(key),
									'Available interpretations:',
									*['\t'+str(self.hashing.dictkey(tuplekey)) 
									  for tuplekey in tuplekeys]
								]))
	def __setitem__(self, key, value):
		'''
		Store `value` within the indices represented by `key`.
		'''
		if isinstance(key, tuple):
			return self.content[key]
		else:
			for tuplekey in self.hashing.tuplekeys(key):
				self.content[tuplekey] = value
	def __contains__(self, key):
		if isinstance(key, tuple):
			return key in self.content
		else:
			return any(tuplekey in self.content 
				       for tuplekey in self.hashing.tuplekeys(key))
	def __iter__(self):
		return self.content.__iter__()
	def __len__(self):
		return self.content.__len__()
	def values(self, dictkey):
		for tuplekey in self.hashing.tuplekeys(dictkey):
			if tuplekey in self.content:
				yield self.content[tuplekey]
	def keys(self, dictkey):
		for tuplekey in self.hashing.tuplekeys(dictkey):
			if tuplekey in self.content:
				yield self.hashing.dictkey(tuplekey)
	def items(self, dictkey):
		for tuplekey in self.hashing.tuplekeys(dictkey):
			if tuplekey in self.content:
				yield self.hashing.dictkey(tuplekey), self.content[tuplekey]


inflection_lookup_hashing = DictKeyHashing('lookup')

conjugation_template_lookups = DictLookup(
	inflection_lookup_hashing, 
	{
		# verbs that indicate a subject
		'finite': DictLookup(
			DictTupleHashing([
					'lemma',           
					'person',           
					'plurality',           
					'modifier',   # needed for Spanish ("voseo")
					'mood',           
					'voice',           
					'tense',           
					'aspect',           
				])),

		# verbs that do not indicate a subject
		'infinitive': DictLookup(
			DictTupleHashing([
					'lemma',           
					'completion', # needed for Old English
					'voice',      # needed for Latin, Swedish
					'tense',      # needed for German, Latin
					'aspect',     # needed for Greek
				])),

		# verbs used as adjectives, indicating that an action is done upon a noun at some point in time
		'participle': DictLookup(
			DictTupleHashing([
					'lemma',           
					'plurality',  # needed for German
					'gender',     # needed for Latin, German, Russian
					'case',       # needed for Latin
					'voice',      # needed for Russian
					'tense',      # needed for Greek, Russian, Spanish, Swedish, French
					'aspect',     # needed for Greek, Latin, German, Russian
				])),

		# verbs used as adjectives, indicating the purpose of something
		'gerundive': DictLookup(
			DictTupleHashing([
					'lemma',           
					'plurality',  # needed in principle
					'gender',     # needed in principle
					'case',       # needed in principle
				])),

		# verbs used as nouns
		'gerund': DictLookup(
			DictTupleHashing([
					'lemma',           
					'plurality',  # needed for German
					'gender',     # needed for Latin, German, Russian
					'case',       # needed for Latin
				])),

		# verbs used as nouns, indicating the objective of something
		'supine': DictLookup(
			DictTupleHashing([
					'lemma',           
					'plurality',  # needed for German
					'gender',     # needed for Latin, German, Russian
					'case',       # needed for Latin
				])),

		# verbs used as adverbs
		'adverbial': DictLookup(
			DictKeyHashing('lemma')),

		# a pattern in conjugation that the verb is meant to demonstrate
		'group': DictLookup(
			DictKeyHashing('lemma')),

		# text that follows a verb in a sentence that demonstrates the verb
		'context': DictLookup(
			DictTupleHashing([
					'lemma',           
					'language',           
					'voice',      # needed for Greek
					'gender',     # needed for Greek
					'plurality',  # needed for Russian
				])),

		# an emoji depiction of a sentence that demonstrates the verb
		'emoji': DictLookup(
			DictTupleHashing([
					'lemma',           
					'voice',      # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
				])),
	})


def constantdict(value):
	return collections.defaultdict(lambda: value)

tsv_parsing = SeparatedValuesFileParsing()
inflection_annotation  = TableAnnotation(
	grammeme_to_category, {}, {0:'lemma'}, 
	{**category_to_grammemes, 'lookup':'finite'})
verb_phrase_annotation = TableAnnotation(
	grammeme_to_category, {}, {}, 
	{**category_to_grammemes, 'lookup':'finite'})
mood_annotation        = TableAnnotation(
	{}, {0:'column'}, {0:'mood'}, {})

conjugation_indexing = NestedTableIndexing(conjugation_template_lookups)
declension_indexing  = FlatTableIndexing(DictLookup(DictTupleHashing(['person','plurality','case'])))
verb_phrase_indexing = FlatTableIndexing(DictLookup(DictTupleHashing(['lookup','voice','tense','aspect'])))
mood_indexing = FlatTableIndexing(DictLookup(DictTupleHashing(['mood','column'])))

english_conjugation = \
	conjugation_indexing.index(
		inflection_annotation.annotate(
			tsv_parsing.rows('english/conjugations.tsv'), 3, 2))
english_declension = \
	declension_indexing.index(
		inflection_annotation.annotate(tsv_parsing.rows('english/pronoun-declensions.tsv'), 1, 3))
english_mood_templates = \
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('english/mood-templates.tsv'), 1, 1))
english_verb_phrase_templates = \
	verb_phrase_indexing.index(
		verb_phrase_annotation.annotate(
			tsv_parsing.rows('english/verb-phrase-templates.tsv'), 1, 4))

emoji_mood_templates = \
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('emoji/mood-templates.tsv'), 1, 1))

for k,v in list(english_conjugation['finite'].items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
for k,v in list(english_verb_phrase_templates.items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)

def english(grammemes, 
		pronoun_declensions, conjugations, 
		contexts, mood_templates, verb_phrase_templates):
	base = {**grammemes, 'gender': 'masculine', 'language':'english'}
	speaker_base = {
		'person':    '1', 
		'plurality': 'singular', 
		'tense':     base['tense'] if base['tense'] in {'past','present'} else 'present'
	}
	lemmas = ['be', 'have', 'command', 'forbid', 'permit', 'wish', 'intend', grammemes['lemma']]
	context = contexts[{**base}]
	mood_replacements = [
		('{subject}',            pronoun_declensions[{**grammemes, 'case':'nominative'}]),
		('{phrase}',             verb_phrase_templates[{**grammemes,'lookup':'finite'}]),
		('{phrase|infinitive}',  verb_phrase_templates[{**grammemes,'lookup':'infinitive'}]),
	]
	sentence = mood_templates[{**grammemes,'column':'template'}]
	for replaced, replacement in mood_replacements:
		sentence = sentence.replace(replaced, replacement)
	sentence = sentence.replace('{verb', '{'+grammemes['lemma'])
	sentence = sentence.replace('{context}', context)
	for lemma in lemmas:
		replacements = [
			('{'+lemma+'|speaker}',    conjugations[{**base, 'lemma':lemma, **speaker_base}]),
			('{'+lemma+'|present}',    conjugations[{**base, 'lemma':lemma, 'tense':   'present'    }]),
			('{'+lemma+'|past}',       conjugations[{**base, 'lemma':lemma, 'tense':   'past'       }]),
			('{'+lemma+'|perfect}',    conjugations[{**base, 'lemma':lemma, 'aspect':  'perfect'    }]),
			('{'+lemma+'|imperfect}',  conjugations[{**base, 'lemma':lemma, 'aspect':  'imperfect'  }]),
			('{'+lemma+'|infinitive}', lemma),
		]
		for replaced, replacement in replacements:
			sentence = sentence.replace(replaced, replacement)
	if grammemes['voice'] == 'middle':
		sentence = f'[middle voice:] {sentence}'
	return sentence

english({**grammemes, 'voice':'middle'}, english_declension, english_conjugation['finite'], lookups['context'], english_mood_templates, english_verb_phrase_templates)

lookups = inflection_indexing.index([
	*inflection_annotation.annotate(
		tsv_parsing.rows('ancient-greek/finite-conjugations.tsv'), 3, 4),
	*inflection_annotation.annotate(
		tsv_parsing.rows('ancient-greek/nonfinite-conjugations.tsv'), 3, 2)
])

def format(lookups, lemmas, category_to_grammemes):
	category_to_grammemes = {**category_to_grammemes, 'lemma':lemmas}
	for grammemes, conjugation in lookups['finite'].items(category_to_grammemes):
		print((grammemes, conjugation))

for k,v in list(lookups['finite'].items({'lemma':'release',**category_to_grammemes}))[:100]: print(k,v)

grammemes = {
	'lemma': 'release', 
	'person': '3', 
	'plurality': 'plural', 
	'modifier': 'unmodified', 
	'mood': 'imperative', 
	'voice': 'passive', 
	'tense': 'past', 
	'aspect': 'aorist'
}


def update(default, annotations):
	for content, annotation in annotations:


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
