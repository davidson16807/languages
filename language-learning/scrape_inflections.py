# HUMAN WRITTEN

# built-in libraries
import collections
import os
import requests
import sys
import time

# 3rd party libraries
from bs4 import BeautifulSoup

# in-house libraries
from tools.inflections import write
from tools.parsing import TokenParsing

'''
USAGE: python scrape_inflections.py <language-code> <output-directory>
	e.g. python scrape_inflections.py sv data/inflection/indo-european/germanic/swedish/modern

For every (part-of-speech, lemma) pair in translations.tsv,
translations whose language code matches <language-code> are crawled in order until one is found that has an inflection table,
and the tables of that translation are written to "scraped-<part-of-speech>s.tsv".
Genders of nouns are also written to "scraped-genders.tsv".
'''

class Uniform:
    def __init__(self, value):
        self.value = value
    def __iter__(self):
        return self
    def __next__(self):
        return self.value

class TableScraping:
	def __init__(self, ops):
		self.ops = ops
	def scrape(self, parsing, lemma_html):
		for (lemma, html) in lemma_html:
			soup = BeautifulSoup(html)
			bunched = self.ops.bunch(
				Uniform([lemma]), 
				parsing.parse(soup))
			# print a progress indicator since rate limiting slows us down considerably
			print('\t'.join(['    ' if bunched else 'FAIL', lemma]))
			for row in bunched:
				yield row

class RowMajorTableOps:
	def __init__(self):
		pass
	def stack(self, *tables):
		return [row
			for table in tables
			for row in table
		]
	def bunch(self, *tables):
		return [[cell 
				for row  in rows
				for cell in row]
			for rows in zip(*tables)]

class RowMajorTableText:
	def __init__(self, cellbreak=',', linebreak='\n'):
		self.cellbreak = cellbreak
		self.linebreak = linebreak
	def parse(self, table): 
		[[cell for cell in row.split(self.cellbreak)]
			for row in  table.split(self.linebreak)]
	def format(self, table): 
		for row in table:
			yield self.cellbreak.join([
				cell.replace(self.cellbreak, '').replace(self.linebreak, '') 
				for cell in row])

class RowMajorWikiTableHtml:
	def __init__(self, ops, part_of_speech_text, table_texts, language_id, language_code=None, table_count=1):
		self.ops = ops
		self.part_of_speech_text = part_of_speech_text
		self.table_texts = table_texts
		self.language_id = language_id
		self.language_code = language_code
		self.table_count = table_count
	def body(self, content): 
		def extract(source, extractions):
			remainder = source.text
			for extraction in extractions:
				remainder = remainder.replace(extraction.text, '')
			return [remainder, *[extraction.text for extraction in extractions]]
		def maxi(vectors, i):
			return max([0,*[vector[i]+1 for vector in vectors]])
		def span(attrs, span):
			return int(attrs[span]) if span in attrs and '%' not in attrs[span] else 1
		cells = {}
		for (y, row) in enumerate(content.select('tr')):
			x = 0
			for cell in row.select('td,th'):
				while (x,y,0) in cells: x+=1
				colspan = span(cell.attrs, 'colspan')
				rowspan = span(cell.attrs, 'rowspan')
				lines = (extract(cell, cell.select('span.tr')) if cell.name == 'td' else [cell.text.lower()])
				for dx in range(colspan):
					for dy in range(rowspan):
						for (z, line) in enumerate(lines):
							cells[(x+dx,y+dy,z)] = line
		lx = maxi(cells.keys(), 0)
		ly = maxi(cells.keys(), 1)
		lz = maxi(cells.keys(), 2)
		for y in range(ly):
			yield [(cells[(x,y,z)] if (x,y,z) in cells else '') 
				for x in range(lx)
				for z in range(lz)]
	def parse(self, soup):
		header = lambda level_id: [f'h{i}' for i in range(level_id,7)]
		language_section = soup.find(header(1), id=self.language_id)
		if language_section:
			level_id = int(language_section.name.replace('h',''))
			part_of_speech_section = language_section.find_next(header(level_id+1), text=self.part_of_speech_text)
			if part_of_speech_section:
				for section in part_of_speech_section.find_all_next(header(level_id+2), text=self.table_texts):
					for i in range(self.table_count):
						section2 = section.find_next('table')
						if not section2:
							break
						else:
							if not self.language_code or section2.select(f'span[lang="{self.language_code}"]'):
								for row in self.body(section2):
									yield row
								section = section2

class GreekRowMajorWikiTableHtml(RowMajorWikiTableHtml):
	def __init__(self, ops):
		self.ops = ops
	def dialect(self, head): 
		head = head
		dialect = head.select_one('.extiw')
		# if dialect:
		# 	return dialect.text.lower()
		return head.text or ''
	def parse(self, soup):
		for frame in soup.select('.NavFrame'):
			for row in self.ops.bunch(
					Uniform([self.dialect(frame.select_one('.NavHead'))]), 
					self.body(frame.select_one('.NavContent'))):
				yield row

class GenderWikiHtml:
	def __init__(self, ops, part_of_speech_text, language_id):
		self.ops = ops
		self.part_of_speech_text = part_of_speech_text
		self.language_id = language_id
	def parse(self, soup):
		header = lambda level_id: [f'h{i}' for i in range(level_id,7)]
		language_section = soup.find(header(1), id=self.language_id)
		if language_section:
			level_id = int(language_section.name.replace('h',''))
			part_of_speech_section = language_section.find_next(header(level_id+1), text=self.part_of_speech_text)
			if part_of_speech_section:
				gender_sections = language_section.find_all_next('span', class_='gender')
				if gender_sections:
					for gender in (gender_sections[0].text
										.replace('n','neuter')
										.replace('m','masculine')
										.replace('f','feminine')
										.split(' or ')):
						yield [gender]


class Caching:
	def __init__(self):
		pass
	def crawl(self, lemma_urls):
		result = {}
		for lemma, url in lemma_urls:
			try:
				print(f'{lemma}\t{url}')
				time.sleep(1) # rate limit for kindness
				headers={'User-Agent': 
					'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
				}
				result[url.split('#')[0]] = requests.get(url,headers=headers).text
			except Exception as ex:
				print(ex)
		return result

ops = RowMajorTableOps()
scraping = TableScraping(ops)
parsing = TokenParsing()
caching = Caching()
formatting = RowMajorTableText('\t','\n')

# HUMAN VETTED

# the wiktionary section headers that are searched for tables, by part of speech
section_texts_for_part_of_speech = {
	'noun':         ('Noun',         ['Declension','Inflection']),
	'verb':         ('Verb',         ['Conjugation','Inflection']),
	'adjective':    ('Adjective',    ['Declension','Inflection']),
	'determiner':   ('Determiner',   ['Declension','Inflection']),
	'article':      ('Article',      ['Declension','Inflection']),
	'pronoun':      ('Pronoun',      ['Declension','Inflection']),
	'adverb':       ('Adverb',       ['Inflection']),
	'conjunction':  ('Conjunction',  ['Inflection']),
	'interjection': ('Interjection', ['Inflection']),
}

# language specific settings, reproduced from the calls in scrape_special_inflections.py
table_count_for_language_code = {
	# Finnish, Georgian, Hungarian, and Quechua spread noun declensions across 2 tables
	'fi':  {'noun':2},
	'ka':  {'noun':2},
	'hu':  {'noun':2},
	'qu':  {'noun':2},
	'hit': {'noun':2, 'verb':2},
}
# languages whose tables do not mark their cells with a "lang" attribute
unmarked_language_codes = {'xtg', 'kw', 'ta', 'hit'}

class Translation:
	def __init__(self, part_of_speech, intent, lemma, gloss, language_code, url, language_id=None):
		self.part_of_speech = part_of_speech
		self.intent = intent
		self.lemma = lemma
		self.gloss = gloss
		self.language_code = language_code
		self.url = url
		self.language_id = None if language_id is None else language_id.split(':')[0] 

def parse_translations(text):
	translations = []
	for row in text.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) >= 8:
				_, part_of_speech, intent, lemma, word_url, gloss, language_code, translation_url = parameters[:8]
				translations.append(Translation(part_of_speech, intent, lemma, gloss, language_code, *translation_url.split('#')))
	return translations

translations = []

with open('translations.tsv','r') as file:
	translations += parse_translations(file.read())

with open('translation-specializations.tsv','r') as file:
	translations += parse_translations(file.read())

with open('translation-languages.tsv','r') as file:
	code_directories = [
		list(cell.strip() for cell in row.split('\t'))[1:]
		for row in file.read().split('\n')
		if row.strip() and not row.startswith('#')
	]

for target_language_code, output_directory in code_directories:

	cache_directory = os.path.join('cache', output_directory)
	scrape_directory = os.path.join('data', 'inflection', output_directory)

	language_translations = [translation 
		for translation in translations 
		if translation.language_code == target_language_code]

	count_for_language_id = collections.Counter([
		translation.language_id
		for translation in language_translations
		if translation.language_id
	])

	if not language_translations:
		print(f'no translations found for language code: "{target_language_code}"')
		sys.exit(1)

	if not count_for_language_id:
		print(f'no wiktionary language section could be determined for language code: "{target_language_code}"')
		sys.exit(1)

	# the wiktionary section id (e.g. "Old_English") is the anchor that is most often used in translation urls
	if len(count_for_language_id) != 1:
		print(f'more than one language id found for code "{target_language_code}": ' + 
			','.join([str(language_id) for language_id in count_for_language_id]))
		sys.exit(1)

	translations_for_part_of_speech_lemma = collections.defaultdict(list)
	for translation in language_translations:
		translations_for_part_of_speech_lemma[(translation.part_of_speech, translation.lemma)].append(translation)

	lemmas_for_part_of_speech = collections.defaultdict(list)
	for (part_of_speech, lemma) in translations_for_part_of_speech_lemma:
		lemmas_for_part_of_speech[part_of_speech].append(lemma)

	((language_id, _),) = count_for_language_id.most_common(1)

	os.makedirs(output_directory, exist_ok=True)

	html_for_url = caching.crawl({(translation.lemma, translation.url) for translation in language_translations})

	for part_of_speech, lemmas in lemmas_for_part_of_speech.items():
		part_of_speech_text, table_texts = section_texts_for_part_of_speech[part_of_speech]
		table_count = table_count_for_language_code.get(target_language_code, {}).get(part_of_speech, 1)
		table_parsing = (
			GreekRowMajorWikiTableHtml(ops) if target_language_code == 'grc' else
			RowMajorWikiTableHtml(ops, part_of_speech_text, table_texts, language_id, target_language_code, table_count))
		gender_parsing = GenderWikiHtml(ops, part_of_speech_text, language_id)
		lemma_html = [
			(lemma, html_for_url[url])
			for lemma in lemmas
			if (part_of_speech, lemma) in translations_for_part_of_speech_lemma
			for translation in translations_for_part_of_speech_lemma[(part_of_speech, lemma)]
			if (url:=translation.url.split('#')[0]) in html_for_url
		]

		if part_of_speech == 'noun':
			write(os.path.join(output_directory, f'scraped-genders.tsv'),
				formatting.format(
					scraping.scrape(gender_parsing, lemma_html)
				)
			)

		write(os.path.join(output_directory, f'scraped-{part_of_speech}s.tsv'),
			formatting.format(
				scraping.scrape(table_parsing, lemma_html)
			)
		)
