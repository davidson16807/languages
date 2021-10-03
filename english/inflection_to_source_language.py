from parse_wiktionary import *

def source_languages(etymology_tags):
    for word, layer, tag in etymology_tags:
        split = tag.split('|')
        if len(split) >= 4:
            type_, language, source, original, *args = split
            if language == 'en' and type_ == 'inh':
                yield word, layer, source

for word, layer, language_tag in chain_compose(
        raw, pages, 
        header2('English'),
        anyheader('Etymology\\s*\\d*'), 
        # bulleted_list_items, 
        # first_tag,
        source_languages
    )(1e9):
    print(f'{word.lower()}\t{language_tag}')
    # print(f'{word.upper():<15} {language_tag}')
