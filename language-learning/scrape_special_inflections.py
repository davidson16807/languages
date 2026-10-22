
# built-in libraries
import requests
import time

# 3rd party libraries
from bs4 import BeautifulSoup

# in-house libraries
from tools.inflections import write
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
