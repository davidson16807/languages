import re

class HtmlPersonPositioning:
    def __init__(self):
        pass
    def farleft(self, person):
        return f'''<span style="position:relative; left:0.2em; top:0.2em;">{person}</span>'''
    def left(self, person):
        return f'''<span style="position:relative; left:0.4em; top:0.2em;">{person}</span>'''
    def center(self, person):
        return f'''{person}'''
    def right(self, person):
        return f'''<span style="position:relative; right:0.4em; top:0.2em;">{person}</span>'''

class HtmlGesturePositioning:
    def __init__(self):
        pass
    def lowered(self, hand): 
        return f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; left:0.3em; top:0.8em;">{hand}</span>'''
    def raised(self, hand): 
        return f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; right:0.6em; bottom:0.7em;">{hand}</span>'''
    def overhead(self, hand): 
        return f'''<span style="display: inline-block; width:0; position:relative; bottom:0.8em;">{hand}</span>'''
    def chestlevel(self, hand): 
        return f'''<span style="font-size: 50%; display: inline-block; width:0; position:relative; right:0.7em; top:0em;">{hand}</span>'''

class HtmlTextTransform:
    def __init__(self):
        pass
    def mirror(self, emoji):
        return f'''<span style="display: inline-block; transform: scale(-1,1)">{emoji}</span>'''
    def flip(self, emoji):
        return f'''<span style="display: inline-block; transform: scale(1,-1)">{emoji}</span>'''

class HtmlPluralityTransform:
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
    def present(scene): 
        return f'''{scene}'''
    def past(scene): 
        return f'''<span style="filter: sepia(0.8)  drop-shadow(0px 0px 5px black)">{scene}</span>'''
    def future(scene): 
        return f'''<span style="filter: blur(0.6px) drop-shadow(0px 0px 5px black)">{scene}</span>'''

class HtmlAspectTransform:
    def __init__(self):
        pass
    def imperfect(scene): 
        return f'''{scene}<progress style="width: 1em;" max="10" value="7"></progress>'''
    def perfect(scene): 
        return f'''{scene}<progress style="width: 1em;" max="10" value="10"></progress>'''
    def aortist(scene): 
        return f'''{scene}'''
    def perfect_progressive(scene): 
        return f'''<span style="filter: sepia(0.3) drop-shadow(0px 0px 2px black)">{scene}<progress style="width: 1em;" max="10" value="10"></progress></span>'''

class HtmlBubble:
    def __init__(self):
        pass
    def affirmative(scene): 
        return f'''<div><span style="border-radius: 0.5em; padding: 0.3em; background:#ddd; ">{scene}</span></div>'''
    def negative(scene): 
        return f'''<div><span style="border-radius: 0.5em; padding: 0.3em; background: linear-gradient(to left top, #ddd 47%, red 48%, red 52%, #ddd 53%); border-style: solid; border-color:red; border-width:6px;">{scene}</span></div>'''

class HtmlBubbleStem:
    def __init__(self):
        pass
    def speech(content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><sup style="color:#ddd;">◥</sup><sub>{speaker}</sub>'''
    def thought(content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><span style="color:#ddd;">•<sub>•</sub></span><sub>{speaker}</sub>'''
    def quote(content, audience, speaker): 
        return f'''{content}<sup style="padding-left: 0.5em; color:#ddd;">◤</sup><sub>{audience}{speaker}</sub>'''

class Enclosures:
    '''
    Finds start and end positions of the first region of text enclosed 
    by an outermost pair of start and end markers, 
    denoted "L" and "R" for short.
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

class EmojiEntityShorthand:
    '''
    Introduces LaTEX style escape sequences that are
    shorthands for characteristics of entities
    that are depicted one or more times within a scene using emoji. 
    For instance, the first entity may 
    be a group of two people ('d' for 'dual')
    who are both male ('m' for 'male')
    and have medium shade skin color (3 on a scale from 1 to 5)
    Whenever the shorthand user desires an emoji modifier 
    that represents these aspects, he can write \p1, \g1, and \c1 respectively.
    [The letters p, g, and c are short for 'person', 'gender', and 'color'] 
    '''
    def __init__(self, emojiPluralityShorthand, pluralities, genders, colors):
        self.emojiPluralityShorthand = emojiPluralityShorthand
        self.pluralities = pluralities
        self.genders = genders
        self.colors = colors
    def decode(self, code):
        '''
        Example usage: 
        shorthand.decode(
            '\p1{🤷\c1\g1}'
            ['s','d','p','di','pi'], 
            ['m','f','m'],
            [3,4,2,3] )
        '''
        emoji = code
        for (i, pluralty) in enumerate(self.pluralities):
            emoji = emoji.replace(f'\\p{i+1}', f'\\{pluralty}')
        '''
        Plurality potentially adds entities to the group
        (e.g. "1st person plural inclusive" includes the 2nd person)
        Therefore we need to decode the plurality shorhand before 
        processing any other characteristics of entities.
        '''
        emoji = self.emojiPluralityShorthand.decode(emoji)
        for (i, gender) in enumerate(self.genders):
            emoji = emoji.replace(f'\\g{i+1}', f'\\{gender}')
        for (i, color) in enumerate(self.colors):
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

class EmojiPluralityShorthand:
    '''
    Introduces LaTEX style escape sequences that represent
    standardized patterns of styled html elements 
    that surround emoji characters and represent the size of groups.
    As an example, plurality is indicated in the shorthand 
    by a 's', 'd', or 'p' (singular, dual, or plural).
    This causes an emoji to be depicted overlapping 
    with other identical emoji characters.
    Information is lost in decoding so no encode() function exists.
    '''
    def __init__(self, htmlPluralityTransform, bracketedShorthand):
        self.htmlPluralityTransform = htmlPluralityTransform
        self.bracketedShorthand = bracketedShorthand
    def decode(self, code):
        emoji = code
        def get_transform(inner_transform, gestureless_count, inclusive=False):
            def _transform(content):
                gestureless = self.bracketedShorthand.decode(
                    r'\\(chestlevel|raised|lowered|overhead)', content, lambda x:'')
                person2 = content.replace('\\g1','\\g2').replace('\\c1','\\c2')
                return inner_transform(
                        person2 if inclusive else content, 
                        *([gestureless]*gestureless_count))
            return _transform
        '''
        "inclusive" plural and "inclusive" dual include the audience,
        so substitute markers for skin color and gender with 
        the equivalent markers for the audience.
        '''
        emoji = self.bracketedShorthand.decode(r'\\s',  emoji, get_transform(self.htmlPluralityTransform.singular, 0))
        emoji = self.bracketedShorthand.decode(r'\\di', emoji, get_transform(self.htmlPluralityTransform.dual_inclusive, 1, True))
        emoji = self.bracketedShorthand.decode(r'\\d',  emoji, get_transform(self.htmlPluralityTransform.dual, 1))
        emoji = self.bracketedShorthand.decode(r'\\pi', emoji, get_transform(self.htmlPluralityTransform.plural_inclusive, 2, True))
        emoji = self.bracketedShorthand.decode(r'\\p',  emoji, get_transform(self.htmlPluralityTransform.plural, 2))
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
            ('\\5',u'\U0001F3FB'), # light
            ('\\3',u'\U0001F3FC'),
            ('\\1',u'\U0001F3FD'), # medium
            ('\\2',u'\U0001F3FE'),
            ('\\4',u'\U0001F3FF'), # dark
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
            ('\\m','\u200D♂️️'),
            ('\\f','\u200D♀️'),
            ('\\','\u200D'),
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

bracket_shorthand = BracketedShorthand(Enclosures())

plurality_shorhand = \
    EmojiPluralityShorthand(
        HtmlPluralityTransform(HtmlPersonPositioning()),
        bracket_shorthand)

emoji_shorthand = AggregateShorthand( 
    EmojiEntityShorthand(plurality_shorhand, ['pi','p'], ['f','m'], ['2','3']),
    TextTransformShorthand(HtmlTextTransform(), bracket_shorthand),
    EmojiGestureShorthand(HtmlGesturePositioning(), bracket_shorthand),
    EmojiModifierShorthand()
)

depiction = lambda content: f'''<div style="font-size:3em; padding: 0.5em;">{content}</div>'''



modifiers = EmojiModifierShorthand()
for emoji in ['👨🏿‍🌾', '🏋🏿‍♂️️', '🏋🏿‍♀️', '👨‍🎓', '👮🏽‍♀️', '🕺', '💃', '🤴', '👸']:
    assert modifiers.decode(modifiers.encode(emoji))==emoji
for code in ['🧑\\m\\4\\🌾', '🧍\\4\\♂️', '🤼\\4\\♂️', '🕺\\m', '🤴\\m', '🕺\\f', '🤴\\f']:
    assert modifiers.encode(modifiers.decode(code))==code

for emoji in ['🧑\\g1\\c1\\🌾']:
    for plurality in ['s','d','p','di','pi']:
        print(depiction(plurality_shorhand.decode('\\'+plurality+'{'+emoji+'}')))

entities = EmojiEntityShorthand(plurality_shorhand, ['pi','p'], ['f','m'], ['2','3'])
print(depiction(
    entities.decode('\\p1{\\🧑\\g1\\c1\\🌾}')))

print(depiction(
    emoji_shorthand.decode('\\p1{\\chestlevel{\\mirror{👍\\c1}}🧑\\g1\\c1\\🌾}')))

