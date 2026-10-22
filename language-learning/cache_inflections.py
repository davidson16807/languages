# built-in libraries
import collections
import os
import requests
import time

'''
USAGE: python download_html.py

For every (language-code, output-directory) pair in translation-languages.tsv,
the urls of translations in translations.tsv and translation-specializations.tsv whose language code matches are downloaded,
and the html of each url is written to "<output-directory>/<lemma>.html".
Where a lemma has more than one url, the files are named "<lemma>.html", "<lemma>-2.html", "<lemma>-3.html", etc.
'''

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

caching = Caching()

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

	output_directory = os.path.join('cache', output_directory)

	language_translations = [translation 
		for translation in translations 
		if translation.language_code == target_language_code]

	if not language_translations:
		print(f'no translations found for language code: "{target_language_code}"')
		continue

	os.makedirs(output_directory, exist_ok=True)

	for translation in language_translations:
		try:
			url = translation.url.split('#')[0]
			filestem = url.split('/')[-1]
			filepath = os.path.join(output_directory, f'{filestem}.html')
			print('\t'.join([translation.lemma, translation.url, filepath]))
			if not os.path.exists(filepath):
				time.sleep(1) # rate limit for kindness
				headers={'User-Agent': 
					'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
				}
				html = requests.get(url,headers=headers).text
				with open(filepath, 'w', encoding='utf-8') as file:
					file.write(html)
		except Exception as ex:
			print(ex)

