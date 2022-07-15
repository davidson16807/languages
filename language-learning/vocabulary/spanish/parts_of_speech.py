from parse_wiktionary import *

for (word, part_of_speech), layer, root in chain_compose(
        lambda max_line_count: raw(max_line_count, filename='../../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        header2('Spanish'),
        part_of_speech_header('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
    )(1e9):
    print(f'{word.lower()}\t{part_of_speech_header.lower()}')
    # print(f'{word.upper():<15} {root}')
