
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

