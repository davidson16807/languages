import time

import requests
from bs4 import BeautifulSoup


with open('minimal-vocabulary.tsv','r') as file:
	content = file.read()
	for row in content.split('\n'):
		if not row.startswith('#'):
			parameters = row.split('\t')
			if len(parameters) > 5:
				_, url, intent, lemma, part_of_speech = parameters[:5]
				if url:
					time.sleep(1) # rate limit for kindness
					html = requests.get(url,headers={'User-Agent': 
						'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
					}).text
					soup = BeautifulSoup(html)
					header = lambda level_id: [f'h{i}' for i in range(level_id,7)]
					part_of_speech_section = soup.find(header(1), text=part_of_speech.strip().title())
					if part_of_speech_section:
						glosses = [[_, part_of_speech, intent, lemma, url, table.attrs['data-gloss']]
							for table in part_of_speech_section.find_all_next('table') 
							if table.has_attr('data-gloss')
						]
						print('\n'.join(['\t'.join(gloss) for gloss in glosses]))
