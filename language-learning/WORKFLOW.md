
# Developer Workflow

`minimal-vocabulary.tsv`
	↓	`scrape_glosses.py`
`scraped-glosses.tsv`
	↓ 	manual selection
`glosses.tsv`
	↑
	⋅	 → 	`gloss-specializations.tsv`
	↓ 	`scrape_translations.py`
translations.tsv
	↑
	⋅	 → 	`translation-specializations.tsv`, `translation-languages.tsv`
	↓	`scrape_inflections.py`
`data/inflection/**/scraped-*.tsv`
	↓ 	manual cleanup
`data/inflection/**/*.tsv`

`track_inflections.py` can be used to monitor the progress of each language when populating inflections for each lemma