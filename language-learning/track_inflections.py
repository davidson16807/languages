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

parts_of_speech = 'adjective adverb article determiner interjection noun verb'.split()

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

minimal_lemmas = collections.defaultdict(list)
with open('minimal-vocabulary.tsv','r') as file:
	content = file.read()
	for row in content.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) > 5:
				_, url, intent, lemma, part_of_speech = parameters[:5]
				minimal_lemmas[part_of_speech].append((intent, lemma))

language_id_for_code = {
	translation.language_code: translation.language_id
	for translation in translations
	if translation.language_code and translation.language_id
}

with open(f'unscraped.tsv','w') as unscraped_file:

	for target_language_code, output_directory in code_directories:

		scrape_directory = os.path.join('data', 'inflection', output_directory)

		language_translations = [translation 
			for translation in translations 
			if translation.language_code == target_language_code]

		translations_for_part_of_speech_lemma = collections.defaultdict(list)
		for translation in language_translations:
			translations_for_part_of_speech_lemma[translation.part_of_speech, translation.lemma].append(translation)

		for part_of_speech in parts_of_speech:
			if part_of_speech in minimal_lemmas:
				for intent, lemma in minimal_lemmas[part_of_speech]:

					if (part_of_speech, lemma) not in translations_for_part_of_speech_lemma:
						unscraped_file.write('\t'.join([
							part_of_speech, 
							intent,
							lemma, 
							'',
							'',
							target_language_code, 
							'',
							'#' + language_id_for_code[target_language_code] if target_language_code in language_id_for_code else '', 
						])+'\n')

					else:
						part_of_speech_translations = translations_for_part_of_speech_lemma[part_of_speech, lemma]

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
							'\t'.join([
								part_of_speech, 
								intent,
								lemma, 
								'',
								'',
								target_language_code, 
								translation.url,
								'#'+str(translation.language_id), 
							])
							for translation in unscraped
						])+'\n' if unscraped else '')
