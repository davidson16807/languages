from parse_wiktionary import *
import ipa_hash

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
        # must_not_include_any_of_text('{{a|RP', '{{a|NZ', '{{a|AU', '{{a|UK', '{{a|Australia', '{{a|New Zealand', '{{a|Tasmanian', '{{a|non-rhotic'), 
        tags, 
        ipa_pronunciation,
        ipa_hash.broad,
        unique,
    )(1e9):
    print(f'{pronunciation}\t{word}')
    # print(f'{word.upper():<15} {pronunciation}')
    
