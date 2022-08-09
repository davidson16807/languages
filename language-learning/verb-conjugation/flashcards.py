import re
import copy
import collections
import itertools

category_to_grammemes = {

	# needed to lookup the argument that is used to demonstrate a verb
	'language':   ['english', 'translated'], 

	# needed for infinitives
	'completion': ['full', 'bare'],

	# needed for finite forms
	'person':     ['1','2','3'],
	'number':     ['singular', 'dual', 'plural'],
	'inclusivity':['inclusive', 'exclusive'],
	'mood':       ['indicative', 'subjunctive', 'conditional', 
	               'optative', 'benedictive', 'jussive', 'potential', 
	               'imperative', 'prohibitive', 'desiderative', 
	               'dubitative', 'hypothetical', 'presumptive', 'permissive', 
	               'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
	               'precative', 'volitive', 'involutive', 'inferential', 
	               'necessitative', 'interrogative', 'injunctive', 
	               'suggestive', 'comissive', 'deliberative', 
	               'propositive', 'dynamic', 
	              ],

	# needed for correlatives in general
	'proform':    ['personal', 
	               'interrogative', 'demonstrative', 'indefinite', 'elective', 'universal', 'negative', 
	               'relative', 'numeral'],
	'pronoun':    ['human','nonhuman','selection'],
	'proadverb':  ['location','source','goal','time','manner','reason','quality','amount'],
	'distance':   ['proximal','medial','distal'],

	# needed for Spanish
	'formality':  ['familiar', 'formal', 'voseo'],

	# needed for Sanskrit
	'stem':       ['primary', 'causative', 'intensive',],

	# needed for gerunds, supines, participles, and gerundives
	'gender':     ['masculine', 'feminine', 'neuter'],
	'case':       ['nominative', 'accusative', 'dative', 'ablative', 
	               'genitive', 'locative', 'instrumental'],

    # needed for infinitive forms, finite forms, participles, arguments, and graphic depictions
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
	               'argument', 'group', 'emoji'],
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes_with_lookups.items() 
    for instance in instances
}

class SeparatedValuesFileParsing:
	def __init__(self, comment='#', delimeter='\t', padding=' \t\r\n'):
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
			lookup = lookups[annotation]
			lookup[annotation] = cell
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
	def __init__(self, key):
		self.key = key
	def dictkey(self, tuplekey):
		return {self.key:tuplekey}
	def tuplekeys(self, dictkey):
		'''
		Returns a generator that iterates through possible values for the given `key`
		given values from a `dictkey` dict that maps a key to either a value or a set of possible values.
		'''
		key = self.key
		if type(dictkey) in {dict}:
			return dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
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
	def __init__(self, keys):
		self.keys = keys
	def dictkey(self, tuplekey):
		return {key:tuplekey[i] for i, key in enumerate(self.keys)}
	def tuplekeys(self, dictkey):
		'''
		Returns a generator that iterates through 
		possible tuples whose keys are given by `keys`
		and whose values are given by a `dictkey` dict 
		that maps a key from `keys` to either a value or a set of possible values.
		'''
		return [tuple(reversed(tuplekey)) 
		        for tuplekey in itertools.product(
					*[dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
					  for key in reversed(self.keys)])]

class DictLookup:
	'''
	`DictLookup` is a lookup that indexes "dictkeys" by a given `hashing` method,
	where `hashing` is of a class that shares the same iterface as `DictHashing`.
	A "dictkey" is a dictionary that maps each key to either a value or a set of values.
	A "dictkey" is indexed by one or more "tuplekeys", which are ordinary tuples of values.
	'''
	def __init__(self, name, hashing, content=None):
		self.name = name
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
									*(['Lookup:', '\t'+str(self.name)] if self.name else []),
									'Key:', '\t'+str(key),
								]))
			else:
				raise IndexError('\n'.join([
									'Key is ambiguous.',
									*(['Lookup:', '\t'+str(self.name)] if self.name else []),
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

lemma_hashing = DictKeyHashing('lemma')

declension_hashing = DictTupleHashing([
		'lemma',           
		'number',     # needed for German
		'gender',     # needed for Latin, German, Russian
		'case',       # needed for Latin
	])

conjugation_template_lookups = DictLookup(
	'conjugation',
	DictKeyHashing('lookup'), 
	{
		# verbs that indicate a subject
		'finite': DictLookup(
			'finite',
			DictTupleHashing([
					'lemma',           
					'person',           
					'number',           
					'formality',   # needed for Spanish ("voseo")
					'mood',           
					'voice',           
					'tense',           
					'aspect',           
				])),
		# verbs that do not indicate a subject
		'infinitive': DictLookup(
			'infinitive',
			DictTupleHashing([
					'lemma',           
					'completion', # needed for Old English
					'voice',      # needed for Latin, Swedish
					'tense',      # needed for German, Latin
					'aspect',     # needed for Greek
				])),
		# verbs used as adjectives, indicating that an action is done upon a noun at some point in time
		'participle': DictLookup(
			'participle',
			DictTupleHashing([
					'lemma',           
					'number',  # needed for German
					'gender',     # needed for Latin, German, Russian
					'case',       # needed for Latin
					'voice',      # needed for Russian
					'tense',      # needed for Greek, Russian, Spanish, Swedish, French
					'aspect',     # needed for Greek, Latin, German, Russian
				])),
		# verbs used as adjectives, indicating the purpose of something
		'gerundive': DictLookup('gerundive', declension_hashing),
		# verbs used as nouns
		'gerund': DictLookup('gerund', declension_hashing),
		# verbs used as nouns, indicating the objective of something
		'supine': DictLookup('supine', declension_hashing),
		# verbs used as adverbs
		'adverbial': DictLookup('adverbial', lemma_hashing),
		# a pattern in conjugation that the verb is meant to demonstrate
		'group': DictLookup('group', lemma_hashing),
		# text that follows a verb in a sentence that demonstrates the verb
		'argument': DictLookup(
			'argument',
			DictTupleHashing([
					'lemma',           
					'language',           
					'voice',      # needed for Greek
					'gender',     # needed for Greek
					'number',  # needed for Russian
				])),
		# an emoji depiction of a sentence that demonstrates the verb
		'emoji': DictLookup(
			'emoji',
			DictTupleHashing([
					'lemma',           
					'voice',      # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
				])),
	})

basic_pronoun_declension_hashing = DictTupleHashing([
		'number',     # needed for German
		'gender',     # needed for Latin, German, Russian
		'case',       # needed for Latin
	])

declension_template_lookups = DictLookup(
	'declension',
	DictKeyHashing('proform'), 
	{
		'personal': DictLookup(
			'personal',
			DictTupleHashing([
					'person',           
					'number',           
					'formality',   # needed for Spanish ("voseo")
					'gender',           
					'case',           
				])),
		'demonstrative': DictLookup(
			'demonstrative',
			DictTupleHashing([
					'distance',
					'number',     
					'gender',     
					'case',       
				])),
		'interrogative': DictLookup('interrogative', basic_pronoun_declension_hashing),
		'indefinite': DictLookup('indefinite', basic_pronoun_declension_hashing),
		'universal': DictLookup('universal', basic_pronoun_declension_hashing),
		'relative': DictLookup('relative', basic_pronoun_declension_hashing),
		'numeral': DictLookup('numeral', basic_pronoun_declension_hashing),
	})

tsv_parsing = SeparatedValuesFileParsing()
conjugation_annotation  = TableAnnotation(
	grammeme_to_category, {}, {0:'lemma'}, 
	{**category_to_grammemes, 'lookup':'finite'})
pronoun_annotation  = TableAnnotation(
	grammeme_to_category, {}, {}, 
	{**category_to_grammemes, 'proform':'personal'})
predicate_annotation = TableAnnotation(
	grammeme_to_category, {}, {}, 
	{**category_to_grammemes, 'lookup':'finite'})
mood_annotation        = TableAnnotation(
	{}, {0:'column'}, {0:'mood'}, {})

conjugation_indexing = NestedTableIndexing(conjugation_template_lookups)
declension_indexing  = NestedTableIndexing(declension_template_lookups)
predicate_indexing = FlatTableIndexing(DictLookup('predicate', DictTupleHashing(['lookup','voice','tense','aspect'])))
mood_indexing = FlatTableIndexing(DictLookup('mood', DictTupleHashing(['mood','column'])))

class English:
	def __init__(self, 
			pronoun_declension_lookups, 
			conjugation_lookups, 
			predicate_templates, 
			mood_templates):
		self.pronoun_declension_lookups = pronoun_declension_lookups
		self.conjugation_lookups = conjugation_lookups
		self.predicate_templates = predicate_templates
		self.mood_templates = mood_templates
	def conjugate(self, grammemes, argument_lookup):
		dependant_clause = {
			**grammemes,
			'language': 'english',
		}
		independant_clause = {
			**grammemes,
			'language': 'english',
			'aspect': 'aorist',
			'tense':     
				'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
				'present' if dependant_clause['tense'] in {'future'} else
				dependant_clause['tense']
		}
		lemmas = ['be', 'have', 
		          'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
		          dependant_clause['lemma']]
		if dependant_clause not in argument_lookup:
			return None
		argument = argument_lookup[dependant_clause]
		mood_replacements = [
			('{subject}',              self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'nominative'}]),
			('{subject|accusative}',   self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'accusative'}]),
			('{predicate}',            self.predicate_templates[{**dependant_clause,'lookup':'finite'}]),
			('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'lookup':'infinitive'}]),
		]
		sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
		for replaced, replacement in mood_replacements:
			sentence = sentence.replace(replaced, replacement)
		sentence = sentence.replace('{verb', '{'+dependant_clause['lemma'])
		sentence = sentence.replace('{argument}', argument)
		table = self.conjugation_lookups['finite']
		for lemma in lemmas:
			replacements = [
				('{'+lemma+'|independant}',         table[{**independant_clause, 'lemma':lemma, }]),
				('{'+lemma+'|independant|speaker}', table[{**independant_clause, 'lemma':lemma, 'person':'1', 'number':'singular'}]),
				('{'+lemma+'|present}',             table[{**dependant_clause,   'lemma':lemma, 'tense':  'present',  'aspect':'aorist'}]),
				('{'+lemma+'|past}',                table[{**dependant_clause,   'lemma':lemma, 'tense':  'past',     'aspect':'aorist'}]),
				('{'+lemma+'|perfect}',             table[{**dependant_clause,   'lemma':lemma, 'aspect': 'perfect'    }]),
				('{'+lemma+'|imperfect}',           table[{**dependant_clause,   'lemma':lemma, 'aspect': 'imperfect'  }]),
				('{'+lemma+'|infinitive}',          lemma),
			]
			for replaced, replacement in replacements:
				sentence = sentence.replace(replaced, replacement)
		if dependant_clause['voice'] == 'middle':
			sentence = f'[middle voice:] {sentence}'
		return sentence

english = English(
	declension_indexing.index(
		pronoun_annotation.annotate(tsv_parsing.rows('english/pronoun-declensions.tsv'), 1, 3)),
	conjugation_indexing.index(
		conjugation_annotation.annotate(
			tsv_parsing.rows('english/conjugations.tsv'), 3, 2)),
	predicate_indexing.index(
		predicate_annotation.annotate(
			tsv_parsing.rows('english/predicate-templates.tsv'), 1, 4)),
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('english/mood-templates.tsv'), 1, 1)),
)

class Translation:
	def __init__(self, 
			pronoun_declension_lookups, 
			conjugation_lookups, 
			subject_map=lambda x:x, 
			verb_map=lambda x:x):
		self.pronoun_declension_lookups = pronoun_declension_lookups
		self.conjugation_lookups = conjugation_lookups
		self.subject_map = subject_map
		self.verb_map = verb_map
	def conjugate(self, grammemes, argument_lookup):
		grammemes = {**grammemes, 'language':'translated'}
		if grammemes not in self.conjugation_lookups['finite']:
			return None
		elif grammemes not in argument_lookup:
			return None
		else:
			return ' '.join([
					self.subject_map(self.pronoun_declension_lookups['personal'][{**grammemes, 'case':'nominative'}]),
					self.verb_map(self.conjugation_lookups['finite'][grammemes]),
					argument_lookup[grammemes],
				])

class CardGeneration:
	def __init__(self, category_to_grammemes, finite_traversal):
		self.category_to_grammemes = category_to_grammemes
		self.finite_traversal = finite_traversal
	def generate(self, translation, lemmas):
		for lemma in lemmas:
			for tuplekey in self.finite_traversal.tuplekeys(self.category_to_grammemes):
				dictkey = {
						**self.finite_traversal.dictkey(tuplekey), 
						'lemma':   lemma,
						'proform': 'personal'
					}
				argument_lookup = translation.conjugation_lookups['argument']
				translated_text = translation.conjugate(dictkey, argument_lookup)
				english_text    = english.conjugate(dictkey, argument_lookup)
				if translated_text and english_text:
					yield dictkey, english_text, translated_text

def emoji(cell):
	fonts = "'sans-serif', 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji'"
	return f'<div style="font-size:3em; font-family: {fonts}">{cell}</div>'

def foreign_focus(cell):
	return f'<div style="font-size:3em">{cell}</div>'

def foreign_side_note(cell):
	return f'<div style="font-size:2em">{cell}</div>'

def english_word(cell):
	return f'<div>{cell}</div>'

def first_of_options(cell):
	return cell.split('/')[0]

def cloze(id):
	return lambda cell: '{{'+f'c{id}::{cell}'+'}}'

def replace(replacements):
	def _replace(cell):
		for replaced, replacement in replacements:
			cell = cell.replace(replaced, replacement)
		return cell
	return _replace

def require(cell):
	return cell if cell.strip() else None

def compose(*cell_functions):
	if len(cell_functions) > 1:
		return lambda cell: cell_functions[0](compose(cell_functions[1:]))
	else:
		return cell_functions[0]

greek_conjugation = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('ancient-greek/finite-conjugations.tsv'), 3, 4),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('ancient-greek/nonfinite-conjugations.tsv'), 3, 2)
])


greek_pronoun_declension = declension_indexing.index(
	pronoun_annotation.annotate(
		tsv_parsing.rows('ancient-greek/pronoun-declensions.tsv'), 1, 4))


translation = Translation(
	greek_pronoun_declension, 
	greek_conjugation, 
	subject_map=first_of_options, 
	verb_map=cloze(1))

translation.conjugate({**grammemes, 'proform':'personal'}, translation.conjugation_lookups['argument'])

infinitive_traversal = DictTupleHashing(
	['tense', 'aspect', 'mood', 'voice'])

def irrelevant_gender_and_formality_filter(grammemes):
	number = grammemes['number']
	person = grammemes['person']
	gender = grammemes['gender']
	formality = grammemes['formality']
	if formality != 'familiar':
		return False
	elif person == '3' and number == 'singular' and gender != 'masculine':
		return False
	elif gender != 'neuter':
		return False
	else:
		return True

card_generation = CardGeneration(category_to_grammemes, 
	DictTupleHashing(['person','number','gender','formality','tense', 'aspect', 'mood', 'voice']))
for grammemes, english_text, translated_text in card_generation.generate(translation, ['be','go','release']):
	if irrelevant_gender_and_formality_filter(grammemes):
		print(grammemes)
		print(english_text)
		print(translated_text)


for k,v in list(english_conjugation['finite'].items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
for k,v in list(english_predicate_templates.items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)
for k,v in list(lookups['finite'].items({'lemma':'release',**category_to_grammemes}))[:100]: print(k,v)



lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('french/finite-conjugations.tsv'), 4, 3),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('french/nonfinite-conjugations.tsv'), 3, 1),
])

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('german/finite-conjugations.tsv'), 2, 3),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('german/nonfinite-conjugations.tsv'), 4, 1),
])

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('latin/finite-conjugations.tsv'), 3, 4),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('latin/nonfinite-conjugations.tsv'), 6, 2),
])

lookups = conjugation_indexing.index(
	conjugation_annotation.annotate(
		tsv_parsing.rows('old-english/conjugations.tsv'), 5, 1))

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('proto-indo-european/finite-conjugations.tsv'), 2, 4),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('proto-indo-european/nonfinite-conjugations.tsv'), 2, 2),
])

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('russian/finite-conjugations.tsv'), 2, 4),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('russian/nonfinite-conjugations.tsv'), 2, 2),
])

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('sanskrit/conjugations.tsv'), 2, 4),
])

lookups = conjugation_indexing.index([
	*conjugation_annotation.annotate(
		tsv_parsing.rows('spanish/finite-conjugations.tsv'), 2, 4),
	*conjugation_annotation.annotate(
		tsv_parsing.rows('spanish/nonfinite-conjugations.tsv'), 3, 1),
])

lookups = conjugation_indexing.index(
	conjugation_annotation.annotate(
		tsv_parsing.rows('swedish/conjugations.tsv'), 4, 2),
)


def write(filename, columns):
	with open(filename, 'w') as file:
		for row in zip(*columns):
			if all(cell is not None for cell in row):
				file.write(''.join(row)+'\n')

grammemes = {
	'lemma': 'release', 
	'person': '3', 
	'number': 'singular', 
	'formality': 'familiar', 
	'voice': 'active', 
	'tense': 'present', 
	'aspect': 'aorist',
	'mood': 'indicative', 
	'gender': 'masculine', 
	'language':'english',
}


emoji_mood_templates = \
	mood_indexing.index(
		mood_annotation.annotate(
			tsv_parsing.rows('emoji/mood-templates.tsv'), 1, 1))

