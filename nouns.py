from parse_wiktionary import *

for word, layer, text in chain_compose( 
        raw, pages, 
        header2('English'),
        anyheader('Noun') 
        bulleted_list_items, 
        must_not_include_any_of_annotations(*ignored_annotations), 
        must_not_include_abbreviations,
    )(1e9):
    print(word.lower())
