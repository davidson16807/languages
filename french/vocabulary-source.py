from parse_wiktionary import *

def translations(translation_tags):
    for word, layer, tag in translation_tags:
        split = tag.split('|')
        if len(split) >= 3:
            type_, language, translation, *args = split
            yield word.replace('/translations',''), layer, translation.replace('[','').replace(']','')

for word, layer, translation in chain_compose( 
        lambda: raw(filename='../enwiktionary-latest-pages-articles.xml'), pages, 
        header2('English'),
        anyheader('Translations'), 
        bulleted_list_items, 
        must_include_text('French'), 
        tags,
        translations,
        unique
    )(1e9):
    print(f'{word.lower()}\t{translation}')
    # print(f'{word.upper():<15} {translation}')
