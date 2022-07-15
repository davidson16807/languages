import re

from csv_functions import csv_tuples

class FeaturalPhoneticAlphabet:
	def __init__(self, vowels, consonants):
		self.preclean = [('←→',''),('↑↓','')]
		self.vowels = [(ipa, featural) for (ipa, featural) in vowels]
		self.consonants = [(ipa, featural) for (ipa, featural) in consonants]
		self.postclean = [('[↑↓←→ⁿᴿᴸʳˡₒʰᵛᵖʷᴵ`]+',''),]
	def from_ipa(self, ipa_text):
		featural_text = ipa_text
		for ipa, featural in self.vowels:
			featural_text = featural_text.replace(ipa, featural)
		for ipa, featural in self.consonants:
			featural_text = featural_text.replace(ipa, featural)
		return featural_text
	def to_ipa(self, featural_text):
		ipa_text = featural_text
		# for ipa, featural in self.preclean:
		# 	ipa_text = ipa_text.replace(featural, ipa)
		for ipa, featural in self.vowels:
			ipa_text = ipa_text.replace(featural, ipa)
		for ipa, featural in self.consonants:
			ipa_text = ipa_text.replace(featural, ipa)
		# for ipa, featural in self.postclean:
		# 	ipa_text = ipa_text.replace(featural, ipa)
		return ipa_text

# featural = FeaturalPhoneticAlphabet(
# 	csv_tuples('ipa-vowel-to-schwa-relative-featural.tsv'), 
# 	csv_tuples('ipa-consonant-to-featural.tsv'))
# print('æbdɑmɪnoʊθɔɹæsɪk')
# print(featural.to_ipa(featural.from_ipa('æbdɑmɪnoʊθɔɹæsɪk')))