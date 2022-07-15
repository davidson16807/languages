
import re
# import sys

def column(filename, column_id, *formatters, delimeter='\t', padding=' \t\r\n'):
	cells = []
	with open(filename) as file:
		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				row = [column.strip(padding) for column in line.split(delimeter)]
				cell = row[column_id]
				for formatter in formatters:
					if cell is not None:
						cell = formatter(cell)
				cells.append(cell)
	return cells

def strip_asterisks(cell):
	return cell.replace('*','')

def inside_first_parens(cell):
	return ', '.join(
		re.search('[(][^)]*?[)]', segment).group(0).strip('()') + re.split('[(][^)]*?[)]', segment, 1)[1]
		for segment in cell.split(',')
		if re.search('[(][^)]*?[)]', segment)
	)

def outside_first_parens(cell):
	return ', '.join(
		re.sub('[(][^)]*?[)]', '', segment, 1).strip()
		for segment in cell.split(',')
	)

def add_ipa_markers(cell):
	return ', '.join(f'/{segment.strip()}/' for segment in cell.split(','))

def strip_ipa_markers(cell):
	return ', '.join(segment.replace('/','').strip() for segment in cell.split(','))

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



def sound_laws(tuples):
	def _sound_laws(text):
		modified = text
		for (regex, replacement) in tuples:
			modified = re.sub(regex, replacement, modified)
		return modified
	return _sound_laws


def write(filename, columns):
	with open(filename, 'w') as file:
		for row in zip(*columns):
			if all(cell is not None for cell in row):
				file.write(''.join(row)+'\n')



# english ↔ proto-indo-european
write('flashcards/english-and-proto-indo-european.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 3, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-indo-european → proto-germanic
write('flashcards/proto-indo-european-to-proto-germanic.html', [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-european-branches.tsv', 4, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-germanic
write('flashcards/english-and-proto-germanic.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 4, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-germanic → old english
write('flashcards/proto-germanic-to-old english.html', [
	column('germanic-languages.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('germanic-languages.tsv', 4, require, cloze(1), foreign_focus), 
])

# english ↔ old english
write('flashcards/english-and-old english.html', [
	column('emoji.tsv', 3, cloze(1), emoji), 
	column('germanic-languages.tsv', 2, cloze(1), english_word), 
	column('germanic-languages.tsv', 4, require, cloze(2), foreign_focus), 
	column('germanic-languages.tsv', 5, require, cloze(3), foreign_side_note), 
])

# proto-germanic → swedish
write('flashcards/proto-germanic-to-swedish.html', [
	column('germanic-languages.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('germanic-languages.tsv', 18, require, cloze(1), foreign_focus), 
])

# english ↔ swedish
write('flashcards/english-and-swedish.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('germanic-languages.tsv', 2, cloze(1), english_word), 
	column('germanic-languages.tsv', 18, require, cloze(2), foreign_focus), 
])

# proto-indo-european → proto-italic
write('flashcards/proto-indo-european-to-proto-italic.html', [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-european-branches.tsv', 5, require, strip_asterisks, cloze(1), foreign_side_note), 
])

# english ↔ proto-italic
write('flashcards/english-and-proto-italic.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 5, require, strip_asterisks, cloze(2), foreign_focus), 
])


# proto-italic → latin
write('flashcards/proto-italic-to-latin.html', [
	column('romance-languages.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('romance-languages.tsv', 4, require, cloze(1), foreign_focus), 
])

# proto-indo-european → latin
write('flashcards/proto-indo-european-to-latin.html', [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('romance-languages.tsv', 4, require, cloze(1), foreign_focus), 
])

# english ↔ latin
write('flashcards/english-and-latin.html', [
	column('emoji.tsv', 3, cloze(1), emoji), 
	column('romance-languages.tsv', 2, cloze(1), english_word), 
	column('romance-languages.tsv', 4, require, cloze(2), foreign_focus), 
	column('romance-languages.tsv', 5, require, cloze(3), foreign_side_note), 
])

# latin → vulgar latin
write('flashcards/latin-to-vulgar latin.html', [
	column('romance-languages.tsv', 4, require, foreign_focus), 
	column('romance-languages.tsv', 6, require, strip_asterisks, cloze(1), foreign_focus), 
])

# vulgar latin → spanish
write('flashcards/vulgar latin-to-spanish.html', [
	column('romance-languages.tsv', 6, require, strip_asterisks, foreign_focus), 
	column('romance-languages.tsv', 9, require, cloze(1), foreign_focus), 
])

# english ↔ spanish
write('flashcards/english-and-spanish.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('romance-languages.tsv', 2, cloze(1), english_word), 
	column('romance-languages.tsv', 9, require, cloze(2), foreign_focus), 
])

# vulgar latin → french
write('flashcards/vulgar latin-to-french.html', [
	column('romance-languages.tsv', 6, require, strip_asterisks, foreign_focus), 
	column('romance-languages.tsv', 7, require, cloze(1), foreign_focus), 
])

# english ↔ french
write('flashcards/english-and-french.html', [
	column('emoji.tsv', 3, cloze(1), emoji), 
	column('romance-languages.tsv', 2, cloze(1), english_word),
	column('romance-languages.tsv', 7, require, cloze(2), foreign_focus),
	column('romance-languages.tsv', 8, require, cloze(3), foreign_side_note),
])


# proto-indo-european → proto-hellenic
write('flashcards/proto-indo-european-to-proto-hellenic.html', [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-european-branches.tsv', 6, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-hellenic
write('flashcards/english-and-proto-hellenic.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 6, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-hellenic → ancient greek
write('flashcards/proto-hellenic-to-ancient greek.html', [
	column('hellenic-languages.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('hellenic-languages.tsv', 4, require, inside_first_parens, cloze(1), foreign_focus), 
])

# english ↔ ancient greek
write('flashcards/english-and-ancient greek.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('hellenic-languages.tsv', 2, cloze(1), english_word), 
	column('hellenic-languages.tsv', 4, require, outside_first_parens, cloze(2), foreign_focus), 
	column('hellenic-languages.tsv', 4, require, inside_first_parens, cloze(3), foreign_side_note), 
])


# proto-indo-european → proto-indo-iranian
write('flashcards/proto-indo-european-to-proto-indo-iranian.html', [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-european-branches.tsv', 7, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-indo-iranian
write('flashcards/english-and-proto-indo-iranian.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 7, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-indo-iranian → sanskrit
write('flashcards/proto-indo-iranian-to-sanskrit.html', [
	column('indo-iranian-languages.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-iranian-languages.tsv', 4, require, inside_first_parens, cloze(1), foreign_focus), 
])

# english ↔ sanskrit
write('flashcards/english-and-sanskrit.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-iranian-languages.tsv', 2, cloze(1), english_word), 
	column('indo-iranian-languages.tsv', 4, require, outside_first_parens, cloze(2), foreign_focus), 
	column('indo-iranian-languages.tsv', 4, require, inside_first_parens, cloze(3), foreign_side_note), 
])


# english ↔ vietnamese
write('flashcards/english-and-vietnamese.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('vietnamese.tsv', 2, cloze(1), english_word), 
	column('vietnamese.tsv', 3, require, cloze(2), foreign_focus), 
])

# english ↔ sumerian
write('flashcards/english-and-sumerian.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('sumerian.tsv', 2, cloze(1), english_word), 
	column('sumerian.tsv', 3, require, cloze(2), foreign_focus), 
])














'''
# proto-indo-european → proto-italic
columns = [
	column('indo-european-branches.tsv', 3, require, strip_asterisks, foreign_focus), 
	column('indo-european-branches.tsv', 3, require, strip_asterisks, 
		sound_laws([
			('\bbʰ','f'), 
			('\bdʰ','f'), 
			('\bgʰ','h'), 
			('\bgʷʰ','f'),
			('bʰ','b'), 
			('dʰ','d'), 
			('gʰ','g'), 
			('gʷʰ','v'),
			('(r[aeiou]*)dʰ','\\1b'),
			('([aeiou])s([aeiou])','\\1r\\2'),]), cloze(1), foreign_focus),
	column('romance-languages.tsv', 4, require, cloze(1), foreign_focus), 
]
'''
