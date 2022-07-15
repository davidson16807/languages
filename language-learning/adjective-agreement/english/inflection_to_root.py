from parse_wiktionary import *

def roots(etymology_tags):
    for word, layer, tag in etymology_tags:
        split = tag.split('|')
        if len(split) >= 4:
            type_, language, part1, part2, *args = split
            if language == 'en':
                if type_ == 'prefix':
                    yield word, layer, part2
                elif type_ == 'suffix':
                    yield word, layer, part1
            
for word, layer, root in chain_compose(
        raw, pages, 
        header2('English'),
        # preheader('Etymology\\s*\\d*'), 
        # bulleted_list_items, 
        tags,
        roots
    )(1e9):
    print(f'{word.lower()}\t{root}')
    # print(f'{word.upper():<15} {root}')
