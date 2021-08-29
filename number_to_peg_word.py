from parse_wiktionary import *
from ipa_hash import *

def ipa_pronunciation(pronunciation_tags):
    for word, layer, tag in pronunciation_tags:
        split = tag.split('|')
        if len(split) >= 3:
            type_, language, *pronunciations = split
            if language == 'en' and type_ == 'IPA':
                for pronunciation in pronunciations:
                    yield word, layer, pronunciation.strip('/').strip('[').strip(']')

def ipa_peg_hash(pronunciations):
    for word, layer, pronunciation in ipa_narrow_hash(pronunciations):
        simplification = pronunciation
        simplification = re.compile('[aeiouæɑɒʌɛɪɔʊəɜhjwy ]+').sub('', simplification)
        simplification = re.compile('[td]?[ʃʒ]').sub('6', simplification)
        simplification = re.compile('[sz]').sub('0', simplification)
        simplification = re.compile('[tdðθ]').sub('1', simplification)
        simplification = re.compile('[nŋ]').sub('2', simplification)
        simplification = re.compile('[m]').sub('3', simplification)
        simplification = re.compile('[r]').sub('4', simplification)
        simplification = re.compile('[l]').sub('5', simplification)
        simplification = re.compile('[ckg]').sub('7', simplification)
        simplification = re.compile('[fv]').sub('8', simplification)
        simplification = re.compile('[pb]').sub('9', simplification)
        if len(simplification) > 0 and not re.compile('\\D').search(simplification):
            yield word, layer, simplification

for word, layer, number in chain_compose( 
        raw, pages, 
        header2('English'),
        anyheader('Pronunciation'), 
        bulleted_list_items, 
        must_not_include_any_of_text('|RP', '|NZ', '|AU', '|UK', 
            '|Australia', '|New Zealand', '|Tasmanian', 
            '|non-rhotic', '|near-square'), 
        tags, 
        ipa_pronunciation,
        ipa_peg_hash,
        unique,
        lambda pegs:  sorted(pegs, key=lambda peg: int(peg[2]))
    )(1e9):
    print(f'{number}\t{word}')
    # print(f'{word.upper():<15} {pronunciation}')
    
