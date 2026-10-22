import os
import collections

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

parts_of_speech = 'adjectives adverbs articles determiners interjections nouns verbs'.split()

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

with open(f'unscraped.tsv','w') as unscraped_file:

	for target_language_code, output_directory in code_directories:

		scrape_directory = os.path.join('data', 'inflection', output_directory)

		language_translations = [translation 
			for translation in translations 
			if translation.language_code == target_language_code]

		translations_for_part_of_speech = collections.defaultdict(list)
		for translation in language_translations:
			translations_for_part_of_speech[translation.part_of_speech].append(translation)

		for part_of_speech in translations_for_part_of_speech:
			part_of_speech_translations = translations_for_part_of_speech[part_of_speech]

			with open(os.path.join(scrape_directory, f'scraped-{part_of_speech}s.tsv'),'r') as file:
				scraped = {
					row.strip().split('\t')[0]
					for row in file.read().split('\n')
					if row.strip() and not row.startswith('#')
				}

			unscraped = [translation
				for translation in part_of_speech_translations
				if translation.lemma not in scraped
			]

			unscraped_file.write('\n'.join([
				'\t'.join([target_language_code, str(translation.language_id), part_of_speech, translation.lemma, translation.url])
				for translation in unscraped
			])+'\n')
