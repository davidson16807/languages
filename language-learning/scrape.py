
# built-in libraries
import requests
import time

# 3rd party libraries
from bs4 import BeautifulSoup

# in-house libraries
from inflections import write
from tools.parsing import TokenParsing

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
				result.append((lemma, requests.get(url).text))
		return result

ops = RowMajorTableOps()
scraping = TableScraping(ops)
parsing = TokenParsing()
caching = Caching(parsing)
formatting = RowMajorTableText('\t','\n')

print('SWEDISH')
write('data/inflection/indo-european/germanic/swedish/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Swedish', 'sv'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/framtr%C3%A4da#Swedish
				be-inherently  https://en.wiktionary.org/wiki/vara#Swedish
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%C3%A4ndra#Swedish
				climb     https://en.wiktionary.org/wiki/kl%C3%A4ttra#Swedish
				crawl     
				cool      https://en.wiktionary.org/wiki/kyla#Swedish
				direct    https://en.wiktionary.org/wiki/leda#Swedish
				displease 
				eat       https://en.wiktionary.org/wiki/%C3%A4ta#Swedish
				endure    https://en.wiktionary.org/wiki/utst%C3%A5#Swedish
				fall      https://en.wiktionary.org/wiki/falla#Swedish
				fly       https://en.wiktionary.org/wiki/flyga#Swedish
				flow      
				hear      https://en.wiktionary.org/wiki/h%C3%B6ra#Swedish
				occupy    https://en.wiktionary.org/wiki/uppta#Swedish
				resemble  https://en.wiktionary.org/wiki/likna#Swedish
				rest      
				see       https://en.wiktionary.org/wiki/se#Swedish
				show      https://en.wiktionary.org/wiki/visa#Swedish
				startle   https://en.wiktionary.org/wiki/spritta#Swedish
				swim      https://en.wiktionary.org/wiki/simma#Swedish
				walk      https://en.wiktionary.org/wiki/g%C3%A5#Swedish
				warm      https://en.wiktionary.org/wiki/v%C3%A4rma#Swedish
				watch     https://en.wiktionary.org/wiki/se_p%C3%A5#Swedish
				work      https://en.wiktionary.org/wiki/arbeta#Swedish

				#go        https://en.wiktionary.org/wiki/g%C3%A5#Swedish # same as "walk"
                call      https://en.wiktionary.org/wiki/kalla#Swedish
                close     https://en.wiktionary.org/wiki/st%C3%A4nga#Swedish
                read      https://en.wiktionary.org/wiki/l%C3%A4sa#Swedish
                sew       https://en.wiktionary.org/wiki/sy#Swedish
                strike    https://en.wiktionary.org/wiki/stryka#Swedish
			''')
		)
	)
)

noun_html = caching.crawl('''
	animal    https://en.wiktionary.org/wiki/djur#Swedish
	attention https://en.wiktionary.org/wiki/uppm%C3%A4rksamhet#Swedish
	bird      https://en.wiktionary.org/wiki/f%C3%A5gel#Swedish
	boat      https://en.wiktionary.org/wiki/b%C3%A5t#Swedish
	book      https://en.wiktionary.org/wiki/bok#Swedish
	brother   https://en.wiktionary.org/wiki/bror#Swedish
	bug       https://en.wiktionary.org/wiki/kryp#Swedish
	clothing  https://en.wiktionary.org/wiki/kl%C3%A4der#Swedish
	daughter  https://en.wiktionary.org/wiki/dotter#Swedish
	dog       https://en.wiktionary.org/wiki/hund#Swedish
	door      https://en.wiktionary.org/wiki/d%C3%B6rr#Swedish
	drum      https://en.wiktionary.org/wiki/trumma#Swedish
	enemy     https://en.wiktionary.org/wiki/fiende#Swedish
	fire      https://en.wiktionary.org/wiki/eld#Swedish
	food      https://en.wiktionary.org/wiki/mat#Swedish
	gift      https://en.wiktionary.org/wiki/g%C3%A5va#Swedish
	glass     https://en.wiktionary.org/wiki/glas#Swedish
	guard     https://en.wiktionary.org/wiki/vakt#Swedish
	horse     https://en.wiktionary.org/wiki/h%C3%A4st#Swedish
	house     https://en.wiktionary.org/wiki/hus#Swedish
	livestock https://en.wiktionary.org/wiki/boskapsdjur#Swedish
	love      https://en.wiktionary.org/wiki/k%C3%A4rlek#Swedish
	idea      https://en.wiktionary.org/wiki/id%C3%A9#Swedish
	man       https://en.wiktionary.org/wiki/man#Swedish
	money     https://en.wiktionary.org/wiki/pengar#Swedish
	monster   https://en.wiktionary.org/wiki/odjur#Swedish
	name      https://en.wiktionary.org/wiki/namn#Swedish
	rock      https://en.wiktionary.org/wiki/sten#Swedish
	rope      https://en.wiktionary.org/wiki/rep#Swedish
	size      https://en.wiktionary.org/wiki/storlek#Swedish
	son       https://en.wiktionary.org/wiki/son#Swedish
	sound     https://en.wiktionary.org/wiki/ljud#Swedish
	warmth    https://en.wiktionary.org/wiki/v%C3%A4rme#Swedish
	water     https://en.wiktionary.org/wiki/vatten#Swedish
	way       https://en.wiktionary.org/wiki/v%C3%A4g#Swedish
	wind      https://en.wiktionary.org/wiki/vind#Swedish
	window    https://en.wiktionary.org/wiki/f%C3%B6nster#Swedish
	woman     https://en.wiktionary.org/wiki/kvinna#Swedish
	work      https://en.wiktionary.org/wiki/arbete#Swedish
''')

write('data/inflection/indo-european/germanic/swedish/modern/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Swedish'), noun_html)
	)
)

write('data/inflection/indo-european/germanic/swedish/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Swedish', 'sv'), 
			noun_html
		)
	)
)

raise 'done'

write('data/inflection/indo-european/greek/attic/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(
			GreekRowMajorWikiTableHtml(ops),
			# RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Ancient_Greek', 'grc', table_count=9), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%CE%B5%E1%BC%B4%CE%B4%CE%BF%CE%BC%CE%B1%CE%B9#Ancient_Greek
				be-inherently  https://en.wiktionary.org/wiki/%CE%B5%E1%BC%B0%CE%BC%CE%AF#Ancient_Greek
				be-momentarily
				change    https://en.wiktionary.org/wiki/%E1%BC%80%CE%BB%CE%BB%CE%AC%CF%83%CF%83%CF%89#Ancient_Greek
				crawl     https://en.wiktionary.org/wiki/%E1%BC%95%CF%81%CF%80%CF%89#Ancient_Greek
				cool      
				direct    https://en.wiktionary.org/wiki/%E1%BC%84%CE%B3%CF%89#Ancient_Greek
				displease https://en.wiktionary.org/wiki/%E1%BC%80%CF%80%CE%B1%CF%81%CE%AD%CF%83%CE%BA%CF%89#Ancient_Greek
				eat       https://en.wiktionary.org/wiki/%E1%BC%94%CE%B4%CF%89#Ancient_Greek
				endure    https://en.wiktionary.org/wiki/%E1%BD%91%CF%80%CE%BF%CE%BC%CE%AD%CE%BD%CF%89#Ancient_Greek
				fall      https://en.wiktionary.org/wiki/%CF%80%CE%AF%CF%80%CF%84%CF%89#Ancient_Greek
				fly       https://en.wiktionary.org/wiki/%CF%80%CE%AD%CF%84%CE%BF%CE%BC%CE%B1%CE%B9#Ancient_Greek
				flow      https://en.wiktionary.org/wiki/%E1%BF%A5%CE%AD%CF%89#Ancient_Greek
				hear      
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/%CE%B2%CE%BB%CE%AD%CF%80%CF%89#Ancient_Greek
				show      https://en.wiktionary.org/wiki/%CE%B4%CE%B5%CE%AF%CE%BA%CE%BD%CF%85%CE%BC%CE%B9#Ancient_Greek
				startle   https://en.wiktionary.org/wiki/%CF%86%CE%BF%CE%B2%CE%AD%CF%89#Ancient_Greek # "terrify"
				swim      https://en.wiktionary.org/wiki/%CE%BD%CE%AD%CF%89#Ancient_Greek
				walk      https://en.wiktionary.org/wiki/%CF%80%CE%B1%CF%84%CE%AD%CF%89#Ancient_Greek
				warm      https://en.wiktionary.org/wiki/%CE%B8%CE%AC%CE%BB%CF%80%CF%89#Ancient_Greek
				watch     https://en.wiktionary.org/wiki/%CF%83%CE%BA%CE%BF%CF%80%CE%AD%CF%89#Ancient_Greek
				work      https://en.wiktionary.org/wiki/%E1%BC%90%CF%81%CE%B3%CE%AC%CE%B6%CE%BF%CE%BC%CE%B1%CE%B9#Ancient_Greek

				go        https://en.wiktionary.org/wiki/%CE%B5%E1%BC%B6%CE%BC%CE%B9#Ancient_Greek
				release   https://en.wiktionary.org/wiki/%CE%BB%CF%8D%CF%89#Ancient_Greek
			''')
		)
	)
)

noun_html = caching.crawl('''
	animal    https://en.wiktionary.org/wiki/%CE%B6%E1%BF%B7%CE%BF%CE%BD#Ancient_Greek
	attention https://en.wiktionary.org/wiki/%CF%86%CF%81%CE%BF%CE%BD%CF%84%CE%AF%CF%82#Ancient_Greek
	bird      https://en.wiktionary.org/wiki/%E1%BD%84%CF%81%CE%BD%CE%B9%CF%82#Ancient_Greek
	boat      https://en.wiktionary.org/wiki/%CE%BD%CE%B1%E1%BF%A6%CF%82#Ancient_Greek
	book      https://en.wiktionary.org/wiki/%CE%B2%CE%B9%CE%B2%CE%BB%CE%AF%CE%BF%CE%BD#Ancient_Greek
	brother   https://en.wiktionary.org/wiki/%E1%BC%80%CE%B4%CE%B5%CE%BB%CF%86%CF%8C%CF%82#Ancient_Greek
	bug       https://en.wiktionary.org/wiki/%E1%BC%94%CE%BD%CF%84%CE%BF%CE%BC%CE%BF%CE%BD#Ancient_Greek
	dog       https://en.wiktionary.org/wiki/%CE%BA%CF%8D%CF%89%CE%BD#Ancient_Greek
	door      https://en.wiktionary.org/wiki/%CE%B8%CF%8D%CF%81%CE%B1#Ancient_Greek
	clothing  https://en.wiktionary.org/wiki/%E1%BC%90%CF%83%CE%B8%CE%AE%CF%82#Ancient_Greek
	daughter  https://en.wiktionary.org/wiki/%CE%B8%CF%85%CE%B3%CE%AC%CF%84%CE%B7%CF%81#Ancient_Greek
	drum      https://en.wiktionary.org/wiki/%CF%84%CF%8D%CE%BC%CF%80%CE%B1%CE%BD%CE%BF%CE%BD#Ancient_Greek
	enemy     https://en.wiktionary.org/wiki/%E1%BC%90%CF%87%CE%B8%CF%81%CF%8C%CF%82#Ancient_Greek
	fire      https://en.wiktionary.org/wiki/%CF%80%E1%BF%A6%CF%81#Ancient_Greek
	food      https://en.wiktionary.org/wiki/%CE%B2%CF%81%E1%BF%B6%CE%BC%CE%B1#Ancient_Greek
	food      https://en.wiktionary.org/wiki/%CE%B5%E1%BC%B6%CE%B4%CE%B1%CF%81#Ancient_Greek
	gift      https://en.wiktionary.org/wiki/%CE%B4%E1%BF%B6%CF%81%CE%BF%CE%BD#Ancient_Greek
	glass     https://en.wiktionary.org/wiki/%E1%BD%95%CE%B1%CE%BB%CE%BF%CF%82#Ancient_Greek
	guard     https://en.wiktionary.org/wiki/%CF%84%CE%B7%CF%81%CF%8C%CF%82#Ancient_Greek
	horse     https://en.wiktionary.org/wiki/%E1%BC%B5%CF%80%CF%80%CE%BF%CF%82#Ancient_Greek
	house     https://en.wiktionary.org/wiki/%CE%BF%E1%BC%B6%CE%BA%CE%BF%CF%82#Ancient_Greek
	livestock https://en.wiktionary.org/wiki/%CE%BA%CF%84%E1%BF%86%CE%BD%CE%BF%CF%82#Ancient_Greek
	love      https://en.wiktionary.org/wiki/%CF%86%CE%B9%CE%BB%CE%AF%CE%B1#Ancient_Greek
	idea      https://en.wiktionary.org/wiki/%E1%BC%B0%CE%B4%CE%AD%CE%B1#Ancient_Greek
	man       https://en.wiktionary.org/wiki/%E1%BC%80%CE%BD%CE%AE%CF%81#Ancient_Greek
	money     https://en.wiktionary.org/wiki/%CE%BA%CE%AD%CF%81%CE%BC%CE%B1#Ancient_Greek
	monster   https://en.wiktionary.org/wiki/%CF%84%CE%AD%CF%81%CE%B1%CF%82#Ancient_Greek
	name      https://en.wiktionary.org/wiki/%E1%BD%84%CE%BD%CE%BF%CE%BC%CE%B1#Ancient_Greek
	rock      https://en.wiktionary.org/wiki/%CE%BB%CE%AF%CE%B8%CE%BF%CF%82#Ancient_Greek
	rope      https://en.wiktionary.org/wiki/%CF%83%CE%B5%CE%B9%CF%81%CE%AC#Ancient_Greek
	size      https://en.wiktionary.org/wiki/%CE%BC%CE%AD%CE%B3%CE%B5%CE%B8%CE%BF%CF%82#Ancient_Greek
	sister    https://en.wiktionary.org/wiki/%E1%BC%80%CE%B4%CE%B5%CE%BB%CF%86%CE%AE#Ancient_Greek
	son       https://en.wiktionary.org/wiki/%CF%85%E1%BC%B1%CF%8C%CF%82#Ancient_Greek
	sound     https://en.wiktionary.org/wiki/%E1%BC%A6%CF%87%CE%BF%CF%82#Ancient_Greek
	warmth    https://en.wiktionary.org/wiki/%CE%B8%CE%AD%CF%81%CE%BC%CE%B7#Ancient_Greek
	water     https://en.wiktionary.org/wiki/%E1%BD%95%CE%B4%CF%89%CF%81#Ancient_Greek
	way       https://en.wiktionary.org/wiki/%CE%BA%CE%AD%CE%BB%CE%B5%CF%85%CE%B8%CE%BF%CF%82#Ancient_Greek
	wind      https://en.wiktionary.org/wiki/%E1%BC%84%CE%BD%CE%B5%CE%BC%CE%BF%CF%82#Ancient_Greek
	window    https://en.wiktionary.org/wiki/%CE%B8%CF%85%CF%81%CE%AF%CF%82#Ancient_Greek
	woman     https://en.wiktionary.org/wiki/%CE%B3%CF%85%CE%BD%CE%AE#Ancient_Greek
	work      https://en.wiktionary.org/wiki/%E1%BC%94%CF%81%CE%B3%CE%BF%CE%BD#Ancient_Greek

	young-man https://en.wiktionary.org/wiki/%E1%BC%94%CF%81%CE%B3%CE%BF%CE%BD#Ancient_Greek
	soldier   https://en.wiktionary.org/wiki/%CE%BD%CE%B5%CE%B1%CE%BD%CE%AF%CE%B1%CF%82
	polity    https://en.wiktionary.org/wiki/%CF%83%CF%84%CF%81%CE%B1%CF%84%CE%B9%CF%8E%CF%84%CE%B7%CF%82
	village   https://en.wiktionary.org/wiki/%CF%80%CE%BF%CE%BB%CE%B9%CF%84%CE%B5%CE%AF%CE%B1
	person    https://en.wiktionary.org/wiki/%CE%BA%CF%8E%CE%BC%CE%B7
	street    https://en.wiktionary.org/wiki/%E1%BC%84%CE%BD%CE%B8%CF%81%CF%89%CF%80%CE%BF%CF%82
	circumnavigation https://en.wiktionary.org/wiki/%E1%BD%81%CE%B4%CF%8C%CF%82
	bone      https://en.wiktionary.org/wiki/%CF%80%CE%B5%CF%81%CE%AF%CF%80%CE%BB%CE%BF%CF%85%CF%82
	hero      https://en.wiktionary.org/wiki/%E1%BD%80%CF%83%CF%84%CE%BF%E1%BF%A6%CE%BD
	fish      https://en.wiktionary.org/wiki/%E1%BC%A5%CF%81%CF%89%CF%82
	oak       https://en.wiktionary.org/wiki/%E1%BC%B0%CF%87%CE%B8%CF%8D%CF%82
	city      https://en.wiktionary.org/wiki/%CE%B4%CF%81%E1%BF%A6%CF%82
	axe       https://en.wiktionary.org/wiki/%CF%80%CF%8C%CE%BB%CE%B9%CF%82
	town      https://en.wiktionary.org/wiki/%CF%80%CE%AD%CE%BB%CE%B5%CE%BA%CF%85%CF%82
	master    https://en.wiktionary.org/wiki/%E1%BC%84%CF%83%CF%84%CF%85
	old-woman https://en.wiktionary.org/wiki/%CE%B2%CE%B1%CF%83%CE%B9%CE%BB%CE%B5%CF%8D%CF%82
	cow       https://en.wiktionary.org/wiki/%CE%B3%CF%81%CE%B1%E1%BF%A6%CF%82
	echo      https://en.wiktionary.org/wiki/%CE%B2%CE%BF%E1%BF%A6%CF%82
	Clio      https://en.wiktionary.org/wiki/%E1%BC%A0%CF%87%CF%8E
	crow      https://en.wiktionary.org/wiki/%CE%9A%CE%BB%CE%B5%CE%B9%CF%8E
	vulture   https://en.wiktionary.org/wiki/%CE%BA%CF%8C%CF%81%CE%B1%CE%BE
	rug       https://en.wiktionary.org/wiki/%CE%B3%CF%8D%CF%88
	giant     https://en.wiktionary.org/wiki/%CF%84%CE%AC%CF%80%CE%B7%CF%82
	tooth     https://en.wiktionary.org/wiki/%CE%B3%CE%AF%CE%B3%CE%B1%CF%82
	old-man   https://en.wiktionary.org/wiki/%E1%BD%80%CE%B4%CE%BF%CF%8D%CF%82
	property  https://en.wiktionary.org/wiki/%CE%B3%CE%AD%CF%81%CF%89%CE%BD
	Greek     https://en.wiktionary.org/wiki/%CE%BA%CF%84%E1%BF%86%CE%BC%CE%B1
	winter    https://en.wiktionary.org/wiki/%E1%BC%9D%CE%BB%CE%BB%CE%B7%CE%BD
	Titan     https://en.wiktionary.org/wiki/%CF%87%CE%B5%CE%B9%CE%BC%CF%8E%CE%BD
	light-ray https://en.wiktionary.org/wiki/%CE%A4%CE%B9%CF%84%CE%AC%CE%BD
	shepherd  https://en.wiktionary.org/wiki/%E1%BC%80%CE%BA%CF%84%CE%AF%CF%82
	guide     https://en.wiktionary.org/wiki/%CF%80%CE%BF%CE%B9%CE%BC%CE%AE%CE%BD
	neighbor  https://en.wiktionary.org/wiki/%E1%BC%A1%CE%B3%CE%B5%CE%BC%CF%8E%CE%BD
	ichor     https://en.wiktionary.org/wiki/%CE%B3%CE%B5%CE%AF%CF%84%CF%89%CE%BD
	chaff     https://en.wiktionary.org/wiki/%E1%BC%B0%CF%87%CF%8E%CF%81
	orator    https://en.wiktionary.org/wiki/%E1%BC%80%CE%B8%CE%AE%CF%81
	father    https://en.wiktionary.org/wiki/%E1%BF%A5%CE%AE%CF%84%CF%89%CF%81
	Demeter   https://en.wiktionary.org/wiki/%CF%80%CE%B1%CF%84%CE%AE%CF%81
	Socrates  https://en.wiktionary.org/wiki/%CE%94%CE%B7%CE%BC%CE%AE%CF%84%CE%B7%CF%81
	Pericles  https://en.wiktionary.org/wiki/%CE%A3%CF%89%CE%BA%CF%81%CE%AC%CF%84%CE%B7%CF%82
	arrow     https://en.wiktionary.org/wiki/%CE%A0%CE%B5%CF%81%CE%B9%CE%BA%CE%BB%E1%BF%86%CF%82
    foundationhttps://en.wiktionary.org/wiki/%CE%B2%CE%AD%CE%BB%CE%BF%CF%82
    shame      https://en.wiktionary.org/wiki/%E1%BC%94%CE%B4%CE%B1%CF%86%CE%BF%CF%82#Ancient_Greek
    Ares      https://en.wiktionary.org/wiki/%CE%B1%E1%BC%B0%CE%B4%CF%8E%CF%82#Ancient_Greek
    Thales    https://en.wiktionary.org/wiki/%E1%BC%8C%CF%81%CE%B7%CF%82
    Oedipus   https://en.wiktionary.org/wiki/%CE%98%CE%B1%CE%BB%E1%BF%86%CF%82
    Apollo    https://en.wiktionary.org/wiki/%CE%9F%E1%BC%B0%CE%B4%CE%AF%CF%80%CE%BF%CF%85%CF%82
    knee      https://en.wiktionary.org/wiki/%E1%BC%88%CF%80%CF%8C%CE%BB%CE%BB%CF%89%CE%BD
    wood      https://en.wiktionary.org/wiki/%CE%B3%CF%8C%CE%BD%CF%85
    Zeus      https://en.wiktionary.org/wiki/%CE%B4%CF%8C%CF%81%CF%85
    liver     https://en.wiktionary.org/wiki/%CE%96%CE%B5%CF%8D%CF%82
    ship      https://en.wiktionary.org/wiki/%E1%BC%A7%CF%80%CE%B1%CF%81
    ear       https://en.wiktionary.org/wiki/%CE%BD%CE%B1%E1%BF%A6%CF%82
    hand      https://en.wiktionary.org/wiki/%CE%BF%E1%BD%96%CF%82
''')

print('GREEK/ANCIENT')
write('data/inflection/indo-european/greek/attic/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Ancient_Greek'), noun_html)
	)
)

print('GREEK/ANCIENT')
write('data/inflection/indo-european/greek/attic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(GreekRowMajorWikiTableHtml(ops), noun_html)
	)
)


noun_html = caching.crawl('''
	animal    https://en.wiktionary.org/wiki/animal#Latin
	attention https://en.wiktionary.org/wiki/attentio#Latin
	bird      https://en.wiktionary.org/wiki/avis#Latin
	boat      https://en.wiktionary.org/wiki/navis#Latin
	book      https://en.wiktionary.org/wiki/caudex#Latin
	brother   https://en.wiktionary.org/wiki/frater#Latin
	bug       https://en.wiktionary.org/wiki/cimex#Latin
	clothing  https://en.wiktionary.org/wiki/vestis#Latin
	daughter  https://en.wiktionary.org/wiki/filia#Latin
	dog       https://en.wiktionary.org/wiki/canis#Latin
	door      https://en.wiktionary.org/wiki/foris#Latin
	drum      https://en.wiktionary.org/wiki/tympanum#Latin
	enemy     https://en.wiktionary.org/wiki/inimicus#Latin
	fire      https://en.wiktionary.org/wiki/ignis#Latin
	food      https://en.wiktionary.org/wiki/cibus#Latin
	gift      https://en.wiktionary.org/wiki/donum#Latin
	glass     https://en.wiktionary.org/wiki/vitrum#Latin
	guard     https://en.wiktionary.org/wiki/custos#Latin
	horse     https://en.wiktionary.org/wiki/equus#Latin
	house     https://en.wiktionary.org/wiki/domus#Latin
	livestock https://en.wiktionary.org/wiki/pecus#Latin
	love      https://en.wiktionary.org/wiki/caritas#Latin
	idea      https://en.wiktionary.org/wiki/idea#Latin
	man       https://en.wiktionary.org/wiki/homo#Latin
	money     https://en.wiktionary.org/wiki/pecunia#Latin
	monster   https://en.wiktionary.org/wiki/belua#Latin
	name      https://en.wiktionary.org/wiki/saxum#Latin
	rock      https://en.wiktionary.org/wiki/saxum#Latin
	rope      https://en.wiktionary.org/wiki/restis#Latin
	size      https://en.wiktionary.org/wiki/magnitudo#Latin
	sister    https://en.wiktionary.org/wiki/soror#Latin
	son       https://en.wiktionary.org/wiki/filius#Latin
	sound     https://en.wiktionary.org/wiki/sonus#Latin
	warmth    https://en.wiktionary.org/wiki/calor#Latin
	water     https://en.wiktionary.org/wiki/aqua#Latin
	way       https://en.wiktionary.org/wiki/via#Latin
	wind      https://en.wiktionary.org/wiki/ventus#Latin
	window    https://en.wiktionary.org/wiki/fenestra#Latin
	woman     https://en.wiktionary.org/wiki/femina#Latin
	work      https://en.wiktionary.org/wiki/labor#Latin

	day       https://en.wiktionary.org/wiki/dies#Latin
	hand      https://en.wiktionary.org/wiki/manus#Latin
	night     https://en.wiktionary.org/wiki/nox#Latin
	thing     https://en.wiktionary.org/wiki/res#Latin
	war       https://en.wiktionary.org/wiki/bellum#Latin
	air       https://en.wiktionary.org/wiki/aero#Latin
	boy       https://en.wiktionary.org/wiki/puer#Latin
	star      https://en.wiktionary.org/wiki/stella#Latin
	tower     https://en.wiktionary.org/wiki/turris
	horn      https://en.wiktionary.org/wiki/cornu#Latin
	sailor    https://en.wiktionary.org/wiki/nauta#Latin
	foundation https://en.wiktionary.org/wiki/basis#Latin
	echo      https://en.wiktionary.org/wiki/echo#Latin
	phenomenon https://en.wiktionary.org/wiki/phaenomenon#Latin
	vine      https://en.wiktionary.org/wiki/ampelos#Latin
	myth      https://en.wiktionary.org/wiki/mythos#Latin
	atom      https://en.wiktionary.org/wiki/atomus#Latin
	nymph     https://en.wiktionary.org/wiki/nymphe#Latin
	comet     https://en.wiktionary.org/wiki/cometes#Latin
''')

print('LATIN')
write('data/inflection/indo-european/romance/latin/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Latin'), noun_html)
	)
)

print('LATIN')
write('data/inflection/indo-european/romance/latin/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Latin', 'la'), 
			noun_html
		)
	)
)

write('data/inflection/indo-european/romance/latin/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Latin', 'la'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/appareo#Latin
				be-inherently  https://en.wiktionary.org/wiki/sum#Latin
				be-momentarily https://en.wiktionary.org/wiki/sum#Latin
				change    https://en.wiktionary.org/wiki/cambio#Latin
				climb     https://en.wiktionary.org/wiki/ascendo#Latin
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/duco#Latin
				displease https://en.wiktionary.org/wiki/displiceo#Latin
				eat       https://en.wiktionary.org/wiki/edo#Latin
				endure    https://en.wiktionary.org/wiki/perpetior#Latin
				fall      https://en.wiktionary.org/wiki/cado#Latin
				fly       https://en.wiktionary.org/wiki/volo#Latin
				flow      
				hear      https://en.wiktionary.org/wiki/audio#Latin
				occupy    
				resemble  https://en.wiktionary.org/wiki/similo#Latin
				rest      https://en.wiktionary.org/wiki/requiesco#Latin
				see       https://en.wiktionary.org/wiki/video#Latin
				show      https://en.wiktionary.org/wiki/monstro#Latin
				startle   https://en.wiktionary.org/wiki/pavefacio#Latin
				swim      https://en.wiktionary.org/wiki/nato#Latin
				walk      https://en.wiktionary.org/wiki/ambulo#Latin
				warm      https://en.wiktionary.org/wiki/calefacio#Latin
				watch     https://en.wiktionary.org/wiki/specto#Latin
				work      https://en.wiktionary.org/wiki/laboro#Latin

				be        https://en.wiktionary.org/wiki/sum#Latin
				be-able   https://en.wiktionary.org/wiki/possum#Latin
				want      https://en.wiktionary.org/wiki/volo#Latin
				become    https://en.wiktionary.org/wiki/fio#Latin
				go        https://en.wiktionary.org/wiki/eo#Latin
				carry     https://en.wiktionary.org/wiki/fero#Latin
				love      https://en.wiktionary.org/wiki/amo#Latin
				advise    https://en.wiktionary.org/wiki/moneo#Latin
				capture   https://en.wiktionary.org/wiki/capio#Latin
				figure    https://en.wiktionary.org/wiki/puto#Latin
			''')
		)
	)
)

noun_html = caching.crawl('''
	animal    # oxsus
	attention # ueliia
	bird      # etnos
	boat      # nawa
	book      # libros
	brother   # 
	bug       https://en.wiktionary.org/wiki/bekos#Gaulish # "bee"
	clothing  # karakalla "tunic"
	daughter  https://en.wiktionary.org/wiki/duxtir#Gaulish
	dog       # cu
	door      # dworon
	drum      # tanaros
	enemy     https://en.wiktionary.org/wiki/Reconstruction:Gaulish/namants
	fire      # aidus
	food      # depron
	gift      # danus
	glass     # lagos
	guard     # soliduryos
	horse     https://en.wiktionary.org/wiki/markos#Gaulish
	house     # tegia
	livestock https://en.wiktionary.org/wiki/taruos#Gaulish # "domestic horned beast"
	love      # serka
	idea      # britus
	man       # uiros
	money     # sutegon
	monster   # angos
	name      # anuan
	rock      https://en.wiktionary.org/wiki/artua#Gaulish
	rope      # soka
	size      # manti
	son       https://en.wiktionary.org/wiki/mapos#Gaulish
	sound     # bruxtus
	warmth    # tessis
	water     # dubron
	way       # mantle
	wind      # auelos
	window    # iagos
	woman     https://en.wiktionary.org/wiki/bena#Gaulish
	work      # uergon

''')

print('GAULISH')
write('data/inflection/indo-european/celtic/gaulish/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Gaulish'), noun_html)
	)
)

print('GAULISH')
write('data/inflection/indo-european/celtic/gaulish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Gaulish'), 
			noun_html
		)
	)
)

# write('data/inflection/indo-european/celtic/gaulish/scraped-verbs.tsv',
# 	formatting.format(
# 		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Gaulish'), 
# 			caching.crawl('''
# 				appear    
# 				be-inherently  # essi
# 				be-momentarily # essi
# 				change    # cambī-t
# 				climb     # dreng-et
# 				crawl     
# 				cool      
# 				direct    # reg-et "conduct"
# 				displease 
# 				eat       # esset
# 				endure    # pass-et
# 				fall      # cedet
# 				fly       # etet
# 				flow      
# 				hear      
# 				occupy    # atrebā-t
# 				resemble  
# 				rest      
# 				see       # appiseto
# 				show      # deicet
# 				startle   
# 				swim      # snat
# 				walk      # cerd-et
# 				warm      # taiet
# 				watch     # uiliet
# 				work      # ureget
# 			''')
# 		)
# 	)
# )

noun_html = caching.crawl('''
	animal    https://en.wiktionary.org/wiki/nieten#Old_English
	attention https://en.wiktionary.org/wiki/ge%C3%BEoht#Old_English
	bird      https://en.wiktionary.org/wiki/fugol#Old_English
	boat      https://en.wiktionary.org/wiki/bat#Old_English
	book      https://en.wiktionary.org/wiki/boc#Old_English
	brother   https://en.wiktionary.org/wiki/bro%C3%BEor#Old_English
	bug       https://en.wiktionary.org/wiki/budda#Old_English
	clothing  https://en.wiktionary.org/wiki/scrud#Old_English
	daughter  https://en.wiktionary.org/wiki/dohtor#Old_English
	dog       https://en.wiktionary.org/wiki/hund#Old_English
	door      https://en.wiktionary.org/wiki/duru#Old_English
	drum      
	enemy     https://en.wiktionary.org/wiki/feond#Old_English
	fire      https://en.wiktionary.org/wiki/fyr#Old_English
	food      https://en.wiktionary.org/wiki/foda#Old_English
	gift      https://en.wiktionary.org/wiki/giefu#Old_English
	glass     https://en.wiktionary.org/wiki/gl%C3%A6s#Old_English
	guard     https://en.wiktionary.org/wiki/weard#Old_English
	horse     https://en.wiktionary.org/wiki/hors#Old_English
	house     https://en.wiktionary.org/wiki/hus#Old_English
	livestock https://en.wiktionary.org/wiki/feoh#Old_English
	love      https://en.wiktionary.org/wiki/lufu#Old_English
	idea      https://en.wiktionary.org/wiki/ge%C3%BEoht#Old_English
	man       https://en.wiktionary.org/wiki/mann#Old_English
	money     https://en.wiktionary.org/wiki/feoh#Old_English
	monster   https://en.wiktionary.org/wiki/%C3%BEyrs#Old_English
	name      https://en.wiktionary.org/wiki/nama#Old_English
	rock      https://en.wiktionary.org/wiki/Reconstruction:Old_English/rocc
	rope      https://en.wiktionary.org/wiki/rap#Old_English
	size      https://en.wiktionary.org/wiki/micelnes#Old_English
	son       https://en.wiktionary.org/wiki/sunu#Old_English
	sound     https://en.wiktionary.org/wiki/sweg#Old_English
	warmth    https://en.wiktionary.org/wiki/h%C3%A6tu#Old_English
	water     https://en.wiktionary.org/wiki/w%C3%A6ter#Old_English
	way       https://en.wiktionary.org/wiki/weg#Old_English
	wind      https://en.wiktionary.org/wiki/wind#Old_English
	window    https://en.wiktionary.org/wiki/eagduru#Old_English
	woman     https://en.wiktionary.org/wiki/cwene#Old_English
	work      https://en.wiktionary.org/wiki/weorc#Old_English

	light     https://en.wiktionary.org/wiki/scip#Old_English
	raid      https://en.wiktionary.org/wiki/rad#Old_English
	moon      https://en.wiktionary.org/wiki/mona#Old_English
	sun       https://en.wiktionary.org/wiki/sunne#Old_English
	eye       https://en.wiktionary.org/wiki/eage#Old_English
	time      https://en.wiktionary.org/wiki/tid#Old_English
	English   https://en.wiktionary.org/wiki/Engle#Old_English
	hand      https://en.wiktionary.org/wiki/hand#Old_English
	person    https://en.wiktionary.org/wiki/mann#Old_English
	nut       https://en.wiktionary.org/wiki/hnutu#Old_English
	goose     https://en.wiktionary.org/wiki/gos#Old_English
	friend    https://en.wiktionary.org/wiki/freond#Old_English
	bystander https://en.wiktionary.org/wiki/ymbstandend#Old_English
	father    https://en.wiktionary.org/wiki/f%C3%A6der#Old_English
	mother    https://en.wiktionary.org/wiki/modor#Old_English
	brother   https://en.wiktionary.org/wiki/bro%C3%BEor#Old_English
	sister    https://en.wiktionary.org/wiki/sweostor#Old_English
	lamb      https://en.wiktionary.org/wiki/lamb#Old_English
	shoe      https://en.wiktionary.org/wiki/scoh#Old_English
	piglet    https://en.wiktionary.org/wiki/fearh#Old_English
	shadow    https://en.wiktionary.org/wiki/sceadu#Old_English
	meadow    https://en.wiktionary.org/wiki/m%C3%A6d#Old_English
''')

print('ENGLISH/OLD')
write('data/inflection/indo-european/germanic/english/old/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Old_English'), noun_html)
	)
)

write('data/inflection/indo-european/germanic/english/old/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Old_English', 'ang'), 
			noun_html)
	)
)

write('data/inflection/indo-european/germanic/english/old/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Old_English', 'ang'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%C3%A6tiewan#Old_English
				be-inherently  https://en.wiktionary.org/wiki/wesan#Old_English
				be-momentarily https://en.wiktionary.org/wiki/beon#Old_English
				change    https://en.wiktionary.org/wiki/wendan#Old_English
				climb     https://en.wiktionary.org/wiki/climban#Old_English
				crawl     
				cool      https://en.wiktionary.org/wiki/colian#Old_English
				direct    https://en.wiktionary.org/wiki/lead#Old_English
				displease https://en.wiktionary.org/wiki/drefan#Old_English
				eat       https://en.wiktionary.org/wiki/etan#Old_English
				endure    https://en.wiktionary.org/wiki/adreogan#Old_English
				fall      https://en.wiktionary.org/wiki/feallan#Old_English
				fly       https://en.wiktionary.org/wiki/fleogan#Old_English
				flow      https://en.wiktionary.org/wiki/flowan#Old_English
				hear      https://en.wiktionary.org/wiki/gehieran#Old_English
				occupy    https://en.wiktionary.org/wiki/weardian#Old_English
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/geseon#Old_English
				show      https://en.wiktionary.org/wiki/%C3%A6tiewan#Old_English
				startle   https://en.wiktionary.org/wiki/greosan#Old_English # "frighten"
				swim      https://en.wiktionary.org/wiki/swimman#Old_English
				walk      https://en.wiktionary.org/wiki/gan#Old_English
				warm      
				watch     https://en.wiktionary.org/wiki/w%C3%A6cce#Old_English
				work      https://en.wiktionary.org/wiki/wyrcan#Old_English

				do        https://en.wiktionary.org/wiki/don#Old_English
				go        https://en.wiktionary.org/wiki/gan#Old_English
				want      https://en.wiktionary.org/wiki/willan#Old_English
            	steal     https://en.wiktionary.org/wiki/stelan#Old_English
            	share     https://en.wiktionary.org/wiki/d%C3%A6lan#Old_English
            	tame      https://en.wiktionary.org/wiki/teman#Old_English
            	move      https://en.wiktionary.org/wiki/styrian
            	love      https://en.wiktionary.org/wiki/lufian
            	have      https://en.wiktionary.org/wiki/habban
            	live      https://en.wiktionary.org/wiki/libban
            	say       https://en.wiktionary.org/wiki/secgan
            	think     https://en.wiktionary.org/wiki/hycgan
			''')
		)
	)
)

print('PROTO-INDO-EUROPEAN/SIHLER')
write('data/inflection/indo-european/proto-indo-european/sihler/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Proto-Indo-European', 'ine-pro'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/t%C3%A1wros
				attention https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/m%C3%A9nos
				bird      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9wis
				boat      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/n%C3%A9h%E2%82%82us
				book      
				brother   https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/b%CA%B0r%C3%A9h%E2%82%82t%C4%93r
				bug       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/pl%C3%BAsis # "flea"
				clothing  https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%A9stis
				daughter  https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%CA%B0ugh%E2%82%82t%E1%B8%97r
				dog       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/%E1%B8%B1w%E1%B9%93
				door      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%CA%B0w%E1%B9%93r
				drum      
				enemy     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B0%C3%B3stis
				fire      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9h%E2%82%82wr%CC%A5
				food      
				gift      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%C3%A9h%E2%82%83nom
				glass     
				guard     # *péh₂-s-tōr ~ *ph₂-s-tr-és
				horse     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9%E1%B8%B1wos
				house     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%E1%B9%93m
				livestock https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9%E1%B8%B1u
				love      
				idea      
				man       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/wiHr%C3%B3s
				money     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/k%CA%B7oyn%C3%A9h%E2%82%82 # "payment"
				monster   https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%B3g%CA%B7%CA%B0is
				name      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81n%C3%B3mn%CC%A5
				rock      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9%E1%B8%B1m%C5%8D
				rope      
				sister    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/sw%C3%A9s%C5%8Dr
				size      
				son       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/suHy%C3%BAs
				sound     
				warmth    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B7%CA%B0%C3%A9ros
				water     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9k%CA%B7eh%E2%82%82
				way       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9ytr%CC%A5
				wind      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82w%C3%A9h%E2%82%81n%CC%A5ts
				window    
				woman     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B7%E1%B8%97n
				work      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%A9r%C7%B5om

				wolf      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C4%BA%CC%A5k%CA%B7os
				egg       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C5%8Dwy%C3%B3m
				mare
				seed      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/%C7%B5%C3%A9nh%E2%82%81mn%CC%A5
				father    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/ph%E2%82%82t%E1%B8%97r
				cow       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B7%E1%B9%93ws
				sea       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/m%C3%B3ri
				fight     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/k%C3%A9h%E2%82%83tus
				cloud     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/n%C3%A9b%CA%B0os
				stone     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9%E1%B8%B1m%C5%8D
			''')
		)
	)
)

write('data/inflection/indo-european/proto-indo-european/sihler/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Proto-Indo-European', 'ine-pro'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81lud%CA%B0%C3%A9t # "arrive"
				be        https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9sti
				change    
				climb     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/st%C3%A9yg%CA%B0eti
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%C3%A9wkti # "pull, lead"
				displease 
				eat       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9dti
				endure    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/t%C3%A9rh%E2%82%82uti # "overcome"
				fall      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9th%E2%82%82eti
				fly       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9th%E2%82%82eti
				flow      
				hear      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/%E1%B8%B1l%C3%A9wt
				occupy    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/t%E1%B8%B1%C3%A9yti # "settle, dwell"
				resemble  
				rest      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/l%C3%A9g%CA%B0yeti
				see       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/sp%C3%A9%E1%B8%B1yeti
				hear      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/%E1%B8%B1l%C3%A9wt
				show      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%C3%A9y%E1%B8%B1ti # "point out"
				startle   
				swim      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/(s)n%C3%A9h%E2%82%82ti
				walk      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/st%C3%A9yg%CA%B0eti
				warm      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B7%CA%B0or%C3%A9yeti
				watch     
				work      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/wr%CC%A5%C7%B5y%C3%A9ti

				be          https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9sti
				become      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/b%CA%B0%C3%BAHt
				leave       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/l%C3%A9yk%CA%B7t
				carry       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/b%CA%B0%C3%A9reti
				do          https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%CA%B0%C3%A9d%CA%B0eh%E2%82%81ti
				ask         https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/pr%CC%A5s%E1%B8%B1%C3%A9ti
				stretch     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/tn%CC%A5n%C3%A9wti
				know        https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%B3yde
				sit         https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/s%C3%ADsdeti
				protect     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82l%C3%A9kseti
				be-red      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81rud%CA%B0%C3%A9h%E2%82%81ti
				set-down    https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/sod%C3%A9yeti
				want-to-see https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%A9ydseti
				renew       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/n%C3%A9weh%E2%82%82ti
				arrive      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81lud%CA%B0%C3%A9t
				say         https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%A9wket
				point-out   https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%E1%B8%97y%E1%B8%B1st
				think       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/mem%C3%B3ne

			''')
		)
	)
)


noun_html = caching.crawl('''
	animal    https://en.wiktionary.org/wiki/%D0%B6%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D0%BE%D0%B5#Russian
	attention https://en.wiktionary.org/wiki/%D0%B2%D0%BD%D0%B8%D0%BC%D0%B0%D0%BD%D0%B8%D0%B5#Russian
	bird      https://en.wiktionary.org/wiki/%D0%BF%D1%82%D0%B8%D1%86%D0%B0#Russian
	boat      https://en.wiktionary.org/wiki/%D0%BB%D0%BE%D0%B4%D0%BA%D0%B0#Russian
	book      https://en.wiktionary.org/wiki/%D0%BA%D0%BD%D0%B8%D0%B3%D0%B0#Russian
	brother   https://en.wiktionary.org/wiki/%D0%B1%D1%80%D0%B0%D1%82#Russian
	bug       https://en.wiktionary.org/wiki/%D0%B1%D1%83%D0%BA%D0%B0%D1%88%D0%BA%D0%B0#Russian
	clothing  https://en.wiktionary.org/wiki/%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0#Russian
	daughter  https://en.wiktionary.org/wiki/%D0%B4%D0%BE%D1%87%D1%8C#Russian
	dog       https://en.wiktionary.org/wiki/%D1%81%D0%BE%D0%B1%D0%B0%D0%BA%D0%B0#Russian
	door      https://en.wiktionary.org/wiki/%D0%B4%D0%B2%D0%B5%D1%80%D1%8C#Russian
	drum      https://en.wiktionary.org/wiki/%D0%B1%D0%B0%D1%80%D0%B0%D0%B1%D0%B0%D0%BD#Russian
	enemy     https://en.wiktionary.org/wiki/%D0%B2%D1%80%D0%B0%D0%B3#Russian
	fire      https://en.wiktionary.org/wiki/%D0%BE%D0%B3%D0%BE%D0%BD%D1%8C#Russian
	food      https://en.wiktionary.org/wiki/%D0%B5%D0%B4%D0%B0#Russian
	gift      https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA#Russian
	glass     https://en.wiktionary.org/wiki/%D1%81%D1%82%D0%B5%D0%BA%D0%BB%D0%BE#Russian
	guard     https://en.wiktionary.org/wiki/%D1%81%D1%82%D1%80%D0%B0%D0%B6%D0%BD%D0%B8%D0%BA#Russian
	horse     https://en.wiktionary.org/wiki/%D0%BB%D0%BE%D1%88%D0%B0%D0%B4%D1%8C#Russian
	house     https://en.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC#Russian
	livestock https://en.wiktionary.org/wiki/%D1%81%D0%BA%D0%BE%D1%82#Russian
	love      https://en.wiktionary.org/wiki/%D0%BB%D1%8E%D0%B1%D0%BE%D0%B2%D1%8C#Russian
	idea      https://en.wiktionary.org/wiki/%D0%B8%D0%B4%D0%B5%D1%8F#Russian
	man       https://en.wiktionary.org/wiki/%D0%BC%D1%83%D0%B6%D1%87%D0%B8%D0%BD%D0%B0#Russian
	money     https://en.wiktionary.org/wiki/%D0%B4%D0%B5%D0%BD%D1%8C%D0%B3%D0%B8#Russian
	monster   https://en.wiktionary.org/wiki/%D1%87%D1%83%D0%B4%D0%BE%D0%B2%D0%B8%D1%89%D0%B5#Russian
	name      https://en.wiktionary.org/wiki/%D0%B8%D0%BC%D1%8F#Russian
	rock      https://en.wiktionary.org/wiki/%D0%BA%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C#Russian
	rope      https://en.wiktionary.org/wiki/%D0%BA%D0%B0%D0%BD%D0%B0%D1%82#Russian
	size      https://en.wiktionary.org/wiki/%D0%B2%D0%B5%D0%BB%D0%B8%D1%87%D0%B8%D0%BD%D0%B0#Russian
	son       https://en.wiktionary.org/wiki/%D1%81%D1%8B%D0%BD#Russian
	sound     https://en.wiktionary.org/wiki/%D0%B7%D0%B2%D1%83%D0%BA#Russian
	warmth    https://en.wiktionary.org/wiki/%D1%82%D0%B5%D0%BF%D0%BB%D0%BE#Russian
	water     https://en.wiktionary.org/wiki/%D0%B2%D0%BE%D0%B4%D0%B0#Russian
	way       https://en.wiktionary.org/wiki/%D0%BF%D1%83%D1%82%D1%8C#Russian
	wind      https://en.wiktionary.org/wiki/%D0%B2%D0%B5%D1%82%D0%B5%D1%80#Russian
	window    https://en.wiktionary.org/wiki/%D0%BE%D0%BA%D0%BD%D0%BE#Russian
	woman     https://en.wiktionary.org/wiki/%D0%B6%D0%B5%D0%BD%D1%89%D0%B8%D0%BD%D0%B0#Russian
	work      https://en.wiktionary.org/wiki/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0#Russian

	job       https://en.wiktionary.org/wiki/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0#Russian
	bathhouse https://en.wiktionary.org/wiki/%D0%B1%D0%B0%D0%BD%D1%8F#Russian
	line      https://en.wiktionary.org/wiki/%D0%BB%D0%B8%D0%BD%D0%B8%D1%8F#Russian
	movie     https://en.wiktionary.org/wiki/%D1%84%D0%B8%D0%BB%D1%8C%D0%BC#Russian
	writer    https://en.wiktionary.org/wiki/%D0%BF%D0%B8%D1%81%D0%B0%D1%82%D0%B5%D0%BB%D1%8C
	hero      https://en.wiktionary.org/wiki/%D0%B3%D0%B5%D1%80%D0%BE%D0%B9#Russian
	comment   https://en.wiktionary.org/wiki/%D0%BA%D0%BE%D0%BC%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%80%D0%B8%D0%B9
	building  https://en.wiktionary.org/wiki/%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5#Russian
	place     https://en.wiktionary.org/wiki/%D0%BC%D0%B5%D1%81%D1%82%D0%BE#Russian
	sea       https://en.wiktionary.org/wiki/%D0%BC%D0%BE%D1%80%D0%B5#Russian
	bone      https://en.wiktionary.org/wiki/%D0%BA%D0%BE%D1%81%D1%82%D1%8C#Russian
	mouse     https://en.wiktionary.org/wiki/%D0%BC%D1%8B%D1%88%D1%8C#Russian
''')

print('RUSSIAN')
write('data/inflection/indo-european/slavic/russian/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Russian'), 
			noun_html
		)
	)
)

print('RUSSIAN')
write('data/inflection/indo-european/slavic/russian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Russian', 'ru'), 
			noun_html
		)
	)
)


write('data/inflection/indo-european/slavic/russian/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Russian', 'ru'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D1%8F%D0%B2%D0%BB%D1%8F%D1%82%D1%8C%D1%81%D1%8F#Russian
				be        https://en.wiktionary.org/wiki/%D0%B1%D1%8B%D1%82%D1%8C#Russian
				be-inherently  https://en.wiktionary.org/wiki/%D0%B1%D1%8B%D1%82%D1%8C#Russian
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D1%8F%D1%82%D1%8C#Russian
				climb     https://en.wiktionary.org/wiki/%D0%B2%D0%B7%D0%B1%D0%B8%D1%80%D0%B0%D1%82%D1%8C%D1%81%D1%8F#Russian
				crawl     https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D0%BB%D0%B7%D0%B0%D1%82%D1%8C#Russian
				cool      https://en.wiktionary.org/wiki/%D0%BE%D1%81%D1%82%D1%83%D0%B4%D0%B8%D1%82%D1%8C#Russian
				direct    https://en.wiktionary.org/wiki/%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D1%8C#Russian
				displease https://en.wiktionary.org/wiki/%D0%BE%D0%B3%D0%BE%D1%80%D1%87%D0%B0%D1%82%D1%8C#Russian
				eat       https://en.wiktionary.org/wiki/%D0%B5%D1%81%D1%82%D1%8C#Russian
				endure    https://en.wiktionary.org/wiki/%D1%82%D0%B5%D1%80%D0%BF%D0%B5%D1%82%D1%8C#Russian
				fall      https://en.wiktionary.org/wiki/%D0%BF%D0%B0%D0%B4%D0%B0%D1%82%D1%8C#Russian
				fly       https://en.wiktionary.org/wiki/%D0%BB%D0%B5%D1%82%D0%B0%D1%82%D1%8C#Russian
				flow      https://en.wiktionary.org/wiki/%D1%82%D0%B5%D1%87%D1%8C#Russian
				hear      https://en.wiktionary.org/wiki/%D1%81%D0%BB%D1%8B%D1%88%D0%B0%D1%82%D1%8C#Russian
				occupy    https://en.wiktionary.org/wiki/%D0%B7%D0%B0%D0%BD%D0%B8%D0%BC%D0%B0%D1%82%D1%8C#Russian
				resemble  https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D1%85%D0%BE%D0%B4%D0%B8%D1%82%D1%8C#Russian
				rest      
				see       https://en.wiktionary.org/wiki/%D0%B2%D0%B8%D0%B4%D0%B5%D1%82%D1%8C#Russian
				show      https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D0%BA%D0%B0%D0%B7%D1%8B%D0%B2%D0%B0%D1%82%D1%8C#Russian
				startle   https://en.wiktionary.org/wiki/%D0%BF%D1%83%D0%B3%D0%B0%D1%82%D1%8C#Russian
				swim      https://en.wiktionary.org/wiki/%D0%BF%D0%BB%D1%8B%D1%82%D1%8C#Russian
				walk      https://en.wiktionary.org/wiki/%D1%88%D0%B0%D0%B3%D0%B0%D1%82%D1%8C#Russian
				warm      https://en.wiktionary.org/wiki/%D0%B3%D1%80%D0%B5%D1%82%D1%8C#Russian
				watch     https://en.wiktionary.org/wiki/%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B0%D1%82%D1%8C#Russian
				work      https://en.wiktionary.org/wiki/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D1%82%D1%8C#Russian

				give      https://en.wiktionary.org/wiki/%D0%B4%D0%B0%D0%B2%D0%B0%D1%82%D1%8C#Russian
				eat       https://en.wiktionary.org/wiki/%D0%B5%D1%81%D1%82%D1%8C#Russian
				live      https://en.wiktionary.org/wiki/%D0%B6%D0%B8%D1%82%D1%8C#Russian
				call      https://en.wiktionary.org/wiki/%D0%B7%D0%B2%D0%B0%D1%82%D1%8C#Russian
				go        https://en.wiktionary.org/wiki/%D0%B8%D0%B4%D1%82%D0%B8#Russian
				write     https://en.wiktionary.org/wiki/%D0%BF%D0%B8%D1%81%D0%B0%D1%82%D1%8C#Russian
				read      https://en.wiktionary.org/wiki/%D1%87%D0%B8%D1%82%D0%B0%D1%82%D1%8C#Russian
				return    https://en.wiktionary.org/wiki/%D0%B2%D0%B5%D1%80%D0%BD%D1%83%D1%82%D1%8C#Russian
				draw      https://en.wiktionary.org/wiki/%D1%80%D0%B8%D1%81%D0%BE%D0%B2%D0%B0%D1%82%D1%8C#Russian
				spit      https://en.wiktionary.org/wiki/%D0%BF%D0%BB%D0%B5%D0%B2%D0%B0%D1%82%D1%8C#Russian
				dance     https://en.wiktionary.org/wiki/%D1%82%D0%B0%D0%BD%D1%86%D0%B5%D0%B2%D0%B0%D1%82%D1%8C#Russian
				be-able   https://en.wiktionary.org/wiki/%D0%BC%D0%BE%D1%87%D1%8C#Russian
				bake      https://en.wiktionary.org/wiki/%D0%BF%D0%B5%D1%87%D1%8C#Russian
				carry     https://en.wiktionary.org/wiki/%D0%BD%D0%B5%D1%81%D1%82%D0%B8#Russian
				lead      https://en.wiktionary.org/wiki/%D0%B2%D0%B5%D1%81%D1%82%D0%B8#Russian
				sweep     https://en.wiktionary.org/wiki/%D0%BC%D0%B5%D1%81%D1%82%D0%B8#Russian
				row       https://en.wiktionary.org/wiki/%D0%B3%D1%80%D0%B5%D1%81%D1%82%D0%B8#Russian
				steal     https://en.wiktionary.org/wiki/%D0%BA%D1%80%D0%B0%D1%81%D1%82%D1%8C#Russian
				convey    https://en.wiktionary.org/wiki/%D0%B2%D0%B5%D0%B7%D1%82%D0%B8#Russian
				climb     https://en.wiktionary.org/wiki/%D0%BB%D0%B5%D0%B7%D1%82%D1%8C#Russian
				wash      https://en.wiktionary.org/wiki/%D0%BC%D1%8B%D1%82%D1%8C#Russian
				beat      https://en.wiktionary.org/wiki/%D0%B1%D0%B8%D1%82%D1%8C#Russian
				wind      https://en.wiktionary.org/wiki/%D0%B2%D0%B8%D1%82%D1%8C#Russian
				pour      https://en.wiktionary.org/wiki/%D0%BB%D0%B8%D1%82%D1%8C#Russian
				drink     https://en.wiktionary.org/wiki/%D0%BF%D0%B8%D1%82%D1%8C#Russian
				sew       https://en.wiktionary.org/wiki/%D1%88%D0%B8%D1%82%D1%8C#Russian
				swim      https://en.wiktionary.org/wiki/%D0%BF%D0%BB%D1%8B%D1%82%D1%8C#Russian
				pass-for  https://en.wiktionary.org/wiki/%D1%81%D0%BB%D1%8B%D1%82%D1%8C#Russian
				speak     https://en.wiktionary.org/wiki/%D0%B3%D0%BE%D0%B2%D0%BE%D1%80%D0%B8%D1%82%D1%8C#Russian
				love      https://en.wiktionary.org/wiki/%D0%BB%D1%8E%D0%B1%D0%B8%D1%82%D1%8C#Russian
				catch     https://en.wiktionary.org/wiki/%D0%BB%D0%BE%D0%B2%D0%B8%D1%82%D1%8C#Russian
				sink      https://en.wiktionary.org/wiki/%D1%82%D0%BE%D0%BF%D0%B8%D1%82%D1%8C#Russian
				feed      https://en.wiktionary.org/wiki/%D0%BA%D0%BE%D1%80%D0%BC%D0%B8%D1%82%D1%8C#Russian
				ask       https://en.wiktionary.org/wiki/%D0%BF%D1%80%D0%BE%D1%81%D0%B8%D1%82%D1%8C#Russian
				pay       https://en.wiktionary.org/wiki/%D0%BF%D0%BB%D0%B0%D0%BA%D0%B0%D1%82%D1%8C#Russian
				forgive   https://en.wiktionary.org/wiki/%D1%85%D0%BE%D0%B4%D0%B8%D1%82%D1%8C#Russian
			''')
		)
	)
)


# raise 'done'


print('ARABIC')
write('data/inflection/semitic/arabic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Arabic', 'ar'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%D8%AD%D9%8A%D9%88%D8%A7%D9%86#Arabic
				attention https://en.wiktionary.org/wiki/%D8%A7%D9%87%D8%AA%D9%85%D8%A7%D9%85#Arabic
				bird      https://en.wiktionary.org/wiki/%D8%B7%D8%A7%D8%A6%D8%B1#Arabic
				boat      https://en.wiktionary.org/wiki/%D9%83%D8%AA%D8%A7%D8%A8#Arabic
				book      https://en.wiktionary.org/wiki/%D9%83%D8%AA%D8%A7%D8%A8#Arabic
				brother   https://en.wiktionary.org/wiki/%D8%A3%D8%AE#Arabic
				bug       https://en.wiktionary.org/wiki/%D8%AD%D8%B4%D8%B1%D8%A9#Arabic
				clothing  https://en.wiktionary.org/wiki/%D9%85%D9%84%D8%A7%D8%A8%D8%B3#Arabic
				daughter  https://en.wiktionary.org/wiki/%D8%A7%D8%A8%D9%86%D8%A9#Arabic
				dog       https://en.wiktionary.org/wiki/%D9%83%D9%84%D8%A8#Arabic
				door      https://en.wiktionary.org/wiki/%D8%A8%D8%A7%D8%A8#Arabic
				drum      https://en.wiktionary.org/wiki/%D8%B7%D8%A8%D9%84#Arabic
				enemy     https://en.wiktionary.org/wiki/%D8%B9%D8%AF%D9%88#Arabic
				fire      https://en.wiktionary.org/wiki/%D9%86%D8%A7%D8%B1#Arabic
				food      https://en.wiktionary.org/wiki/%D8%B7%D8%B9%D8%A7%D9%85#Arabic
				gift      https://en.wiktionary.org/wiki/%D9%87%D8%AF%D9%8A%D8%A9#Arabic
				glass     https://en.wiktionary.org/wiki/%D8%B2%D8%AC%D8%A7%D8%AC#Arabic
				guard     https://en.wiktionary.org/wiki/%D8%AD%D8%A7%D8%B1%D8%B3#Arabic
				horse     https://en.wiktionary.org/wiki/%D8%AD%D8%B5%D8%A7%D9%86#Arabic
				house     https://en.wiktionary.org/wiki/%D8%A8%D9%8A%D8%AA#Arabic
				livestock https://en.wiktionary.org/wiki/%D9%85%D8%A7%D8%B4%D9%8A%D8%A9#Arabic
				love      https://en.wiktionary.org/wiki/%D9%85%D8%AD%D8%A8%D8%A9#Arabic
				idea      https://en.wiktionary.org/wiki/%D9%81%D9%83%D8%B1%D8%A9#Arabic
				man       https://en.wiktionary.org/wiki/%D8%B1%D8%AC%D9%84#Arabic
				money     https://en.wiktionary.org/wiki/%D9%86%D9%82%D9%88%D8%AF#Arabic
				monster   https://en.wiktionary.org/wiki/%D9%88%D8%AD%D8%B4#Arabic
				name      https://en.wiktionary.org/wiki/%D8%A7%D8%B3%D9%85#Arabic
				rock      https://en.wiktionary.org/wiki/%D8%B5%D8%AE%D8%B1%D8%A9#Arabic
				rope      https://en.wiktionary.org/wiki/%D8%AD%D8%A8%D9%84#Arabic
				size      https://en.wiktionary.org/wiki/%D9%85%D9%82%D8%A7%D8%B3#Arabic
				son       https://en.wiktionary.org/wiki/%D8%A7%D8%A8%D9%86#Arabic
				sound     https://en.wiktionary.org/wiki/%D8%B5%D9%88%D8%AA#Arabic
				warmth    https://en.wiktionary.org/wiki/%D8%AD%D8%B1%D8%A7%D8%B1%D8%A9#Arabic
				water     https://en.wiktionary.org/wiki/%D9%85%D8%A7%D8%A1#Arabic
				way       https://en.wiktionary.org/wiki/%D8%B7%D8%B1%D9%8A%D9%82#Arabic
				wind      https://en.wiktionary.org/wiki/%D8%B1%D9%8A%D8%AD#Arabic
				window    https://en.wiktionary.org/wiki/%D9%86%D8%A7%D9%81%D8%B0%D8%A9#Arabic
				woman     https://en.wiktionary.org/wiki/%D8%A7%D9%85%D8%B1%D8%A3%D8%A9#Arabic
				work      https://en.wiktionary.org/wiki/%D8%AE%D8%AF%D9%85%D8%A9#Arabic
			''')
		)
	)
)

write('data/inflection/semitic/arabic/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Arabic', 'ar'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%D8%B9%D8%B1%D8%B6#Arabic
				be-inherently  https://en.wiktionary.org/wiki/%D9%83%D8%A7%D9%86#Arabic # indicates that subject is a predicate, not that it is self-same to
				be-momentarily https://en.wiktionary.org/wiki/%D9%83%D8%A7%D9%86#Arabic # indicates that subject is a predicate, not that it is self-same to
				change    https://en.wiktionary.org/wiki/%D8%AA%D8%BA%D9%8A%D8%B1#Arabic
				climb     https://en.wiktionary.org/wiki/%D8%AA%D8%B3%D9%84%D9%82#Arabic
				crawl     
				cool      https://en.wiktionary.org/wiki/%D8%A8%D8%B1%D8%AF#Arabic
				direct    https://en.wiktionary.org/wiki/%D9%82%D8%A7%D8%AF#Arabic
				displease https://en.wiktionary.org/wiki/%D8%A3%D8%B3%D8%AE%D8%B7#Arabic
				eat       https://en.wiktionary.org/wiki/%D8%A3%D9%83%D9%84#Arabic
				endure    https://en.wiktionary.org/wiki/%D8%AA%D8%AD%D9%85%D9%84#Arabic
				fall      https://en.wiktionary.org/wiki/%D9%88%D9%82%D8%B9#Arabic
				fly       https://en.wiktionary.org/wiki/%D8%B7%D8%A7%D8%B1#Arabic
				flow      
				hear      https://en.wiktionary.org/wiki/%D8%B3%D9%85%D8%B9#Arabic
				occupy    
				resemble  https://en.wiktionary.org/wiki/%D8%B4%D8%A8%D9%87#Arabic
				rest      https://en.wiktionary.org/wiki/%D8%A7%D8%B3%D8%AA%D8%B1%D8%A7%D8%AD#Arabic
				see       https://en.wiktionary.org/wiki/%D8%B1%D8%A3%D9%89#Arabic
				show      https://en.wiktionary.org/wiki/%D8%B9%D8%B1%D8%B6#Arabic
				startle   https://en.wiktionary.org/wiki/%D9%81%D8%A7%D8%AC%D8%A3#Arabic
				swim      https://en.wiktionary.org/wiki/%D8%B3%D8%A8%D8%AD#Arabic
				walk      https://en.wiktionary.org/wiki/%D9%85%D8%B4%D9%89#Arabic
				warm      https://en.wiktionary.org/wiki/%D8%B3%D8%AE%D9%86#Arabic
				watch     https://en.wiktionary.org/wiki/%D8%B4%D8%A7%D9%87%D8%AF#Arabic
				work      https://en.wiktionary.org/wiki/%D8%B9%D9%85%D9%84#Arabic
			''')
		)
	)
)

print('BASQUE')
write('data/inflection/basque/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Basque', 'eu'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/animalia#Basque
				attention https://en.wiktionary.org/wiki/gogo#Basque
				bird      https://en.wiktionary.org/wiki/txori#Basque
				boat      https://en.wiktionary.org/wiki/txalupa#Basque
				book      https://en.wiktionary.org/wiki/liburu#Basque
				brother   https://en.wiktionary.org/wiki/anaia#Basque
				bug       https://en.wiktionary.org/wiki/zomorro#Basque
				clothing  https://en.wiktionary.org/wiki/jantzi#Basque
				daughter  https://en.wiktionary.org/wiki/alaba#Basque
				dog       https://en.wiktionary.org/wiki/txakur#Basque
				door      https://en.wiktionary.org/wiki/ate#Basque
				drum      https://en.wiktionary.org/wiki/danbor#Basque
				enemy     https://en.wiktionary.org/wiki/janari#Basque
				fire      https://en.wiktionary.org/wiki/su#Basque
				food      https://en.wiktionary.org/wiki/janari#Basque
				gift      
				glass     
				guard     
				horse     https://en.wiktionary.org/wiki/zaldi#Basque
				house     https://en.wiktionary.org/wiki/etxe#Basque
				livestock https://en.wiktionary.org/wiki/abere#Basque
				love      https://en.wiktionary.org/wiki/amodio#Basque
				idea      https://en.wiktionary.org/wiki/gogo#Basque
				man       https://en.wiktionary.org/wiki/gizon#Basque
				money     https://en.wiktionary.org/wiki/diru#Basque
				monster   https://en.wiktionary.org/wiki/munstro#Basque
				name      https://en.wiktionary.org/wiki/izen#Basque
				rock      https://en.wiktionary.org/wiki/harri#Basque
				rope      https://en.wiktionary.org/wiki/soka#Basque
				size      https://en.wiktionary.org/wiki/tamaina#Basque
				son       https://en.wiktionary.org/wiki/seme#Basque
				sound     https://en.wiktionary.org/wiki/hots#Basque
				warmth    https://en.wiktionary.org/wiki/bero#Basque
				water     https://en.wiktionary.org/wiki/ur#Basque
				way       https://en.wiktionary.org/wiki/bide#Basque
				wind      https://en.wiktionary.org/wiki/haize#Basque
				window    https://en.wiktionary.org/wiki/leiho#Basque
				woman     https://en.wiktionary.org/wiki/andre#Basque
				work      https://en.wiktionary.org/wiki/lan#Basque
			''')
		)
	)
)


write('data/inflection/basque/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Basque', 'eu'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/izan#Basque
				be-momentarily https://en.wiktionary.org/wiki/egon#Basque
				change    https://en.wiktionary.org/wiki/aldatu#Basque
				climb     
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/jan#Basque
				endure    
				fall      https://en.wiktionary.org/wiki/erori#Basque
				fly       https://en.wiktionary.org/wiki/hegan_egin#Basque
				flow      
				hear      https://en.wiktionary.org/wiki/entzun#Basque
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/ikusi#Basque
				show      
				startle   
				swim      https://en.wiktionary.org/wiki/igeri_egin#Basque
				walk      https://en.wiktionary.org/wiki/ibili#Basque
				warm      
				watch     
				work      
			''')
		)
	)
)



write('data/inflection/indo-european/celtic/cornish/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Cornish'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/bones#Cornish
				be-momentarily https://en.wiktionary.org/wiki/bones#Cornish
				change    
				climb     
				crawl     
				cool      
				direct    
				displease 
				eat       
				endure    
				fall      
				fly       
				flow      
				hear      
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/gweles#Cornish
				show      
				startle   
				swim      
				walk      
				warm      
				watch     
				work      

				love      https://en.wiktionary.org/wiki/kara#Cornish
				have      https://en.wiktionary.org/wiki/kavos#Cornish
				do        https://en.wiktionary.org/wiki/gul#Cornish
				know      https://en.wiktionary.org/wiki/godhvos#Cornish
				wish      https://en.wiktionary.org/wiki/mynnes#Cornish
			''')
		)
	)
)

print('EGYPTIAN')
write('data/inflection/egyptian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Egyptian', 'egy'), 
			caching.crawl('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/%EA%9C%A3pd#Egyptian
				boat      https://en.wiktionary.org/wiki/jmw#Egyptian
				book      https://en.wiktionary.org/wiki/m%E1%B8%8F%EA%9C%A3t#Egyptian
				brother   https://en.wiktionary.org/wiki/sn#Egyptian
				bug       https://en.wiktionary.org/wiki/%EA%9C%A5p%C5%A1%EA%9C%A3y#Egyptian
				clothing  https://en.wiktionary.org/wiki/mn%E1%B8%ABt#Egyptian
				daughter  https://en.wiktionary.org/wiki/z%EA%9C%A3t#Egyptian
				dog       https://en.wiktionary.org/wiki/%E1%B9%AFzm#Egyptian
				door      https://en.wiktionary.org/wiki/rwt#Egyptian
				drum      
				enemy     https://en.wiktionary.org/wiki/%E1%B8%ABftj#Egyptian
				fire      https://en.wiktionary.org/wiki/s%E1%B8%8Ft#Egyptian
				food      https://en.wiktionary.org/wiki/%C5%A1bw#Egyptian
				gift      
				glass     
				guard     
				horse     https://en.wiktionary.org/wiki/ssm#Egyptian
				house     
				livestock 
				love      https://en.wiktionary.org/wiki/mrwt#Egyptian
				idea      
				man       https://en.wiktionary.org/wiki/z#Egyptian
				money     
				monster   
				name      https://en.wiktionary.org/wiki/rn#Egyptian
				rock      https://en.wiktionary.org/wiki/jnr#Egyptian
				rope      https://en.wiktionary.org/wiki/nw%E1%B8%A5#Egyptian
				size      
				son       https://en.wiktionary.org/wiki/z%EA%9C%A3#Egyptian
				sound     
				warmth    https://en.wiktionary.org/wiki/srf#Egyptian
				water     https://en.wiktionary.org/wiki/mw#Egyptian
				way       https://en.wiktionary.org/wiki/m%E1%B9%AFn#Egyptian
				wind      https://en.wiktionary.org/wiki/%E1%B9%AF%EA%9C%A3w#Egyptian
				window    
				woman     https://en.wiktionary.org/wiki/zt#Egyptian
				work      
			''')
		)
	)
)


write('data/inflection/egyptian/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Egyptian', 'egy'), 
			caching.crawl('''
				appear    
				be-inherently 
				be-momentarily
				change    
				climb     https://en.wiktionary.org/wiki/j%EA%9C%A3q#Egyptian
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/wnm#Egyptian
				endure    
				fall      
				fly       https://en.wiktionary.org/wiki/p%EA%9C%A3j#Egyptian
				flow      
				hear      https://en.wiktionary.org/wiki/s%E1%B8%8Fm#Egyptian
				occupy    
				resemble  https://en.wiktionary.org/wiki/twt#Egyptian
				rest      
				see       https://en.wiktionary.org/wiki/m%EA%9C%A3%EA%9C%A3#Egyptian
				show      
				startle   
				swim      
				walk      https://en.wiktionary.org/wiki/h%EA%9C%A3j#Egyptian
				warm      
				watch     
				work      
			''')
		)
	)
)

print('FINNISH')
write('data/inflection/uralic/finnish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Finnish', 'fi',2), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/el%C3%A4in#Finnish
				attention https://en.wiktionary.org/wiki/huomio#Finnish
				bird      https://en.wiktionary.org/wiki/lintu#Finnish
				boat      https://en.wiktionary.org/wiki/vene#Finnish
				book      https://en.wiktionary.org/wiki/kirja#Finnish
				brother   https://en.wiktionary.org/wiki/veli#Finnish
				bug       https://en.wiktionary.org/wiki/%C3%B6t%C3%B6kk%C3%A4#Finnish
				clothing  https://en.wiktionary.org/wiki/vaatetus#Finnish
				daughter  https://en.wiktionary.org/wiki/tyt%C3%A4r#Finnish
				dog       https://en.wiktionary.org/wiki/koira#Finnish
				door      https://en.wiktionary.org/wiki/ovi#Finnish
				drum      https://en.wiktionary.org/wiki/rumpu#Finnish
				enemy     https://en.wiktionary.org/wiki/vihollinen#Finnish
				fire      https://en.wiktionary.org/wiki/tuli#Finnish
				food      https://en.wiktionary.org/wiki/ruoka#Finnish
				gift      https://en.wiktionary.org/wiki/lahja#Finnish
				glass     https://en.wiktionary.org/wiki/lasi#Finnish
				guard     https://en.wiktionary.org/wiki/vartija#Finnish
				horse     https://en.wiktionary.org/wiki/hevonen#Finnish
				house     https://en.wiktionary.org/wiki/talo#Finnish
				livestock https://en.wiktionary.org/wiki/karja#Finnish
				love      https://en.wiktionary.org/wiki/rakkaus#Finnish
				idea      https://en.wiktionary.org/wiki/idea#Finnish
				man       https://en.wiktionary.org/wiki/mies#Finnish
				money     https://en.wiktionary.org/wiki/raha#Finnish
				monster   https://en.wiktionary.org/wiki/hirvi%C3%B6#Finnish
				name      https://en.wiktionary.org/wiki/nimi#Finnish
				rock      https://en.wiktionary.org/wiki/kivi#Finnish
				rope      https://en.wiktionary.org/wiki/k%C3%B6ysi#Finnish
				size      https://en.wiktionary.org/wiki/koko#Finnish
				son       https://en.wiktionary.org/wiki/poika#Finnish
				sound     https://en.wiktionary.org/wiki/%C3%A4%C3%A4ni#Finnish
				warmth    https://en.wiktionary.org/wiki/l%C3%A4mp%C3%B6#Finnish
				water     https://en.wiktionary.org/wiki/vesi#Finnish
				way       https://en.wiktionary.org/wiki/tie#Finnish
				wind      https://en.wiktionary.org/wiki/tuuli#Finnish
				window    https://en.wiktionary.org/wiki/ikkuna#Finnish
				woman     https://en.wiktionary.org/wiki/nainen#Finnish
				work      https://en.wiktionary.org/wiki/ty%C3%B6#Finnish
			''')
		)
	)
)


write('data/inflection/uralic/finnish/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Finnish', 'fi'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/ilmesty%C3%A4#Finnish
				be-inherently  https://en.wiktionary.org/wiki/olla#Finnish
				be-momentarily https://en.wiktionary.org/wiki/olla#Finnish
				change    https://en.wiktionary.org/wiki/muuttua#Finnish
				climb     https://en.wiktionary.org/wiki/kiivet%C3%A4#Finnish
				crawl     
				cool      https://en.wiktionary.org/wiki/j%C3%A4%C3%A4hdytt%C3%A4%C3%A4#Finnish
				direct    https://en.wiktionary.org/wiki/johdattaa#Finnish
				displease https://en.wiktionary.org/wiki/hermostuttaa#Finnish
				eat       https://en.wiktionary.org/wiki/sy%C3%B6d%C3%A4#Finnish
				endure    https://en.wiktionary.org/wiki/kest%C3%A4%C3%A4#Finnish
				fall      https://en.wiktionary.org/wiki/kaatua#Finnish
				fly       https://en.wiktionary.org/wiki/lent%C3%A4%C3%A4#Finnish
				flow      
				hear      https://en.wiktionary.org/wiki/kuulla#Finnish
				occupy    https://en.wiktionary.org/wiki/asuttaa#Finnish
				resemble  https://en.wiktionary.org/wiki/muistuttaa#Finnish
				rest      https://en.wiktionary.org/wiki/nojata#Finnish
				see       https://en.wiktionary.org/wiki/n%C3%A4hd%C3%A4#Finnish
				show      https://en.wiktionary.org/wiki/n%C3%A4ytt%C3%A4%C3%A4#Finnish
				startle   https://en.wiktionary.org/wiki/h%C3%A4tk%C3%A4ytt%C3%A4%C3%A4#Finnish
				swim      https://en.wiktionary.org/wiki/uida#Finnish
				walk      https://en.wiktionary.org/wiki/k%C3%A4vell%C3%A4#Finnish
				warm      https://en.wiktionary.org/wiki/l%C3%A4mmitt%C3%A4%C3%A4#Finnish
				watch     https://en.wiktionary.org/wiki/katsella#Finnish
				work      https://en.wiktionary.org/wiki/ty%C3%B6skennell%C3%A4#Finnish
			''')
		)
	)
)


write('data/inflection/indo-european/romance/french/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'French', 'fr'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/appara%C3%AEtre#French
				be-inherently  https://en.wiktionary.org/wiki/%C3%AAtre#French
				be-momentarily 
				change    https://en.wiktionary.org/wiki/changer#French
				climb     https://en.wiktionary.org/wiki/escalader#French
				crawl     
				cool      https://en.wiktionary.org/wiki/refroidir#French
				direct    https://en.wiktionary.org/wiki/conduire#French
				displease https://en.wiktionary.org/wiki/%C3%A9nerver#French #"annoy"
				eat       https://en.wiktionary.org/wiki/manger#French
				endure    https://en.wiktionary.org/wiki/endurer#French
				fall      https://en.wiktionary.org/wiki/tomber#French
				fly       https://en.wiktionary.org/wiki/voler#French
				flow      
				hear      https://en.wiktionary.org/wiki/entendre#French
				occupy    https://en.wiktionary.org/wiki/occuper#French
				resemble  https://en.wiktionary.org/wiki/ressembler#French
				rest      https://en.wiktionary.org/wiki/reposer#French
				see       https://en.wiktionary.org/wiki/voir#French
				show      https://en.wiktionary.org/wiki/montrer#French
				startle   https://en.wiktionary.org/wiki/surprendre#French
				swim      https://en.wiktionary.org/wiki/nager#French
				walk      https://en.wiktionary.org/wiki/marcher#French
				warm      https://en.wiktionary.org/wiki/chauffer#French
				watch     https://en.wiktionary.org/wiki/regarder#French
				work      https://en.wiktionary.org/wiki/travailler#French

				have      https://en.wiktionary.org/wiki/avoir#French
				be        https://en.wiktionary.org/wiki/%C3%AAtre#French
				go        https://en.wiktionary.org/wiki/aller#French
				speak     https://en.wiktionary.org/wiki/parler#French
				choose    https://en.wiktionary.org/wiki/choisir#French
				loose     https://en.wiktionary.org/wiki/perdre#French
				receive   https://en.wiktionary.org/wiki/recevoir#French
			''')
		)
	)
)




print('GEORGIAN')
write('data/inflection/kartvelian/georgian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Georgian', 'ka',2), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%E1%83%AA%E1%83%AE%E1%83%9D%E1%83%95%E1%83%94%E1%83%9A%E1%83%98#Georgian
				attention https://en.wiktionary.org/wiki/%E1%83%A7%E1%83%A3%E1%83%A0%E1%83%90%E1%83%93%E1%83%A6%E1%83%94%E1%83%91%E1%83%90#Georgian
				bird      https://en.wiktionary.org/wiki/%E1%83%A9%E1%83%98%E1%83%A2%E1%83%98#Georgian
				boat      https://en.wiktionary.org/wiki/%E1%83%9C%E1%83%90%E1%83%95%E1%83%98#Georgian
				book      https://en.wiktionary.org/wiki/%E1%83%AC%E1%83%98%E1%83%92%E1%83%9C%E1%83%98#Georgian
				brother   https://en.wiktionary.org/wiki/%E1%83%AB%E1%83%9B%E1%83%90#Georgian
				bug       https://en.wiktionary.org/wiki/%E1%83%9B%E1%83%AC%E1%83%94%E1%83%A0%E1%83%98#Georgian
				clothing  https://en.wiktionary.org/wiki/%E1%83%A2%E1%83%90%E1%83%9C%E1%83%A1%E1%83%90%E1%83%AA%E1%83%9B%E1%83%94%E1%83%9A%E1%83%98#Georgian
				daughter  https://en.wiktionary.org/wiki/%E1%83%90%E1%83%A1%E1%83%A3%E1%83%9A%E1%83%98#Georgian
				dog       https://en.wiktionary.org/wiki/%E1%83%AB%E1%83%90%E1%83%A6%E1%83%9A%E1%83%98#Georgian
				door      https://en.wiktionary.org/wiki/%E1%83%99%E1%83%90%E1%83%A0%E1%83%98#Georgian
				drum      https://en.wiktionary.org/wiki/%E1%83%93%E1%83%9D%E1%83%9A%E1%83%98#Georgian
				enemy     https://en.wiktionary.org/wiki/%E1%83%9B%E1%83%A2%E1%83%94%E1%83%A0%E1%83%98#Georgian
				fire      https://en.wiktionary.org/wiki/%E1%83%AA%E1%83%94%E1%83%AA%E1%83%AE%E1%83%9A%E1%83%98#Georgian
				food      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%90%E1%83%99%E1%83%95%E1%83%94%E1%83%91%E1%83%98#Georgian
				gift      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%90%E1%83%A9%E1%83%A3%E1%83%A5%E1%83%90%E1%83%A0%E1%83%98#Georgian
				glass     https://en.wiktionary.org/wiki/%E1%83%A8%E1%83%A3%E1%83%A8%E1%83%90#Georgian
				guard     
				horse     https://en.wiktionary.org/wiki/%E1%83%AA%E1%83%AE%E1%83%94%E1%83%9C%E1%83%98#Georgian
				house     https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%90%E1%83%AE%E1%83%9A%E1%83%98#Georgian
				livestock https://en.wiktionary.org/wiki/%E1%83%9E%E1%83%98%E1%83%A0%E1%83%A3%E1%83%A2%E1%83%A7%E1%83%95%E1%83%98#Georgian
				love      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%98%E1%83%A7%E1%83%95%E1%83%90%E1%83%A0%E1%83%A3%E1%83%9A%E1%83%98#Georgian
				idea      https://en.wiktionary.org/wiki/%E1%83%98%E1%83%93%E1%83%94%E1%83%90#Georgian
				man       https://en.wiktionary.org/wiki/%E1%83%99%E1%83%90%E1%83%AA%E1%83%98#Georgian
				money     https://en.wiktionary.org/wiki/%E1%83%A4%E1%83%A3%E1%83%9A%E1%83%98#Georgian
				monster   https://en.wiktionary.org/wiki/%E1%83%A3%E1%83%A0%E1%83%A9%E1%83%AE%E1%83%A3%E1%83%9A%E1%83%98#Georgian
				name      https://en.wiktionary.org/wiki/%E1%83%93%E1%83%90%E1%83%A1%E1%83%90%E1%83%AE%E1%83%94%E1%83%9A%E1%83%94%E1%83%91%E1%83%90#Georgian
				rock      https://en.wiktionary.org/wiki/%E1%83%A5%E1%83%95%E1%83%90#Georgian
				rope      https://en.wiktionary.org/wiki/%E1%83%97%E1%83%9D%E1%83%99%E1%83%98#Georgian
				size      https://en.wiktionary.org/wiki/%E1%83%96%E1%83%9D%E1%83%9B%E1%83%90#Georgian
				son       https://en.wiktionary.org/wiki/%E1%83%AB%E1%83%94#Georgian
				sound     https://en.wiktionary.org/wiki/%E1%83%AE%E1%83%9B%E1%83%90#Georgian
				warmth    
				water     https://en.wiktionary.org/wiki/%E1%83%AC%E1%83%A7%E1%83%90%E1%83%9A%E1%83%98#Georgian
				way       https://en.wiktionary.org/wiki/%E1%83%92%E1%83%96%E1%83%90#Georgian
				wind      https://en.wiktionary.org/wiki/%E1%83%A5%E1%83%90%E1%83%A0%E1%83%98#Georgian
				window    https://en.wiktionary.org/wiki/%E1%83%A4%E1%83%90%E1%83%9C%E1%83%AF%E1%83%90%E1%83%A0%E1%83%90#Georgian
				woman     https://en.wiktionary.org/wiki/%E1%83%A5%E1%83%90%E1%83%9A%E1%83%98#Georgian
				work      
			''')
		)
	)
)


write('data/inflection/kartvelian/georgian/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Georgian', 'ka'), 
			caching.crawl('''
				appear    
				be-inherently 
				be-momentarily
				change    
				climb     
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/%E1%83%AD%E1%83%90%E1%83%9B%E1%83%90#Georgian
				endure    
				fall      
				fly       
				flow      
				hear      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%9B%E1%83%94%E1%83%9C%E1%83%90#Georgian
				occupy    
				resemble  
				rest      https://en.wiktionary.org/wiki/%E1%83%93%E1%83%90%E1%83%A1%E1%83%95%E1%83%94%E1%83%9C%E1%83%94%E1%83%91%E1%83%90#Georgian
				see       https://en.wiktionary.org/wiki/%E1%83%AE%E1%83%94%E1%83%93%E1%83%90%E1%83%95%E1%83%A1#Georgian
				show      https://en.wiktionary.org/wiki/%E1%83%A9%E1%83%95%E1%83%94%E1%83%9C%E1%83%94%E1%83%91%E1%83%90#Georgian
				startle   
				swim      
				walk      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%95%E1%83%9A%E1%83%90#Georgian
				warm      https://en.wiktionary.org/wiki/%E1%83%90%E1%83%97%E1%83%91%E1%83%9D%E1%83%91%E1%83%A1#Georgian
				watch     
				work      https://en.wiktionary.org/wiki/%E1%83%9B%E1%83%A3%E1%83%A8%E1%83%90%E1%83%9D%E1%83%91%E1%83%90#Georgian
			''')
		)
	)
)


print('GERMAN')
write('data/inflection/indo-european/germanic/german/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'German', 'de'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/Tier#German
				attention https://en.wiktionary.org/wiki/Beachtung#German
				bird      https://en.wiktionary.org/wiki/Vogel#German
				boat      https://en.wiktionary.org/wiki/Boot#German
				book      https://en.wiktionary.org/wiki/Buch#German
				brother   https://en.wiktionary.org/wiki/Bruder#German
				bug       https://en.wiktionary.org/wiki/Wanze#German
				clothing  https://en.wiktionary.org/wiki/Kleidungsst%C3%BCck#German # "garment"
				daughter  https://en.wiktionary.org/wiki/Tochter#German
				dog       https://en.wiktionary.org/wiki/Hund#German
				door      https://en.wiktionary.org/wiki/T%C3%BCr#German
				drum      https://en.wiktionary.org/wiki/Trommel#German
				enemy     https://en.wiktionary.org/wiki/Feind#German
				fire      https://en.wiktionary.org/wiki/Feuer#German
				food      https://en.wiktionary.org/wiki/Nahrung#German
				gift      https://en.wiktionary.org/wiki/Geschenk#German
				glass     https://en.wiktionary.org/wiki/Glas#German
				guard     https://en.wiktionary.org/wiki/W%C3%A4chter#German
				horse     https://en.wiktionary.org/wiki/Pferd#German
				house     https://en.wiktionary.org/wiki/Haus#German
				livestock https://en.wiktionary.org/wiki/Vieh#German
				love      https://en.wiktionary.org/wiki/Zuneigung#German
				idea      https://en.wiktionary.org/wiki/Gedanke#German
				man       https://en.wiktionary.org/wiki/Mann#German
				money     https://en.wiktionary.org/wiki/Geld#German
				monster   https://en.wiktionary.org/wiki/Monster#German
				name      https://en.wiktionary.org/wiki/Name#German
				rock      https://en.wiktionary.org/wiki/Fels#German
				rope      https://en.wiktionary.org/wiki/Seil#German
				size      https://en.wiktionary.org/wiki/Gr%C3%B6%C3%9Fe#German
				son       https://en.wiktionary.org/wiki/Sohn#German
				sound     https://en.wiktionary.org/wiki/gesund#German
				warmth    https://en.wiktionary.org/wiki/W%C3%A4rme#German
				water     https://en.wiktionary.org/wiki/Wasser#German
				way       https://en.wiktionary.org/wiki/Weg#German
				wind      https://en.wiktionary.org/wiki/Wind#German
				window    https://en.wiktionary.org/wiki/Fenster#German
				woman     https://en.wiktionary.org/wiki/Frau#German
				work      https://en.wiktionary.org/wiki/Arbeit#German
			''')
		)
	)
)

write('data/inflection/indo-european/germanic/german/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'German', 'de'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/erscheinen#German
				be-inherently  https://en.wiktionary.org/wiki/sein#German
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%C3%A4ndern#German
				climb     https://en.wiktionary.org/wiki/klettern#German
				crawl     
				cool      https://en.wiktionary.org/wiki/abk%C3%BChlen#German
				direct    https://en.wiktionary.org/wiki/f%C3%BChren#German
				displease https://en.wiktionary.org/wiki/%C3%A4rgern#German #"anger"
				eat       https://en.wiktionary.org/wiki/essen#German
				endure    https://en.wiktionary.org/wiki/ertragen#German
				fall      https://en.wiktionary.org/wiki/fallen#German
				fly       https://en.wiktionary.org/wiki/fliegen#German
				flow      
				hear      https://en.wiktionary.org/wiki/h%C3%B6ren#German
				occupy    
				resemble  https://en.wiktionary.org/wiki/%C3%A4hneln#German
				rest      https://en.wiktionary.org/wiki/ruhen#German
				see       https://en.wiktionary.org/wiki/sehen#German
				show      https://en.wiktionary.org/wiki/zeigen#German
				startle   https://en.wiktionary.org/wiki/erschrecken#German
				swim      https://en.wiktionary.org/wiki/schwimmen#German
				walk      https://en.wiktionary.org/wiki/gehen#German
				warm      https://en.wiktionary.org/wiki/w%C3%A4rmen#German
				watch     https://en.wiktionary.org/wiki/zusehen#German
				work      https://en.wiktionary.org/wiki/arbeiten#German
			''')
		)
	)
)

print('GOTHIC')
write('data/inflection/indo-european/germanic/gothic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Gothic', 'got'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8C%B9%F0%90%8C%BF%F0%90%8D%83#Gothic
				attention https://en.wiktionary.org/wiki/%F0%90%8C%BC%F0%90%8C%B9%F0%90%8D%84%F0%90%8D%89%F0%90%8C%BD%F0%90%8D%83#Gothic
				bird      https://en.wiktionary.org/wiki/%F0%90%8D%86%F0%90%8C%BF%F0%90%8C%B2%F0%90%8C%BB%F0%90%8D%83#Gothic
				boat      https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8C%BA%F0%90%8C%B9%F0%90%8D%80#Gothic
				book      https://en.wiktionary.org/wiki/%F0%90%8C%B1%F0%90%8D%89%F0%90%8C%BA%F0%90%8D%89%F0%90%8D%83#Gothic
				brother   
				bug       
				clothing  https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B0%F0%90%8D%83%F0%90%8D%84%F0%90%8C%B9#Gothic
				daughter  https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8C%B0%F0%90%8C%BF%F0%90%8C%B7%F0%90%8D%84%F0%90%8C%B0%F0%90%8D%82#Gothic
				dog       https://en.wiktionary.org/wiki/%F0%90%8C%B7%F0%90%8C%BF%F0%90%8C%BD%F0%90%8C%B3%F0%90%8D%83#Gothic
				door      https://en.wiktionary.org/wiki/%F0%90%8C%B7%F0%90%8C%B0%F0%90%8C%BF%F0%90%8D%82%F0%90%8C%B3%F0%90%8D%83#Gothic
				drum      
				enemy     https://en.wiktionary.org/wiki/%F0%90%8D%86%F0%90%8C%B9%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD%F0%90%8C%B3%F0%90%8D%83#Gothic
				fire      https://en.wiktionary.org/wiki/%F0%90%8D%86%F0%90%8D%89%F0%90%8C%BD#Gothic
				food      https://en.wiktionary.org/wiki/%F0%90%8C%BC%F0%90%8C%B0%F0%90%8D%84%F0%90%8D%83#Gothic
				gift      https://en.wiktionary.org/wiki/%F0%90%8C%BC%F0%90%8C%B0%F0%90%8C%B9%F0%90%8C%B8%F0%90%8C%BC%F0%90%8D%83#Gothic
				glass     
				guard     https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B0%F0%90%8D%82%F0%90%8C%B3%F0%90%8C%BE%F0%90%8C%B0#Gothic
				horse     
				house     https://en.wiktionary.org/wiki/%F0%90%8D%82%F0%90%8C%B0%F0%90%8C%B6%F0%90%8C%BD#Gothic
				livestock https://en.wiktionary.org/wiki/%F0%90%8C%B0%F0%90%8C%BF%F0%90%8C%B7%F0%90%8D%83%F0%90%8C%B0#Gothic # "cattle"
				love      https://en.wiktionary.org/wiki/%F0%90%8D%86%F0%90%8D%82%F0%90%8C%B9%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%B8%F0%90%8D%85%F0%90%8C%B0#Gothic
				idea      https://en.wiktionary.org/wiki/%F0%90%8C%BC%F0%90%8C%B9%F0%90%8D%84%F0%90%8D%89%F0%90%8C%BD%F0%90%8D%83#Gothic # "thought"
				man       https://en.wiktionary.org/wiki/%F0%90%8C%BC%F0%90%8C%B0%F0%90%8C%BD%F0%90%8C%BD%F0%90%8C%B0#Gothic
				money     https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8C%BA%F0%90%8C%B0%F0%90%8D%84%F0%90%8D%84%F0%90%8D%83#Gothic
				monster   https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8C%B9%F0%90%8C%BF%F0%90%8D%83#Gothic # "beast"
				name      https://en.wiktionary.org/wiki/%F0%90%8C%BD%F0%90%8C%B0%F0%90%8C%BC%F0%90%8D%89#Gothic
				rock      https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8D%84%F0%90%8C%B0%F0%90%8C%B9%F0%90%8C%BD%F0%90%8D%83#Gothic
				rope      
				size      
				son       https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8C%BF%F0%90%8C%BD%F0%90%8C%BF%F0%90%8D%83#Gothic
				sound     https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8D%82%F0%90%8C%BF%F0%90%8C%BD%F0%90%8C%BE%F0%90%8C%BF%F0%90%8D%83#Gothic
				warmth    
				water     https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B0%F0%90%8D%84%F0%90%8D%89#Gothic
				way       
				wind      https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B9%F0%90%8C%BD%F0%90%8C%B3%F0%90%8D%83#Gothic
				window    
				woman     https://en.wiktionary.org/wiki/%F0%90%8C%B5%F0%90%8C%B9%F0%90%8C%BD%F0%90%8D%89#Gothic
				work      https://en.wiktionary.org/wiki/%F0%90%8C%B0%F0%90%8D%82%F0%90%8C%B1%F0%90%8C%B0%F0%90%8C%B9%F0%90%8C%B8%F0%90%8D%83#Gothic
			''')
		)
	)
)


write('data/inflection/indo-european/germanic/gothic/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Gothic', 'got'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%F0%90%8C%B0%F0%90%8D%84%F0%90%8D%86%F0%90%8C%B0%F0%90%8D%82%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic # "arrive"
				be-inherently  https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B9%F0%90%8D%83%F0%90%8C%B0%F0%90%8C%BD#Gothic
				be-momentarily 
				change    
				climb     https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8D%84%F0%90%8C%B4%F0%90%8C%B9%F0%90%8C%B2%F0%90%8C%B0%F0%90%8C%BD#Gothic
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/%F0%90%8D%84%F0%90%8C%B9%F0%90%8C%BF%F0%90%8C%B7%F0%90%8C%B0%F0%90%8C%BD#Gothic # "lead"
				displease https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8D%82%F0%90%8D%89%F0%90%8C%B1%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic # "upset"
				eat       https://en.wiktionary.org/wiki/%F0%90%8C%B9%F0%90%8D%84%F0%90%8C%B0%F0%90%8C%BD#Gothic
				endure    https://en.wiktionary.org/wiki/%F0%90%8C%B2%F0%90%8C%B0%F0%90%8C%B1%F0%90%8C%B4%F0%90%8C%B9%F0%90%8C%B3%F0%90%8C%B0%F0%90%8C%BD#Gothic
				fall      https://en.wiktionary.org/wiki/%F0%90%8C%B3%F0%90%8D%82%F0%90%8C%B9%F0%90%8C%BF%F0%90%8D%83%F0%90%8C%B0%F0%90%8C%BD#Gothic
				fly       
				flow      
				hear      https://en.wiktionary.org/wiki/%F0%90%8C%B7%F0%90%8C%B0%F0%90%8C%BF%F0%90%8D%83%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic
				occupy    
				resemble  
				rest      https://en.wiktionary.org/wiki/%F0%90%8D%88%F0%90%8C%B4%F0%90%8C%B9%F0%90%8C%BB%F0%90%8C%B0%F0%90%8C%BD#Gothic
				see       https://en.wiktionary.org/wiki/%F0%90%8D%83%F0%90%8C%B0%F0%90%8C%B9%F0%90%8D%88%F0%90%8C%B0%F0%90%8C%BD#Gothic
				show      https://en.wiktionary.org/wiki/%F0%90%8C%B0%F0%90%8C%BF%F0%90%8C%B2%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic
				startle   https://en.wiktionary.org/wiki/%F0%90%8D%89%F0%90%8C%B2%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic # "frighten"
				swim      
				walk      https://en.wiktionary.org/wiki/%F0%90%8D%88%F0%90%8C%B0%F0%90%8D%82%F0%90%8C%B1%F0%90%8D%89%F0%90%8C%BD#Gothic
				warm      
				watch     
				work      https://en.wiktionary.org/wiki/%F0%90%8D%85%F0%90%8C%B0%F0%90%8C%BF%F0%90%8D%82%F0%90%8C%BA%F0%90%8C%BE%F0%90%8C%B0%F0%90%8C%BD#Gothic
			''')
		)
	)
)



print('GREEK/MODERN')
write('data/inflection/indo-european/greek/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Greek', 'el'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%CE%B6%CF%8E%CE%BF#Greek
				attention https://en.wiktionary.org/wiki/%CF%80%CF%81%CE%BF%CF%83%CE%BF%CF%87%CE%AE#Greek
				bird      https://en.wiktionary.org/wiki/%CF%80%CF%84%CE%B7%CE%BD%CF%8C#Greek
				boat      https://en.wiktionary.org/wiki/%CE%B2%CE%AC%CF%81%CE%BA%CE%B1#Greek
				book      https://en.wiktionary.org/wiki/%CE%B2%CE%B9%CE%B2%CE%BB%CE%AF%CE%BF#Greek
				brother   https://en.wiktionary.org/wiki/%CE%B1%CE%B4%CE%B5%CE%BB%CF%86%CF%8C%CF%82#Greek
				bug       https://en.wiktionary.org/wiki/%CE%B6%CE%BF%CF%85%CE%B6%CE%BF%CF%8D%CE%BD%CE%B9#Greek
				clothing  https://en.wiktionary.org/wiki/%CF%81%CE%BF%CF%8D%CF%87%CE%BF#Greek
				daughter  https://en.wiktionary.org/wiki/%CE%BA%CF%8C%CF%81%CE%B7#Greek
				dog       https://en.wiktionary.org/wiki/%CF%83%CE%BA%CF%8D%CE%BB%CE%BF%CF%82#Greek
				door      https://en.wiktionary.org/wiki/%CF%80%CF%8C%CF%81%CF%84%CE%B1#Greek
				drum      https://en.wiktionary.org/wiki/%CF%84%CF%8D%CE%BC%CF%80%CE%B1%CE%BD%CE%BF#Greek
				enemy     https://en.wiktionary.org/wiki/%CE%B5%CF%87%CE%B8%CF%81%CF%8C%CF%82#Greek
				fire      https://en.wiktionary.org/wiki/%CF%86%CF%89%CF%84%CE%B9%CE%AC#Greek
				food      https://en.wiktionary.org/wiki/%CF%86%CE%B1%CE%90#Greek
				gift      https://en.wiktionary.org/wiki/%CE%B4%CF%8E%CF%81%CE%BF#Greek
				glass     https://en.wiktionary.org/wiki/%CE%B3%CF%85%CE%B1%CE%BB%CE%AF#Greek
				guard     https://en.wiktionary.org/wiki/%CF%86%CF%8D%CE%BB%CE%B1%CE%BA%CE%B1%CF%82#Greek
				horse     https://en.wiktionary.org/wiki/%CE%AF%CF%80%CF%80%CE%BF%CF%82#Greek
				house     https://en.wiktionary.org/wiki/%CF%83%CF%80%CE%AF%CF%84%CE%B9#Greek
				livestock https://en.wiktionary.org/wiki/%CE%B2%CE%BF%CE%BF%CE%B5%CE%B9%CE%B4%CE%AE#Greek
				love      https://en.wiktionary.org/wiki/%CE%B1%CE%B3%CE%AC%CF%80%CE%B7#Greek
				idea      https://en.wiktionary.org/wiki/%CE%B9%CE%B4%CE%AD%CE%B1#Greek
				man       https://en.wiktionary.org/wiki/%CE%AC%CE%BD%CE%B4%CF%81%CE%B1%CF%82#Greek
				money     https://en.wiktionary.org/wiki/%CE%BB%CE%B5%CF%86%CF%84%CE%AC#Greek
				monster   https://en.wiktionary.org/wiki/%CF%84%CE%AD%CF%81%CE%B1%CF%82#Greek
				name      https://en.wiktionary.org/wiki/%CF%8C%CE%BD%CE%BF%CE%BC%CE%B1#Greek
				rock      https://en.wiktionary.org/wiki/%CF%80%CE%AD%CF%84%CF%81%CE%B1#Greek
				rope      https://en.wiktionary.org/wiki/%CF%83%CF%87%CE%BF%CE%B9%CE%BD%CE%AF#Greek
				size      https://en.wiktionary.org/wiki/%CE%BC%CE%AD%CE%B3%CE%B5%CE%B8%CE%BF%CF%82#Greek
				son       https://en.wiktionary.org/wiki/%CE%B3%CE%B9%CE%BF%CF%82#Greek
				sound     https://en.wiktionary.org/wiki/%CE%AE%CF%87%CE%BF%CF%82#Greek
				warmth    https://en.wiktionary.org/wiki/%CE%B8%CE%B5%CF%81%CE%BC%CF%8C%CF%84%CE%B7%CF%84%CE%B1#Greek
				water     https://en.wiktionary.org/wiki/%CE%BD%CE%B5%CF%81%CF%8C#Greek
				way       https://en.wiktionary.org/wiki/%CE%B4%CF%81%CF%8C%CE%BC%CE%BF%CF%82#Greek
				wind      https://en.wiktionary.org/wiki/%CE%AC%CE%BD%CE%B5%CE%BC%CE%BF%CF%82#Greek
				window    https://en.wiktionary.org/wiki/%CF%80%CE%B1%CF%81%CE%AC%CE%B8%CF%85%CF%81%CE%BF#Greek
				woman     https://en.wiktionary.org/wiki/%CE%B3%CF%85%CE%BD%CE%B1%CE%AF%CE%BA%CE%B1#Greek
				work      https://en.wiktionary.org/wiki/%CE%B5%CF%81%CE%B3%CE%B1%CF%83%CE%AF%CE%B1#Greek
			''')
		)
	)
)

write('data/inflection/indo-european/greek/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Greek', 'el'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%CE%B5%CE%BC%CF%86%CE%B1%CE%BD%CE%AF%CE%B6%CE%BF%CE%BC%CE%B1%CE%B9#Greek
				be-inherently  https://en.wiktionary.org/wiki/%CE%B5%CE%AF%CE%BC%CE%B1%CE%B9#Greek
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%CE%B1%CE%BB%CE%BB%CE%AC%CE%B6%CF%89#Greek
				climb     https://en.wiktionary.org/wiki/%CE%B1%CE%BD%CE%B5%CE%B2%CE%B1%CE%AF%CE%BD%CF%89#Greek
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/%CF%84%CF%81%CF%8E%CF%89#Greek
				endure    https://en.wiktionary.org/wiki/%CE%B1%CE%BD%CF%84%CE%AD%CF%87%CF%89#Greek
				fall      https://en.wiktionary.org/wiki/%CF%80%CE%AD%CF%86%CF%84%CF%89#Greek
				fly       https://en.wiktionary.org/wiki/%CF%80%CE%B5%CF%84%CF%8E#Greek
				flow      
				hear      
				occupy    
				resemble  https://en.wiktionary.org/wiki/%CE%BC%CE%BF%CE%B9%CE%AC%CE%B6%CF%89#Greek
				rest      https://en.wiktionary.org/wiki/%CE%B1%CE%BA%CE%BF%CF%85%CE%BC%CF%80%CF%8E#Greek
				see       https://en.wiktionary.org/wiki/%CE%B2%CE%BB%CE%AD%CF%80%CF%89#Greek
				show      https://en.wiktionary.org/wiki/%CE%B5%CE%BC%CF%86%CE%B1%CE%BD%CE%AF%CE%B6%CF%89#Greek
				startle   https://en.wiktionary.org/wiki/%CE%B1%CE%B9%CF%86%CE%BD%CE%B9%CE%B4%CE%B9%CE%AC%CE%B6%CF%89#Greek
				swim      https://en.wiktionary.org/wiki/%CE%BA%CE%BF%CE%BB%CF%85%CE%BC%CF%80%CE%AC%CF%89#Greek
				walk      https://en.wiktionary.org/wiki/%CF%80%CE%B5%CF%81%CF%80%CE%B1%CF%84%CE%AC%CF%89#Greek
				warm      
				watch     https://en.wiktionary.org/wiki/%CF%80%CE%B1%CF%81%CE%B1%CE%BA%CE%BF%CE%BB%CE%BF%CF%85%CE%B8%CF%8E#Greek
				work      https://en.wiktionary.org/wiki/%CE%B4%CE%BF%CF%85%CE%BB%CE%B5%CF%8D%CF%89#Greek
			''')
		)
	)
)

print('HEBREW')
write('data/inflection/semitic/hebrew/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Hebrew', 'he'), 
			caching.crawl('''
				animal    
				attention https://en.wiktionary.org/wiki/%D7%9E%D7%97%D7%A9%D7%91%D7%94#Hebrew
				bird      
				boat      
				book      https://en.wiktionary.org/wiki/%D7%A1%D7%A4%D7%A8#Hebrew
				brother   https://en.wiktionary.org/wiki/%D7%90%D7%97#Hebrew
				bug       
				clothing  
				daughter  https://en.wiktionary.org/wiki/%D7%91%D7%AA#Hebrew
				dog       https://en.wiktionary.org/wiki/%D7%9B%D7%9C%D7%91#Hebrew
				door      https://en.wiktionary.org/wiki/%D7%93%D7%9C%D7%AA#Hebrew
				drum      
				enemy     
				fire      
				food      https://en.wiktionary.org/wiki/%D7%9E%D7%96%D7%95%D7%9F#Hebrew
				gift      
				glass     https://en.wiktionary.org/wiki/%D7%96%D7%9B%D7%95%D7%9B%D7%99%D7%AA#Hebrew
				guard     
				horse     https://en.wiktionary.org/wiki/%D7%A1%D7%95%D7%A1#Hebrew
				house     https://en.wiktionary.org/wiki/%D7%91%D7%99%D7%AA#Hebrew
				livestock 
				love      https://en.wiktionary.org/wiki/%D7%90%D7%94%D7%91%D7%94#Hebrew
				idea      https://en.wiktionary.org/wiki/%D7%9E%D7%97%D7%A9%D7%91%D7%94#Hebrew
				man       https://en.wiktionary.org/wiki/%D7%90%D7%99%D7%A9#Hebrew
				money     https://en.wiktionary.org/wiki/%D7%9B%D7%A1%D7%A3#Hebrew
				monster   https://en.wiktionary.org/wiki/%D7%91%D7%94%D7%9E%D7%94#Hebrew #beast
				name      https://en.wiktionary.org/wiki/%D7%A9%D7%9D#Hebrew
				rock      https://en.wiktionary.org/wiki/%D7%90%D7%91%D7%9F#Hebrew
				rope      
				size      
				son       https://en.wiktionary.org/wiki/%D7%91%D7%9F#Hebrew
				sound     
				warmth    
				water     https://en.wiktionary.org/wiki/%D7%9E%D7%99%D7%9D#Hebrew
				way       https://en.wiktionary.org/wiki/%D7%93%D7%A8%D7%9A#Hebrew
				wind      https://en.wiktionary.org/wiki/%D7%A8%D7%95%D7%97#Hebrew
				window    
				woman     
				work      https://en.wiktionary.org/wiki/%D7%9E%D7%9C%D7%90%D7%9B%D7%94#Hebrew
			''')
		)
	)
)


write('data/inflection/semitic/hebrew/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Hebrew', 'he'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%D7%94%D7%95%D7%A4%D7%99%D7%A2#Hebrew
				be-inherently  https://en.wiktionary.org/wiki/%D7%94%D7%99%D7%94#Hebrew
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%D7%94%D7%A9%D7%AA%D7%A0%D7%94#Hebrew
				climb     https://en.wiktionary.org/wiki/%D7%98%D7%99%D7%A4%D7%A1#Hebrew
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/%D7%94%D7%95%D7%91%D7%99%D7%9C#Hebrew
				displease 
				eat       https://en.wiktionary.org/wiki/%D7%90%D7%9B%D7%9C#Hebrew
				endure    
				fall      https://en.wiktionary.org/wiki/%D7%A0%D7%A4%D7%9C#Hebrew
				fly       https://en.wiktionary.org/wiki/%D7%98%D7%A1#Hebrew
				flow      
				hear      https://en.wiktionary.org/wiki/%D7%A9%D7%9E%D7%A2#Hebrew
				occupy    
				resemble  
				rest      https://en.wiktionary.org/wiki/%D7%A0%D7%97#Hebrew
				see       https://en.wiktionary.org/wiki/%D7%A8%D7%90%D7%94#Hebrew
				show      https://en.wiktionary.org/wiki/%D7%94%D7%A8%D7%90%D7%94#Hebrew
				startle   
				swim      https://en.wiktionary.org/wiki/%D7%A9%D7%97%D7%94#Hebrew
				walk      https://en.wiktionary.org/wiki/%D7%94%D7%9C%D7%9A#Hebrew
				warm      https://en.wiktionary.org/wiki/%D7%97%D7%99%D7%9E%D7%9D#Hebrew
				watch     https://en.wiktionary.org/wiki/%D7%A6%D7%A4%D7%94#Hebrew
				work      https://en.wiktionary.org/wiki/%D7%A2%D7%91%D7%93#Hebrew
			''')
		)
	)
)

print('HINDI')
write('data/inflection/indo-european/indo-iranian/hindi/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Hindi', 'hi'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%BE%E0%A4%A8%E0%A4%B5%E0%A4%B0#Hindi
				attention https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%A8#Hindi
				bird      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%82%E0%A4%9B%E0%A5%80#Hindi
				boat      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%BE%E0%A4%B5#Hindi
				book      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%81%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%95#Hindi
				brother   https://en.wiktionary.org/wiki/%E0%A4%AD%E0%A4%BE%E0%A4%88#Hindi
				bug       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%80%E0%A4%A1%E0%A4%BC%E0%A4%BE#Hindi
				clothing  https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%8D%E0%A4%B0#Hindi
				daughter  https://en.wiktionary.org/wiki/%E0%A4%AC%E0%A5%87%E0%A4%9F%E0%A5%80#Hindi
				dog       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%81%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%BE#Hindi
				door      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%8D%E0%A4%B5%E0%A4%BE%E0%A4%B0#Hindi
				drum      https://en.wiktionary.org/wiki/%E0%A4%A2%E0%A5%8B%E0%A4%B2#Hindi
				enemy     https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%81%E0%A4%B6%E0%A5%8D%E0%A4%AE%E0%A4%A8#Hindi
				fire      https://en.wiktionary.org/wiki/%E0%A4%86%E0%A4%97#Hindi
				food      https://en.wiktionary.org/wiki/%E0%A4%96%E0%A4%BE%E0%A4%A8%E0%A4%BE#Hindi
				gift      https://en.wiktionary.org/wiki/%E0%A4%89%E0%A4%AA%E0%A4%B9%E0%A4%BE%E0%A4%B0#Hindi
				glass     https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%BE%E0%A4%81%E0%A4%9A#Hindi
				guard     https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%B8%E0%A4%AC%E0%A4%BE%E0%A4%A8#Hindi
				horse     https://en.wiktionary.org/wiki/%E0%A4%98%E0%A5%8B%E0%A4%A1%E0%A4%BC%E0%A4%BE#Hindi
				house     https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A4%95%E0%A4%BE%E0%A4%A8#Hindi
				livestock https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%B6%E0%A5%81#Hindi
				love      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A5%87%E0%A4%AE#Hindi
				idea      https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BF%E0%A4%9A%E0%A4%BE%E0%A4%B0#Hindi
				man       https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A4%BE%E0%A4%A8%E0%A5%81%E0%A4%B8#Hindi
				money     https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A4%A8#Hindi
				monster   https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%88%E0%A4%A4%E0%A5%8D%E0%A4%AF#Hindi
				name      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%BE%E0%A4%AE#Hindi
				rock      https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A4%BF%E0%A4%B2%E0%A4%BE#Hindi
				rope      https://en.wiktionary.org/wiki/%E0%A4%A1%E0%A5%8B%E0%A4%B0%E0%A5%80#Hindi
				size      https://en.wiktionary.org/wiki/%E0%A4%86%E0%A4%95%E0%A4%BE%E0%A4%B0#Hindi
				son       https://en.wiktionary.org/wiki/%E0%A4%AC%E0%A5%87%E0%A4%9F%E0%A4%BE#Hindi
				sound     https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A5%8D%E0%A4%B5%E0%A4%A8%E0%A5%80#Hindi
				warmth    https://en.wiktionary.org/wiki/%E0%A4%A4%E0%A4%BE%E0%A4%AA#Hindi
				water     https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%BE%E0%A4%A8%E0%A5%80#Hindi
				way       https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%A5#Hindi
				wind      https://en.wiktionary.org/wiki/%E0%A4%B9%E0%A4%B5%E0%A4%BE#Hindi
				window    https://en.wiktionary.org/wiki/%E0%A4%96%E0%A4%BF%E0%A4%A1%E0%A4%BC%E0%A4%95%E0%A5%80#Hindi
				woman     https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%BE%E0%A4%B0%E0%A5%80#Hindi
				work      https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%AF#Hindi
			''')
		)
	)
)

write('data/inflection/indo-european/indo-iranian/hindi/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Hindi', 'hi'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/%E0%A4%B9%E0%A5%8B%E0%A4%A8%E0%A4%BE#Hindi
				be-momentarily 
				change    https://en.wiktionary.org/wiki/%E0%A4%AC%E0%A4%A6%E0%A4%B2%E0%A4%A8%E0%A4%BE#Hindi
				climb     https://en.wiktionary.org/wiki/%E0%A4%9A%E0%A4%A2%E0%A4%BC%E0%A4%A8%E0%A4%BE#Hindi
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/%E0%A4%96%E0%A4%BE%E0%A4%A8%E0%A4%BE#Hindi
				endure    
				fall      https://en.wiktionary.org/wiki/%E0%A4%97%E0%A4%BF%E0%A4%B0%E0%A4%A8%E0%A4%BE#Hindi
				fly       https://en.wiktionary.org/wiki/%E0%A4%89%E0%A4%A1%E0%A4%BC%E0%A4%A8%E0%A4%BE#Hindi
				flow      
                hear      https://en.wiktionary.org/wiki/%E0%A4%B8%E0%A5%81%E0%A4%A8%E0%A4%A8%E0%A4%BE#Hindi
				occupy    
				resemble  
				rest      https://en.wiktionary.org/wiki/%E0%A4%86%E0%A4%B0%E0%A4%BE%E0%A4%AE_%E0%A4%95%E0%A4%B0%E0%A4%A8%E0%A4%BE#Hindi
				see       https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%87%E0%A4%96%E0%A4%A8%E0%A4%BE#Hindi
				show      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A4%BF%E0%A4%96%E0%A4%BE%E0%A4%A8%E0%A4%BE#Hindi
				startle   https://en.wiktionary.org/wiki/%E0%A4%A1%E0%A4%B0%E0%A4%BE%E0%A4%A8%E0%A4%BE#Hindi # "frighten"
				swim      https://en.wiktionary.org/wiki/%E0%A4%A4%E0%A5%88%E0%A4%B0%E0%A4%A8%E0%A4%BE#Hindi
				walk      https://en.wiktionary.org/wiki/%E0%A4%9F%E0%A4%B9%E0%A4%B2%E0%A4%A8%E0%A4%BE#Hindi
				warm      
				watch     https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%87%E0%A4%96%E0%A4%A8%E0%A4%BE#Hindi
				work      https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%BE%E0%A4%AE_%E0%A4%95%E0%A4%B0%E0%A4%A8%E0%A4%BE#Hindi
			''')
		)
	)
)

#TODO: Hittite needs its own custom format that does not rely on language code
print('HITTITE')
write('data/inflection/indo-european/hittite/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Hittite', table_count=2), 
			caching.crawl('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/%F0%92%84%A9%F0%92%80%80%F0%92%8A%8F%F0%92%80%B8#Hittite # eagle
				boat      
				book      
				brother
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/%F0%92%86%AA%F0%92%89%BF%F0%92%80%B8#Hittite
				door      
				drum      
				enemy     
				fire      https://en.wiktionary.org/wiki/%F0%92%89%BA%F0%92%84%B4%F0%92%84%AF#Hittite
				food      https://en.wiktionary.org/wiki/%F0%92%82%8A%F0%92%89%BF%F0%92%80%AD#Hittite # a kind of soup
				gift      
				glass     
				guard     
				horse     
				house     
				livestock 
				love      
				idea      
				man       https://en.wiktionary.org/wiki/%F0%92%80%AD%F0%92%8C%85%F0%92%89%BF%F0%92%84%B4%F0%92%84%A9%F0%92%80%B8#Hittite
				money     
				monster   
				name      https://en.wiktionary.org/wiki/%F0%92%86%B7%F0%92%80%80%F0%92%88%A0%F0%92%80%AD#Hittite
				rock      
				rope      https://en.wiktionary.org/wiki/%F0%92%85%96%F0%92%84%AD%F0%92%88%A0%F0%92%80%80%F0%92%80%B8#Hittite
				size      
				son       
				sound     
				warmth    
				water     https://en.wiktionary.org/wiki/%F0%92%89%BF%F0%92%80%80%F0%92%8B%BB#Hittite
				way       https://en.wiktionary.org/wiki/%F0%92%86%9C%F0%92%80%B8#Hittite
				wind      https://en.wiktionary.org/wiki/%F0%92%84%B7%F0%92%8C%8B%F0%92%89%BF%F0%92%80%AD%F0%92%8D%9D
				window    
				woman     https://en.wiktionary.org/wiki/%F0%92%85%96%F0%92%84%A9%F0%92%80%B8%F0%92%8A%AD%F0%92%8A%8F%F0%92%80%B8#Hittite
				work      

				place     https://en.wiktionary.org/wiki/%F0%92%81%89%F0%92%82%8A%F0%92%81%95%F0%92%80%AD#Hittite
				army      https://en.wiktionary.org/wiki/%F0%92%8C%85%F0%92%8A%BB%F0%92%8D%A3%F0%92%85%96#Hittite
				bone      https://en.wiktionary.org/wiki/%F0%92%84%A9%F0%92%80%B8%F0%92%8B%AB%F0%92%84%BF#Hittite
				king      https://en.wiktionary.org/wiki/%F0%92%88%97%F0%92%8D%91#Hittite
				night     https://en.wiktionary.org/wiki/%F0%92%85%96%F0%92%89%BA%F0%92%80%AD%F0%92%8D%9D#Hittite
				earth     https://en.wiktionary.org/wiki/%F0%92%8B%BC%F0%92%82%8A%F0%92%83%B7#Hittite
				star      https://en.wiktionary.org/wiki/%F0%92%84%A9%F0%92%80%B8%F0%92%8B%BC%F0%92%85%95%F0%92%8D%9D#Hittite
				father    https://en.wiktionary.org/wiki/%F0%92%80%9C%F0%92%8B%AB%F0%92%80%B8#Hittite
				mother    https://en.wiktionary.org/wiki/%F0%92%80%AD%F0%92%88%BE%F0%92%80%B8#Hittite
			''')
		)
	)
)


write('data/inflection/indo-european/hittite/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Hittite', table_count=2), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/%F0%92%82%8A%F0%92%8C%8D%F0%92%8D%A3#Hittite
				be-momentarily https://en.wiktionary.org/wiki/%F0%92%82%8A%F0%92%8C%8D%F0%92%8D%A3#Hittite
				change    
				climb     
				crawl     
				cool      https://en.wiktionary.org/wiki/%F0%92%84%BF%F0%92%82%B5%F0%92%80%80%F0%92%84%91%F0%92%8D%A3#Hittite
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/%F0%92%82%8A%F0%92%84%91%F0%92%8D%9D%F0%92%8A%8D%F0%92%8D%A3#Hittite
				endure    
				fall      
				fly       
				flow      
				hear      
				occupy    
				resemble  
				rest      
				see       
				show      
				startle   https://en.wiktionary.org/wiki/%F0%92%88%BE%F0%92%84%B4%F0%92%8A%AD%F0%92%85%88%F0%92%89%A1%F0%92%8D%A3#Hittite # "frighten"
				swim      
				walk      
				warm      
				watch     
				work      https://en.wiktionary.org/wiki/%F0%92%80%AD%F0%92%89%8C%F0%92%84%BF%F0%92%84%91%F0%92%8D%A3#Hittite
			''')
		)
	)
)

print('HUNGARIAN')
write('data/inflection/uralic/hungarian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Hungarian', 'hu', 2), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%C3%A1llat#Hungarian
				attention https://en.wiktionary.org/wiki/figyelem#Hungarian
				bird      https://en.wiktionary.org/wiki/mad%C3%A1r#Hungarian
				boat      https://en.wiktionary.org/wiki/cs%C3%B3nak#Hungarian
				book      https://en.wiktionary.org/wiki/k%C3%B6nyv#Hungarian
				brother   https://en.wiktionary.org/wiki/fiv%C3%A9r#Hungarian
				bug       https://en.wiktionary.org/wiki/bog%C3%A1r#Hungarian
				clothing  https://en.wiktionary.org/wiki/ruh%C3%A1zat#Hungarian
				daughter  https://en.wiktionary.org/wiki/l%C3%A1ny#Hungarian
				dog       https://en.wiktionary.org/wiki/kutya#Hungarian
				door      https://en.wiktionary.org/wiki/ajt%C3%B3#Hungarian
				drum      https://en.wiktionary.org/wiki/dob#Hungarian:_drum
				enemy     https://en.wiktionary.org/wiki/ellens%C3%A9g#Hungarian
				fire      https://en.wiktionary.org/wiki/t%C5%B1z#Hungarian
				food      https://en.wiktionary.org/wiki/%C3%A9tel#Hungarian
				gift      https://en.wiktionary.org/wiki/aj%C3%A1nd%C3%A9k#Hungarian
				glass     https://en.wiktionary.org/wiki/%C3%BCveg#Hungarian
				guard     https://en.wiktionary.org/wiki/%C5%91r#Hungarian
				horse     https://en.wiktionary.org/wiki/l%C3%B3#Hungarian
				house     https://en.wiktionary.org/wiki/h%C3%A1z#Hungarian
				livestock https://en.wiktionary.org/wiki/j%C3%B3sz%C3%A1g#Hungarian
				love      https://en.wiktionary.org/wiki/szeretet#Hungarian
				idea      https://en.wiktionary.org/wiki/eszme#Hungarian
				man       https://en.wiktionary.org/wiki/f%C3%A9rfi#Hungarian
				money     https://en.wiktionary.org/wiki/p%C3%A9nz#Hungarian
				monster   https://en.wiktionary.org/wiki/sz%C3%B6rny#Hungarian
				name      https://en.wiktionary.org/wiki/n%C3%A9v#Hungarian
				rock      https://en.wiktionary.org/wiki/k%C5%91#Hungarian
				rope      https://en.wiktionary.org/wiki/k%C3%B6t%C3%A9l#Hungarian
				size      https://en.wiktionary.org/wiki/m%C3%A9ret#Hungarian
				son       https://en.wiktionary.org/wiki/fi%C3%BA#Hungarian
				sound     https://en.wiktionary.org/wiki/hang#Hungarian
				warmth    https://en.wiktionary.org/wiki/h%C5%91#Hungarian
				water     https://en.wiktionary.org/wiki/v%C3%ADz#Hungarian
				way       https://en.wiktionary.org/wiki/%C3%BAt#Hungarian
				wind      https://en.wiktionary.org/wiki/sz%C3%A9l#Hungarian
				window    https://en.wiktionary.org/wiki/ablak#Hungarian
				woman     https://en.wiktionary.org/wiki/n%C5%91#Hungarian
				work      https://en.wiktionary.org/wiki/munka#Hungarian
			''')
		)
	)
)



write('data/inflection/uralic/hungarian/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Hungarian', 'hu'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/megjelenik#Hungarian
				be-inherently 
				be-momentarily
				change    https://en.wiktionary.org/wiki/megv%C3%A1ltozik#Hungarian
				climb     
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/vezet#Hungarian
				displease 
				eat       https://en.wiktionary.org/wiki/eszik#Hungarian
				endure    https://en.wiktionary.org/wiki/kitart#Hungarian
				fall      https://en.wiktionary.org/wiki/esik#Hungarian
				fly       https://en.wiktionary.org/wiki/rep%C3%BCl#Hungarian
				flow      
				hear      https://en.wiktionary.org/wiki/hall#Hungarian
				occupy    
				resemble  https://en.wiktionary.org/wiki/hasonl%C3%ADt#Hungarian
				rest      https://en.wiktionary.org/wiki/t%C3%A1maszt#Hungarian
				see       https://en.wiktionary.org/wiki/l%C3%A1t#Hungarian
				show      https://en.wiktionary.org/wiki/megmutat#Hungarian
				startle   
				swim      https://en.wiktionary.org/wiki/%C3%BAszik#Hungarian
				walk      https://en.wiktionary.org/wiki/s%C3%A9t%C3%A1l#Hungarian
				warm      https://en.wiktionary.org/wiki/meleg%C3%ADt#Hungarian
				watch     https://en.wiktionary.org/wiki/n%C3%A9z#Hungarian
				work      https://en.wiktionary.org/wiki/dolgozik#Hungarian
			''')
		)
	)
)


print('IRISH')
write('data/inflection/indo-european/celtic/irish/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Irish', 'ga'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/ainmh%C3%AD#Irish
				attention https://en.wiktionary.org/wiki/aoidh#Irish
				bird      https://en.wiktionary.org/wiki/%C3%A9an#Irish
				boat      https://en.wiktionary.org/wiki/b%C3%A1d#Irish
				book      https://en.wiktionary.org/wiki/leabhar#Irish
				brother   https://en.wiktionary.org/wiki/dearth%C3%A1ir#Irish
				bug       https://en.wiktionary.org/wiki/feithid#Irish
				clothing  https://en.wiktionary.org/wiki/%C3%A9adach#Irish
				daughter  https://en.wiktionary.org/wiki/in%C3%ADon#Irish
				dog       https://en.wiktionary.org/wiki/gadhar#Irish
				door      https://en.wiktionary.org/wiki/doras#Irish
				drum      https://en.wiktionary.org/wiki/druma#Irish
				enemy     https://en.wiktionary.org/wiki/namhaid#Irish
				fire      https://en.wiktionary.org/wiki/tine#Irish
				food      https://en.wiktionary.org/wiki/bia#Irish
				gift      https://en.wiktionary.org/wiki/tabhartas#Irish
				glass     https://en.wiktionary.org/wiki/gloine#Irish
				guard     https://en.wiktionary.org/wiki/garda#Irish
				horse     https://en.wiktionary.org/wiki/capall#Irish
				house     https://en.wiktionary.org/wiki/teach#Irish
				livestock https://en.wiktionary.org/wiki/stoc#Irish
				love      https://en.wiktionary.org/wiki/armacas#Irish
				idea      https://en.wiktionary.org/wiki/smaoineamh#Irish # "thought"
				man       https://en.wiktionary.org/wiki/fear#Irish
				money     https://en.wiktionary.org/wiki/airgead#Irish
				monster   https://en.wiktionary.org/wiki/p%C3%A9ist#Irish
				name      https://en.wiktionary.org/wiki/ainm#Irish
				rock      https://en.wiktionary.org/wiki/carraig#Irish
				rope      https://en.wiktionary.org/wiki/t%C3%A9ad#Irish
				size      https://en.wiktionary.org/wiki/m%C3%A9id#Irish
				son       https://en.wiktionary.org/wiki/mac#Irish
				sound     https://en.wiktionary.org/wiki/fuaim#Irish
				warmth    https://en.wiktionary.org/wiki/teas#Irish
				water     https://en.wiktionary.org/wiki/uisce#Irish
				way       https://en.wiktionary.org/wiki/bealach#Irish
				wind      https://en.wiktionary.org/wiki/gaoth#Irish
				window    https://en.wiktionary.org/wiki/fuinneog#Irish
				woman     https://en.wiktionary.org/wiki/bean#Irish
				work      https://en.wiktionary.org/wiki/obair#Irish
			''')
		)
	)
)


write('data/inflection/indo-european/celtic/irish/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Irish', 'ga'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/is#Irish # for nouns only
				be-momentarily https://en.wiktionary.org/wiki/b%C3%AD#Irish # for adjectives only
				change    
				climb     https://en.wiktionary.org/wiki/ardaigh#Irish
				crawl     
				cool      https://en.wiktionary.org/wiki/fuaraigh#Irish
				direct    https://en.wiktionary.org/wiki/deachtaigh#Irish
				displease 
				eat       https://en.wiktionary.org/wiki/ith#Irish
				endure    https://en.wiktionary.org/wiki/iompair#Irish
				fall      https://en.wiktionary.org/wiki/tit#Irish
				fly       https://en.wiktionary.org/wiki/eitil#Irish
				flow      
				hear      #https://en.wiktionary.org/wiki/airigh#Irish
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/feic#Irish
				show      https://en.wiktionary.org/wiki/taispe%C3%A1in#Irish
				startle   https://en.wiktionary.org/wiki/scanraigh#Irish # "frighten"
				swim      https://en.wiktionary.org/wiki/sn%C3%A1mh#Irish
				walk      https://en.wiktionary.org/wiki/si%C3%BAil#Irish
				warm      
				watch     https://en.wiktionary.org/wiki/fair#Irish
				work      https://en.wiktionary.org/wiki/oibrigh#Irish
			''')
		)
	)
)


print('ITALIAN')
write('data/inflection/indo-european/romance/italian/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Italian', 'it'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/apparire#Italian
				be-inherently 
				be-momentarily
				change    https://en.wiktionary.org/wiki/cambiare#Italian
				climb     https://en.wiktionary.org/wiki/scalare#Italian
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/guidare#Italian
				displease https://en.wiktionary.org/wiki/innervosire#Italian
				eat       https://en.wiktionary.org/wiki/mangiare#Italian
				endure    https://en.wiktionary.org/wiki/durare#Italian
				fall      https://en.wiktionary.org/wiki/cadere#Italian
				fly       https://en.wiktionary.org/wiki/volare#Italian
				flow      
				hear      https://en.wiktionary.org/wiki/udire#Italian
				occupy    https://en.wiktionary.org/wiki/occupare#Italian
				resemble  https://en.wiktionary.org/wiki/rassomigliare#Italian
				rest      https://en.wiktionary.org/wiki/reggersi#Italian
				see       https://en.wiktionary.org/wiki/vedere#Italian
				show      https://en.wiktionary.org/wiki/mostrare#Italian
				startle   https://en.wiktionary.org/wiki/sorprendere#Italian
				swim      https://en.wiktionary.org/wiki/nuotare#Italian
				walk      https://en.wiktionary.org/wiki/camminare#Italian
				warm      https://en.wiktionary.org/wiki/riscaldare#Italian
				watch     https://en.wiktionary.org/wiki/guardare#Italian
				work      https://en.wiktionary.org/wiki/lavorare#Italian
			''')
		)
	)
)

write('data/inflection/japanese/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Japanese', 'ja'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/%E7%8F%BE%E3%82%8C%E3%82%8B#Japanese
				be-inherently  https://en.wiktionary.org/wiki/%E3%81%A0#Japanese
				be-momentarily https://en.wiktionary.org/wiki/%E3%81%A0#Japanese
				change    https://en.wiktionary.org/wiki/%E5%A4%89%E3%82%8F%E3%82%8B#Japanese
				climb     https://en.wiktionary.org/wiki/%E5%A4%89%E3%81%88%E3%82%8B#Japanese
				crawl     
				cool      https://en.wiktionary.org/wiki/%E5%86%B7%E3%82%84%E3%81%99#Japanese
				direct    https://en.wiktionary.org/wiki/%E5%B0%8E%E3%81%8F#Japanese
				displease 
				eat       https://en.wiktionary.org/wiki/%E9%A3%9F%E3%81%B9%E3%82%8B#Japanese
				endure    https://en.wiktionary.org/wiki/%E8%80%90%E3%81%88%E3%82%8B#Japanese
				fall      https://en.wiktionary.org/wiki/%E8%90%BD%E3%81%A1%E3%82%8B#Japanese
				fly       https://en.wiktionary.org/wiki/%E9%A3%9B%E3%81%B6#Japanese
				flow      
				hear      https://en.wiktionary.org/wiki/%E8%81%9E%E3%81%8F#Japanese
				occupy    https://en.wiktionary.org/wiki/%E5%8D%A0%E3%82%81%E3%82%8B#Japanese
				resemble  https://en.wiktionary.org/wiki/%E4%BC%BC%E3%82%8B#Japanese
				rest      https://en.wiktionary.org/wiki/%E4%BC%91%E3%82%80#Japanese
				see       https://en.wiktionary.org/wiki/%E8%A6%8B%E3%82%8B#Japanese
				show      https://en.wiktionary.org/wiki/%E7%A4%BA%E3%81%99#Japanese
				startle   https://en.wiktionary.org/wiki/%E8%84%85%E3%81%8B%E3%81%99#Japanese
				swim      https://en.wiktionary.org/wiki/%E6%B3%B3%E3%81%90#Japanese
				walk      https://en.wiktionary.org/wiki/%E6%AD%A9%E3%81%8F#Japanese
				warm      https://en.wiktionary.org/wiki/%E6%B8%A9%E3%82%81%E3%82%8B#Japanese
				watch     https://en.wiktionary.org/wiki/%E8%A6%8B%E3%82%8B#Japanese
				work      https://en.wiktionary.org/wiki/%E5%83%8D%E3%81%8F#Japanese
			''')
		)
	)
)



print('OLD-CHURCH-SLAVONIC')
write('data/inflection/indo-european/slavic/old-church-slavonic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Old_Church_Slavonic', 'cu'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%D0%B6%D0%B8%D0%B2%D0%BE%D1%82%D1%8A#Old_Church_Slavonic
				attention https://en.wiktionary.org/wiki/%D0%BC%EA%99%91%D1%81%D0%BB%D1%8C#Old_Church_Slavonic
				bird      https://en.wiktionary.org/wiki/%D0%BF%D1%8A%D1%82%D0%B8%D1%86%D0%B0#Old_Church_Slavonic
				boat      https://en.wiktionary.org/wiki/%D0%BB%D0%B0%D0%B4%D0%B8%D0%B8#Old_Church_Slavonic
				book      https://en.wiktionary.org/wiki/%D0%B1%D0%BE%D1%83%D0%BA%EA%99%91#Old_Church_Slavonic
				brother   https://en.wiktionary.org/wiki/%D0%B1%D1%80%D0%B0%D1%82%D1%80%D1%8A#Old_Church_Slavonic
				bug       
				clothing  https://en.wiktionary.org/wiki/%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0#Old_Church_Slavonic
				daughter  https://en.wiktionary.org/wiki/%D0%B4%D1%8A%D1%89%D0%B8#Old_Church_Slavonic
				dog       https://en.wiktionary.org/wiki/%D0%BF%D1%8C%D1%81%D1%8A#Old_Church_Slavonic
				door      https://en.wiktionary.org/wiki/%D0%B4%D0%B2%D1%8C%D1%80%D0%B8#Old_Church_Slavonic
				drum      
				enemy     https://en.wiktionary.org/wiki/%D0%B2%D1%80%D0%B0%D0%B3%D1%8A#Old_Church_Slavonic
				fire      
				food      
				gift      
				glass     
				guard     
				horse     https://en.wiktionary.org/wiki/%D0%BA%D0%BE%D0%BD%D1%8C#Old_Church_Slavonic
				house     https://en.wiktionary.org/wiki/%D0%B4%D0%BE%D0%BC%D1%8A#Old_Church_Slavonic
				livestock 
				love      https://en.wiktionary.org/wiki/%D0%BB%D1%8E%D0%B1%EA%99%91#Old_Church_Slavonic
				idea      https://en.wiktionary.org/wiki/%D0%BC%EA%99%91%D1%81%D0%BB%D1%8C#Old_Church_Slavonic
				man       https://en.wiktionary.org/wiki/%D0%BC%D1%AB%D0%B6%D1%8C#Old_Church_Slavonic
				money     https://en.wiktionary.org/wiki/%D0%BF%D1%A3%D0%BD%D1%A7%D1%95%D1%8C#Old_Church_Slavonic
				monster   https://en.wiktionary.org/wiki/%D0%B7%D0%B2%D1%A3%D1%80%D1%8C#Old_Church_Slavonic
				name      
				rock      https://en.wiktionary.org/wiki/%D0%BA%D0%B0%D0%BC%EA%99%91#Old_Church_Slavonic
				rope      https://en.wiktionary.org/wiki/%D1%AB%D0%B6%D0%B5#Old_Church_Slavonic
				size      
				son       https://en.wiktionary.org/wiki/%D1%81%EA%99%91%D0%BD%D1%8A#Old_Church_Slavonic
				sound     
				warmth    
				water     https://en.wiktionary.org/wiki/%D0%B2%D0%BE%D0%B4%D0%B0#Old_Church_Slavonic
				way       https://en.wiktionary.org/wiki/%D0%BF%D1%AB%D1%82%D1%8C#Old_Church_Slavonic
				wind      https://en.wiktionary.org/wiki/%D0%B2%D1%A3%D1%82%D1%80%D1%8A#Old_Church_Slavonic
				window    
				woman     https://en.wiktionary.org/wiki/%D0%B6%D0%B5%D0%BD%D0%B0#Old_Church_Slavonic
				work      https://en.wiktionary.org/wiki/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0#Old_Church_Slavonic
			''')
		)
	)
)


write('data/inflection/indo-european/slavic/old-church-slavonic/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Old_Church_Slavonic', 'cu'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/%D0%B1%EA%99%91%D1%82%D0%B8#Old_Church_Slavonic
				be-momentarily 
				change    
				climb     
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B8#Old_Church_Slavonic
				displease 
				eat       https://en.wiktionary.org/wiki/%EA%99%97%D1%81%D1%82%D0%B8#Old_Church_Slavonic
				endure    https://en.wiktionary.org/wiki/%D1%82%D1%80%D1%8C%D0%BF%D1%A3%D1%82%D0%B8#Old_Church_Slavonic
				fall      
				fly       https://en.wiktionary.org/wiki/%D0%BB%D0%B5%D1%82%D1%A3%D1%82%D0%B8#Old_Church_Slavonic
				flow      
				hear      https://en.wiktionary.org/wiki/%D1%81%D0%BB%EA%99%91%D1%88%D0%B0%D1%82%D0%B8#Old_Church_Slavonic
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/%D0%B2%D0%B8%D0%B4%D1%A3%D1%82%D0%B8#Old_Church_Slavonic
				show      
				startle   
				swim      
				walk      
				warm      
				watch     
				work      https://en.wiktionary.org/wiki/%D0%B4%D1%A3%D0%BB%D0%B0%D1%82%D0%B8#Old_Church_Slavonic
			''')
		)
	)
)



write('data/inflection/indo-european/romance/portugese/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Portuguese', 'pt'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/aparecer#Portuguese
				be-inherently  https://en.wiktionary.org/wiki/ser#Portuguese
				be-momentarily https://en.wiktionary.org/wiki/estar#Portuguese
				change    https://en.wiktionary.org/wiki/mudar#Portuguese
				climb     https://en.wiktionary.org/wiki/subir#Portuguese
				crawl     https://en.wiktionary.org/wiki/rastejar#Portuguese
				cool      https://en.wiktionary.org/wiki/esfriar#Portuguese
				direct    https://en.wiktionary.org/wiki/dirigir#Portuguese
				displease https://en.wiktionary.org/wiki/perturbar#Portuguese
				eat       https://en.wiktionary.org/wiki/comer#Portuguese
				endure    https://en.wiktionary.org/wiki/aguentar#Portuguese
				fall      https://en.wiktionary.org/wiki/cair#Portuguese
				fly       https://en.wiktionary.org/wiki/voar#Portuguese
				flow      https://en.wiktionary.org/wiki/fluir#Portuguese
				hear      https://en.wiktionary.org/wiki/ouvir#Portuguese
				occupy    https://en.wiktionary.org/wiki/ocupar#Portuguese
				resemble  https://en.wiktionary.org/wiki/semelhar#Portuguese
				rest      https://en.wiktionary.org/wiki/repousar#Portuguese
				see       https://en.wiktionary.org/wiki/ver#Portuguese
				show      https://en.wiktionary.org/wiki/mostrar#Portuguese
				startle   https://en.wiktionary.org/wiki/assustar#Portuguese
				swim      https://en.wiktionary.org/wiki/nadar#Portuguese
				walk      https://en.wiktionary.org/wiki/andar#Portuguese
				warm      https://en.wiktionary.org/wiki/aquecer#Portuguese
				watch     https://en.wiktionary.org/wiki/ver#Portuguese
				work      https://en.wiktionary.org/wiki/trabalhar#Portuguese

				have      https://en.wiktionary.org/wiki/haver#Portuguese
				possess   https://en.wiktionary.org/wiki/ter#Portuguese
				go        https://en.wiktionary.org/wiki/ir#Portuguese
				put       https://en.wiktionary.org/wiki/p%C3%B4r#Portuguese

			''')
		)
	)
)


print('QUECHUAN')
write('data/inflection/quechuan/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Quechua', 'qu', 2), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/uywa#Quechua
				attention 
				bird      https://en.wiktionary.org/wiki/pisqu#Quechua
				boat      https://en.wiktionary.org/wiki/wamp%27u#Quechua
				book      https://en.wiktionary.org/wiki/liwru#Quechua
				brother   https://en.wiktionary.org/wiki/turi#Quechua
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/allqu#Quechua
				door      https://en.wiktionary.org/wiki/punku#Quechua
				drum      
				enemy     https://en.wiktionary.org/wiki/awqa#Quechua
				fire      https://en.wiktionary.org/wiki/nina#Quechua
				food      https://en.wiktionary.org/wiki/mikhuna#Quechua
				gift      
				glass     https://en.wiktionary.org/wiki/q%27ispi#Quechua
				guard     
				horse     https://en.wiktionary.org/wiki/kawallu#Quechua
				house     https://en.wiktionary.org/wiki/wasi#Quechua
				livestock 
				love      https://en.wiktionary.org/wiki/khuya#Quechua
				idea      
				man       https://en.wiktionary.org/wiki/qhari#Quechua
				money     https://en.wiktionary.org/wiki/qullqi#Quechua
				monster   
				name      https://en.wiktionary.org/wiki/suti#Quechua
				rock      https://en.wiktionary.org/wiki/rumi#Quechua
				rope      https://en.wiktionary.org/wiki/watu#Quechua
				size      https://en.wiktionary.org/wiki/chhika#Quechua
				son       
				sound     
				warmth    https://en.wiktionary.org/wiki/ruphay#Quechua
				water     https://en.wiktionary.org/wiki/yaku#Quechua
				way       https://en.wiktionary.org/wiki/%C3%B1an#Quechua
				wind      https://en.wiktionary.org/wiki/wayra#Quechua
				window    
				woman     https://en.wiktionary.org/wiki/warmi#Quechua
				work      
			''')
		)
	)
)


write('data/inflection/quechuan/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Quechua', 'qu'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/qispiy#Quechua
				be-inherently 
				be-momentarily
				change    
				climb     https://en.wiktionary.org/wiki/siqay#Quechua
				crawl     
				cool      https://en.wiktionary.org/wiki/chiriyachiy#Quechua
				direct    https://en.wiktionary.org/wiki/rampay#Quechua
				displease 
				eat       
				endure    
				fall      https://en.wiktionary.org/wiki/urmay#Quechua
				fly       https://en.wiktionary.org/wiki/phaway#Quechua
				flow      
				hear      https://en.wiktionary.org/wiki/uyariy#Quechua
				occupy    
				resemble  https://en.wiktionary.org/wiki/rikch%27akuy#Quechua
				rest      
				see       https://en.wiktionary.org/wiki/rikuy#Quechua
				show      https://en.wiktionary.org/wiki/rikuchiy#Quechua
				startle   
				swim      https://en.wiktionary.org/wiki/wamp%27uy#Quechua
				walk      https://en.wiktionary.org/wiki/riy#Quechua
				warm      
				watch     https://en.wiktionary.org/wiki/qhaway#Quechua
				work      https://en.wiktionary.org/wiki/llamk%27ay#Quechua
			''')
		)
	)
)



print('ROMANIAN')

write('data/inflection/indo-european/romance/romanian/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Romanian', 'ro'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/p%C4%83rea#Romanian
				be        https://en.wiktionary.org/wiki/fi#Romanian
				be-inherently  https://en.wiktionary.org/wiki/fi#Romanian
				be-momentarily https://en.wiktionary.org/wiki/fi#Romanian
				change    https://en.wiktionary.org/wiki/schimba#Romanian
				climb     https://en.wiktionary.org/wiki/urca#Romanian
				crawl     https://en.wiktionary.org/wiki/t%C3%A2r%C3%AE#Romanian
				cool      https://en.wiktionary.org/wiki/r%C4%83ci#Romanian
				direct    https://en.wiktionary.org/wiki/conduce#Romanian
				displease https://en.wiktionary.org/wiki/tulbura#Romanian
				eat       https://en.wiktionary.org/wiki/m%C3%A2nca#Romanian
				endure    https://en.wiktionary.org/wiki/%C3%AEndura#Romanian
				fall      https://en.wiktionary.org/wiki/c%C4%83dea#Romanian
				fly       https://en.wiktionary.org/wiki/zbura#Romanian
				flow      https://en.wiktionary.org/wiki/curge#Romanian
				hear      https://en.wiktionary.org/wiki/auzi#Romanian
				#occupy    
				resemble  https://en.wiktionary.org/wiki/sem%C4%83na#Romanian
				#rest      
				see       https://en.wiktionary.org/wiki/vedea#Romanian
				show      https://en.wiktionary.org/wiki/ar%C4%83ta#Romanian
				#startle   
				swim      https://en.wiktionary.org/wiki/%C3%AEnota#Romanian
				walk      https://en.wiktionary.org/wiki/merge#Romanian
				warm      https://en.wiktionary.org/wiki/%C3%AEnc%C4%83lzi#Romanian
				watch     https://en.wiktionary.org/wiki/privi#Romanian
				work      https://en.wiktionary.org/wiki/face#Romanian

				# irregular
				have       https://en.wiktionary.org/wiki/avea#Romanian
				want       https://en.wiktionary.org/wiki/vrea#Romanian
				sit        https://en.wiktionary.org/wiki/sta#Romanian
				give       https://en.wiktionary.org/wiki/da#Romanian
				throw      https://en.wiktionary.org/wiki/azv%C3%A2rli#Romanian
				take       https://en.wiktionary.org/wiki/lua#Romanian
				drink      https://en.wiktionary.org/wiki/bea#Romanian
				know       https://en.wiktionary.org/wiki/%C8%99ti#Romanian
				dry        https://en.wiktionary.org/wiki/usca#Romanian
				continue   https://en.wiktionary.org/wiki/continua#Romanian
				#eat        
				#come-late https://en.wiktionary.org/wiki/%C3%AEnt%C3%A2rzia#Romanian

				# regular
				sing      https://en.wiktionary.org/wiki/c%C3%A2nta#Romanian
				sleep     https://en.wiktionary.org/wiki/dormi#Romanian
				offer     https://en.wiktionary.org/wiki/oferi#Romanian
				choose    https://en.wiktionary.org/wiki/alege#Romanian
				know      https://en.wiktionary.org/wiki/%C8%99ti#Romanian
			''')
		)
	)
)

noun_html = caching.crawl('''
	animal     https://en.wiktionary.org/wiki/animal#Romanian
	attention  https://en.wiktionary.org/wiki/aten%C8%9Bie#Romanian
	bird       https://en.wiktionary.org/wiki/pas%C4%83re#Romanian
	boat       https://en.wiktionary.org/wiki/barc%C4%83#Romanian
	book       https://en.wiktionary.org/wiki/carte#Romanian
	brother    https://en.wiktionary.org/wiki/frate#Romanian
	bug        https://en.wiktionary.org/wiki/insect%C4%83#Romanian
	clothing   https://en.wiktionary.org/wiki/%C3%AEmbr%C4%83c%C4%83minte#Romanian
	daughter   https://en.wiktionary.org/wiki/fiic%C4%83#Romanian
	dog        https://en.wiktionary.org/wiki/c%C3%A2ine#Romanian
	door       https://en.wiktionary.org/wiki/u%C8%99%C4%83#Romanian
	drum       https://en.wiktionary.org/wiki/tob%C4%83#Romanian
	enemy      https://en.wiktionary.org/wiki/du%C8%99man#Romanian
	fire       https://en.wiktionary.org/wiki/foc#Romanian
	food       https://en.wiktionary.org/wiki/aliment#Romanian
	gift       https://en.wiktionary.org/wiki/cadou#Romanian
	glass      https://en.wiktionary.org/wiki/sticl%C4%83#Romanian
	guard      https://en.wiktionary.org/wiki/gard%C4%83#Romanian
	horse      https://en.wiktionary.org/wiki/cal#Romanian
	house      https://en.wiktionary.org/wiki/cas%C4%83#Romanian
	livestock  https://en.wiktionary.org/wiki/%C8%99eptel#Romanian
	love       https://en.wiktionary.org/wiki/iubire#Romanian
	idea       https://en.wiktionary.org/wiki/idee#Romanian
	man        https://en.wiktionary.org/wiki/b%C4%83rbat#Romanian
	money      https://en.wiktionary.org/wiki/ban#Romanian
	monster    https://en.wiktionary.org/wiki/monstru#Romanian
	name       https://en.wiktionary.org/wiki/nume#Romanian
	rock       https://en.wiktionary.org/wiki/stan%C4%83#Romanian
	rope       https://en.wiktionary.org/wiki/fr%C3%A2nghie#Romanian
	size       https://en.wiktionary.org/wiki/m%C4%83rime#Romanian
	sister     https://en.wiktionary.org/wiki/sor%C4%83#Romanian
	son        https://en.wiktionary.org/wiki/fiu#Romanian
	sound      https://en.wiktionary.org/wiki/sunet#Romanian
	warmth     https://en.wiktionary.org/wiki/c%C4%83ldur%C4%83#Romanian
	water      https://en.wiktionary.org/wiki/ap%C4%83#Romanian
	way        https://en.wiktionary.org/wiki/cale#Romanian
	wind       https://en.wiktionary.org/wiki/v%C3%A2nt#Romanian
	window     https://en.wiktionary.org/wiki/fereastr%C4%83#Romanian
	woman      https://en.wiktionary.org/wiki/femeie#Romanian
	work       https://en.wiktionary.org/wiki/munc%C4%83#Romanian
''')

write('data/inflection/indo-european/romance/romanian/modern/scraped-genders.tsv',
	formatting.format(
		scraping.scrape(GenderWikiHtml(ops, 'Noun', 'Romanian'), noun_html)
	)
)

write('data/inflection/indo-european/romance/romanian/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Romanian', 'ro'), 
			noun_html
		)
	)
)

print('SANSKRIT')
write('data/inflection/indo-european/indo-iranian/sanskrit/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Sanskrit', 'sa'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A5%83%E0%A4%97#Sanskrit
				attention https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%A8#Sanskrit
				bird      https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BF#Sanskrit
				boat      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A5%8C#Sanskrit
				book      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%81%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%95#Sanskrit
				brother   https://en.wiktionary.org/wiki/%E0%A4%AD%E0%A5%8D%E0%A4%B0%E0%A4%BE%E0%A4%A4%E0%A5%83#Sanskrit
				bug       https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%A8%E0%A5%8D%E0%A4%A4%E0%A5%81#Sanskrit
				clothing  https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%B8%E0%A5%8D%E0%A4%AE%E0%A4%A8%E0%A5%8D#Sanskrit
				daughter  https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%81%E0%A4%B9%E0%A4%BF%E0%A4%A4%E0%A5%83#Sanskrit
				dog       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%81%E0%A4%B0%E0%A5%8D%E0%A4%95%E0%A5%81%E0%A4%B0#Sanskrit
				door      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%8D%E0%A4%B5%E0%A4%BE%E0%A4%B0#Sanskrit
				drum      https://en.wiktionary.org/wiki/%E0%A4%A2%E0%A5%8B%E0%A4%B2#Sanskrit
				enemy     https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A5%81#Sanskrit
				fire      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%97%E0%A5%8D%E0%A4%A8%E0%A4%BF#Sanskrit
				food      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%A8%E0%A5%8D%E0%A4%A8#Sanskrit
				gift      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A4%BE%E0%A4%A8#Sanskrit
				glass     https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%BE%E0%A4%9A#Sanskrit
				guard     
				horse     https://en.wiktionary.org/wiki/%E0%A4%98%E0%A5%8B%E0%A4%9F%E0%A4%95#Sanskrit
				house     https://en.wiktionary.org/wiki/%E0%A4%97%E0%A5%83%E0%A4%B9#Sanskrit
				livestock https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%B6%E0%A5%81#Sanskrit
				love      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%A8%E0%A5%81%E0%A4%B0%E0%A4%BE%E0%A4%97#Sanskrit
				idea      https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BF%E0%A4%9A%E0%A4%BE%E0%A4%B0#Sanskrit
				man       https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%B0#Sanskrit
				money     https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A4%A8#Sanskrit
				monster   https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%88%E0%A4%A4%E0%A5%8D%E0%A4%AF#Sanskrit
				name      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%BE%E0%A4%AE#Sanskrit
				rock      https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A4%BF%E0%A4%B2%E0%A4%BE#Sanskrit
				rope      https://en.wiktionary.org/wiki/%E0%A4%B0%E0%A4%9C%E0%A5%8D%E0%A4%9C%E0%A5%81#Sanskrit
				size      
				son       https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%81%E0%A4%A4%E0%A5%8D%E0%A4%B0#Sanskrit
				sound     https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A4%AC%E0%A5%8D%E0%A4%A6#Sanskrit
				warmth    https://en.wiktionary.org/wiki/%E0%A4%98%E0%A4%B0%E0%A5%8D%E0%A4%AE#Sanskrit
				water     https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BE%E0%A4%B0%E0%A4%BF#Sanskrit
				way       https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%A5#Sanskrit
				wind      https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%97%E0%A4%A4%E0%A5%8D#Sanskrit
				window    https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BE%E0%A4%A4%E0%A4%BE%E0%A4%AF%E0%A4%A8#Sanskrit
				woman     https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%A8%E0%A4%BF#Sanskrit
				work      https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%B0%E0%A5%8D%E0%A4%AE%E0%A4%A8%E0%A5%8D#Sanskrit

				god       https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%87%E0%A4%B5#Sanskrit
				desire    https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%BE%E0%A4%AE#Sanskrit
				yoke      https://en.wiktionary.org/wiki/%E0%A4%AF%E0%A5%81%E0%A4%97%E0%A5%8D%E0%A4%AE#Sanskrit
				fruit     
				Agni      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%97%E0%A5%8D%E0%A4%A8%E0%A4%BF#Sanskrit
				motion    https://en.wiktionary.org/wiki/%E0%A4%97%E0%A4%A4%E0%A4%BF#Sanskrit
				cow       https://en.wiktionary.org/wiki/%E0%A4%B8%E0%A5%82%E0%A4%A8%E0%A5%81#Sanskrit
				honey     https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A4%A7%E0%A5%81#Sanskrit
				father    https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%BF%E0%A4%A4%E0%A4%BE#Sanskrit
				brother   https://en.wiktionary.org/wiki/%E0%A4%AD%E0%A5%8D%E0%A4%B0%E0%A4%BE%E0%A4%A4%E0%A5%83#Sanskrit
				sister    https://en.wiktionary.org/wiki/%E0%A4%B8%E0%A5%8D%E0%A4%B5%E0%A4%B8%E0%A5%83#Sanskrit
				army      https://en.wiktionary.org/wiki/%E0%A4%B8%E0%A5%87%E0%A4%A8%E0%A4%BE#Sanskrit
				maiden    https://en.wiktionary.org/wiki/%E0%A4%95%E0%A4%A8%E0%A5%8D%E0%A4%AF%E0%A4%BE#Sanskrit
				goddess   https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%87%E0%A4%B5%E0%A5%80#Sanskrit
				wife      https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%A7%E0%A5%82#Sanskrit
				mind      https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A4%A8%E0%A4%B8%E0%A5%8D#Sanskrit
				king      https://en.wiktionary.org/wiki/%E0%A4%B0%E0%A4%BE%E0%A4%9C%E0%A4%BE#Sanskrit
				yogi      https://en.wiktionary.org/wiki/%E0%A4%AF%E0%A5%8B%E0%A4%97%E0%A4%BF%E0%A4%A8%E0%A5%8D#Sanskrit
				world     
			''')
		)
	)
)


write('data/inflection/indo-european/indo-iranian/sanskrit/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Sanskrit', 'sa'), 
			caching.crawl('''
				appear    
				be-inherently 
				be-momentarily
				change    
				climb     https://en.wiktionary.org/wiki/%E0%A4%B0%E0%A5%8B%E0%A4%B9%E0%A4%A4%E0%A4%BF#Sanskrit
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%AF%E0%A4%A4%E0%A4%BF#Sanskrit
				displease 
				eat       https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%BF#Sanskrit
				endure    
				fall      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%A4%E0%A4%A4%E0%A4%BF#Sanskrit
				fly       
				flow      
				hear      https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A5%8D%E0%A4%B0%E0%A5%81#Sanskrit
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%B6%E0%A5%8D%E0%A4%AF%E0%A4%A4%E0%A4%BF#Sanskrit
				show      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A4%BF%E0%A4%B6%E0%A4%A4%E0%A4%BF#Sanskrit
				startle   
				swim      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%8D%E0%A4%B2%E0%A4%B5%E0%A4%A4%E0%A5%87#Sanskrit
				walk      https://en.wiktionary.org/wiki/%E0%A4%9A%E0%A4%B2%E0%A4%A4%E0%A4%BF#Sanskrit
				warm      https://en.wiktionary.org/wiki/%E0%A4%A4%E0%A4%AA%E0%A4%A4%E0%A4%BF#Sanskrit
				watch     
				work      
			''')
		)
	)
)

print('SPANISH')
write('data/inflection/indo-european/romance/spanish/modern/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Spanish', 'es'), 
			caching.crawl('''
				appear    https://en.wiktionary.org/wiki/aparecer#Spanish
				be-inherently  https://en.wiktionary.org/wiki/ser#Spanish
				be-momentarily https://en.wiktionary.org/wiki/estar#Spanish
				change    https://en.wiktionary.org/wiki/cambiar#Spanish
				climb     https://en.wiktionary.org/wiki/escalar#Spanish
				crawl     https://en.wiktionary.org/wiki/arrastrar#Spanish
				cool      https://en.wiktionary.org/wiki/enfriar#Spanish
				direct    https://en.wiktionary.org/wiki/guiar#Spanish
				displease https://en.wiktionary.org/wiki/desazonar#Spanish
				eat       https://en.wiktionary.org/wiki/comer#Spanish
				endure    https://en.wiktionary.org/wiki/tolerar#Spanish
				fall      https://en.wiktionary.org/wiki/caer#Spanish
				fly       https://en.wiktionary.org/wiki/volar#Spanish
				flow      https://en.wiktionary.org/wiki/fluir#Spanish
				hear      https://en.wiktionary.org/wiki/o%C3%ADr#Spanish
				occupy    https://en.wiktionary.org/wiki/ocupar#Spanish
				resemble  https://en.wiktionary.org/wiki/semejar#Spanish
				rest      https://en.wiktionary.org/wiki/reposar#Spanish
				see       https://en.wiktionary.org/wiki/ver#Spanish
				show      https://en.wiktionary.org/wiki/mostrar#Spanish
				startle   https://en.wiktionary.org/wiki/atemorizar#Spanish # "frighten"
				swim      https://en.wiktionary.org/wiki/nadar#Spanish
				walk      https://en.wiktionary.org/wiki/caminar#Spanish
				warm      https://en.wiktionary.org/wiki/calentar#Spanish
				watch     https://en.wiktionary.org/wiki/mirar#Spanish
				work      https://en.wiktionary.org/wiki/trabajar#Spanish

				have      https://en.wiktionary.org/wiki/haber#Spanish
				have-in-possession https://en.wiktionary.org/wiki/tener#Spanish
				go        https://en.wiktionary.org/wiki/ir#Spanish
				love      https://en.wiktionary.org/wiki/amar#Spanish
				fear      https://en.wiktionary.org/wiki/temer#Spanish
				part      https://en.wiktionary.org/wiki/partir#Spanish
				know      https://en.wiktionary.org/wiki/conocer#Spanish
				drive     https://en.wiktionary.org/wiki/conducir#Spanish
			''')
		)
	)
)


print('TAMIL')
write('data/inflection/dravidian/tamil/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Tamil'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81#Tamil
				attention 
				bird      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%B1%E0%AE%B5%E0%AF%88#Tamil
				boat      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%9F%E0%AE%95%E0%AF%81#Tamil
				book      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AF%81%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AE%95%E0%AE%AE%E0%AF%8D#Tamil
				brother   https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%95%E0%AF%8B%E0%AE%A4%E0%AE%B0%E0%AE%A9%E0%AF%8D#Tamil
				bug       https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%A3%E0%AF%8D%E0%AE%9F%E0%AF%81#Tamil
				clothing  https://en.wiktionary.org/wiki/%E0%AE%86%E0%AE%9F%E0%AF%88#Tamil
				daughter  https://en.wiktionary.org/wiki/%E0%AE%AE%E0%AE%95%E0%AE%B3%E0%AF%8D#Tamil
				dog       https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AE%BE%E0%AE%AF%E0%AF%8D#Tamil
				door      https://en.wiktionary.org/wiki/%E0%AE%95%E0%AE%A4%E0%AE%B5%E0%AF%81#Tamil
				drum      
				enemy     https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%95%E0%AF%88%E0%AE%B5%E0%AE%A9%E0%AF%8D#Tamil
				fire      https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AF%86%E0%AE%B0%E0%AF%81%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AF%81#Tamil
				food      https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%BE%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%BE%E0%AE%9F%E0%AF%81#Tamil
				gift      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%B0%E0%AE%BF%E0%AE%9A%E0%AF%81#Tamil
				glass     https://en.wiktionary.org/wiki/%E0%AE%95%E0%AE%A3%E0%AF%8D%E0%AE%A3%E0%AE%BE%E0%AE%9F%E0%AE%BF#Tamil
				guard     
				horse     https://en.wiktionary.org/wiki/%E0%AE%95%E0%AF%81%E0%AE%A4%E0%AE%BF%E0%AE%B0%E0%AF%88#Tamil
				house     https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AF%80%E0%AE%9F%E0%AF%81#Tamil
				livestock 
				love      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%BE%E0%AE%9A%E0%AE%AE%E0%AF%8D#Tamil
				idea      
				man       https://en.wiktionary.org/wiki/%E0%AE%86%E0%AE%A3%E0%AF%8D#Tamil
				money     https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%A3%E0%AE%AE%E0%AF%8D#Tamil
				monster   
				name      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AF%86%E0%AE%AF%E0%AE%B0%E0%AF%8D#Tamil
				rock      https://en.wiktionary.org/wiki/%E0%AE%95%E0%AE%B2%E0%AF%8D#Tamil
				rope      https://en.wiktionary.org/wiki/%E0%AE%95%E0%AE%AF%E0%AE%BF%E0%AE%B1%E0%AF%81#Tamil
				size      
				son       https://en.wiktionary.org/wiki/%E0%AE%AE%E0%AE%95%E0%AE%A9%E0%AF%8D#Tamil
				sound     https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AE%AE%E0%AF%8D#Tamil
				warmth    https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AF%82%E0%AE%9F%E0%AF%81#Tamil
				water     https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AF%80%E0%AE%B0%E0%AF%8D#Tamil
				way       https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%B4%E0%AE%BF#Tamil
				wind      https://en.wiktionary.org/wiki/%E0%AE%95%E0%AE%BE%E0%AE%B1%E0%AF%8D%E0%AE%B1%E0%AF%81#Tamil
				window    https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%BE%E0%AE%B3%E0%AE%B0%E0%AE%AE%E0%AF%8D#Tamil
				woman     https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AF%86%E0%AE%A3%E0%AF%8D#Tamil
				work      https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AF%87%E0%AE%B2%E0%AF%88#Tamil
			''')
		)
	)
)


write('data/inflection/dravidian/tamil/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Tamil'), 
			caching.crawl('''
				appear    
				be-inherently 
				be-momentarily
				change    https://en.wiktionary.org/wiki/%E0%AE%AE%E0%AE%BE%E0%AE%B1%E0%AF%8D%E0%AE%B1%E0%AF%81#Tamil
				climb     https://en.wiktionary.org/wiki/%E0%AE%8F%E0%AE%B1%E0%AF%81#Tamil
				crawl     
				cool      
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%BE%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%BF%E0%AE%9F%E0%AF%81#Tamil
				endure    
				fall      https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%BF%E0%AE%B4%E0%AF%81#Tamil
				fly       https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%B1#Tamil
				flow      
				hear      https://en.wiktionary.org/wiki/%E0%AE%95%E0%AF%87%E0%AE%B3%E0%AF%8D#Tamil
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%BE%E0%AE%B0%E0%AF%8D#Tamil
				show      
				startle   
				swim      https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AF%80%E0%AE%A8%E0%AF%8D%E0%AE%A4%E0%AF%81#Tamil
				walk      https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AE%9F#Tamil
				warm      
				watch     
				work      
			''')
		)
	)
)

print('TURKISH')
write('data/inflection/turkic/turkish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Turkish', 'tr'), 
			caching.crawl('''
				animal    https://en.wiktionary.org/wiki/hayvan#Turkish
				attention 
				bird      https://en.wiktionary.org/wiki/ku%C5%9F#Turkish
				boat      https://en.wiktionary.org/wiki/kay%C4%B1k#Turkish
				book      https://en.wiktionary.org/wiki/kitap#Turkish
				brother   https://en.wiktionary.org/wiki/karde%C5%9F#Turkish
				bug       https://en.wiktionary.org/wiki/b%C3%B6cek#Turkish
				clothing  https://en.wiktionary.org/wiki/giysi#Turkish
				daughter  https://en.wiktionary.org/wiki/k%C4%B1z#Turkish
				dog       https://en.wiktionary.org/wiki/k%C3%B6pek#Turkish
				door      https://en.wiktionary.org/wiki/kap%C4%B1#Turkish
				drum      https://en.wiktionary.org/wiki/davul#Turkish
				enemy     https://en.wiktionary.org/wiki/d%C3%BC%C5%9Fman#Turkish
				fire      https://en.wiktionary.org/wiki/ate%C5%9F#Turkish
				food      https://en.wiktionary.org/wiki/yiyecek#Turkish
				gift      https://en.wiktionary.org/wiki/hediye#Turkish
				glass     https://en.wiktionary.org/wiki/cam#Turkish
				guard     
				horse     https://en.wiktionary.org/wiki/at#Turkish
				house     https://en.wiktionary.org/wiki/hane#Turkish
				livestock https://en.wiktionary.org/wiki/mal#Turkish
				love      https://en.wiktionary.org/wiki/sevgi#Turkish
				idea      https://en.wiktionary.org/wiki/d%C3%BC%C5%9F%C3%BCnce#Turkish
				man       https://en.wiktionary.org/wiki/erkek#Turkish
				money     https://en.wiktionary.org/wiki/para#Turkish
				monster   https://en.wiktionary.org/wiki/canavar#Turkish
				name      https://en.wiktionary.org/wiki/isim#Turkish
				rock      https://en.wiktionary.org/wiki/halat#Turkish
				rope      
				size      https://en.wiktionary.org/wiki/boy#Turkish
				son       https://en.wiktionary.org/wiki/o%C4%9Ful#Turkish
				sound     https://en.wiktionary.org/wiki/ses#Turkish
				warmth    https://en.wiktionary.org/wiki/%C4%B1s%C4%B1#Turkish
				water     https://en.wiktionary.org/wiki/su#Turkish
				way       https://en.wiktionary.org/wiki/yol#Turkish
				wind      https://en.wiktionary.org/wiki/yel#Turkish
				window    https://en.wiktionary.org/wiki/pencere#Turkish
				woman     https://en.wiktionary.org/wiki/kad%C4%B1n#Turkish
				work      https://en.wiktionary.org/wiki/i%C5%9F#Turkish
			''')
		)
	)
)


write('data/inflection/turkic/turkish/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Turkish', 'tr'), 
			caching.crawl('''
				appear    
				be-inherently 
				be-momentarily
				change    https://en.wiktionary.org/wiki/de%C4%9Fi%C5%9Ftirmek#Turkish
				climb     https://en.wiktionary.org/wiki/t%C4%B1rmanmak#Turkish
				crawl     
				cool      https://en.wiktionary.org/wiki/so%C4%9Futmak#Turkish
				direct    
				displease 
				eat       https://en.wiktionary.org/wiki/yemek#Turkish
				endure    
				fall      https://en.wiktionary.org/wiki/d%C3%BC%C5%9Fmek#Turkish
				fly       https://en.wiktionary.org/wiki/u%C3%A7mak#Turkish
				flow      
				hear      https://en.wiktionary.org/wiki/i%C5%9Fitmek#Turkish
				occupy    
				resemble  https://en.wiktionary.org/wiki/benzemek#Turkish
				rest      
				see       https://en.wiktionary.org/wiki/g%C3%B6rmek#Turkish
				show      https://en.wiktionary.org/wiki/g%C3%B6stermek#Turkish
				startle   https://en.wiktionary.org/wiki/korkutmak#Turkish # "frighten"
				swim      https://en.wiktionary.org/wiki/y%C3%BCzmek#Turkish
				walk      https://en.wiktionary.org/wiki/y%C3%BCr%C3%BCmek#Turkish
				warm      
				watch     https://en.wiktionary.org/wiki/seyretmek#Turkish
				work      https://en.wiktionary.org/wiki/%C3%A7al%C4%B1%C5%9Fmak#Turkish
			''')
		)
	)
)

print('ENGLISH/MIDDLE')
write('data/inflection/indo-european/germanic/english/middle/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Noun', ['Declension','Inflection'], 'Middle_English', 'enm'), 
			caching.crawl('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/brid#Middle_English
				boat      
				book      
				brother   
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/hound#Middle_English
				door      
				drum      
				enemy     
				fire      
				food      
				gift      
				glass     
				guard     
				horse     
				house     
				livestock 
				love      
				idea      
				man       
				money     
				monster   
				name      
				rock      
				rope      
				size      
				son       
				sound     
				warmth    
				water     
				way       
				wind      
				window    
				woman     
				work      
			''')
		)
	)
)


write('data/inflection/indo-european/germanic/english/middle/scraped-verbs.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Verb', ['Conjugation','Inflection'], 'Middle_English', 'enm'), 
			caching.crawl('''
				appear    
				be-inherently  https://en.wiktionary.org/wiki/been#Middle_English
				be-momentarily 
				change    https://en.wiktionary.org/wiki/wenden#Middle_English
				climb     https://en.wiktionary.org/wiki/climben#Middle_English
				crawl     
				cool      
				direct    https://en.wiktionary.org/wiki/dressen#Middle_English
				displease 
				eat       https://en.wiktionary.org/wiki/eten#Middle_English
				endure    https://en.wiktionary.org/wiki/enduren#Middle_English
				fall      https://en.wiktionary.org/wiki/fallen#Middle_English
				fly       https://en.wiktionary.org/wiki/flien#Middle_English
				flow      https://en.wiktionary.org/wiki/flowen#Middle_English
				hear      https://en.wiktionary.org/wiki/heren#Middle_English
				occupy    
				resemble  
				rest      
				see       https://en.wiktionary.org/wiki/seen#Middle_English
				show      https://en.wiktionary.org/wiki/schewen#Middle_English
				startle   https://en.wiktionary.org/wiki/fryghten#Middle_English # "frighten"
				swim      https://en.wiktionary.org/wiki/swymmen#Middle_English
				walk      https://en.wiktionary.org/wiki/walken#Middle_English
				warm      
				watch     https://en.wiktionary.org/wiki/wacche#Middle_English
				work      https://en.wiktionary.org/wiki/werken#Middle_English
			''')
		)
	)
)
