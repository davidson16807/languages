import re

class SoundLawNotation:
	def __init__(self, replaced_notations, replacement_notations):
		self.replaced_notations = replaced_notations
		self.replacement_notations = replacement_notations
	def apply(self, replaced, replacement, phonetic_text):
		result = phonetic_text
		replaced_longhand = replaced
		for replaced2, replacement2 in self.replaced_notations:
			replaced_longhand = replaced_longhand.replace(replaced2, replacement2)
		replacement_longhand = replacement
		for replaced2, replacement2 in self.replacement_notations:
			replacement_longhand = replacement_longhand.replace(replaced2, replacement2)
		return re.sub(replaced_longhand, replacement_longhand, phonetic_text)

# sound_laws = SoundLawNotation([('F','ϕθʂçxχhfsʃħzʁ'), ('V','yiʏɪʉɨʊuɯøeɵɘəoɤœɛɞɜɐɔʌæɶaɒɑ')], [('∅','')])
sound_laws = SoundLawNotation([], [('∅','')])

# print('æbdɑmɪnoʊθɔɹæsɪk')
# print(sound_laws.apply('æbdɑmɪnoʊθɔɹæsɪk', '[V][F]',''))