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

class HtmlBubbleType:
    def __init__(self):
        pass
    def speech(content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><sup style="color:#ddd;">◥</sup><sub>{speaker}</sub>'''
    def thought(content, audience, speaker): 
        return f'''{content}<sub>{audience}</sub><span style="color:#ddd;">•<sub>•</sub></span><sub>{speaker}</sub>'''
    def quote(content, audience, speaker): 
        return f'''{content}<sup style="padding-left: 0.5em; color:#ddd;">◤</sup><sub>{audience}{speaker}</sub>'''

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
    def __init__(self, htmlGesturePositioning):
        self.htmlGesturePositioning = htmlGesturePositioning
    def decode(self, code):
        emoji = code
        brackets = '[{]([^}]*?)[}]'
        print('vanilla', emoji)
        print()
        emoji = re.sub(r'\\raised'+brackets, 
            self.htmlGesturePositioning.raised('\\1'), emoji)
        print('raised', emoji)
        print()
        emoji = re.sub(r'\\lowered'+brackets, 
            self.htmlGesturePositioning.lowered('\\1'), emoji)
        print('lowered', emoji)
        print()
        emoji = re.sub(r'\\overhead'+brackets, 
            self.htmlGesturePositioning.overhead('\\1'), emoji)
        print('overhead', emoji)
        print()
        emoji = re.sub(r'\\chestlevel'+brackets, 
            self.htmlGesturePositioning.chestlevel('\\1'), emoji)
        print('chestlevel', emoji)
        print()
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
    def __init__(self, htmlTextTransform):
        self.htmlTextTransform = htmlTextTransform
    def decode(self, code):
        emoji = code
        brackets = '[{]([^}]*?)[}]'
        print('premirror', emoji)
        print()
        emoji = re.sub(r'\\mirror'+brackets, 
            self.htmlTextTransform.mirror('\\1'), emoji)
        print('mirror', emoji)
        print()
        emoji = re.sub(r'\\flip'+brackets, 
            self.htmlTextTransform.flip('\\1'), emoji)
        print('flip', emoji)
        print()
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
    def __init__(self, htmlPluralityTransform):
        self.htmlPluralityTransform = htmlPluralityTransform
    def decode(self, code):
        emoji1 = code
        brackets = '[{]([^}]*?)[}]'
        # emoji1 = re.sub(r'\\s'+brackets, 
        #     self.htmlPluralityTransform.singular('\\1'), emoji1)
        # emoji1 = re.sub(r'\\d'+brackets, 
        #     self.htmlPluralityTransform.dual('\\1','\\1'), emoji1)
        # emoji1 = re.sub(r'\\p'+brackets, 
        #     self.htmlPluralityTransform.plural('\\1','\\1','\\1'), emoji1)
        emoji2 = emoji1
        '''
        "inclusive" plural and "inclusive" dual include the audience,
        so substitute markers for skin color and gender with 
        the equivalent markers for the audience.
        '''
        for match in re.finditer(r'\\d'+brackets, emoji1):
            markup = match.group(0)
            content = match.group(1)
            gestureless = re.sub(
                r'\\(chestlevel|raised|lowered|overhead)'+brackets, 
                '', content)
            replacement = self.htmlPluralityTransform.dual_inclusive(
                            content, 
                            gestureless)
            emoji2 = emoji2.replace(markup, replacement)
        for match in re.finditer(r'\\di'+brackets, emoji1):
            markup = match.group(0)
            content = match.group(1)
            person2 = content.replace('\\g1','\\g2').replace('\\c1','\\c2')
            gestureless = re.sub(
                r'\\(chestlevel|raised|lowered|overhead)'+brackets, 
                '', content)
            replacement = self.htmlPluralityTransform.dual_inclusive(
                            person2, 
                            gestureless)
            emoji2 = emoji2.replace(markup, replacement)
        emoji1 = emoji2
        for match in re.finditer(r'\\p'+brackets, emoji1):
            markup = match.group(0)
            content = match.group(1)
            gestureless = re.sub(
                r'\\(chestlevel|raised|lowered|overhead)'+brackets, 
                '', content)
            replacement = self.htmlPluralityTransform.plural_inclusive(
                            content, 
                            gestureless, 
                            gestureless)
            emoji2 = emoji2.replace(markup, replacement)
        emoji1 = emoji2
        for match in re.finditer(r'\\pi'+brackets, emoji1):
            markup = match.group(0)
            content = match.group(1)
            gestureless = re.sub(
                r'\\(chestlevel|raised|lowered|overhead)'+brackets, 
                '', content)
            replacement = self.htmlPluralityTransform.plural_inclusive(
                            content.replace('\\g1','\\g2').replace('\\c1','\\c2'), 
                            gestureless, 
                            gestureless)
            emoji2 = emoji2.replace(markup, replacement)
        return emoji2

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

class EmojiShorthands:
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
        print(emoji)
        print()
        for (i, shorthand) in enumerate(self.shorthands):
            emoji = shorthand.decode(emoji)
            print(i, emoji)
            print()
        return emoji

depiction = lambda content: f'''<div style="font-size:3em; padding: 0.5em;">{content}</div>'''

modifiers = EmojiModifierShorthand()
for emoji in ['👨🏿‍🌾', '🏋🏿‍♂️️', '🏋🏿‍♀️', '👨‍🎓', '👮🏽‍♀️', '🕺', '💃', '🤴', '👸']:
    assert modifiers.decode(modifiers.encode(emoji))==emoji
for code in ['🧑\\m\\4\\🌾', '🧍\\4\\♂️', '🤼\\4\\♂️', '🕺\\m', '🤴\\m', '🕺\\f', '🤴\\f']:
    assert modifiers.encode(modifiers.decode(code))==code

pluralities = \
	EmojiPluralityShorthand(
		HtmlPluralityTransform(
			HtmlPersonPositioning()))
for emoji in ['🧑\\g1\\c1\\🌾']:
	for plurality in ['s','d','p','di','pi']:
		print(depiction(pluralities.decode('\\'+plurality+'{'+emoji+'}')))


entities = EmojiEntityShorthand(pluralities, ['pi','p'], ['f','m'], ['2','3'])
print(depiction(
    entities.decode('\\p1{\\🧑\\g1\\c1\\🌾}')))

shorthand = EmojiShorthands( 
    TextTransformShorthand(HtmlTextTransform()), 
    EmojiEntityShorthand(pluralities, ['pi','p'], ['f','m'], ['2','3']),
    EmojiGestureShorthand(HtmlGesturePositioning()),
    EmojiModifierShorthand()
)

print(depiction(
    shorthand.decode('\\p1{\\raised{\\mirror{🖕}}🧑\\g1\\c1\\🌾}')))