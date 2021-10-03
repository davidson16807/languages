import re

from parse_wiktionary import *
import ipa_hash

def accent_header(header):
    def accent_header_(entries):
        for word, layer, entry in entries:
            accents = re.split('\n;\s+', entry, re.MULTILINE | re.DOTALL)
            for accent in accents:
                if header in accent:
                    yield word, layer, accent
    return accent_header_

def accent_without_header(*headers):
    def accent_without_header_(entries):
        for word, layer, entry in entries:
            accents = re.split('\n;\s+', entry, re.MULTILINE | re.DOTALL)
            for accent in accents:
                if not any(header in accent for header in headers):
                    yield word, layer, accent
    return accent_without_header_

def bulleted_list_items_with_text(text):
    return chain_compose(bulleted_list_items, must_include_text(text))

def bulleted_list_items_without_text(*text):
    return chain_compose(bulleted_list_items, must_not_include_any_of_text(*text))

def ipa_pronunciation(pronunciation_tags):
    for word, layer, tag in pronunciation_tags:
        split = tag.split('|')
        if len(split) >= 3:
            type_, language, *pronunciations = split
            if language == 'en':
                if type_ == 'IPA':
                    for pronunciation in pronunciations:
                        if '=' not in pronunciation:
                            yield word, layer, pronunciation.strip('/').strip('[').strip(']')
                if type_ == 'audio-IPA':
                    for pronunciation in pronunciations[1:]:
                        if '=' not in pronunciation:
                            yield word, layer, pronunciation.strip('/').strip('[').strip(']')

for word, layer, pronunciation in chain_compose( 
        lambda max_line_count: raw(max_line_count, filename='../../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        try_fallbacks(
            header2('English'),
            preheader,
        ),
        must_not_include_any_of_text('{{initialism of|'),
        anyheader('Pronunciation'),
        try_fallbacks(
            accent_header('|GenAm'),
            accent_header('|GA'),
            accent_header('|US'),
            accent_header('|Northern US'),
            accent_header('|Canada'),
            accent_header('|CA'),
            accent_header('|rhotic'),
            accent_without_header('|AAVE', '|Southern US', '|Maine', 
                '|NZ', '|AU', '|AusE', '|Australia', '|New Zealand', '|Tasmanian', 
                '|UK', '|Ireland', '|West Country', 
                '|non-rhotic', '|near-square', '|obsolete', '|colloquial', '|unstressed'),
            identity,
        ),
        try_fallbacks(
            bulleted_list_items_with_text('|GenAm'), 
            bulleted_list_items_with_text('|GA'), 
            bulleted_list_items_with_text('|US'), 
            bulleted_list_items_with_text('|Northern US'), 
            bulleted_list_items_with_text('|Canada'), 
            bulleted_list_items_with_text('|CA'), 
            bulleted_list_items_with_text('|rhotic'), 
            bulleted_list_items_without_text(
                '|AAVE', '|Southern US', '|Maine', 
                '|NZ', '|AU', '|AusE', '|Australia', '|New Zealand', '|Tasmanian', 
                '|UK', '|Ireland', '|West Country', 
                '|non-rhotic', '|near-square', '|obsolete', '|colloquial', '|unstressed'), 
        ),
        tags, 
        ipa_pronunciation,
        ipa_hash.sound_law,
        unique,
    )(1e9):
    print(f'{pronunciation}\t{word.lower()}')
    # print(f'{word.upper():<15} {pronunciation}')
    
