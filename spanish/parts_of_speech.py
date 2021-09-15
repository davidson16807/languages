from parse_wiktionary import *

def part_of_speech(part_of_speech_regex_string):
    part_of_speech_regex = re.compile(part_of_speech_regex_string, re.IGNORECASE)
    def part_of_speech_(entries):
        for word, layer, entry in entries:
            for next_layer in range(1,7):
                header_regex = re.compile('^'+'='*next_layer+'([^=]+)'+'='*next_layer+'\\s*$', re.MULTILINE)
                matches = header_regex.finditer(entry)
                current = None
                next_ = None
                for match in itertools.chain(matches, [None]):
                    current = next_
                    next_ = match
                    if current:
                        header = current.group(1)
                        if part_of_speech_regex.fullmatch(header):
                            part_of_speech = header
                            section = entry[current.end():next_.start()] if next_ else entry[current.end():]
                            yield (word, part_of_speech), next_layer, section
    return part_of_speech_

for (word, part_of_speech), layer, root in chain_compose(
        lambda max_line_count: raw(max_line_count, filename='../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        header2('Spanish'),
        part_of_speech('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
    )(1e9):
    print(f'{word.lower()}\t{part_of_speech.lower()}')
    # print(f'{word.upper():<15} {root}')
