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
USAGE: python scrape_inflections.py <language-code> [output-directory]
	e.g. python scrape_inflections.py sv data/inflection/indo-european/germanic/swedish/modern

For every (part-of-speech, intent) pair in translations.tsv,
the first translation whose language code matches <language-code> is crawled,
and its inflection tables are written to "scraped-<language-code>-<part-of-speech>s.tsv".
Genders of nouns are also written to "scraped-<language-code>-genders.tsv".

The classes below are copied verbatim from scrape_special_inflections.py,
since importing that file would run every crawl that it contains.
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
	def __init__(self, parsing):
		self.parsing = parsing
	def crawl(self, lemma_url_text):
		result = []
		for lemma_url in self.parsing.tokenpoints(lemma_url_text):
			if len(lemma_url) == 2:
				(lemma, url) = lemma_url
				print('\t'.join([lemma, url]))
				time.sleep(1) # rate limit for kindness
				headers={'User-Agent': 
					'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
				}
				result.append((lemma, requests.get(url,headers=headers).text))
		return result

ops = RowMajorTableOps()
scraping = TableScraping(ops)
parsing = TokenParsing()
caching = Caching(parsing)
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

if len(sys.argv) < 3:
	print('USAGE: python scrape_inflections.py <language-code> [output-directory]')
	sys.exit(1)

target_language_code = sys.argv[1].strip()
output_directory = sys.argv[2]

# find the first available translation for each (part-of-speech, intent) pair
first_translations = collections.OrderedDict()
language_id_counts = collections.Counter()
with open('translations.tsv','r') as file:
	content = file.read()
	for row in content.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) == 9:
				_, part_of_speech, intent, lexeme, url, gloss, language_code, translation_url, translation = parameters
				if language_code == target_language_code:
					if '#' in translation_url:
						language_id_counts[translation_url.split('#')[-1]] += 1
					if (part_of_speech, intent) not in first_translations:
						first_translations[(part_of_speech, intent)] = translation_url

if not first_translations:
	print(f'no translations found for language code: {target_language_code}')
	sys.exit(1)

if not language_id_counts:
	print(f'no wiktionary language section could be determined for language code: {target_language_code}')
	sys.exit(1)

# the wiktionary section id (e.g. "Old_English") is the anchor that is most often used in translation urls
((language_id, _),) = language_id_counts.most_common(1)

lemma_urls_for_part_of_speech = collections.OrderedDict()
for ((part_of_speech, intent), translation_url) in first_translations.items():
	if part_of_speech not in lemma_urls_for_part_of_speech:
		lemma_urls_for_part_of_speech[part_of_speech] = []
	lemma_urls_for_part_of_speech[part_of_speech].append(f'{intent}\t{translation_url}')

os.makedirs(output_directory, exist_ok=True)

print(language_id.upper())
for (part_of_speech, lemma_urls) in lemma_urls_for_part_of_speech.items():

	(part_of_speech_text, table_texts) = section_texts_for_part_of_speech.get(
		part_of_speech, (part_of_speech.title(), ['Inflection']))

	table_count = table_count_for_language_code.get(target_language_code, {}).get(part_of_speech, 1)
	table_language_code = None if target_language_code in unmarked_language_codes else target_language_code

	lemma_html = caching.crawl('\n'.join(['', *lemma_urls, '']))

	if part_of_speech == 'noun':
		write(os.path.join(output_directory, f'scraped-genders.tsv'),
			formatting.format(
				scraping.scrape(GenderWikiHtml(ops, part_of_speech_text, language_id), lemma_html)
			)
		)

	write(os.path.join(output_directory, f'scraped-{part_of_speech}s.tsv'),
		formatting.format(
			scraping.scrape(
				GreekRowMajorWikiTableHtml(ops) if target_language_code == 'grc' else
				RowMajorWikiTableHtml(ops, part_of_speech_text, table_texts, language_id, table_language_code, table_count),
				lemma_html
			)
		)
	)
