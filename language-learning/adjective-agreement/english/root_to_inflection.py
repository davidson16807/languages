from parse_wiktionary import *

def inflections(plural_tags):
    for word, layer, tag in plural_tags:
        split = tag.split('|')
        if len(split) >= 5:
            type_, language, verb, person, plurality, *args = split
            if language == 'en' and type_ == 'inflection of':
                yield word, layer, [verb, person, plurality, *args]

for word, layer, tags in chain_compose( 
        raw, pages, 
        header2('English'),
        anyheader('Verb'), 
        # preheader, 
        bulleted_list_items, 
        must_not_include_any_of_annotations(*ignored_annotations), 
        must_not_include_abbreviations,
        tags,
        inflections,
    )(1e9):
    print(f'{'|'.join(tags)}\t{word}')
    # print(f'{word.upper():<15} {tags}')


