from parse_wiktionary import *

def before_pattern(regex):
    matcher = re.compile(regex, re.IGNORECASE)
    def before_pattern_(items):
        for word, layer, text in items:
            yield word, layer, matcher.split(text, maxsplit=1)[0]
    return before_pattern_

def replace_regex(regex, replacement):
    matcher = re.compile(regex, re.IGNORECASE)
    def replace_regex_(items):
        for word, layer, text in items:
            yield word, layer, matcher.sub('', text)
    return replace_regex_

hyperlink_matcher = re.compile('\[\[([^\]]+?)\]\]')
hyperlink_markup = re.compile('\[\[([^\]|]+?)\|   |   \[\[ (?![^\]|]+?\|)   |   \]\]', re.VERBOSE)
outside_hyperlink_markup = re.compile('\[[^\]]*\]', re.VERBOSE)
bold_italics_markup = re.compile("'''?", re.VERBOSE)
html_escape_markup = re.compile("&\S+;", re.VERBOSE)
replacements = [
    ('&quot;', '"'),
]
for (word, part_of_speech), layer, text in chain_compose( 
        lambda max_line_count: raw(max_line_count, filename='../../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        header2('Spanish', allow_if_no_headers_exist=False),
        part_of_speech_header('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Presposition|Particle|Pronoun|Phrase'),
        before_pattern('=(Usage notes|derived +terms|descend[ea]nts|inflection|related +terms|reconstruction +notes|extensions|alternative reconstructions|Translations)='),
        bulleted_list_items, 
        replace_regex('{{lb\|[^}]+}}', ''),
        replace_regex('{{gloss\|[^}]+}}', ''),
        replace_regex('{{([^}|=]+\|)*', '('),
        replace_regex('}}', ')'),
        replace_regex('</?[^>]+?>', ''),
        replace_regex('#', ''),
        replace_regex('&lt;.*', ''),
        replace_regex('\([^\)]+?\)', ''),
        replace_regex('\[[^\]+?]\]', ''),
        replace_regex('^[ ,]+', ''),
    )(1e9):
    # print('=====================================================================')
    # print(word)
    # print(text)
    lemmata = set([hyperlink.group(1).split('|')[0] for hyperlink in hyperlink_matcher.finditer(text)])
    for lemma in lemmata:
        user_text = text
        user_text = hyperlink_markup.sub('', user_text)
        user_text = outside_hyperlink_markup.sub('', user_text)
        user_text = bold_italics_markup.sub('', user_text)
        user_text = user_text.strip(';:,. \t\r\n')
        for replaced, replacement in replacements:
            user_text = user_text.replace(replaced, replacement)
        print(word.lower(), '\t', part_of_speech.lower(), '\t', lemma, '\t', user_text)