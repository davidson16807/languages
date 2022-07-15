from parse_wiktionary import *

def plurals(plural_tags):
    for word, layer, tag in plural_tags:
        split = tag.split('|')
        if len(split) >= 3:
            type_, language, singular, *args = split
            if language == 'en' and type_ == 'plural of':
                yield word, layer, singular

for plural, layer, singular in chain_compose( 
        raw, pages, 
        header2('English'),
        anyheader('Noun'), 
        # preheader, 
        bulleted_list_items, 
        must_not_include_any_of_annotations(*ignored_annotations), 
        must_not_include_abbreviations,
        tags,
        plurals
    )(1e9):
    print(f'{singular.lower()}\t{plural}')
    # print(f'{plural.upper():<15} {singular}')

