import re
import inflection
import collections

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

# returns a list of indexible strings 
# that represent synonyms within the same note
def get_keys(keytext):
	for key in keytext.split(','):
		key = key.strip().lower()
		key = re.sub('^to +', '', key)
		key = re.sub('\([^)]*\)', '', key)
		key = key.replace('...', '')
		yield key.strip()

def get_value_keys_prompt_tuple(line):
	columns = [ column.strip() for column in line.split('\t', 2) ]
	value = columns[0] if len(columns) > 1 else ''
	keys = list(get_keys(columns[1])) if len(columns) > 1 else []
	prompt = columns[2] if len(columns) > 2 else columns[1] if len(columns) > 1 else columns[0]
	return value, keys, prompt

with open('../emoji/vocabulary_and_sequence.txt') as file:
	lines = [
		line 
		for line in file.readlines() 
		if not line.strip().startswith('#')
	]
	line_groups = split(lines, whitespace)
	emoji_keys_text = [
		[ get_value_keys_prompt_tuple(line) for line in line_group ]
		for line_group in line_groups
	]
	key_to_emoji = collections.defaultdict(list)
	for line_group in emoji_keys_text:
		for emoji, keys, text in line_group:
			for key in keys:
				key_to_emoji[key].append(emoji)

	key_to_sequence = collections.defaultdict(list)
	for line_group in emoji_keys_text:
		sequence = [keys for emoji, keys, text in line_group]
		for emoji, keys, text in line_group:
			for key in keys:
				if (key not in key_to_sequence or 
					len(key_to_sequence[key]) > len(sequence)):
					key_to_sequence[key] = sequence

# We ideally want to order the words we learn by the frequency they would have been spoken in Proto Indo European.
# We obviously do not have a corpus reflecting this, 
# however we can presume it would most resemble that of the oldest Indo European corpuses available. 
# Pragmatically this would be a Classical Greek corpus,
# however until we reach MVP we don't want to spend time creating the additional map to English,
# so for right now we settle on using English word frequencies from the Project Gutenberg corpus.
# words_ignored = set()
with open('../english/frequency_from_gutenberg_ignored.txt') as file:
	words_ignored = { 
		line.strip().lower() 
		for line in file.readlines()
	}

with open('../english/frequency_from_gutenberg.txt') as file:
	lines = [
		line.strip().lower().split(' ', 2)[0]
		for line in file.readlines()
	]
	frequency_to_keys = [
		line
		for line in lines
		if line not in words_ignored
	]

with open('vocabulary-source.tsv') as file:
	pie_keys_english = [
		get_value_keys_prompt_tuple(line)
		for line in file.readlines()
	]
	key_to_pie = collections.defaultdict(list)
	for pie, keys, english in pie_keys_english:
		for key in keys:
			key_to_pie[key].append(pie)

	pie_to_key = collections.defaultdict(list)
	for pie, keys, english in pie_keys_english:
		for key in keys:
			pie_to_key[pie].append(key)

	pie_to_english = collections.defaultdict(list)
	for pie, keys, english in pie_keys_english:
		pie_to_english[pie].append(english)

	english_to_pie = collections.defaultdict(list)
	for pie, keys, english in pie_keys_english:
		english_to_pie[english].append(pie)

def keys_to_values(listdict, keys):
	return [ value for key in keys 
		for value in listdict[key] ]

def pie_to_english_card(emoji, question, answer):
	emoji_style = "font-size:11em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
	return f'''<br/><div style="font-size:5em">{question}</div>\t<div style="{emoji_style}">{emoji}</div><div style="font-size:medium">{answer}</div><br/>'''

def english_to_pie_card(emoji, question, answer):
	emoji_style = "font-size:11em; font-family: 'DejaVu Sans', 'sans-serif', 'Twemoji Mozilla','Segoe UI Emoji','Noto Color Emoji'"
	return f'<br/><div style="{emoji_style}">{emoji}</div><div style="font-size:medium">{question}</div>\t<div style="font-size:5em">{answer}</div><br/>'

def standardize_word(word):
	standardized = re.sub('[ -aeiouéōó]*', '', word)
	for replaced, replacement in [('l̥', 'l'),('n̥', 'n'),('m̥', 'm'),('r̥', 'r'),('h₁','')]:
		standardized = standardized.replace(replaced, replacement)
	return standardized

def is_root_word_of(word1, word2):
	return (word1 != word2 
		and standardize_word(word1).startswith(standardize_word(word2))
	)


class DeckConstructionStateManagement:
	"""an RAII state manager for generating cards"""
	def __init__(self):
		self.forward_translation_included = set()
		self.back_translation_included = set()
	def cards(self, pie, keys):
		# prefer emojis within the topic before searching elsewhere
		key_emojis = keys_to_values(key_to_emoji, keys)
		pie_emojis = keys_to_values(key_to_emoji, keys_to_values(pie_to_key, [pie]))
		shared_emojis = set(key_emojis).intersection(set(pie_emojis))
		emojis = shared_emojis if len(shared_emojis) > 0 else set(pie_emojis)
		emoji = max(emojis, key=pie_emojis.count) if len(emojis) > 0 else ''

		valid_english_translations = pie_to_english[pie]
		valid_pie_backtranslations = set(keys_to_values(english_to_pie, valid_english_translations))
		# remove similar words when formed from the same root
		valid_pie_backtranslations = set(valid 
			for valid in valid_pie_backtranslations 
			if not any(is_root_word_of(other, valid) for other in valid_pie_backtranslations)
		)

		# start with english->pie question to introduce concept gently, just as long as there are few synonyms to remember
		if pie not in self.back_translation_included and len(valid_pie_backtranslations) <= 2: 
			for synonym in valid_pie_backtranslations:
				self.back_translation_included.add(synonym)
			yield english_to_pie_card(emoji, 
				', '.join(valid_english_translations), 
				', '.join(valid_pie_backtranslations)
			)

		if pie not in self.forward_translation_included:
			self.forward_translation_included.add(pie)
			yield pie_to_english_card(emoji, 
				pie, 
				', '.join(valid_english_translations)
			)

		# if there are many synonyms, display them as review
		if pie not in self.back_translation_included and len(valid_pie_backtranslations) <= 4: 
			for synonym in valid_pie_backtranslations:
				self.back_translation_included.add(synonym)
			message = ''
			if len(valid_pie_backtranslations) > 2:
				message = "<div style='font-size:medium'>mark the answer correct if at least one word was remembered</div>"
			yield english_to_pie_card(emoji, 
				', '.join(valid_english_translations), 
				', '.join(valid_pie_backtranslations) + message
			)

keys_included = set()
deck_construction = DeckConstructionStateManagement()
for i, priority_key in enumerate(frequency_to_keys):
	# print(priority_key)
	priority_key = priority_key.lower()
	if priority_key not in keys_included:
		keys_included.add(priority_key)
		sequence = key_to_sequence[priority_key]
		for topic in sequence:
			keys = topic # the topic (e.g. "carrying") is defined by a set of keys (e.g. "carry", "carried", "carrying")
			for key in keys: keys_included.add(key)
			for pie in set(keys_to_values(key_to_pie, keys)):
				for card in deck_construction.cards(pie, keys):
					print(card)

#handle the remaining known pie words
for pie in pie_to_english:
	for card in deck_construction.cards(pie, keys):
		print(card)

