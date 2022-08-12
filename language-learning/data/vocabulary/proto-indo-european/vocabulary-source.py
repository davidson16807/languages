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

def remove_subwords(*subwords):
    def remove_subwords_(items):
        for word, layer, text in items:
            if not any(subword in word for subword in subwords):
                yield word, layer, text
    return remove_subwords_

def insert_words_and_text(*tuples):
    def insert_words_and_text_(items):
        for word, text in tuples:
            yield word, 0, text
        for word, layer, text in items:
            yield word, layer, text
    return insert_words_and_text_

def fewer_than_number_of_matches(regex, count):
    def fewer_than_number_of_matches_(items):
        for word, layer, text in items:
            if len(re.findall(regex, text)) <= count:
                yield word, layer, text
    return fewer_than_number_of_matches_

hyperlink_matcher = re.compile('\[\[([^\]]+?)\]\]')
hyperlink_markup = re.compile('\[\[([^\]|]+?)\|   |   \[\[ (?![^\]|]+?\|)   |   \]\]', re.VERBOSE)
hyperlink_markup = re.compile('\[\[([^\]|]+?)\|   |   \[\[ (?![^\]|]+?\|)   |   \]\]', re.VERBOSE)
for word, layer, text in chain_compose( 
        lambda: raw(filename='../enwiktionary-latest-pages-articles.xml'), pages, 
        pie_word('reconstruction:proto-indo-european/(.*)$'),
        fewer_than_number_of_matches('==Root==', 1), # exclude highly ambiguous roots
        anyheader('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Particle|Pronoun|Root'),
        before_pattern('Usage notes|derived +terms|descend[ea]nts|inflection|related +terms|reconstruction +notes|extensions|alternative reconstructions'),
        bulleted_list_items, 
        replace_regex('{{[^}]+?}}', ''),
        replace_regex('</?[^>]+?>', ''),
        replace_regex('#', ''),
        replace_regex('&lt;.*', ''),
        replace_regex('\(\'\'[^\)]+?\)', ''),
        replace_regex('\[[^\]+?]\]', ''),
        replace_regex('^[ ,]+', ''),
        replace_literals(
            ('[[year]] (as a measure of time)', 'year (as a measure of time)'),
            ('[[nail]] (of the finger or toe)', '[[fingernail]], [[toenail]]'),
            ('[[mouth]] [[of]] [[an]] [[inlet]]', 'mouth of an inlet'),
            ('[[sheatfish]]', '[[sheatfish]], [[whale]], [[shark]]'),
            ('[[place]] of [[sacrifice]]', 'place of [[sacrifice]]'),
            ('[[something]] [[leaning]]', 'something [[leaning]]'),
            ('[[throwing]] [[spear]]', 'throwing [[spear]]'),
            ('[[standing]] [[water]]', 'standing [[water]]'),
            ('[[summer]], [[year]]', '[[summer]], year'),
            ('[[spit]], [[skewer]]', 'spit, [[skewer]]'),
            ('[[lying]] [[flat]]', '[[laying]] flat'),
            ('[[lean]] ([[on]])', '[[lean]] (on)'),
            ('[[wild]] [[bull]]', 'wild [[bull]]'),
            ('[[mountain]] [[elm]]', '[[elm]]'),
            ('you (plural)', '[[you all]]'),
            ('[[bear]]ing', '[[bearing]]'),
            ('[[act]] of ', 'act of'),
            ('rape', '[[rapeseed]]'),
            ('[[second]]', 'second'),
            ('[[off]]', 'off'),
            ('[[of]]', 'of'),
            ('[[an]]', 'an'),
        ),
        # these words/roots are omitted either because either they  are too ambiguous, 
        # they overload the user with infrequent or trivial synonyms, 
        # or they interrupt order
        remove_subwords(
            'plew-', # too ambiguous
            'plewk-', # too ambiguous
            'plewd-', # too ambiguous
            'h₃er-', # too ambiguous
            'dʰregʰ-', #too ambiguous
            'márkos', # controverial
            'kr̥snós', #customized below
        ), 
        insert_words_and_text(
            ('kr̥snós-',         "[[black]], dusk or dawn",                ),
            ('h₂eus-',          "[[gold]]",                               ),
            ('(s)h₁es-',        "[[autumn]], [[fall]]",                   ),
            ('h₂eus-teros',     "[[east]] ('towards the dawn')",          ),
            ('h₃nṓgʰs',         "[[fingernail]]",                         ),
            ('swepnos',         "[[dream]]",                              ),
            ('dʰǵʰuos,',        "[[fish]]",                               ),
            ('peysḱos',         "[[fish]]",                               ),
            ('h₂ents',          "[[forehead]] ('[[front]]')",             ),
            ('bʰerǵʰos',        "[[hill]], [[mountain]] ('the rise')",    ),
            ('steríh₂s',        "[[heifer]], sterile cow, barren woman",  ),
            ('bʰerH-',          "[[brown]], [[hole]], to [[pierce]]",     ),
            # ('kóslos',          "[[hazel]]",                              ),
            # ('ḱwentos',         "[[holy]]",                               ),
            # ('gʰel-, ǵʰelh₃-',  "[[green]], [[yellow]]",                  ),
            # ('h₁eygō',          "[[ice]], [[frost]]",                     ),
        ),
        nonmatching_text('^[ \t\n\r,:.{}*]*$'),
        # hyperlink_text(),
    )(1e9):
    lemma = ', '.join(set([hyperlink.group(1).split('|')[0] for hyperlink in hyperlink_matcher.finditer(text)]))
    user_text = hyperlink_markup.sub('', text)
    print(word.lower(), '\t', lemma, '\t', user_text)
