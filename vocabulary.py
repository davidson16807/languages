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

# returns a list of indexible strings 
# that represent synonyms within the same note
def get_word_keys(keytext):
	for key in keytext.split(','):
		key = key.strip().lower()
		key = re.sub('^to +', '', key)
		key = re.sub('\([^)]*\)', '', key)
		key = key.replace('...', '')
		yield key.strip()

def get_note(line):
	columns = [ column.strip() for column in line.split('\t', 2) ]
	emoji = columns[0] if len(columns) > 1 else ''
	keys = list(get_word_keys(columns[1])) if len(columns) > 1 else []
	text = columns[2] if len(columns) > 2 else columns[1] if len(columns) > 1 else columns[0]
	return emoji, keys, text

with open('english_to_learning_sequence.txt') as file:
	lines = [
		line 
		for line in file.readlines() 
		if not line.strip().startswith('#')
	]
	line_groups = split(lines, whitespace)
	line_groups = [
		[ get_note(line) for line in line_group ]
		for line_group in line_groups
	]
	word_to_sequence = {}
	for line_group in line_groups:
		for emoji, keys, text in line_group:
			# print(emoji, keys, text)
			for key in keys:
				if (key not in word_to_sequence or 
					len(word_to_sequence[key]) > len(line_group)):
					word_to_sequence[key] = line_group


with open('frequency_to_subtitle_english_ignored.txt') as file:
	words_omitted = { 
		line.strip().lower() 
		for line in file.readlines()
	}

with open('frequency_to_subtitle_english.txt') as file:
	lines = [
		line.strip().lower().split(' ', 2)[0]
		for line in file.readlines()
	]
	words_by_frequency = [
		inflection.singularize(line)
		for line in lines
		if line not in words_omitted
	]

words_completed = set()
for i, priority_word in enumerate(words_by_frequency):
	priority_word = priority_word.lower()
	if priority_word not in words_completed and i < 300:
		words_completed.add(priority_word)
		if priority_word not in word_to_sequence:
			print('', '\t', priority_word)
		else:
			for emoji, keys, text in word_to_sequence[priority_word]:
				# print(emoji, keys, text)
				# if not all(key in words_completed for key in keys):
				for key in keys: words_completed.add(key)
				print(emoji, '\t', text)

