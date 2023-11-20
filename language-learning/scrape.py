
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
	def scrape(self, html, lemma_urls):
		for lemma_url in lemma_urls:
			if len(lemma_url)==2:
				(lemma, url) = lemma_url
				time.sleep(1) # rate limit for kindness
				soup = BeautifulSoup(requests.get(url).text)
				bunched = self.ops.bunch(
					Uniform([lemma]), 
					html.parse(soup))
				# print a progress indicator since rate limiting slows us down considerably
				print('\t'.join(['    ' if bunched else 'FAIL', lemma, url]))
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
	def __init__(self, ops, language_id, language_code=None, table_count=1):
		self.ops = ops
		self.language_id = language_id
		self.language_code = language_code
		self.table_count = table_count
	def body(self, content): 
		def extract(source, extractions):
			remainder = source.text
			for extraction in extractions:
				remainder = remainder.replace(extraction.text, '')
			return [remainder, *[extraction.text for extraction in extractions]]
		cells = {}
		for (y, row) in enumerate(content.select('tr')):
			x = 0
			for cell in row.select('td,th'):
				while (x,y) in cells: x+=1
				colspan = int(cell.attrs['colspan']) if 'colspan' in cell.attrs else 1
				rowspan = int(cell.attrs['rowspan']) if 'rowspan' in cell.attrs else 1
				lines = (extract(cell, cell.select('span.tr')) if cell.name == 'td' else [cell.text.lower()])
				m = len(lines)
				for dx in range(colspan):
					for dy in range(rowspan):
						for (i,line) in enumerate(lines):
							cells[(x+m*dx+i,y+dy)] = line
		lx = max([0,*[x+1 for (x,y) in cells.keys()]])
		ly = max([0,*[y+1 for (x,y) in cells.keys()]])
		for y in range(ly):
			yield [(cells[(x,y)] if (x,y) in cells else '') for x in range(lx)]
	def parse(self, soup):
		language_section =  soup.find('span', id=self.language_id)
		part_of_speech_section = soup.find_next('span', text='Noun')
		for section in language_section.find_all_next('span', text=['Declension','Inflection']):
			for i in range(self.table_count):
				section2 = section.find_next('table')
				if section2:
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
		if dialect:
			return dialect.text.lower()
		return head.text or ''
	def parse(self, soup):
		for frame in soup.select('.NavFrame'):
			for row in self.ops.bunch(
					Uniform([self.dialect(frame.select_one('.NavHead'))]), 
					self.body(frame.select_one('.NavContent'))):
				yield row

ops = RowMajorTableOps()
scraping = TableScraping(ops)
parsing = TokenParsing()
formatting = RowMajorTableText('\t','\n')

print('GREEK/ANCIENT')
write('data/inflection/indo-european/greek/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(GreekRowMajorWikiTableHtml(ops),
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%CE%B6%E1%BF%B7%CE%BF%CE%BD#Ancient_Greek
				attention https://en.wiktionary.org/wiki/%CF%86%CF%81%CE%BF%CE%BD%CF%84%CE%AF%CF%82#Ancient_Greek
				bird      https://en.wiktionary.org/wiki/%E1%BD%84%CF%81%CE%BD%CE%B9%CF%82#Ancient_Greek
				boat      https://en.wiktionary.org/wiki/%CE%BD%CE%B1%E1%BF%A6%CF%82#Ancient_Greek
				book      https://en.wiktionary.org/wiki/%CE%B2%CE%B9%CE%B2%CE%BB%CE%AF%CE%BF%CE%BD#Ancient_Greek
				bug       https://en.wiktionary.org/wiki/%E1%BC%94%CE%BD%CF%84%CE%BF%CE%BC%CE%BF%CE%BD#Ancient_Greek
				dog       https://en.wiktionary.org/wiki/%CE%BA%CF%8D%CF%89%CE%BD#Ancient_Greek
				clothing  https://en.wiktionary.org/wiki/%E1%BC%90%CF%83%CE%B8%CE%AE%CF%82#Ancient_Greek
				daughter  https://en.wiktionary.org/wiki/%CE%B8%CF%85%CE%B3%CE%AC%CF%84%CE%B7%CF%81#Ancient_Greek
				drum      https://en.wiktionary.org/wiki/%CF%84%CF%8D%CE%BC%CF%80%CE%B1%CE%BD%CE%BF%CE%BD#Ancient_Greek
				enemy     https://en.wiktionary.org/wiki/%E1%BC%90%CF%87%CE%B8%CF%81%CF%8C%CF%82#Ancient_Greek
				fire      https://en.wiktionary.org/wiki/%CF%80%E1%BF%A6%CF%81#Ancient_Greek
				food      https://en.wiktionary.org/wiki/%CE%B2%CF%81%E1%BF%B6%CE%BC%CE%B1#Ancient_Greek
				food      https://en.wiktionary.org/wiki/%CE%B5%E1%BC%B6%CE%B4%CE%B1%CF%81#Ancient_Greek
				gift      https://en.wiktionary.org/wiki/%CE%B4%E1%BF%B6%CF%81%CE%BF%CE%BD#Ancient_Greek
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
				son       https://en.wiktionary.org/wiki/%CF%85%E1%BC%B1%CF%8C%CF%82#Ancient_Greek
				sound     https://en.wiktionary.org/wiki/%E1%BC%A6%CF%87%CE%BF%CF%82#Ancient_Greek
				warmth    https://en.wiktionary.org/wiki/%CE%B8%CE%AD%CF%81%CE%BC%CE%B7#Ancient_Greek
				water     https://en.wiktionary.org/wiki/%E1%BD%95%CE%B4%CF%89%CF%81#Ancient_Greek
				way       https://en.wiktionary.org/wiki/%CE%BA%CE%AD%CE%BB%CE%B5%CF%85%CE%B8%CE%BF%CF%82#Ancient_Greek
				wind      https://en.wiktionary.org/wiki/%E1%BC%84%CE%BD%CE%B5%CE%BC%CE%BF%CF%82#Ancient_Greek
				window    https://en.wiktionary.org/wiki/%CE%B8%CF%85%CF%81%CE%AF%CF%82#Ancient_Greek
				woman     https://en.wiktionary.org/wiki/%CE%B3%CF%85%CE%BD%CE%AE#Ancient_Greek
				work      https://en.wiktionary.org/wiki/%E1%BC%94%CF%81%CE%B3%CE%BF%CE%BD#Ancient_Greek

				young-man https://en.wiktionary.org/wiki/%CE%BD%CE%B5%CE%B1%CE%BD%CE%AF%CE%B1%CF%82
				soldier   https://en.wiktionary.org/wiki/%CF%83%CF%84%CF%81%CE%B1%CF%84%CE%B9%CF%8E%CF%84%CE%B7%CF%82
				polity    https://en.wiktionary.org/wiki/%CF%80%CE%BF%CE%BB%CE%B9%CF%84%CE%B5%CE%AF%CE%B1
				village   https://en.wiktionary.org/wiki/%CE%BA%CF%8E%CE%BC%CE%B7
				person    https://en.wiktionary.org/wiki/%E1%BC%84%CE%BD%CE%B8%CF%81%CF%89%CF%80%CE%BF%CF%82
				street    https://en.wiktionary.org/wiki/%E1%BD%81%CE%B4%CF%8C%CF%82
				circumnavigation https://en.wiktionary.org/wiki/%CF%80%CE%B5%CF%81%CE%AF%CF%80%CE%BB%CE%BF%CF%85%CF%82
				bone      https://en.wiktionary.org/wiki/%E1%BD%80%CF%83%CF%84%CE%BF%E1%BF%A6%CE%BD
				hero      https://en.wiktionary.org/wiki/%E1%BC%A5%CF%81%CF%89%CF%82
				fish      https://en.wiktionary.org/wiki/%E1%BC%B0%CF%87%CE%B8%CF%8D%CF%82
				oak       https://en.wiktionary.org/wiki/%CE%B4%CF%81%E1%BF%A6%CF%82
				city      https://en.wiktionary.org/wiki/%CF%80%CF%8C%CE%BB%CE%B9%CF%82
				axe       https://en.wiktionary.org/wiki/%CF%80%CE%AD%CE%BB%CE%B5%CE%BA%CF%85%CF%82
				town      https://en.wiktionary.org/wiki/%E1%BC%84%CF%83%CF%84%CF%85
				master    https://en.wiktionary.org/wiki/%CE%B2%CE%B1%CF%83%CE%B9%CE%BB%CE%B5%CF%8D%CF%82
				old-woman https://en.wiktionary.org/wiki/%CE%B3%CF%81%CE%B1%E1%BF%A6%CF%82
				cow       https://en.wiktionary.org/wiki/%CE%B2%CE%BF%E1%BF%A6%CF%82
				echo      https://en.wiktionary.org/wiki/%E1%BC%A0%CF%87%CF%8E
				Clio      https://en.wiktionary.org/wiki/%CE%9A%CE%BB%CE%B5%CE%B9%CF%8E
				crow      https://en.wiktionary.org/wiki/%CE%BA%CF%8C%CF%81%CE%B1%CE%BE
				vulture   https://en.wiktionary.org/wiki/%CE%B3%CF%8D%CF%88
				rug       https://en.wiktionary.org/wiki/%CF%84%CE%AC%CF%80%CE%B7%CF%82
				giant     https://en.wiktionary.org/wiki/%CE%B3%CE%AF%CE%B3%CE%B1%CF%82
				tooth     https://en.wiktionary.org/wiki/%E1%BD%80%CE%B4%CE%BF%CF%8D%CF%82
				old-man   https://en.wiktionary.org/wiki/%CE%B3%CE%AD%CF%81%CF%89%CE%BD
				property  https://en.wiktionary.org/wiki/%CE%BA%CF%84%E1%BF%86%CE%BC%CE%B1
				Greek     https://en.wiktionary.org/wiki/%E1%BC%9D%CE%BB%CE%BB%CE%B7%CE%BD
				winter    https://en.wiktionary.org/wiki/%CF%87%CE%B5%CE%B9%CE%BC%CF%8E%CE%BD
				Titan     https://en.wiktionary.org/wiki/%CE%A4%CE%B9%CF%84%CE%AC%CE%BD
				light-ray https://en.wiktionary.org/wiki/%E1%BC%80%CE%BA%CF%84%CE%AF%CF%82
				shepherd  https://en.wiktionary.org/wiki/%CF%80%CE%BF%CE%B9%CE%BC%CE%AE%CE%BD
				guide     https://en.wiktionary.org/wiki/%E1%BC%A1%CE%B3%CE%B5%CE%BC%CF%8E%CE%BD
				neighbor  https://en.wiktionary.org/wiki/%CE%B3%CE%B5%CE%AF%CF%84%CF%89%CE%BD
				ichor     https://en.wiktionary.org/wiki/%E1%BC%B0%CF%87%CF%8E%CF%81
				chaff     https://en.wiktionary.org/wiki/%E1%BC%80%CE%B8%CE%AE%CF%81
				orator    https://en.wiktionary.org/wiki/%E1%BF%A5%CE%AE%CF%84%CF%89%CF%81
				father    https://en.wiktionary.org/wiki/%CF%80%CE%B1%CF%84%CE%AE%CF%81
				Demeter   https://en.wiktionary.org/wiki/%CE%94%CE%B7%CE%BC%CE%AE%CF%84%CE%B7%CF%81
				Socrates  https://en.wiktionary.org/wiki/%CE%A3%CF%89%CE%BA%CF%81%CE%AC%CF%84%CE%B7%CF%82
				Pericles  https://en.wiktionary.org/wiki/%CE%A0%CE%B5%CF%81%CE%B9%CE%BA%CE%BB%E1%BF%86%CF%82
				arrow     https://en.wiktionary.org/wiki/%CE%B2%CE%AD%CE%BB%CE%BF%CF%82
	            foundation https://en.wiktionary.org/wiki/%E1%BC%94%CE%B4%CE%B1%CF%86%CE%BF%CF%82#Ancient_Greek
	            shame     https://en.wiktionary.org/wiki/%CE%B1%E1%BC%B0%CE%B4%CF%8E%CF%82#Ancient_Greek
	            Ares      https://en.wiktionary.org/wiki/%E1%BC%8C%CF%81%CE%B7%CF%82
	            Thales    https://en.wiktionary.org/wiki/%CE%98%CE%B1%CE%BB%E1%BF%86%CF%82
	            Oedipus   https://en.wiktionary.org/wiki/%CE%9F%E1%BC%B0%CE%B4%CE%AF%CF%80%CE%BF%CF%85%CF%82
	            Apollo    https://en.wiktionary.org/wiki/%E1%BC%88%CF%80%CF%8C%CE%BB%CE%BB%CF%89%CE%BD
	            knee      https://en.wiktionary.org/wiki/%CE%B3%CF%8C%CE%BD%CF%85
	            wood      https://en.wiktionary.org/wiki/%CE%B4%CF%8C%CF%81%CF%85
	            Zeus      https://en.wiktionary.org/wiki/%CE%96%CE%B5%CF%8D%CF%82
	            liver     https://en.wiktionary.org/wiki/%E1%BC%A7%CF%80%CE%B1%CF%81
	            ship      https://en.wiktionary.org/wiki/%CE%BD%CE%B1%E1%BF%A6%CF%82
	            ear       https://en.wiktionary.org/wiki/%CE%BF%E1%BD%96%CF%82
	            hand      https://en.wiktionary.org/wiki/%CF%87%CE%B5%CE%AF%CF%81
			''')
		)
	)
)

print('ARABIC')
write('data/inflection/semitic/arabic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Arabic', 'ar'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%D8%AD%D9%8A%D9%88%D8%A7%D9%86#Arabic
				attention https://en.wiktionary.org/wiki/%D8%A7%D9%87%D8%AA%D9%85%D8%A7%D9%85#Arabic
				bird      https://en.wiktionary.org/wiki/%D8%B7%D8%A7%D8%A6%D8%B1#Arabic
				boat      https://en.wiktionary.org/wiki/%D9%83%D8%AA%D8%A7%D8%A8#Arabic
				book      https://en.wiktionary.org/wiki/%D9%83%D8%AA%D8%A7%D8%A8#Arabic
				bug       https://en.wiktionary.org/wiki/%D8%AD%D8%B4%D8%B1%D8%A9#Arabic
				clothing  https://en.wiktionary.org/wiki/%D9%85%D9%84%D8%A7%D8%A8%D8%B3#Arabic
				daughter  https://en.wiktionary.org/wiki/%D8%A7%D8%A8%D9%86%D8%A9#Arabic
				dog       https://en.wiktionary.org/wiki/%D9%83%D9%84%D8%A8#Arabic
				drum      https://en.wiktionary.org/wiki/%D8%B7%D8%A8%D9%84#Arabic
				enemy     https://en.wiktionary.org/wiki/%D8%B9%D8%AF%D9%88#Arabic
				fire      https://en.wiktionary.org/wiki/%D9%86%D8%A7%D8%B1#Arabic
				food      https://en.wiktionary.org/wiki/%D8%B7%D8%B9%D8%A7%D9%85#Arabic
				gift      https://en.wiktionary.org/wiki/%D9%87%D8%AF%D9%8A%D8%A9#Arabic
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

print('BASQUE')
write('data/inflection/basque/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Basque', 'eu'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/animalia#Basque
				attention https://en.wiktionary.org/wiki/gogo#Basque
				bird      https://en.wiktionary.org/wiki/txori#Basque
				boat      https://en.wiktionary.org/wiki/txalupa#Basque
				book      https://en.wiktionary.org/wiki/liburu#Basque
				bug       https://en.wiktionary.org/wiki/zomorro#Basque
				clothing  https://en.wiktionary.org/wiki/jantzi#Basque
				daughter  https://en.wiktionary.org/wiki/alaba#Basque
				dog       https://en.wiktionary.org/wiki/txakur#Basque
				drum      https://en.wiktionary.org/wiki/danbor#Basque
				enemy     https://en.wiktionary.org/wiki/janari#Basque
				fire      https://en.wiktionary.org/wiki/su#Basque
				food      https://en.wiktionary.org/wiki/janari#Basque
				gift      
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

print('EGYPTIAN')
write('data/inflection/egyptian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Egyptian', 'egy'), 
			parsing.tokenpoints('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/%EA%9C%A3pd#Egyptian
				boat      https://en.wiktionary.org/wiki/jmw#Egyptian
				book      https://en.wiktionary.org/wiki/m%E1%B8%8F%EA%9C%A3t#Egyptian
				bug       https://en.wiktionary.org/wiki/%EA%9C%A5p%C5%A1%EA%9C%A3y#Egyptian
				clothing  https://en.wiktionary.org/wiki/mn%E1%B8%ABt#Egyptian
				daughter  https://en.wiktionary.org/wiki/z%EA%9C%A3t#Egyptian
				dog       https://en.wiktionary.org/wiki/%E1%B9%AFzm#Egyptian
				drum      
				enemy     https://en.wiktionary.org/wiki/%E1%B8%ABftj#Egyptian
				fire      https://en.wiktionary.org/wiki/s%E1%B8%8Ft#Egyptian
				food      https://en.wiktionary.org/wiki/%C5%A1bw#Egyptian
				gift      
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

print('FINNISH')
write('data/inflection/uralic/finnish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Finnish', 'fi',2), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/el%C3%A4in#Finnish
				attention https://en.wiktionary.org/wiki/huomio#Finnish
				bird      https://en.wiktionary.org/wiki/lintu#Finnish
				boat      https://en.wiktionary.org/wiki/vene#Finnish
				book      https://en.wiktionary.org/wiki/kirja#Finnish
				bug       https://en.wiktionary.org/wiki/%C3%B6t%C3%B6kk%C3%A4#Finnish
				clothing  https://en.wiktionary.org/wiki/vaatetus#Finnish
				daughter  https://en.wiktionary.org/wiki/tyt%C3%A4r#Finnish
				dog       https://en.wiktionary.org/wiki/koira#Finnish
				drum      https://en.wiktionary.org/wiki/rumpu#Finnish
				enemy     https://en.wiktionary.org/wiki/vihollinen#Finnish
				fire      https://en.wiktionary.org/wiki/tuli#Finnish
				food      https://en.wiktionary.org/wiki/ruoka#Finnish
				gift      https://en.wiktionary.org/wiki/lahja#Finnish
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

print('GEORGIAN')
write('data/inflection/kartvelian/georgian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Georgian', 'ka',2), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%E1%83%AA%E1%83%AE%E1%83%9D%E1%83%95%E1%83%94%E1%83%9A%E1%83%98#Georgian
				attention https://en.wiktionary.org/wiki/%E1%83%A7%E1%83%A3%E1%83%A0%E1%83%90%E1%83%93%E1%83%A6%E1%83%94%E1%83%91%E1%83%90#Georgian
				bird      https://en.wiktionary.org/wiki/%E1%83%A9%E1%83%98%E1%83%A2%E1%83%98#Georgian
				boat      https://en.wiktionary.org/wiki/%E1%83%9C%E1%83%90%E1%83%95%E1%83%98#Georgian
				book      https://en.wiktionary.org/wiki/%E1%83%AC%E1%83%98%E1%83%92%E1%83%9C%E1%83%98#Georgian
				bug       https://en.wiktionary.org/wiki/%E1%83%9B%E1%83%AC%E1%83%94%E1%83%A0%E1%83%98#Georgian
				clothing  https://en.wiktionary.org/wiki/%E1%83%A2%E1%83%90%E1%83%9C%E1%83%A1%E1%83%90%E1%83%AA%E1%83%9B%E1%83%94%E1%83%9A%E1%83%98#Georgian
				daughter  https://en.wiktionary.org/wiki/%E1%83%90%E1%83%A1%E1%83%A3%E1%83%9A%E1%83%98#Georgian
				dog       https://en.wiktionary.org/wiki/%E1%83%AB%E1%83%90%E1%83%A6%E1%83%9A%E1%83%98#Georgian
				drum      https://en.wiktionary.org/wiki/%E1%83%93%E1%83%9D%E1%83%9A%E1%83%98#Georgian
				enemy     https://en.wiktionary.org/wiki/%E1%83%9B%E1%83%A2%E1%83%94%E1%83%A0%E1%83%98#Georgian
				fire      https://en.wiktionary.org/wiki/%E1%83%AA%E1%83%94%E1%83%AA%E1%83%AE%E1%83%9A%E1%83%98#Georgian
				food      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%90%E1%83%99%E1%83%95%E1%83%94%E1%83%91%E1%83%98#Georgian
				gift      https://en.wiktionary.org/wiki/%E1%83%A1%E1%83%90%E1%83%A9%E1%83%A3%E1%83%A5%E1%83%90%E1%83%A0%E1%83%98#Georgian
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

print('GREEK/MODERN')
write('data/inflection/indo-european/greek/modern/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Greek', 'el'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%CE%B6%CF%8E%CE%BF#Greek
				attention https://en.wiktionary.org/wiki/%CF%80%CF%81%CE%BF%CF%83%CE%BF%CF%87%CE%AE#Greek
				bird      https://en.wiktionary.org/wiki/%CF%80%CF%84%CE%B7%CE%BD%CF%8C#Greek
				boat      https://en.wiktionary.org/wiki/%CE%B2%CE%AC%CF%81%CE%BA%CE%B1#Greek
				book      https://en.wiktionary.org/wiki/%CE%B2%CE%B9%CE%B2%CE%BB%CE%AF%CE%BF#Greek
				bug       https://en.wiktionary.org/wiki/%CE%B6%CE%BF%CF%85%CE%B6%CE%BF%CF%8D%CE%BD%CE%B9#Greek
				clothing  https://en.wiktionary.org/wiki/%CF%81%CE%BF%CF%8D%CF%87%CE%BF#Greek
				daughter  https://en.wiktionary.org/wiki/%CE%BA%CF%8C%CF%81%CE%B7#Greek
				dog       https://en.wiktionary.org/wiki/%CF%83%CE%BA%CF%8D%CE%BB%CE%BF%CF%82#Greek
				drum      https://en.wiktionary.org/wiki/%CF%84%CF%8D%CE%BC%CF%80%CE%B1%CE%BD%CE%BF#Greek
				enemy     https://en.wiktionary.org/wiki/%CE%B5%CF%87%CE%B8%CF%81%CF%8C%CF%82#Greek
				fire      https://en.wiktionary.org/wiki/%CF%86%CF%89%CF%84%CE%B9%CE%AC#Greek
				food      https://en.wiktionary.org/wiki/%CF%86%CE%B1%CE%90#Greek
				gift      https://en.wiktionary.org/wiki/%CE%B4%CF%8E%CF%81%CE%BF#Greek
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

print('HEBREW')
write('data/inflection/semitic/hebrew/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Hebrew', 'he'), 
			parsing.tokenpoints('''
				animal    
				attention https://en.wiktionary.org/wiki/%D7%9E%D7%97%D7%A9%D7%91%D7%94#Hebrew
				bird      
				boat      
				book      https://en.wiktionary.org/wiki/%D7%A1%D7%A4%D7%A8#Hebrew
				bug       
				clothing  
				daughter  https://en.wiktionary.org/wiki/%D7%91%D7%AA#Hebrew
				dog       https://en.wiktionary.org/wiki/%D7%9B%D7%9C%D7%91#Hebrew
				drum      
				enemy     
				fire      
				food      https://en.wiktionary.org/wiki/%D7%9E%D7%96%D7%95%D7%9F#Hebrew
				gift      
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

print('HINDI')
write('data/inflection/indo-european/indo-iranian/hindi/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Hindi', 'hi'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%BE%E0%A4%A8%E0%A4%B5%E0%A4%B0#Hindi
				attention https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%A8#Hindi
				bird      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A4%82%E0%A4%9B%E0%A5%80#Hindi
				boat      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A4%BE%E0%A4%B5#Hindi
				book      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%81%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%95#Hindi
				bug       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%80%E0%A4%A1%E0%A4%BC%E0%A4%BE#Hindi
				clothing  https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%8D%E0%A4%B0#Hindi
				daughter  https://en.wiktionary.org/wiki/%E0%A4%AC%E0%A5%87%E0%A4%9F%E0%A5%80#Hindi
				dog       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%81%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%BE#Hindi
				drum      https://en.wiktionary.org/wiki/%E0%A4%A2%E0%A5%8B%E0%A4%B2#Hindi
				enemy     https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%81%E0%A4%B6%E0%A5%8D%E0%A4%AE%E0%A4%A8#Hindi
				fire      https://en.wiktionary.org/wiki/%E0%A4%86%E0%A4%97#Hindi
				food      https://en.wiktionary.org/wiki/%E0%A4%96%E0%A4%BE%E0%A4%A8%E0%A4%BE#Hindi
				gift      https://en.wiktionary.org/wiki/%E0%A4%89%E0%A4%AA%E0%A4%B9%E0%A4%BE%E0%A4%B0#Hindi
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

#TODO: Hittite needs its own custom format that does not rely on language code
print('HITTITE')
write('data/inflection/indo-european/hittite/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Hittite', 'hit',2), 
			parsing.tokenpoints('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/%F0%92%84%A9%F0%92%80%80%F0%92%8A%8F%F0%92%80%B8#Hittite # eagle
				boat      
				book      
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/%F0%92%86%AA%F0%92%89%BF%F0%92%80%B8#Hittite
				drum      
				enemy     
				fire      https://en.wiktionary.org/wiki/%F0%92%89%BA%F0%92%84%B4%F0%92%84%AF#Hittite
				food      https://en.wiktionary.org/wiki/%F0%92%82%8A%F0%92%89%BF%F0%92%80%AD#Hittite # a kind of soup
				gift      
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

print('HUNGARIAN')
write('data/inflection/uralic/hungarian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Hungarian', 'hu',2), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%C3%A1llat#Hungarian
				attention https://en.wiktionary.org/wiki/figyelem#Hungarian
				bird      https://en.wiktionary.org/wiki/mad%C3%A1r#Hungarian
				boat      https://en.wiktionary.org/wiki/cs%C3%B3nak#Hungarian
				book      https://en.wiktionary.org/wiki/k%C3%B6nyv#Hungarian
				bug       https://en.wiktionary.org/wiki/bog%C3%A1r#Hungarian
				clothing  https://en.wiktionary.org/wiki/ruh%C3%A1zat#Hungarian
				daughter  https://en.wiktionary.org/wiki/l%C3%A1ny#Hungarian
				dog       https://en.wiktionary.org/wiki/kutya#Hungarian
				drum      https://en.wiktionary.org/wiki/dob#Hungarian:_drum
				enemy     https://en.wiktionary.org/wiki/ellens%C3%A9g#Hungarian
				fire      https://en.wiktionary.org/wiki/t%C5%B1z#Hungarian
				food      https://en.wiktionary.org/wiki/%C3%A9tel#Hungarian
				gift      https://en.wiktionary.org/wiki/aj%C3%A1nd%C3%A9k#Hungarian
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

print('LATIN')
write('data/inflection/indo-european/romance/latin/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Latin', 'la'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/animal#Latin
				attention https://en.wiktionary.org/wiki/attentio#Latin
				bird      https://en.wiktionary.org/wiki/avis#Latin
				boat      https://en.wiktionary.org/wiki/navis#Latin
				book      https://en.wiktionary.org/wiki/caudex#Latin
				bug       https://en.wiktionary.org/wiki/cimex#Latin
				clothing  https://en.wiktionary.org/wiki/vestis#Latin
				daughter  https://en.wiktionary.org/wiki/filia#Latin
				dog       https://en.wiktionary.org/wiki/canis#Latin
				drum      https://en.wiktionary.org/wiki/tympanum#Latin
				enemy     https://en.wiktionary.org/wiki/inimicus#Latin
				fire      https://en.wiktionary.org/wiki/ignis#Latin
				food      https://en.wiktionary.org/wiki/cibus#Latin
				gift      https://en.wiktionary.org/wiki/donum#Latin
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
		)
	)
)

print('OLD-CHURCH-SLAVONIC')
write('data/inflection/indo-european/slavic/old-church-slavonic/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Old_Church_Slavonic', 'cu'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%D0%B6%D0%B8%D0%B2%D0%BE%D1%82%D1%8A#Old_Church_Slavonic
				attention https://en.wiktionary.org/wiki/%D0%BC%EA%99%91%D1%81%D0%BB%D1%8C#Old_Church_Slavonic
				bird      https://en.wiktionary.org/wiki/%D0%BF%D1%8A%D1%82%D0%B8%D1%86%D0%B0#Old_Church_Slavonic
				boat      https://en.wiktionary.org/wiki/%D0%BB%D0%B0%D0%B4%D0%B8%D0%B8#Old_Church_Slavonic
				book      https://en.wiktionary.org/wiki/%D0%B1%D0%BE%D1%83%D0%BA%EA%99%91#Old_Church_Slavonic
				bug       
				clothing  https://en.wiktionary.org/wiki/%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0#Old_Church_Slavonic
				daughter  https://en.wiktionary.org/wiki/%D0%B4%D1%8A%D1%89%D0%B8#Old_Church_Slavonic
				dog       https://en.wiktionary.org/wiki/%D0%BF%D1%8C%D1%81%D1%8A#Old_Church_Slavonic
				drum      
				enemy     https://en.wiktionary.org/wiki/%D0%B2%D1%80%D0%B0%D0%B3%D1%8A#Old_Church_Slavonic
				fire      
				food      
				gift      
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

print('ENGLISH/OLD')
write('data/inflection/indo-european/germanic/english/old/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Old_English', 'ang'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/nieten#Old_English
				attention https://en.wiktionary.org/wiki/ge%C3%BEoht#Old_English
				bird      https://en.wiktionary.org/wiki/fugol#Old_English
				boat      https://en.wiktionary.org/wiki/bat#Old_English
				book      https://en.wiktionary.org/wiki/boc#Old_English
				bug       https://en.wiktionary.org/wiki/budda#Old_English
				clothing  https://en.wiktionary.org/wiki/scrud#Old_English
				daughter  https://en.wiktionary.org/wiki/dohtor#Old_English
				dog       https://en.wiktionary.org/wiki/hund#Old_English
				drum      
				enemy     https://en.wiktionary.org/wiki/feond#Old_English
				fire      https://en.wiktionary.org/wiki/fyr#Old_English
				food      https://en.wiktionary.org/wiki/foda#Old_English
				gift      https://en.wiktionary.org/wiki/giefu#Old_English
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
				sister    https://en.wiktionary.org/wiki/sweostor
				lamb      https://en.wiktionary.org/wiki/lamb#Old_English
				shoe      https://en.wiktionary.org/wiki/scoh#Old_English
				piglet    https://en.wiktionary.org/wiki/fearh#Old_English
				shadow    https://en.wiktionary.org/wiki/sceadu#Old_English
				meadow    https://en.wiktionary.org/wiki/m%C3%A6d#Old_English
			''')
		)
	)
)

print('QUECHUAN')
write('data/inflection/quechuan/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Quechua', 'qu',2), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/uywa#Quechua
				attention 
				bird      https://en.wiktionary.org/wiki/pisqu#Quechua
				boat      https://en.wiktionary.org/wiki/wamp%27u#Quechua
				book      https://en.wiktionary.org/wiki/liwru#Quechua
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/allqu#Quechua
				drum      
				enemy     https://en.wiktionary.org/wiki/awqa#Quechua
				fire      https://en.wiktionary.org/wiki/nina#Quechua
				food      https://en.wiktionary.org/wiki/mikhuna#Quechua
				gift      
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

print('RUSSIAN')
write('data/inflection/indo-european/slavic/russian/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Russian', 'ru'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%D0%B6%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D0%BE%D0%B5#Russian
				attention https://en.wiktionary.org/wiki/%D0%B2%D0%BD%D0%B8%D0%BC%D0%B0%D0%BD%D0%B8%D0%B5#Russian
				bird      https://en.wiktionary.org/wiki/%D0%BF%D1%82%D0%B8%D1%86%D0%B0#Russian
				boat      https://en.wiktionary.org/wiki/%D0%BB%D0%BE%D0%B4%D0%BA%D0%B0#Russian
				book      https://en.wiktionary.org/wiki/%D0%BA%D0%BD%D0%B8%D0%B3%D0%B8#Russian
				bug       https://en.wiktionary.org/wiki/%D0%B1%D1%83%D0%BA%D0%B0%D1%88%D0%BA%D0%B0#Russian
				clothing  https://en.wiktionary.org/wiki/%D0%BE%D0%B4%D0%B5%D0%B6%D0%B4%D0%B0#Russian
				daughter  https://en.wiktionary.org/wiki/%D0%B4%D0%BE%D1%87%D1%8C#Russian
				dog       https://en.wiktionary.org/wiki/%D1%81%D0%BE%D0%B1%D0%B0%D0%BA%D0%B0#Russian
				drum      https://en.wiktionary.org/wiki/%D0%B1%D0%B0%D1%80%D0%B0%D0%B1%D0%B0%D0%BD#Russian
				enemy     https://en.wiktionary.org/wiki/%D0%B2%D1%80%D0%B0%D0%B3#Russian
				fire      https://en.wiktionary.org/wiki/%D0%BE%D0%B3%D0%BE%D0%BD%D1%8C#Russian
				food      https://en.wiktionary.org/wiki/%D0%B5%D0%B4%D0%B0#Russian
				gift      https://en.wiktionary.org/wiki/%D0%BF%D0%BE%D0%B4%D0%B0%D1%80%D0%BE%D0%BA#Russian
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
				place     https://en.wiktionary.org/wiki/%D0%BC%D0%B5%D1%81%D1%82%D0%B0#Russian
				sea       https://en.wiktionary.org/wiki/%D0%BC%D0%BE%D1%80%D1%8F#Russian
				bone      https://en.wiktionary.org/wiki/%D0%BA%D0%BE%D1%81%D1%82%D1%8C#Russian
				mouse     https://en.wiktionary.org/wiki/%D0%BC%D1%8B%D1%88%D1%8C#Russian
			''')
		)
	)
)

print('SANSKRIT')
write('data/inflection/indo-european/indo-iranian/sanskrit/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Sanskrit', 'sa'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%E0%A4%AE%E0%A5%83%E0%A4%97#Sanskrit
				attention https://en.wiktionary.org/wiki/%E0%A4%A7%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%A8#Sanskrit
				bird      https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%BF#Sanskrit
				boat      https://en.wiktionary.org/wiki/%E0%A4%A8%E0%A5%8C#Sanskrit
				book      https://en.wiktionary.org/wiki/%E0%A4%AA%E0%A5%81%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%95#Sanskrit
				bug       https://en.wiktionary.org/wiki/%E0%A4%9C%E0%A4%A8%E0%A5%8D%E0%A4%A4%E0%A5%81#Sanskrit
				clothing  https://en.wiktionary.org/wiki/%E0%A4%B5%E0%A4%B8%E0%A5%8D%E0%A4%AE%E0%A4%A8%E0%A5%8D#Sanskrit
				daughter  https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A5%81%E0%A4%B9%E0%A4%BF%E0%A4%A4%E0%A5%83#Sanskrit
				dog       https://en.wiktionary.org/wiki/%E0%A4%95%E0%A5%81%E0%A4%B0%E0%A5%8D%E0%A4%95%E0%A5%81%E0%A4%B0#Sanskrit
				drum      https://en.wiktionary.org/wiki/%E0%A4%A2%E0%A5%8B%E0%A4%B2#Hindi
				enemy     https://en.wiktionary.org/wiki/%E0%A4%B6%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A5%81#Sanskrit
				fire      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%97%E0%A5%8D%E0%A4%A8%E0%A4%BF#Sanskrit
				food      https://en.wiktionary.org/wiki/%E0%A4%85%E0%A4%A8%E0%A5%8D%E0%A4%A8#Sanskrit
				gift      https://en.wiktionary.org/wiki/%E0%A4%A6%E0%A4%BE%E0%A4%A8#Sanskrit
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

print('SWEDISH')
write('data/inflection/indo-european/germanic/swedish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Swedish', 'sv'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/djur#Swedish
				attention https://en.wiktionary.org/wiki/uppm%C3%A4rksamhet#Swedish
				bird      https://en.wiktionary.org/wiki/f%C3%A5gel#Swedish
				boat      https://en.wiktionary.org/wiki/b%C3%A5t#Swedish
				book      https://en.wiktionary.org/wiki/bok#Swedish
				bug       https://en.wiktionary.org/wiki/kryp#Swedish
				clothing  https://en.wiktionary.org/wiki/kl%C3%A4der#Swedish
				daughter  https://en.wiktionary.org/wiki/dotter#Swedish
				dog       https://en.wiktionary.org/wiki/hund#Swedish
				drum      https://en.wiktionary.org/wiki/trumma#Swedish
				enemy     https://en.wiktionary.org/wiki/fiende#Swedish
				fire      https://en.wiktionary.org/wiki/eld#Swedish
				food      https://en.wiktionary.org/wiki/mat#Swedish
				gift      https://en.wiktionary.org/wiki/g%C3%A5va#Swedish
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
		)
	)
)

"""

"""

print('TAMIL')
write('data/inflection/dravidian/tamil/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Tamil'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%BF%E0%AE%B2%E0%AE%99%E0%AF%8D%E0%AE%95%E0%AF%81#Tamil
				attention 
				bird      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%B1%E0%AE%B5%E0%AF%88#Tamil
				boat      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%9F%E0%AE%95%E0%AF%81#Tamil
				book      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AF%81%E0%AE%A4%E0%AF%8D%E0%AE%A4%E0%AE%95%E0%AE%AE%E0%AF%8D#Tamil
				bug       https://en.wiktionary.org/wiki/%E0%AE%B5%E0%AE%A3%E0%AF%8D%E0%AE%9F%E0%AF%81#Tamil
				clothing  https://en.wiktionary.org/wiki/%E0%AE%86%E0%AE%9F%E0%AF%88#Tamil
				daughter  https://en.wiktionary.org/wiki/%E0%AE%AE%E0%AE%95%E0%AE%B3%E0%AF%8D#Tamil
				dog       https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AE%BE%E0%AE%AF%E0%AF%8D#Tamil
				drum      
				enemy     https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%95%E0%AF%88%E0%AE%B5%E0%AE%A9%E0%AF%8D#Tamil
				fire      https://en.wiktionary.org/wiki/%E0%AE%A8%E0%AF%86%E0%AE%B0%E0%AF%81%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AF%81#Tamil
				food      https://en.wiktionary.org/wiki/%E0%AE%9A%E0%AE%BE%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AE%BE%E0%AE%9F%E0%AF%81#Tamil
				gift      https://en.wiktionary.org/wiki/%E0%AE%AA%E0%AE%B0%E0%AE%BF%E0%AE%9A%E0%AF%81#Tamil
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

print('TURKISH')
write('data/inflection/turkic/turkish/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Turkish', 'tr'), 
			parsing.tokenpoints('''
				animal    https://en.wiktionary.org/wiki/hayvan#Turkish
				attention 
				bird      https://en.wiktionary.org/wiki/ku%C5%9F#Turkish
				boat      https://en.wiktionary.org/wiki/kay%C4%B1k#Turkish
				book      https://en.wiktionary.org/wiki/kitap#Turkish
				bug       https://en.wiktionary.org/wiki/b%C3%B6cek#Turkish
				clothing  https://en.wiktionary.org/wiki/giysi#Turkish
				daughter  https://en.wiktionary.org/wiki/k%C4%B1z#Turkish
				dog       https://en.wiktionary.org/wiki/k%C3%B6pek#Turkish
				drum      https://en.wiktionary.org/wiki/davul#Turkish
				enemy     https://en.wiktionary.org/wiki/d%C3%BC%C5%9Fman#Turkish
				fire      https://en.wiktionary.org/wiki/ate%C5%9F#Turkish
				food      https://en.wiktionary.org/wiki/yiyecek#Turkish
				gift      https://en.wiktionary.org/wiki/hediye#Turkish
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

print('ENGLISH/MIDDLE')
write('data/inflection/indo-european/germanic/english/middle/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Middle_English', 'enm'), 
			parsing.tokenpoints('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/brid#Middle_English
				boat      
				book      
				bug       
				clothing  
				daughter  
				dog       https://en.wiktionary.org/wiki/hound#Middle_English
				drum      
				enemy     
				fire      
				food      
				gift      
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

print('PROTO-INDO-EUROPEAN/SIHLER')
write('data/inflection/indo-european/proto-indo-european/sihler/scraped-nouns.tsv',
	formatting.format(
		scraping.scrape(RowMajorWikiTableHtml(ops, 'Proto-Indo-European', 'ine-pro'), 
			parsing.tokenpoints('''
				animal    
				attention 
				bird      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9wis
				boat      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/n%C3%A9h%E2%82%82us
				book      
				bug       
				clothing  https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/w%C3%A9stis
				daughter  https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%CA%B0ugh%E2%82%82t%E1%B8%97r
				dog       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/%E1%B8%B1w%E1%B9%93
				drum      
				enemy     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/g%CA%B0%C3%B3stis
				fire      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9h%E2%82%82wr%CC%A5
				food      
				gift      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%C3%A9h%E2%82%83nom
				guard     
				horse     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%81%C3%A9%E1%B8%B1wos
				house     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/d%E1%B9%93m
				livestock https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%A9%E1%B8%B1u
				love      
				idea      
				man       
				money     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82r%CC%A5%C7%B5n%CC%A5t%C3%B3m
				monster   
				name      
				rock      https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9%E1%B8%B1m%C5%8D
				rope      
				size      
				son       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/suHy%C3%BAs
				sound     
				warmth    
				water     https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/h%E2%82%82%C3%A9k%CA%B7eh%E2%82%82
				way       https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/p%C3%B3ntoh%E2%82%81s
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
