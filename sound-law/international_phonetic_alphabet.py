import re
import inflection

class EnglishIpaInflection:
	def __init__(self):
		pass
	def is_maybe_plural(self, text):
		return re.search("[zs]\\b", text)
	def is_maybe_singular(self, text):
		return not self.is_maybe_plural(text)
	def is_maybe_possessive(self, text):
		return self.is_maybe_plural(text)
	def plural_to_singular(self, plural_ipa):
		return re.sub(f'[ieɘə]?[sz]\\b', '', plural_ipa)
	def singular_to_plural(self, singular_ipa):
		return f'{singular_ipa}z' if singular_ipa[-1] in 'bvdðgmnrl' else f'{singular_ipa}s'
	def possessive_to_root(self, possessive_ipa):
		return re.sub(f'[ieɘə]?[sz]\\b', '', possessive_ipa)
	def root_to_possessive(self, root_ipa):
		return self.singular_to_plural(root_ipa)


class EnglishTextInflection:
	def __init__(self):
		pass
	def is_maybe_plural(self, text):
		return "'" in text and not text.startswith("'") and not text.endswith("'")
	def is_maybe_singular(self, text):
		return not self.is_maybe_plural(text)
	def is_maybe_possessive(self, text):
		return "'" in text
	def plural_to_singular(self, plural_ipa):
		return inflection.singularize(plural_ipa)
	def singular_to_plural(self, singular_ipa):
		return inflection.pluralize(singular_ipa)
	def possessive_to_root(self, posessive_ipa):
		return posessive_ipa.split("'")[0]


class LanguageIpaInference:
	def __init__(self, regex_ipa_tuples):
		self.regex_ipa_tuples = regex_ipa_tuples
	def pronounce(self, word):
		result = word
		for replaced, replacement in self.regex_ipa_tuples:
			result = re.sub(replaced, replacement, result)
		# replacements may use capitals to distinguish English letters from IPA phonemes, 
		# so remember to set to lowercase afterward
		return result.lower() 


class LanguageIpaReference:
	def __init__(self, ipa_lookup, ipa_inflection, text_inflection):
		self.ipa_lookup = ipa_lookup
		self.ipa_inflection = ipa_inflection
		self.text_inflection = text_inflection
	def pronounce(self, word):
		lower_case = word.lower()
		stripped = lower_case.strip("'")
		singular = self.text_inflection.plural_to_singular(word)
		return (list(self.ipa_lookup[lower_case])[0] if lower_case in self.ipa_lookup
			else f"'{self.pronounce(stripped) or ''}" if lower_case.startswith("'") and lower_case.endswith("'")
			else f"'{self.pronounce(stripped) or ''}" if lower_case.startswith("'")
			else f"{self.pronounce(stripped) or ''}'" if lower_case.endswith("'")
			else self.ipa_inflection.singular_to_plural(list(self.ipa_lookup[singular])[0]) 
				if singular in self.ipa_lookup
			else self.ipa_inflection.root_to_possessive(self.pronounce(self.text_inflection.possessive_to_root(stripped)) or '') 
				if self.text_inflection.is_maybe_possessive(stripped)
			else None)
