import time

import requests
from bs4 import BeautifulSoup

class Gloss:
	def __init__(self, part_of_speech, intent, lexeme, url, gloss):
		self.part_of_speech = part_of_speech
		self.intent = intent
		self.lexeme = lexeme
		self.url = url
		self.gloss = gloss

def parse_glosses(text):
	glosses = []
	content = file.read()
	for row in content.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) == 6:
				_, part_of_speech, intent, lexeme, url, gloss = parameters
				glosses.append(Gloss(part_of_speech, intent, lexeme, url, gloss))
	return glosses

glosses = []
with open('glosses.tsv','r') as file:
	glosses += parse_glosses(file.read())

with open('gloss-specializations.tsv','r') as file:
	glosses += parse_glosses(file.read())

for gloss in glosses:
	time.sleep(1) # rate limit for kindness
	html = requests.get(gloss.url,headers={'User-Agent': 
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
	}).text
	soup = BeautifulSoup(html)
	translations = [[*parameters, translation['lang'], 'https://en.wiktionary.org'+translation.find('a')['href'], translation.text]
		for table in soup.find_all('table') 
		if table.has_attr('data-gloss') and
		gloss.gloss in table.attrs['data-gloss']
		for translation in table.find_all('span')
		if translation.has_attr('lang') 
		and translation.find('a')
		and '/wiki/' in translation.find('a')['href']
	]
	print('\n'.join(['\t'.join(gloss) for gloss in translations]))

