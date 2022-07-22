
import re
import copy

import pypeg2
from pypeg2 import attr, optional, maybe_some, blank, endl

text = re.compile(r'[^\\{}]*', re.MULTILINE | re.DOTALL)
name = re.compile(r'[a-z0-9]*', re.IGNORECASE | re.MULTILINE | re.DOTALL)

'''
"ShorthandElement" is the parent class of all grammar rule classes in our LaTEX style shorthands
'''
class ShorthandElement:
    def __init__(self):
        pass

class Text(ShorthandElement):
    def __init__(self, content=''):
        self.content = content

class EscapedExpression(ShorthandElement):
    def __init__(self, name=''):
        self.name = name

class BracketedExpression(ShorthandElement):
    def __init__(self, name='', content=None):
        self.name = name
        self.content = content

shorthand = \
	pypeg2.some([
		BracketedExpression, 
		EscapedExpression, 
		Text
	])

Text.grammar = ('\\', attr('content', text))

EscapedExpression.grammar = ('\\', attr('name', name))

BracketedExpression.grammar = \
	('\\', attr('name', name), '{', attr('content', shorthand), '}')

escape_lookup = {
	'\\': '\u200D'
}

bracketed_lookup = {
	'raised': lambda x: f''''''
	'lowered': lambda x: f''''''
	'overhead': lambda x: f''''''
	'chestlevel': lambda x: f''''''
}

class Shorthand:
	def __init__(self, bracketed_lookup, escape_lookup):
		self.bracketed_lookup = bracketed_lookup
		self.escape_lookup = escape_lookup
	def transform(input_elements):
		output_elements = []
		for element in input_elements:
		    if isinstance(element, EscapedExpression):
		    	output_elements.append(bracketed_lookup[element.name](element.content))
		    elif isinstance(element, EscapedExpression):
		    	output_elements.append(escape_lookup[element.name])
		    elif isinstance(element, Text):
		    	output_elements.append(element.content)
		return output_elements

shorthand1 = Shorthand(
	{}, 
	{
        '\\5': u'\U0001F3FB', # light
        '\\3': u'\U0001F3FC',
        '\\1': u'\U0001F3FD', # medium
        '\\2': u'\U0001F3FE',
        '\\4': u'\U0001F3FF', # dark
        '🧒\\m': '👦',
        '🧒\\f': '👧',
        '🧑\\m': '👨',
        '🧑\\f': '👩',
        '🧓\\m': '👴',
        '🧓\\f': '👵',
        '🕺\\m': '🕺',
        '🕺\\f': '💃',
        '🤴\\m': '🤴',
        '🤴\\f': '👸',
        '\\m': '\u200D♂️️',
        '\\f': '\u200D♀️',
        '\\': '\u200D',
    }
)
elements = pypeg2.parse(code, shorthand)
elements = shorthand1.transform(elements)
elements = shorthand2.transform(elements)