import time

import requests
from bs4 import BeautifulSoup

with open('glosses.tsv','r') as file:
	content = file.read()
	for row in content.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) == 6:
				_, part_of_speech, intent, lexeme, url, gloss = parameters
				time.sleep(1) # rate limit for kindness
				html = requests.get(url,headers={'User-Agent': 
					'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
				}).text
				soup = BeautifulSoup(html)
				glosses = [[*parameters, translation['lang'], 'https://en.wiktionary.org'+translation.find('a')['href'], translation.text]
					for table in soup.find_all('table') 
					if table.has_attr('data-gloss') and
					gloss in table.attrs['data-gloss']
					for translation in table.find_all('span')
					if translation.has_attr('lang') 
					and translation.find('a')
					and '/wiki/' in translation.find('a')['href']
				]
				print('\n'.join(['\t'.join(gloss) for gloss in glosses]))

