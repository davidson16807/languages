import sys
import yaml

from parse_wiktionary import *

foreign_language_config_filename = sys.argv[1]
foreign_language = yaml.load(open(foreign_language_config_filename, 'r'))

for (word, part_of_speech), layer, root in chain_compose(
        lambda max_line_count: raw(max_line_count, filename=foreign_language['wiktionary']), 
        pages, 
        header2(foreign_language['name']),
        part_of_speech_header('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
    )(1e9):
    print(f'{word.lower()}\t{part_of_speech.lower()}')
