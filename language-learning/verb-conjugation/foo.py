
class EmojiEncoding:
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

encoding = EmojiEncoding()
print(encoding.decode(encoding.encode(u'👨🏿‍🌾'))==u'👨🏿‍🌾')
print(encoding.encode(encoding.decode(u'👨\\4\\🌾'))==u'👨\\4\\🌾')
print(encoding.decode(u'🧍\\4\\♂️🤼\\4\\♂️🏋\\4\\♂️️🏊\\4\\♂️💂\\4\\♂️👨\\4\\🌾'))
print(encoding.decode(u'🧍\\4\\♀️🤼\\4\\♀️🏋\\4\\♀️️🏊\\4\\♀️💂\\4\\♀️👨\\4\\🌾'))
print(encoding.decode(u'🧍\\4\\m🤼\\4\\m🏋\\4\\m️🏊\\4\\m💂\\4\\m👨\\4\\🌾🪂\\4\\m'))
print(encoding.decode(u'🧍\\4\\f🤼\\4\\f🏋\\4\\f️🏊\\4\\f💂\\4\\f👨\\4\\🌾🪂\\4\\f'))
print(encoding.encode(u'🏋🏿‍♂️️'))
print(encoding.encode(u'🏋🏿‍♀️'))
print(encoding.encode(u'👨🏿‍🌾'))
print(encoding.encode(u'👨‍🎓'))
print(encoding.encode(u'👩‍⚕️'))
print(encoding.encode(u'👮🏽‍♀️'))
print(encoding.encode(u'🧑‍💼'))
print(encoding.encode(u'🧑‍🏭'))
print(encoding.encode(u'💂‍♀️'))
print(encoding.encode(u'🕺'))
print(encoding.encode(u'💃'))
print(encoding.encode(u'🤴'))
print(encoding.encode(u'👸'))
print(encoding.encode(u'👸'))
print(encoding.decode(u'🕺\\m'))
print(encoding.decode(u'🤴\\m'))
print(encoding.decode(u'🕺\\f'))
print(encoding.decode(u'🤴\\f'))
