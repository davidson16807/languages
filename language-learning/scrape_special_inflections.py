
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
				worm      https://en.wiktionary.org/wiki/worm#Middle_English
				work      
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
	worm      
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
	worm      
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
				worm      
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
				worm      https://en.wiktionary.org/wiki/%D8%AF%D9%88%D8%AF%D8%A9#Arabic
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
				worm      
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
				worm      https://en.wiktionary.org/wiki/p%C3%A9ist#Irish
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
				worm      https://en.wiktionary.org/wiki/kurt#Turkish
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
