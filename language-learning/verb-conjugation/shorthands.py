import re

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
            ('\\m',u'\U0000200D♂️️'),
            ('\\f',u'\U0000200D♀️'),
            ('\\n',''),
            ('\\',u'\U0000200D'),
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

class EmojiBubbleShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    standardized patterns of styled html elements 
    that surround emoji characters and represent speech and thought bubbles.
    Current supported sequences include:
        \bubble{}
        \forbidden{}
        \lspeech{}
        \rspeech{}
        \lthought{}
        \rthought{}
    '''
    def __init__(self, htmlBubble, bracketedShorthand):
        self.htmlBubble = htmlBubble
        self.bracketedShorthand = bracketedShorthand
    def decode(self, code):
        emoji = code
        emoji = self.bracketedShorthand.decode(r'\\bubble', emoji, self.htmlBubble.affirmative)
        emoji = self.bracketedShorthand.decode(r'\\forbidden', emoji, self.htmlBubble.negative)
        emoji = self.bracketedShorthand.decode(r'\\box', emoji, self.htmlBubble.box)
        emoji = emoji.replace('\\rspeech', "<sup style='color:#ddd;'>◥</sup>")
        emoji = emoji.replace('\\lspeech', "<sup style='padding-left: 0.5em; color:#ddd;'>◤</sup>")
        emoji = emoji.replace('\\rthought', "<span style='color:#ddd;'>•<sub>•</sub></span>")
        emoji = emoji.replace('\\lthought', "<span style='padding-left: 0.5em; color:#ddd;'><sub>•</sub>•</span>")
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
