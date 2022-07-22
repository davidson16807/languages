
import re

headers = {'moods', 'aspect', 'tenses', 'voices', 'persons', 'pluralities'}

nonfinites = {'infinitive', 'participle', 'gerund', 'supine'}
moods = {'indicative', 'interrogative', 
		 'subjunctive', 'conditional', 'hypothetical', 'potential', 
		 'optative', 'jussive', 'injunctive', 'suggestive', 'imperative'}
aspect = {'aortist', 'imperfect', 'perfect', 'perfect-progressive'}
tenses = {'present', 'past', 'future'}
voices = {'active', 'middle', 'passive'}
persons = {1,2,3}
pluralities = {'singular', 'dual', 'plural'}

def finite_forms(filename, header_rows, header_columns, delimeter='\t', padding=' \t\r\n'):
	cells = []
	with open(filename) as file:
		for line in range(header_rows):
			if not len(line.strip()) < 1:
				row = [column.strip(padding) for column in line.split(delimeter)]

		for line in file.readlines():
			if not line.strip().startswith('#') and not len(line.strip()) < 1:
				row = [column.strip(padding) for column in line.split(delimeter)]
				cell = row[column_id]
				for formatter in formatters:
					if cell is not None:
						cell = formatter(cell)
				cells.append(cell)
	return cells

finite_forms('proto-indo-european/finite-conjugations.tsv',
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



# english ↔ proto-indo-european
write('flashcards/english-and-proto-indo-european.html', [
	column('emoji.tsv', 3, cloze(1), emoji),
	column('indo-european-branches.tsv', 2, cloze(1), english_word), 
	column('indo-european-branches.tsv', 3, require, strip_asterisks, cloze(2), foreign_focus), 
])
