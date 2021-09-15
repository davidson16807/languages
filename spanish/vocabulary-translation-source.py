from parse_wiktionary import *


def translations(language_code):
    def translations_(translation_tags):
        for (word, part_of_speech), layer, tag in translation_tags:
            split = tag.split('|')
            if len(split) >= 3:
                type_, language, translation, *args = split
                if type_ in {'t','t+','tt','tt+'} and language == language_code:
                    yield (word.replace('/translations',''), part_of_speech), layer, translation.replace('[','').replace(']','')
    return translations_

def page_title(regex):
    matcher = re.compile(regex, re.IGNORECASE)
    def page_title(items):
        for word, layer, text in items:
            match = matcher.search(word)
            if match:
                yield match.group(1), layer, text
    return page_title

def try_both(*chains):
    def try_both_(items):
        for item in items:
            for chain in chains:
                for word, layer, text in chain([item]):
                    yield word, layer, text
    return try_both_

def try_fallbacks(*chains):
    def try_with_fallback_(items):
        for item in items:
            found = False
            for chain in chains:
                if not found: 
                    for word, layer, text in chain([item]):
                        found = True
                        yield word, layer, text
    return try_with_fallback_

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

def debug(word):
    def debug_(items):
        for word, layer, text in items:
            if 'three' == word:
                yield word, layer, text
    return debug_

for (word, part_of_speech), layer, text in chain_compose( 
        lambda max_line_count: raw(max_line_count, filename='../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        try_both(
            chain_compose( 
                try_fallbacks(
                    header2('English'),
                    preheader,
                ),
                part_of_speech('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
            ),
            chain_compose( 
                page_title('([^/]*)/translations'),
                header2('English'),
                part_of_speech('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
            ),
        ),
        # must_not_include_any_of_annotations(*ignored_annotations),
        # bulleted_list_items, 
        # must_include_text('Spanish'), 
        tags,
        translations('es')
    )(1e9):
    print(f'{word.lower()}\t{part_of_speech.lower()}\t{text}')
    # print(f'{word.lower()}')
    # print(f'{text}')
    # print(f'{word.upper():<15} {text}')

