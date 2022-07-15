import re
import functools
import itertools

################################ ITERATION TOOLS ###############################
def compose(f, g): 
    return lambda x : f(g(x)) 

def chain_compose(*func): 
    return functools.reduce(compose, reversed(func), lambda x : x) 

def identity(entries): 
    for word, layer, entry in entries:
        yield word, layer, entry

def try_both(*chains):
    def try_both_(items):
        for item in items:
            for chain in chains:
                for word, layer, text in chain([item]):
                    yield word, layer, text
    return try_both_

def try_fallbacks(*chains):
    def try_with_fallback_(items):
        for item in items:
            found = False
            for chain in chains:
                if not found: 
                    for word, layer, text in chain([item]):
                        found = True
                        yield word, layer, text
    return try_with_fallback_

################################### pages ####################################
def raw(max_line_count, filename='enwiktionary-latest-pages-articles.xml'):
    with open(filename) as wiktionary:
        line_id = 0
        entry = ''
        for line in wiktionary:
            if line_id > max_line_count:
                break
            if '<title>' in line:
                yield entry
                entry = ''
                line_id += 1
            entry += line

def pages(raw):
    title_matcher = re.compile('<title>(.*)</title>', re.MULTILINE)
    for entry in raw:
        title_match = title_matcher.search(entry)
        if title_match:
            word = title_match.group(1)
            yield word, 0, entry


def pairwise(elements):
    last = elements[0]
    for current in elements[1:]:
        yield last, current
        last = current

################################### SECTIONS ###################################
def header2(language, allow_if_no_headers_exist=True):
    def header2_(entries):
        header_regex = re.compile('^'+'='*2+'([^=]+)'+'='*2+'\\s*$', re.MULTILINE)
        for word, layer, entry in entries:
            matches = header_regex.finditer(entry)
            for current, next_ in pairwise(list(itertools.chain(matches, [None]))):
                section = entry[current.end():next_.start()] if next_ else entry[current.end():]
                if language.strip().lower() == current.group(1).strip().lower():
                    yield word, 2, section
    return header2_

def anyheader(title_regex_string):
    title_regex = re.compile(title_regex_string, re.IGNORECASE)
    def anyheader_(entries):
        for word, layer, entry in entries:
            for next_layer in range(1,6):
                header_regex = re.compile('^'+'='*next_layer+'([^=]+)'+'='*next_layer+'\\s*$', re.MULTILINE)
                matches = header_regex.finditer(entry)
                current = None
                next_ = None
                for match in pairwise(list(itertools.chain(matches, [None]))):
                    current = next_
                    next_ = match
                    if current:
                        header = current.group(1)
                        if title_regex.fullmatch(header):
                            section = entry[current.end():next_.start()] if next_ else entry[current.end():]
                            yield word, next_layer, section
    return anyheader_

def subheader(entries):
    for word, layer, entry in entries:
        next_layer = layer+1
        header_regex = re.compile('^'+'='*next_layer+'([^=]+)'+'='*next_layer+'\\s*$', re.MULTILINE)
        matches = header_regex.finditer(entry)
        current = None
        next_ = None
        for match in itertools.chain(matches, [None]):
            current = next_
            next_ = match
            if current:
                section = entry[current.end():next_.start()] if next_ else entry[current.end():]
                yield word, next_layer, section

def preheader(entries):
    for word, layer, entry in entries:
        next_layer = layer+1
        header_regex = re.compile('^'+'='*next_layer+'([^=]+)'+'='*next_layer+'\\s*$', re.MULTILINE)
        match = header_regex.search(entry)
        if match:
            yield word, next_layer, entry[:match.start()]
        else:
            yield word, next_layer, entry

def part_of_speech_header(part_of_speech_regex_string):
    part_of_speech_regex = re.compile(part_of_speech_regex_string, re.IGNORECASE)
    def part_of_speech_header_(entries):
        for word, layer, entry in entries:
            for next_layer in range(1,7):
                header_regex = re.compile('^'+'='*next_layer+'([^=]+)'+'='*next_layer+'\\s*$', re.MULTILINE)
                matches = header_regex.finditer(entry)
                current = None
                next_ = None
                for match in itertools.chain(matches, [None]):
                    current = next_
                    next_ = match
                    if current:
                        header = current.group(1)
                        if part_of_speech_regex.fullmatch(header):
                            part_of_speech = header
                            section = entry[current.end():next_.start()] if next_ else entry[current.end():]
                            yield (word, part_of_speech), next_layer, section
    return part_of_speech_header_

############################ BULLETED LIST ITEMS ###############################
def bulleted_list_items(sections):
    pattern = re.compile('\n[#\\*][\t ]*([^\n]*)', re.MULTILINE | re.DOTALL)
    for word, layer, section in sections:
        matches = pattern.finditer(section)
        for match in matches:
            list_item = match.group(1)
            yield word, layer, list_item
    
##################################### TAGS #####################################
def tags_in_text(text):
    pattern = re.compile('{{([^}]*)}}', re.MULTILINE | re.DOTALL)
    matches = pattern.finditer(text)
    for match in matches:
        tag = match.group(1)
        type_ = tag.split('|')[0]
        yield tag

def tags_with_types_in_text(*types):
    pattern = re.compile('{{([^}]*)}}', re.MULTILINE)
    def tags_of_type_(text):
        matches = pattern.finditer(text)
        for match in matches:
            tag = match.group(1)
            type_ = tag.split('|')[0]
            if type_ in types:
                yield tag
    return tags_of_type_

def annotations_in_text(text):
    for tag in tags_with_types_in_text('lb')(text):
        annotations = tag.split('|')
        if len(annotations) > 2:
            for annotation in annotations[2:]:
                yield annotation

def tags(sections):
    pattern = re.compile('{{([^}]*)}}', re.MULTILINE | re.DOTALL)
    for word, layer, section in sections:
        matches = pattern.finditer(section)
        for match in matches:
            tag = match.group(1)
            yield word, layer, tag

def first_tag(sections):
    tag_pattern = re.compile('{{([^}]*)}}', re.MULTILINE | re.DOTALL)
    for word,section in sections:
        tag_match = tag_pattern.search(section)
        if tag_match:
            tag = tag_match.group(1)
            yield word, layer, tag
            
def tags_with_types(*types):
    pattern = re.compile('{{([^}]*)}}', re.MULTILINE | re.DOTALL)
    def tags_of_type_(sections):
        for word, layer, section in sections:
            matches = pattern.finditer(section)
            for match in matches:
                contents = match.group(1)
                type_ = contents.split('|')[0]
                if type_ in types:
                    yield word, layer, contents
    return tags_of_type_


################################### UTILITIES ##################################

def must_include_text(text):
    def must_include_text_(items):
        for word, layer, item in items:
            if text in item:
                yield word, layer, item
    return must_include_text_

def must_include_any_of_text(*texts):
    def must_include_any_text_(items):
        for word, layer, item in items:
            if any(text in item for text in texts):
                yield word, layer, item
    return must_include_any_text_

def must_not_include_any_of_text(*texts):
    def must_not_include_any_of_text_(items):
        for word, layer, item in items:
            if not any(text in item for text in texts):
                yield word, layer, item
    return must_not_include_any_of_text_

def must_include_all_of_text(*texts):
    def must_include_all_text_(items):
        for word, layer, item in items:
            if all(text in item for text in texts):
                yield word, layer, item
    return must_include_all_text_
   
def must_include_any_of_annotations(*keywords):
    def must_include_any_of_annotations_(items):
        for word, layer, item in items:
            if any(annotation in keywords for annotation in annotations_in_text(item)):
                yield word, layer, item
    return must_include_any_of_annotations_

def must_not_include_any_of_annotations(*keywords):
    def must_include_none_of_annotations_(items):
        for word, layer, item in items:
            if not any(annotation in keywords for annotation in annotations_in_text(item)):
                yield word, layer, item
    return must_include_none_of_annotations_

def must_not_include_abbreviations(items):
    abbreviations_in_text = tags_with_types_in_text('abbreviation of', 'initialism of')
    for word, layer, item in items:
        if not any(abbreviations_in_text(item)):
            yield word, layer, item

def must_include_abbreviations(items):
    abbreviations_in_text = tags_with_types_in_text('abbreviation of', 'initialism of')
    for word, layer, item in items:
        if any(abbreviations_in_text(item)):
            yield word, layer, item

def must_include_header(title_regex):
    pattern = re.compile(f'={title_regex}=', re.MULTILINE | re.DOTALL | re.IGNORECASE)
    for word, layer, entry in entries:
        match = pattern.search(entry)
        if match:
            yield word, layer, entry

def unique(hashes):
    existing = set()
    for word, layer, hash_ in hashes:
        if (word, hash_) not in existing:
            existing.add((word, hash_))
            yield word, layer, hash_
    
ignored_annotations = [
    'archaic',
    'dialectal',
    'dialect',
    'colloquial',
    'nonstandard',
    'rare',
    'AAVE',
    'dated',
    'informal',
    'leet',
    'slang',
    'obsolete',
    'internet',
    'humorous',
    'Scottish',
    'Scotland',
    'UK',
    'nautical'
]
