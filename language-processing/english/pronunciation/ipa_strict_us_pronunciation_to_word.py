from parse_wiktionary import *

def ipa_pronunciation(pronunciation_tags):
    for word, layer, tag in pronunciation_tags:
        split = tag.split('|')
        if len(split) >= 3:
            type_, language, *pronunciations = split
            if language == 'en' and type_ == 'IPA':
                for pronunciation in pronunciations:
                    yield word, layer, pronunciation.strip('/').strip('[').strip(']')

for word, layer, pronunciation in chain_compose( 
        lambda max_line_count: raw(max_line_count, filename='../../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        header2('English'),
        anyheader('Pronunciation'), 
        bulleted_list_items, 
        must_not_include_any_of_text('|RP', '|NZ', '|AU', '|UK', 
            '|Australia', '|New Zealand', '|Tasmanian', 
            '|non-rhotic', '|near-square'), 
        tags, 
        ipa_pronunciation,
        unique
    )(1e9):
    print(f'{word.lower()}\t{pronunciation}')
    # print(f'{word.upper():<15} {pronunciation}')
