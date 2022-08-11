import re
import copy
import collections
import itertools


class HtmlPersonPositioning:
    def __init__(self):
        pass
    def farleft(self, person):
        return f'''<span style='position:relative; left:0.22em; top:0.2em;'>{person}</span>'''
    def left(self, person):
        return f'''<span style='position:relative; left:0.45em; top:0.2em;'>{person}</span>'''
    def center(self, person):
        return f'''{person}'''
    def right(self, person):
        return f'''<span style='position:relative; right:0.45em; top:0.2em;'>{person}</span>'''

class HtmlGesturePositioning:
    def __init__(self):
        pass
    def lowered(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; left:0.3em; top:0.8em;'>{hand}</span>'''
    def raised(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:0.6em; bottom:0.7em;'>{hand}</span>'''
    def overhead(self, hand): 
        return f'''<span style='display: inline-block; width:0; position:relative; bottom:0.8em;'>{hand}</span>'''
    def chestlevel(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:0.7em; top:0em;'>{hand}</span>'''
    def background(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:1em; bottom:0.9em; z-index:-1'>{hand}</span>'''

class HtmlTextTransform:
    def __init__(self):
        pass
    def mirror(self, emoji):
        return f'''<span style='display: inline-block; transform: scale(-1,1)'>{emoji}</span>'''
    def flip(self, emoji):
        return f'''<span style='display: inline-block; transform: scale(1,-1)'>{emoji}</span>'''

class HtmlNumberTransform:
    def __init__(self, htmlPersonPositioning):
        self.person = htmlPersonPositioning
    def singular(self, a): 
        return a
    def dual(self, a,b): 
        return f'''{self.person.left(a)}{self.person.center(b)}'''
    def plural(self, a,b,c): 
        return f'''{self.person.left(a)}{self.person.center(b)}{self.person.right(c)}'''
    def dual_inclusive(self, a,b): 
        return f'''{self.person.farleft(a)}{self.person.center(b)}'''
    def plural_inclusive(self, a,b,c): 
        return f'''{self.person.farleft(a)}{self.person.center(b)}{self.person.right(c)}'''

class HtmlTenseTransform:
    def __init__(self):
        pass
    def present(self, scene): 
        return f'''{scene}'''
    def past(self, scene): 
        return f'''<span style='filter: sepia(0.8)  drop-shadow(0px 0px 5px black)'>{scene}</span>'''
    def future(self, scene): 
        return f'''<span style='filter: blur(1px) drop-shadow(0px 0px 5px black)'>{scene}</span>'''

class HtmlAspectTransform:
    def __init__(self):
        pass
    def imperfect(self, scene): 
        return f'''{scene}<progress style='width:1em; height:0.8em; position:relative; top:0.5em; right:0.3em;' max='10' value='7'></progress>'''
    def perfect(self, scene): 
        return f'''{scene}<progress style='width:1em; height:0.8em; position:relative; top:0.5em; right:0.3em;' max='10' value='10'></progress>'''
    def aorist(self, scene): 
        return f'''{scene}'''
    def perfect_progressive(self, scene): 
        return f'''<span style='filter: sepia(0.3) drop-shadow(0px 0px 2px black)'>{scene}<progress style='width:1em; height:0.8em; position:relative; top:0.5em; right:0.3em;' max='10' value='10'></progress></span>'''

class HtmlBubble:
    def __init__(self):
        pass
    def affirmative(self, scene): 
        return f'''<div><span style='border-radius: 0.5em; padding: 0.5em; background:#ddd; '>{scene}</span></div>'''
    def negative(self, scene): 
        return f'''<div><span style='border-radius: 0.5em; padding: 0.5em; background: linear-gradient(to left top, #ddd 47%, red 48%, red 52%, #ddd 53%); border-style: solid; border-color:red; border-width:6px;'>{scene}</span></div>'''

class HtmlBubbleScene:
    def __init__(self):
        pass
    def speech(self, content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><sup style='color:#ddd;'>◥</sup><sub>{speaker}</sub>'''
    def thought(self, content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><span style='color:#ddd;'>•<sub>•</sub></span><sub>{speaker}</sub>'''
    def quote(self, content, audience, speaker): 
        return f'''{content}<sup style='padding-left: 0.5em; color:#ddd;'>◤</sup><sub>{audience}{speaker}</sub>'''

class Enclosures:
    '''
    Finds start and end positions of the first region of text enclosed 
    by an outermost pair of start and end markers, 
    denoted 'L' and 'R' for short.
    Text is assumed to follow a grammar that can be described 
    by a Stack Automata featuring only the given start and end markers
    '''
    def __init__(self, L='{', R='}'):
        self.L = L
        self.R = R
    def find(self, string):
        open_count = 0
        start = None
        for match in re.finditer(f'[{self.L}{self.R}]', string):
            start = match.end() if start is None else start 
            delimeter = match.group(0)
            open_count += (1 if delimeter == self.L else -1)
            if open_count == 0:
                return start, match.start()

class BracketedShorthand:
    '''
    Introduces LaTEX style escape sequences (e.g.\\foo{bar}) that 
    feature text enclosed start and end markers (e.g. '{' and '}').
    The style of start and end marker is described by the given `enclosure`.
    When the shorthand is decoded 
    '''
    def __init__(self, enclosure):
        self.enclosure = enclosure
    def decode(self, pattern, string, get_replacement):
        match = re.search(pattern, string)
        while match is not None:
            posttag = string[match.end():]
            bracket_range = self.enclosure.find(posttag)
            if not bracket_range: break
            start, end = bracket_range
            string = ''.join([
                string[:match.start()],
                get_replacement(posttag[start:end]), 
                posttag[end+len(self.enclosure.R):]])
            match = re.search(pattern, string)
        return string

class EmojiSubjectShorthand:
    '''
    Introduces LaTEX style escape sequences that are
    shorthands for characteristics of a grammatical subject
    that are depicted one or more times within a scene using emoji. 
    For instance, the subject may be a group of two people ('d' for 'dual')
    who are both male ('m' for 'male')
    and have medium shade skin color (3 on a scale from 1 to 5)
    Whenever the shorthand user desires an emoji modifier 
    that represents these aspects, he can write \ns, \gs, and \cs respectively.
    [The letters n, g, and c are short for 'number', 'gender', and 'color'] 
    '''
    def __init__(self):
        pass
    def decode(self, code, number, gender, color):
        '''
        Example usage: 
        shorthand.decode('\n1{🤷\c1\g1}', 's','m',3)
        '''
        emoji = code
        emoji = emoji.replace('\\nx', f'\\{number}')
        emoji = emoji.replace('\\gx', f'\\{gender}')
        emoji = emoji.replace('\\cx', f'\\{color}')
        return emoji

class EmojiPersonShorthand:
    '''
    Introduces LaTEX style escape sequences that are
    shorthands for characteristics of grammatical persons (e.g. 1st person, 2nd person)
    that are depicted one or more times within a scene using emoji. 
    For instance, the first entity may 
    be a group of two people ('d' for 'dual')
    who are both male ('m' for 'male')
    and have medium shade skin color (3 on a scale from 1 to 5)
    Whenever the shorthand user desires an emoji modifier 
    that represents these aspects, he can write \n1, \g1, and \c1 respectively.
    [The letters n, g, and c are short for 'number', 'gender', and 'color'] 
    '''
    def __init__(self, emojiNumberShorthand):
        self.emojiNumberShorthand = emojiNumberShorthand
    def decode(self, code, numbers, genders, colors):
        '''
        Example usage: 
        shorthand.decode(
            '\n1{🤷\c1\g1}'
            ['s','d','p','di','pi'], 
            ['m','f','m'],
            [3,4,2,3] )
        '''
        emoji = code
        for (i, number) in enumerate(numbers):
            emoji = emoji.replace(f'\\n{i+1}', f'\\{number}')
        '''
        Number potentially adds persons to the group
        (e.g. '1st person plural inclusive' includes the 2nd person)
        Therefore we need to decode the number shorhand before 
        processing any other characteristics of persons.
        '''
        emoji = self.emojiNumberShorthand.decode(emoji)
        for (i, gender) in enumerate(genders):
            emoji = emoji.replace(f'\\g{i+1}', f'\\{gender}')
        for (i, color) in enumerate(colors):
            emoji = emoji.replace(f'\\c{i+1}', f'\\{color}')
        return emoji

class EmojiGestureShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    standardized patterns of styled html elements 
    that surround emoji characters and represent gestures.
    Current supported gestures include:
        \raised{}
        \lowered{}
        \overhead{}
        \chestlevel{}
        \background{}
    '''
    def __init__(self, htmlGesturePositioning, bracketedShorthand):
        self.htmlGesturePositioning = htmlGesturePositioning
        self.bracketedShorthand = bracketedShorthand
    def decode(self, code):
        emoji = code
        emoji = self.bracketedShorthand.decode(r'\\raised', emoji, self.htmlGesturePositioning.raised)
        emoji = self.bracketedShorthand.decode(r'\\lowered', emoji, self.htmlGesturePositioning.lowered)
        emoji = self.bracketedShorthand.decode(r'\\overhead', emoji, self.htmlGesturePositioning.overhead)
        emoji = self.bracketedShorthand.decode(r'\\chestlevel', emoji, self.htmlGesturePositioning.chestlevel)
        emoji = self.bracketedShorthand.decode(r'\\background', emoji, self.htmlGesturePositioning.background)
        return emoji

class TextTransformShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    standardized patterns of styled html elements 
    that surround text and represent common transformations.
    Current supported transforms include:
        \mirror{}
        \flip{}
    '''
    def __init__(self, htmlTextTransform, bracketedShorthand):
        self.htmlTextTransform = htmlTextTransform
        self.bracketedShorthand = bracketedShorthand
    def decode(self, code):
        emoji = code
        emoji = self.bracketedShorthand.decode(r'\\mirror', emoji, self.htmlTextTransform.mirror)
        emoji = self.bracketedShorthand.decode(r'\\flip', emoji, self.htmlTextTransform.flip)
        return emoji

class EmojiNumberShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    standardized patterns of styled html elements 
    that surround emoji characters and represent the size of groups.
    As an example, number is indicated in the shorthand 
    by a 's', 'd', or 'p' (singular, dual, or plural).
    This causes an emoji to be depicted overlapping 
    with other identical emoji characters.
    Information is lost in decoding so no encode() function exists.
    '''
    def __init__(self, htmlNumberTransform, bracketedShorthand):
        self.htmlNumberTransform = htmlNumberTransform
        self.bracketedShorthand = bracketedShorthand
    def decode(self, code):
        emoji = code
        def get_transform(inner_transform, gestureless_count, inclusive=False):
            def _transform(content):
                gestureless = self.bracketedShorthand.decode(
                    r'\\(chestlevel|raised|lowered|overhead|background)', content, lambda x:'')
                person2 = content.replace('\\g1','\\g2').replace('\\c1','\\c2')
                return inner_transform(
                        person2 if inclusive else content, 
                        *([gestureless]*gestureless_count))
            return _transform
        '''
        'inclusive' plural and 'inclusive' dual include the audience,
        so substitute markers for skin color and gender with 
        the equivalent markers for the audience.
        '''
        emoji = self.bracketedShorthand.decode(r'\\s',  emoji, get_transform(self.htmlNumberTransform.singular, 0))
        emoji = self.bracketedShorthand.decode(r'\\di', emoji, get_transform(self.htmlNumberTransform.dual_inclusive, 1, True))
        emoji = self.bracketedShorthand.decode(r'\\d',  emoji, get_transform(self.htmlNumberTransform.dual, 1))
        emoji = self.bracketedShorthand.decode(r'\\pi', emoji, get_transform(self.htmlNumberTransform.plural_inclusive, 2, True))
        emoji = self.bracketedShorthand.decode(r'\\p',  emoji, get_transform(self.htmlNumberTransform.plural, 2))
        return emoji

class EmojiModifierShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    characters within emoji modifier sequences 
    The shorthand here is strictly bijective, 
    so that shorthands and text can be encoded and decoded 
    without any loss of information.
    '''
    def __init__(self):
        self.equivalences = [
            ('\\1',u'\U0001F3FB'), # light
            ('\\2',u'\U0001F3FC'),
            ('\\3',u'\U0001F3FD'), # medium
            ('\\4',u'\U0001F3FE'),
            ('\\5',u'\U0001F3FF'), # dark
            ('🧒\\m','👦'),
            ('🧒\\f','👧'),
            ('🧑\\m','👨'),
            ('🧑\\f','👩'),
            ('🧓\\m','👴'),
            ('🧓\\f','👵'),
            ('🕺\\m','🕺'),
            ('🕺\\f','💃'),
            ('🤴\\m','🤴'),
            ('🤴\\f','👸'),
            ('\\m',u'\u200D♂️️'),
            ('\\f',u'\u200D♀️'),
            ('\\n',''),
            ('\\',u'\u200D'),
        ]
    def encode(self, emoji):
        code = emoji
        for (escape, character) in self.equivalences:
            code = code.replace(character, escape)
        return code
    def decode(self, code):
        emoji = code
        for (escape, character) in self.equivalences:
            emoji = emoji.replace(escape, character)
        return emoji

class AggregateShorthand:
    '''
    Compiles up to several shorthands that 
    are applied in sequence when decoding text.
    Typical usage involves shorthands 
    that use LaTEX style escape sequences 
    to represent transformations on text 
    that depict scenes through a combination of html and emoji.
    '''
    def __init__(self, *shorthands):
        self.shorthands = shorthands
    def decode(self, code):
        emoji = code
        for (i, shorthand) in enumerate(self.shorthands):
            emoji = shorthand.decode(emoji)
        return emoji

class SeparatedValuesFileParsing:
    def __init__(self, comment='#', delimeter='\t', padding=' \t\r\n'):
        self.comment = comment
        self.delimeter = delimeter
        self.padding = padding
    def rows(self, filename):
        rows_ = []
        with open(filename) as file:
            for line in file.readlines():
                if self.comment is not None and line.startswith(self.comment):
                    continue
                elif len(line.strip()) < 1:
                    continue
                rows_.append([column.strip(self.padding) for column in line.split(self.delimeter)])
        return rows_

class TableAnnotation:
    '''
    `TableAnnotation` instances represent a system for storing tabular data 
    that comes up naturally in things like conjugation or declension tables.

    A table has a given number of header rows and header columns.
    When a predifined keyword occurs within the cell contents of a header row or column, 
     the row or column associated with that header is marked as having that keyword 
     for an associated attribute.
    Keywords are indicated by keys within `keyword_to_attribute`.
    Keywords that are not known at the time of execution may be 
     indicated using `header_column_id_to_attribute`, 
     which marks all cell contents of a given column as keywords for a given attribute.

    As an example, if a header row is marked 'green', and 'green' is a type of 'color',
     then `keyword_to_attribute` may store 'green':'color' as a key:value pair.
    Anytime 'green' is listed in a header row or column, 
     all contents of the row or column associated with that header cell 
     will be marked as having the color 'green'.

    `TableAnnotation` converts tables that are written in this manner between 
    two reprepresentations: 
    The first representation is a list of rows, where rows are lists of cell contents.
    The second representation is a list where each element is a tuple,
     (annotation,cell), where 'cell' is the contents of a cell within the table,
     and 'annotations' is a dict of attribute:keyword associated with a cell.
    '''
    def __init__(self, 
            keyword_to_attribute, 
            header_row_id_to_attribute, header_column_id_to_attribute,
            default_attributes):
        self.keyword_to_attribute = keyword_to_attribute
        self.header_column_id_to_attribute = header_column_id_to_attribute
        self.header_row_id_to_attribute = header_row_id_to_attribute
        self.default_attributes = default_attributes
    def annotate(self, rows, header_row_count=None, header_column_count=None):
        header_row_count = header_row_count if header_row_count is not None else len(self.header_row_id_to_attribute)
        header_column_count = header_column_count if header_column_count is not None else len(self.header_column_id_to_attribute)
        column_count = max([len(row) for row in rows])
        column_base_attributes = [{} for i in range(column_count)]
        header_rows = rows[:header_row_count]
        nonheader_rows = rows[header_row_count:]
        for i, row in enumerate(header_rows):
            for j, cell in enumerate(row):
                if i in self.header_row_id_to_attribute:
                    column_base_attributes[j][self.header_row_id_to_attribute[i]] = cell
                if cell in self.keyword_to_attribute:
                    column_base_attributes[j][self.keyword_to_attribute[cell]] = cell
        annotations = []
        for row in nonheader_rows:
            row_base_attributes = {}
            for i in range(0,header_column_count):
                cell = row[i]
                if i in self.header_column_id_to_attribute:
                    row_base_attributes[self.header_column_id_to_attribute[i]] = cell
                if cell in self.keyword_to_attribute:
                    row_base_attributes[self.keyword_to_attribute[cell]] = cell
            for i in range(header_column_count,len(row)):
                cell = row[i]
                # if cell and column_base_attributes[i]:
                if cell and row_base_attributes and column_base_attributes[i]:
                    annotation = {}
                    annotation.update(self.default_attributes)
                    annotation.update(row_base_attributes)
                    annotation.update(column_base_attributes[i])
                    annotations.append((annotation,cell))
        return annotations

class FlatTableIndexing:
    '''
    `FlatTableIndexing` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in a lookup.
    The cells are indexed by their annotations according to the indexing behavior 
    within a given `template_lookup`.
    '''
    def __init__(self, template_lookup):
        self.template_lookup = template_lookup
    def index(self, annotations):
        lookups = copy.deepcopy(self.template_lookup)
        for annotation,cell in annotations:
            lookups[annotation] = cell
        return lookups

class NestedTableIndexing:
    '''
    `NestedTableIndexing` converts a list of (annotation,cell) tuples
    (such as those output by `TableAnnotation`)
    to a representation where cells are stored in nested lookups.
    The cells are indexed by their annotations according to 
    the indexing behavior within a given `template_lookups`.
    Nested lookups can be especially useful if the data 
    that they are indexing is nonnormalized, 
    since inner nested lookups can each use separate indexing methods,
    so that their content is a strict function of the key and nothing else.
    '''
    def __init__(self, template_lookups):
        self.template_lookups = template_lookups
    def index(self, annotations):
        lookups = copy.deepcopy(self.template_lookups)
        for annotation,cell in annotations:
            lookup = lookups[annotation]
            lookup[annotation] = cell
        return lookups

class DictKeyHashing:
    '''
    `DictKeyHashing` represents a method for using dictionaries as hashable objects.
    It does so by converting between two domains, known as 'dictkeys' and 'tuplekeys'.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values
     that can be indexed natively in Python dictionaries.
    `DictKeyHashing` works by selecting a single key:value pair 
     within a dictkey to serve as the tuplekey(s) to index by.
    It offers several conveniences to allow 
     working with both dictkeys and the values they are indexed by
    '''
    def __init__(self, key):
        self.key = key
    def dictkey(self, tuplekey):
        return {self.key:tuplekey}
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through possible values for the given `key`
        given values from a `dictkey` dict that maps a key to either a value or a set of possible values.
        '''
        key = self.key
        if type(dictkey) in {dict}:
            return dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
        elif type(dictkey) in {set,list}:
            return dictkey
        else:
            return [dictkey]

class DictTupleHashing:
    '''
    `DictTupleHashing` represents a method for using dictionaries as hashable objects.
    It does so by converting between two domains, known as 'dictkeys' and 'tuplekeys'.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values
     that can be indexed natively in Python dictionaries.
    `DictKeyHashing` works by ordering values in a dictkey 
     into one or more tuplekeys according to a given list of `keys`.
    '''
    def __init__(self, keys):
        self.keys = keys
    def dictkey(self, tuplekey):
        return {key:tuplekey[i] for i, key in enumerate(self.keys)}
    def tuplekeys(self, dictkey):
        '''
        Returns a generator that iterates through 
        possible tuples whose keys are given by `keys`
        and whose values are given by a `dictkey` dict 
        that maps a key from `keys` to either a value or a set of possible values.
        '''
        return [tuple(reversed(tuplekey)) 
                for tuplekey in itertools.product(
                    *[dictkey[key] if type(dictkey[key]) in {set,list} else [dictkey[key]]
                      for key in reversed(self.keys)])]

class DictLookup:
    '''
    `DictLookup` is a lookup that indexes 'dictkeys' by a given `hashing` method,
    where `hashing` is of a class that shares the same iterface as `DictHashing`.
    A 'dictkey' is a dictionary that maps each key to either a value or a set of values.
    A 'dictkey' is indexed by one or more 'tuplekeys', which are ordinary tuples of values.
    '''
    def __init__(self, name, hashing, content=None):
        self.name = name
        self.hashing = hashing
        self.content = {} if content is None else content
    def __getitem__(self, key):
        '''
        Return the value that is indexed by `key` 
        if it is the only such value, otherwise return None.
        '''
        if isinstance(key, tuple):
            return self.content[key]
        else:
            tuplekeys = [tuplekey 
                for tuplekey in self.hashing.tuplekeys(key)
                if tuplekey in self.content]
            if len(tuplekeys) == 1:
                return self.content[tuplekeys[0]]
            elif len(tuplekeys) == 0:
                raise IndexError('\n'.join([
                                    'Key does not exist within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                ]))
            else:
                raise IndexError('\n'.join([
                                    'Key is ambiguous.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(key),
                                    'Available interpretations:',
                                    *['\t'+str(self.hashing.dictkey(tuplekey)) 
                                      for tuplekey in tuplekeys]
                                ]))
    def __setitem__(self, key, value):
        '''
        Store `value` within the indices represented by `key`.
        '''
        if isinstance(key, tuple):
            return self.content[key]
        else:
            for tuplekey in self.hashing.tuplekeys(key):
                if tuplekey in self.content and value != self.content[tuplekey]:
                    raise IndexError('\n'.join([
                                    'Key already exists within the dictionary.',
                                    *(['Lookup:', '\t'+str(self.name)] if self.name else []),
                                    'Key:', '\t'+str(self.hashing.dictkey(tuplekey)),
                                    'Old Value:', '\t'+str(self.content[tuplekey]),
                                    'New Value:', '\t'+str(value),
                                ]))
                else:
                    self.content[tuplekey] = value
    def __contains__(self, key):
        if isinstance(key, tuple):
            return key in self.content
        else:
            return any(tuplekey in self.content 
                       for tuplekey in self.hashing.tuplekeys(key))
    def __iter__(self):
        return self.content.__iter__()
    def __len__(self):
        return self.content.__len__()
    def values(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.content[tuplekey]
    def keys(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.hashing.dictkey(tuplekey)
    def items(self, dictkey):
        for tuplekey in self.hashing.tuplekeys(dictkey):
            if tuplekey in self.content:
                yield self.hashing.dictkey(tuplekey), self.content[tuplekey]



category_to_grammemes = {

    # needed to lookup the argument that is used to demonstrate a verb
    'language':   ['english', 'translated'], 

    # needed for infinitives
    'completion': ['full', 'bare'],

    # needed for finite forms
    'person':     ['1','2','3'],
    'number':     ['singular', 'dual', 'plural'],
    'clusivity':  ['inclusive', 'exclusive'],
    'mood':       ['indicative', 'subjunctive', 'conditional', 
                   'optative', 'benedictive', 'jussive', 'potential', 
                   'imperative', 'prohibitive', 'desiderative', 
                   'dubitative', 'hypothetical', 'presumptive', 'permissive', 
                   'admirative', 'ironic-admirative', 'hortative', 'eventitive', 
                   'precative', 'volitive', 'involutive', 'inferential', 
                   'necessitative', 'interrogative', 'injunctive', 
                   'suggestive', 'comissive', 'deliberative', 
                   'propositive', 'dynamic', 
                  ],

    # needed for correlatives in general
    'proform':    ['personal', 'reflexive',
                   'demonstrative', 'interrogative', 'indefinite', 'elective', 'universal', 'negative', 
                   'relative', 'numeral'],
    'pronoun':    ['human','nonhuman','selection'],
    'clitic':     ['tonic', 'enclitic'],
    'proadverb':  ['location','source','goal','time','manner','reason','quality','amount'],
    'distance':   ['proximal','medial','distal'],

    # needed for Spanish
    'formality':  ['familiar', 'polite', 'elevated', 'formal', 'tuteo', 'voseo'],

    # needed for Sanskrit
    'stem':       ['primary', 'causative', 'intensive',],

    # needed for gerunds, supines, participles, and gerundives
    'gender':     ['masculine', 'feminine', 'neuter'],
    'case':       ['nominative', 'accusative', 'dative', 'ablative', 
                   'genitive', 'locative', 'instrumental','disjunctive'],

    # needed for infinitive forms, finite forms, participles, arguments, and graphic depictions
    'voice':      ['active', 'passive', 'middle'], 

    # needed for infinitive forms, finite forms, and participles
    'tense':      ['present', 'past', 'future',], 
    'aspect':     ['aorist', 'imperfect', 'perfect', 'perfect-progressive'], 
}

category_to_grammemes_with_lookups = {
    **category_to_grammemes,
    # needed to tip off which key/lookup should be used to stored cell contents
    'lookup':     ['finite', 'infinitive', 
                   'participle', 'gerundive', 'gerund', 'adverbial', 'supine', 
                   'argument', 'group', 'emoji'],
}

grammeme_to_category = {
    instance:type_ 
    for (type_, instances) in category_to_grammemes_with_lookups.items() 
    for instance in instances
}

lemma_hashing = DictKeyHashing('lemma')

declension_hashing = DictTupleHashing([
        'lemma',           
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'case',       # needed for Latin
    ])

conjugation_template_lookups = DictLookup(
    'conjugation',
    DictKeyHashing('lookup'), 
    {
        # verbs that indicate a subject
        'finite': DictLookup(
            'finite',
            DictTupleHashing([
                    'lemma',           
                    'person',           
                    'number',           
                    'formality',   # needed for Spanish ('voseo')
                    'mood',           
                    'voice',           
                    'tense',           
                    'aspect',           
                ])),
        # verbs that do not indicate a subject
        'infinitive': DictLookup(
            'infinitive',
            DictTupleHashing([
                    'lemma',           
                    'completion', # needed for Old English
                    'voice',      # needed for Latin, Swedish
                    'tense',      # needed for German, Latin
                    'aspect',     # needed for Greek
                ])),
        # verbs used as adjectives, indicating that an action is done upon a noun at some point in time
        'participle': DictLookup(
            'participle',
            DictTupleHashing([
                    'lemma',           
                    'number',  # needed for German
                    'gender',     # needed for Latin, German, Russian
                    'case',       # needed for Latin
                    'voice',      # needed for Russian
                    'tense',      # needed for Greek, Russian, Spanish, Swedish, French
                    'aspect',     # needed for Greek, Latin, German, Russian
                ])),
        # verbs used as adjectives, indicating the purpose of something
        'gerundive': DictLookup('gerundive', declension_hashing),
        # verbs used as nouns
        'gerund': DictLookup('gerund', declension_hashing),
        # verbs used as nouns, indicating the objective of something
        'supine': DictLookup('supine', declension_hashing),
        # verbs used as adverbs
        'adverbial': DictLookup('adverbial', lemma_hashing),
        # a pattern in conjugation that the verb is meant to demonstrate
        'group': DictLookup('group', lemma_hashing),
        # text that follows a verb in a sentence that demonstrates the verb
        'argument': DictLookup(
            'argument',
            DictTupleHashing([
                    'lemma',           
                    'language',           
                    'voice',      # needed for Greek
                    'gender',     # needed for Greek
                    'number',  # needed for Russian
                ])),
        # an emoji depiction of a sentence that demonstrates the verb
        'emoji': DictLookup(
            'emoji',
            DictTupleHashing([
                    'lemma',           
                    'voice',      # needed for Greek, Latin, Proto-Indo-Eurpean, Sanskrit, Swedish
                ])),
    })

basic_pronoun_declension_hashing = DictTupleHashing([
        'number',     # needed for German
        'gender',     # needed for Latin, German, Russian
        'case',       # needed for Latin
    ])

declension_template_lookups = DictLookup(
    'declension',
    DictKeyHashing('proform'), 
    {
        'personal': DictLookup(
            'personal',
            DictTupleHashing([
                    'person',           
                    'number',           
                    'clusivity',   # needed for Quechua
                    'formality',   # needed for Spanish ('voseo')
                    'gender',           
                    'case',           
                ])),
        'demonstrative': DictLookup(
            'demonstrative',
            DictTupleHashing([
                    'distance',
                    'number',     
                    'gender',     
                    'case',       
                ])),
        'interrogative': DictLookup('interrogative', basic_pronoun_declension_hashing),
        'indefinite': DictLookup('indefinite', basic_pronoun_declension_hashing),
        'universal': DictLookup('universal', basic_pronoun_declension_hashing),
        'negative': DictLookup('negative', basic_pronoun_declension_hashing),
        'relative': DictLookup('relative', basic_pronoun_declension_hashing),
        'numeral': DictLookup('numeral', basic_pronoun_declension_hashing),
        'reflexive': DictLookup('reflexive', basic_pronoun_declension_hashing),
    })

class English:
    def __init__(self, 
            pronoun_declension_lookups, 
            conjugation_lookups, 
            predicate_templates, 
            mood_templates):
        self.pronoun_declension_lookups = pronoun_declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.predicate_templates = predicate_templates
        self.mood_templates = mood_templates
    def conjugate(self, grammemes, argument_lookup):
        dependant_clause = {
            **grammemes,
            'language': 'english',
        }
        independant_clause = {
            **grammemes,
            'language': 'english',
            'aspect': 'aorist',
            'tense':     
                'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                'present' if dependant_clause['tense'] in {'future'} else
                dependant_clause['tense']
        }
        lemmas = ['be', 'have', 
                  'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
                  dependant_clause['lemma']]
        if dependant_clause not in argument_lookup:
            # print('ignored english argument:', dependant_clause)
            return None
        argument = argument_lookup[dependant_clause]
        mood_replacements = [
            ('{subject}',              self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'nominative'}]),
            ('{subject|accusative}',   self.pronoun_declension_lookups['personal'][{**dependant_clause, 'case':'accusative'}]),
            ('{predicate}',            self.predicate_templates[{**dependant_clause,'lookup':'finite'}]),
            ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'lookup':'infinitive'}]),
        ]
        sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
        for replaced, replacement in mood_replacements:
            sentence = sentence.replace(replaced, replacement)
        sentence = sentence.replace('{verb', '{'+dependant_clause['lemma'])
        sentence = sentence.replace('{argument}', argument)
        table = self.conjugation_lookups['finite']
        for lemma in lemmas:
            replacements = [
                ('{'+lemma+'|independant}',         table[{**independant_clause, 'lemma':lemma, }]),
                ('{'+lemma+'|independant|speaker}', table[{**independant_clause, 'lemma':lemma, 'person':'1', 'number':'singular'}]),
                ('{'+lemma+'|present}',             table[{**dependant_clause,   'lemma':lemma, 'tense':  'present',  'aspect':'aorist'}]),
                ('{'+lemma+'|past}',                table[{**dependant_clause,   'lemma':lemma, 'tense':  'past',     'aspect':'aorist'}]),
                ('{'+lemma+'|perfect}',             table[{**dependant_clause,   'lemma':lemma, 'aspect': 'perfect'    }]),
                ('{'+lemma+'|imperfect}',           table[{**dependant_clause,   'lemma':lemma, 'aspect': 'imperfect'  }]),
                ('{'+lemma+'|infinitive}',          lemma),
            ]
            for replaced, replacement in replacements:
                sentence = sentence.replace(replaced, replacement)
        if dependant_clause['voice'] == 'middle':
            sentence = f'[middle voice:] {sentence}'
        return sentence

class Emoji:
    def __init__(self, 
            emojiSubjectShorthand, emojiPersonShorthand, emojiShorthand, 
            htmlTenseTransform, htmlAspectTransform, htmlBubble, htmlBubbleScene, 
            mood_templates, person_numbers, person_genders, person_colors):
        self.emojiSubjectShorthand = emojiSubjectShorthand
        self.emojiPersonShorthand = emojiPersonShorthand
        self.emojiShorthand = emojiShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.htmlBubble = htmlBubble
        self.htmlBubbleScene = htmlBubbleScene
        self.mood_templates = mood_templates
        self.person_numbers = person_numbers
        self.person_genders = person_genders
        self.person_colors = person_colors
    def conjugate(self, grammemes, argument_lookup):
        if grammemes not in argument_lookup:
            # print('ignored emoji:', grammemes)
            return None
        audience_lookup = {
            'voseo':    '\\background{🇦🇷}\\n2{🧑\\g2\\c2}',
            'polite':   '\\n2{🧑\\g2\\c2\\💼}',
            'formal':   '\\n2{🤵\\c2\\g2}',
            'elevated': '\\n2{🤴\\g2\\c2}',
        }
        speaker      = self.mood_templates[{**grammemes,'column':'speaker'}]
        audience     = (audience_lookup[grammemes['formality']] 
                        if grammemes['formality'] in audience_lookup 
                        else '\\n2{🧑\\g2\\c2}')
        bubble_style = self.mood_templates[{**grammemes,'column':'bubble-style'}]
        bubble_stem  = self.mood_templates[{**grammemes,'column':'bubble-stem'}]
        prescene_key  = {**grammemes,'column':'prescene'}
        postscene_key = {**grammemes,'column':'postscene'}
        prescene     = self.mood_templates[prescene_key]  if prescene_key  in self.mood_templates else ''
        postscene    = self.mood_templates[postscene_key] if postscene_key in self.mood_templates else ''
        scene        = argument_lookup[grammemes]
        bubble_content = ''.join([
            prescene,
            getattr(self.htmlTenseTransform, grammemes['tense'])(
                getattr(self.htmlAspectTransform, grammemes['aspect'].replace('-','_'))(scene)),
            postscene,
        ])
        bubble = getattr(self.htmlBubble, bubble_style)(bubble_content)
        encoded_recounting = getattr(self.htmlBubbleScene, bubble_stem)(bubble, audience, speaker)
        subject_number = grammemes['number'][0]+('i' if grammemes['clusivity']=='inclusive' else '')
        subject_gender = grammemes['gender'][0]
        recounting = encoded_recounting
        recounting = self.emojiSubjectShorthand.decode(
            recounting, 
            'n'+grammemes['person'], 
            'g'+grammemes['person'],
            'c'+grammemes['person'])
        recounting = self.emojiPersonShorthand.decode(
            recounting,
            [subject_number if str(i+1)==grammemes['person'] else number
             for i, number in enumerate(self.person_numbers)],
            [subject_gender if str(i+1)==grammemes['person'] else gender
             for i, gender in enumerate(self.person_genders)],
            self.person_colors)
        recounting = self.emojiShorthand.decode(recounting)
        return recounting

class Translation:
    def __init__(self, 
            pronoun_declension_lookups, 
            conjugation_lookups, 
            category_to_grammemes,
            filter_lookup,
            english_map=lambda x:x, 
            subject_map=lambda x:x, 
            verb_map=lambda x:x):
        self.pronoun_declension_lookups = pronoun_declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.category_to_grammemes = category_to_grammemes
        self.filter_lookup = filter_lookup
        self.english_map = english_map
        self.subject_map = subject_map
        self.verb_map = verb_map
    def conjugate(self, grammemes, argument_lookup):
        grammemes = {**grammemes, 'language':'translated', 'case':'nominative'}
        if grammemes not in self.pronoun_declension_lookups['personal']:
            print('ignored pronoun:', grammemes)
            return None
        if grammemes not in self.conjugation_lookups['finite']:
            # print('ignored finite:', grammemes)
            return None
        if grammemes not in argument_lookup:
            # print('ignored argument:', grammemes)
            return None
        else:
            return ' '.join([
                    self.subject_map(self.pronoun_declension_lookups['personal'][grammemes]),
                    self.verb_map(self.conjugation_lookups['finite'][grammemes]),
                    argument_lookup[grammemes],
                ])

tsv_parsing = SeparatedValuesFileParsing()
conjugation_annotation  = TableAnnotation(
    grammeme_to_category, {}, {0:'lemma'}, 
    {**category_to_grammemes, 'lookup':'finite'})
pronoun_annotation  = TableAnnotation(
    grammeme_to_category, {}, {}, 
    {**category_to_grammemes, 'proform':'personal'})
predicate_annotation = TableAnnotation(
    grammeme_to_category, {0:'column'}, {}, 
    {**category_to_grammemes, 'lookup':'finite'})
mood_annotation        = TableAnnotation(
    {}, {0:'column'}, {0:'mood'}, {})


conjugation_indexing = NestedTableIndexing(conjugation_template_lookups)
declension_indexing  = NestedTableIndexing(declension_template_lookups)
predicate_indexing = FlatTableIndexing(DictLookup('predicate', DictTupleHashing(['lookup','voice','tense','aspect'])))
mood_indexing = FlatTableIndexing(DictLookup('mood', DictTupleHashing(['mood','column'])))

class CardFormatting:
    def __init__(self):
        pass
    def emoji_focus(self, content):
        fonts = '''sans-serif', 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji'''
        return f'''<div style='font-size:3em; padding: 0.5em; font-family: {fonts}'>{content}</div>'''
    def foreign_focus(self, content):
        return f'''<div style='font-size:3em'>{content}</div>'''
    def foreign_side_note(self, content):
        return f'''<div style='font-size:2em'>{content}</div>'''
    def english_word(self, content):
        return f'''<div>{content}</div>'''

def first_of_options(content):
    return content.split('/')[0]

def cloze(id):
    return lambda content: '{{'+f'''c{id}::{content}'''+'}}'

def replace(replacements):
    def _replace(content):
        for replaced, replacement in replacements:
            content = content.replace(replaced, replacement)
        return content
    return _replace

def require(content):
    return content if content.strip() else None

def compose(*text_functions):
    if len(text_functions) > 1:
        return lambda content: text_functions[0](compose(text_functions[1:]))
    else:
        return text_functions[0]


class CardGeneration:
    def __init__(self, english, emoji, cardFormatting, finite_traversal):
        self.english = english
        self.emoji = emoji
        self.cardFormatting = cardFormatting
        self.finite_traversal = finite_traversal
    def generate(self, translation):
        for tuplekey in self.finite_traversal.tuplekeys(translation.category_to_grammemes):
            dictkey = {
                **self.finite_traversal.dictkey(tuplekey), 
                'proform': 'personal'
            }
            if dictkey in translation.filter_lookup:
                translated_text = translation.conjugate(dictkey, translation.conjugation_lookups['argument'])
                english_text    = self.english.conjugate(dictkey, translation.conjugation_lookups['argument'])
                emoji_text      = self.emoji.conjugate(dictkey, translation.conjugation_lookups['emoji'])
                if translated_text and english_text:
                    yield (dictkey, 
                        self.cardFormatting.emoji_focus(emoji_text), 
                        self.cardFormatting.english_word(translation.english_map(english_text)), 
                        self.cardFormatting.foreign_focus(translated_text))

infinitive_traversal = DictTupleHashing(
    ['tense', 'aspect', 'mood', 'voice'])

bracket_shorthand = BracketedShorthand(Enclosures())

emoji = Emoji(
    EmojiSubjectShorthand(), 
    EmojiPersonShorthand(
        EmojiNumberShorthand(
            HtmlNumberTransform(HtmlPersonPositioning()), bracket_shorthand)),
    AggregateShorthand( 
        TextTransformShorthand(HtmlTextTransform(), bracket_shorthand),
        EmojiGestureShorthand(HtmlGesturePositioning(), bracket_shorthand),
        EmojiModifierShorthand()
    ), 
    HtmlTenseTransform(), HtmlAspectTransform(), HtmlBubble(), HtmlBubbleScene(), 
    mood_indexing.index(
        mood_annotation.annotate(
            tsv_parsing.rows('emoji/mood-templates.tsv'), 1, 1)),
    ['s']*5, 
    ['n']*5, 
    [3,2,1,1,5])
    # [3,1,5,2,4])


english = English(
    declension_indexing.index(
        pronoun_annotation.annotate(tsv_parsing.rows('english/pronoun-declensions.tsv'), 1, 5)),
    conjugation_indexing.index(
        conjugation_annotation.annotate(
            tsv_parsing.rows('english/conjugations.tsv'), 4, 2)),
    predicate_indexing.index(
        predicate_annotation.annotate(
            tsv_parsing.rows('english/predicate-templates.tsv'), 1, 4)),
    mood_indexing.index(
        mood_annotation.annotate(
            tsv_parsing.rows('english/mood-templates.tsv'), 1, 1)),
)

# # ancient greek
# translation = Translation(
#     declension_indexing.index(
#         pronoun_annotation.annotate(
#             tsv_parsing.rows('ancient-greek/pronoun-declensions.tsv'), 1, 4)),
#     conjugation_indexing.index([
#         *conjugation_annotation.annotate(
#             tsv_parsing.rows('ancient-greek/finite-conjugations.tsv'), 3, 4),
#         *conjugation_annotation.annotate(
#             tsv_parsing.rows('ancient-greek/nonfinite-conjugations.tsv'), 3, 2)
#     ]), 
#     subject_map=first_of_options, 
#     verb_map=cloze(1),
#     lemmas = ['be','go','release'])

# spanish
translation = Translation(
    declension_indexing.index(
        pronoun_annotation.annotate(
            tsv_parsing.rows('spanish/pronoun-declensions.tsv'), 1, 5)),
    conjugation_indexing.index([
        *conjugation_annotation.annotate(
            tsv_parsing.rows('spanish/finite-conjugations.tsv'), 3, 4),
        *conjugation_annotation.annotate(
            tsv_parsing.rows('spanish/nonfinite-conjugations.tsv'), 3, 2)
    ]), 
    english_map=replace([('♂','')]),
    subject_map=first_of_options, 
    verb_map=cloze(1),
    category_to_grammemes = {
            **category_to_grammemes,
            'proform':    'personal',
            'number':    ['singular','plural'],
            'clusivity':  'exclusive',
            'formality': ['familiar','tuteo','voseo','formal'],
            'gender':    ['neuter', 'masculine'],
            'voice':      'active',
            'mood':      ['indicative','conditional','subjunctive'],
            'lemma':     ['be [inherently]', 'be [temporarily]', 
                          'have', 'have [in posession]', 
                          'go', 'love', 'fear', 'part', 'know', 'drive'],
        },
    filter_lookup = DictLookup(
        'filter', 
        DictTupleHashing(['formality', 'person', 'number', 'gender']),
        content = {
            ('familiar', '1', 'singular', 'neuter'),
            ('tuteo',    '2', 'singular', 'neuter'),
            ('familiar', '3', 'singular', 'masculine'),
            ('familiar', '1', 'plural',   'masculine'),
            ('familiar', '2', 'plural',   'masculine'),
            ('familiar', '3', 'plural',   'masculine'),
            ('voseo',    '2', 'singular', 'neuter'),
            ('formal',   '2', 'singular', 'masculine'),
            ('formal',   '2', 'plural',   'masculine'),
        }),
)



card_generation = CardGeneration(
    english, emoji, CardFormatting(),
    DictTupleHashing([
    	'formality','clusivity','person','number','gender','tense', 'aspect', 'mood', 'voice', 'lemma']))
for grammemes, emoji_text, english_text, translated_text in card_generation.generate(translation):
    print(grammemes)
    print(emoji_text)
    print(english_text)
    print(translated_text)

# print(emoji.conjugate(grammemes, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'imperative', 'aspect':'imperfect', 'person':'2', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'imperative', 'tense':'past', 'number':'dual'}, translation.conjugation_lookups['emoji']))
# print(emoji.conjugate({**grammemes, 'mood':'dynamic', 'tense':'future', 'number':'plural'}, translation.conjugation_lookups['emoji']))

# translation.conjugate({**grammemes, 'proform':'personal'}, translation.conjugation_lookups['argument'])


# for k,v in list(english_conjugation['finite'].items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_predicate_templates.items({'lemma':'do',**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(english_declension.items({**category_to_grammemes}))[:100]: print(k,v)
# for k,v in list(lookups['finite'].items({'lemma':'release',**category_to_grammemes}))[:100]: print(k,v)



# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('french/finite-conjugations.tsv'), 4, 3),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('french/nonfinite-conjugations.tsv'), 3, 1),
# ])

# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('german/finite-conjugations.tsv'), 2, 3),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('german/nonfinite-conjugations.tsv'), 4, 1),
# ])

# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('latin/finite-conjugations.tsv'), 3, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('latin/nonfinite-conjugations.tsv'), 6, 2),
# ])

# lookups = conjugation_indexing.index(
#     conjugation_annotation.annotate(
#         tsv_parsing.rows('old-english/conjugations.tsv'), 5, 1))

# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('proto-indo-european/finite-conjugations.tsv'), 2, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('proto-indo-european/nonfinite-conjugations.tsv'), 2, 2),
# ])

# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('russian/finite-conjugations.tsv'), 2, 4),
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('russian/nonfinite-conjugations.tsv'), 2, 2),
# ])

# lookups = conjugation_indexing.index([
#     *conjugation_annotation.annotate(
#         tsv_parsing.rows('sanskrit/conjugations.tsv'), 2, 4),
# ])


# lookups = conjugation_indexing.index(
#     conjugation_annotation.annotate(
#         tsv_parsing.rows('swedish/conjugations.tsv'), 4, 2),
# )


# def write(filename, columns):
#     with open(filename, 'w') as file:
#         for row in zip(*columns):
#             if all(cell is not None for cell in row):
#                 file.write(''.join(row)+'\n')




grammemes = {
    'lemma': 'release', 
    'person': '3', 
    'number': 'singular', 
    'clusivity': 'exclusive', 
    'formality': 'familiar', 
    'voice': 'active', 
    'tense': 'present', 
    'aspect': 'aorist',
    'mood': 'indicative', 
    'gender': 'masculine', 
    'language':'english',
}
