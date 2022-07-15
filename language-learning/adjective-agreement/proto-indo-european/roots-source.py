from ..parse_wiktionary import *

def pie_word(regex):
    matcher = re.compile(regex, re.IGNORECASE)
    def pie_word_(items):
        for word, layer, text in items:
            match = matcher.search(word)
            if match:
                yield match.group(1), layer, text
    return pie_word_

def before_pattern(regex):
    matcher = re.compile(regex, re.IGNORECASE)
    def before_pattern_(items):
        for word, layer, text in items:
            yield word, layer, matcher.split(text, maxsplit=1)[0]
    return before_pattern_

def nonmatching_text(regex):
    matcher = re.compile(regex, re.IGNORECASE)
    def nonmatching_text_(items):
        for word, layer, text in items:
            if not matcher.search(text):
                yield word, layer, text
    return nonmatching_text_

def replace_regex(regex, replacement):
    matcher = re.compile(regex, re.IGNORECASE)
    def replace_regex_(items):
        for word, layer, text in items:
            yield word, layer, matcher.sub('', text)
    return replace_regex_

def replace_literals(*replacements):
    def replace_literals_(items):
        for word, layer, text in items:
            replaced = text
            for pattern, replacement in replacements:
                replaced = replaced.replace(pattern, replacement)
            yield word, layer, replaced
    return replace_literals_

hyperlink_matcher = re.compile('\[\[([^\]]+?)\]\]')
hyperlink_markup = re.compile('\[\[([^\]|]+?)\|   |   \[\[ (?![^\]|]+?\|)   |   \]\]', re.VERBOSE)
hyperlink_markup = re.compile('\[\[([^\]|]+?)\|   |   \[\[ (?![^\]|]+?\|)   |   \]\]', re.VERBOSE)
for word, layer, text in chain_compose( 
        lambda: raw(filename='../enwiktionary-latest-pages-articles.xml'), pages, 
        pie_word('reconstruction:proto-indo-european/(.*)$'),
        anyheader('Root'),
        before_pattern('derived +terms|descend[ea]nts|inflection|related +terms|reconstruction +notes|Extensions|Alternative reconstructions'),
        bulleted_list_items, 
        replace_regex('{{[^}]+?}}', ''),
        replace_regex('</?[^>]+?>', ''),
        replace_regex('#', ''),
        replace_regex('&lt;.*', ''),
        replace_regex('\(\'\'[^\)]+?\)', ''),
        replace_regex('\[[^\]+?]\]', ''),
        replace_regex('^[ ,]+', ''),
        replace_literals(
            ('[[mouth]] [[of]] [[an]] [[inlet]]', 'mouth of an inlet'),
            ('you (plural)', '[[you all]]'),
            ('[[nail]] (of the finger or toe)', '[[fingernail]], [[toenail]]'),
            ('rape', '[[rapeseed]]'),
            ('[[mountain]] [[elm]]', '[[elm]]'),
            ('[[sheatfish]]', '[[sheatfish]], [[whale]], [[shark]]'),
            ('[[place]] of [[sacrifice]]', 'place of [[sacrifice]]'),
            ('[[standing]] [[water]]', 'standing [[water]]'),
            ('[[bear]]ing', '[[bearing]]'),
            ('[[cut]]ting [[off]]', '[[cut]]ting off'),
            ('[[second]]', 'second'),
            ('[[spit]], [[skewer]]', 'spit, [[skewer]]'),
            ('[[lying]] [[flat]]', '[[laying]] flat'),
            ('[[black]]\n# [[dark]], [[dusky]]', '[[black]]\n# dark, dusky'),
            ('[[throwing]] [[spear]]', 'throwing [[spear]]'),
            ('[[she-wolf]]', '[[wolf]]'),
            ('[[year]] (as a measure of time)', 'year (as a measure of time)'),
            ('[[lean]] ([[on]])', '[[lean]] (on)'),
        ),
        nonmatching_text('^[ ,:.{}*]*$'),
        # hyperlink_text(),
    )(1e9):
    lemma = ', '.join(set([hyperlink.group(1).split('|')[0] for hyperlink in hyperlink_matcher.finditer(text)]))
    user_text = hyperlink_markup.sub('', text)
    print(word.lower(), '\t', lemma, '\t', user_text)
