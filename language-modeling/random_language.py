import random

wordlist = open('word-lists.md')
correlatives = open('correlatives.md')
words = [ line.replace('\n','') 
	for line in wordlist.readlines() 
	if '#' not in line and len(line.strip())>0]
correlatives = { line.split(':')[0].strip() : line.split(':')[1].strip().replace('\n','') 
	for line in correlatives.readlines() 
	if ':' in line}
vowel = 'aeiou'
plosive = "pbtdkg"
fricative = "fvθð"
sibilant = "szʃʒ"
nasal = "mn"
liquid = "lr"
consonant = plosive+fricative+sibilant+nasal

V = lambda:	random.choice(vowel)
C = lambda:	random.choice(consonant)

language_to_english = {'':''}
english_to_language = {}

# UNSYSTEMIZED ROOTS
for word in words:
	if word not in english_to_language:
		translation = ''
		while translation in language_to_english:
			translation = random.choice([C() + V() + C(), V() + C(), C() + V()])
		language_to_english[translation]=word
		english_to_language[word]=translation
		print(word, translation)

# SYSTEMIZED ROOTS: mother/father
mother = 'm' + V() + C()
language_to_english[mother] = 'mother'
english_to_language['mother']=mother
father = 'p' + V() + C()
language_to_english[father] = 'father'
english_to_language['father']=father

# SYSTEMIZED ROOTS: correlatives
correlative_specifiers = {correlative_specifier : random.choice([V() + C(), C() + V()]) for correlative_specifier in ['what', 'that', 'some', 'any', 'every', 'no']}
correlative_nouns = {correlative_noun : random.choice([V() + C(), C() + V()]) for correlative_noun in ['person', 'thing', 'place', 'time', 'amount', 'way', 'reason', 'owner']}

for specifier in correlative_specifiers:
	for noun in correlative_nouns:
		correlative = f'{specifier} {noun}'
		translation = f'{correlative_specifiers[specifier]}{correlative_nouns[noun]}'
		language_to_english[translation] = correlative
		english_to_language[correlative] = translation
		if correlative in correlatives:
			language_to_english[translation] = correlatives[correlative]
			english_to_language[correlatives[correlative]] = translation

# SYSTEMIZED ROOTS: pronouns
plural_modifier = ''
while plural_modifier in language_to_english: plural_modifier = random.choice([C() + V() + C(), V() + C(), C() + V()])
dual_modifier = ''
while dual_modifier in language_to_english: dual_modifier = random.choice([C() + V() + C(), V() + C(), C() + V()])
possessive_modifier = ''
while possessive_modifier in language_to_english: possessive_modifier = random.choice([C() + V() + C(), V() + C(), C() + V()])
inclusive_modifier = ''
while inclusive_modifier in language_to_english: inclusive_modifier = random.choice([C() + V() + C(), V() + C(), C() + V()])

# SYSTEMIZED ROOTS: declension, conjugation, and pronouns
declension_modifiers = {}
conjugation_modifiers = {}
pronouns = {}
for declension in ['nominative', 'accusative', 'dative', 'genitive', 'possessive']:
	for person in ['feminine', 'masculine', 'neutral']:
		for person in ['1st person', '2nd person', '3rd person']:
			for plurality in ['singular', 'dual', 'plural']:
				combination = f'{declension} {person} {plurality}'
				declension_modifiers[combination] = V() + C()
				pronouns[combination] = V() + C()

for tense in ['past', 'present', 'future']:
	for person in ['feminine', 'masculine', 'neutral']:
		for person in ['1st person', '2nd person', '3rd person']:
			for plurality in ['singular', 'dual', 'plural']:
				combination = f'{tense} {person} {plurality}'
				conjugation_modifiers[combination] = V() + C()

' '.join(english_to_language[word] for word in ['fast','orange','fox','jump','over','calm','dog'])
' '.join(english_to_language[word] for word in ['our', 'father','that person','in','sky','your', 'name', 'be','holy'])

