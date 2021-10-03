import re
import inflection

import csv_functions
from featural_phonetic_alphabet import FeaturalPhoneticAlphabet

pronunciation_tuples = csv_functions.tuples_from_csv('../english/pronunciation/ipa_narrow_pronunciation_to_word.tsv')
pronunciation_lookup = csv_functions.setdict_from_tuples(pronunciation_tuples, ['pronunciation','word'], ['word'])

custom_pronunciation_lookup = {
	'i': 'aɪ',
	'my': 'maɪ',
	'him': 'hɪm',
	'who': 'hu',
	'wʌ': 'wʌt',
	's': 'z',
	'said': 'sɛd',
}

replacements = [
	('ch','t∫'),
	('sh','∫'),
	('th','θ'),
	('qu','kw'),
	('x','ks'),
	('ng','ŋ'),
	('ca','ka'),
	('ce','se'),
	('ci','si'),
	('co','ko'),
	('cu','ku'),
	('ey','eɪ'),
	('ss','s'),
	('tt','t'),
	('tia','t∫ɪeɪ'),
	('tion','t∫n'),
]
def guess_pronunciation(word):
	result = word
	for replaced, replacement in replacements:
		result = result.replace(replaced, replacement)
	return result

def pronounce_plural(singular_ipa):
	return f'{singular_ipa}z' if singular_ipa[-1] in 'bvdðgmnrl' else f'{singular_ipa}s'

def pronounce(word):
	lower_case = word.lower()
	stripped = lower_case.strip("'")
	singular = inflection.singularize(lower_case)
	return (custom_pronunciation_lookup[lower_case] if lower_case in custom_pronunciation_lookup
		else list(pronunciation_lookup[lower_case])[0] if lower_case in pronunciation_lookup
		else pronounce_plural(list(pronunciation_lookup[singular])[0]) if singular in pronunciation_lookup
		else f"'{pronounce(stripped)}" if lower_case.startswith("'")
		else f"{pronounce(stripped)}'" if lower_case.endswith("'")
		else pronounce_plural(pronounce(stripped.split("'")[0])) if "'" in stripped
		else guess_pronunciation(lower_case))

featural = FeaturalPhoneticAlphabet(
	csv_functions.tuples_from_csv('../featural-alphabet/ipa-vowel-to-schwa-relative-featural.tsv'), 
	csv_functions.tuples_from_csv('../featural-alphabet/ipa-consonant-to-featural.tsv'))

# A short sample text with good coverage over the English alphabet
text = 'the quick brown fox jumps over the lazy dog'

# Religious texts: texts for which many translations are available to compare against
text1 = '''
Our father, who art in heaven, hallowed be thy name. Thy kingdom come, thy will be 
done on earth as it is in heaven. Give us this day our daily bread; and forgive us our 
trespasses as we forgive those who trespass against us; and lead us not into 
temptation, but deliver us from evil. Amen.
'''
text1 = '''
Hail Mary full of grace, the Lord is with thee. Blessed are thou among women and 
blessed is the fruit of thy womb Jesus. Holy Mary mother of God, pray for us sinners 
now and at the hour of our death. Amen.
'''
text = '''
And he said, "There was a man who had two sons. And the younger of them said to his father, 
'Father, give me the share of property that is coming to me.' And he divided his property between them. 
Not many days later, the younger son gathered all he had and took a journey into a far country, 
and there he squandered his property in reckless living. 
And when he had spent everything, a severe famine arose in that country, and he began to be in need. 
So he went and hired himself out to one of the citizens of that country, 
who sent him into his fields to feed pigs. 
And he was longing to be fed with the pods that the pigs ate, and no one gave him anything.

"But when he came to himself, he said, 'How many of my father's hired servants have more than enough bread, 
but I perish here with hunger! I will arise and go to my father, and I will say to him, 
"Father, I have sinned against heaven and before you. I am no longer worthy to be called your son. 
Treat me as one of your hired servants."' And he arose and came to his father. 
But while he was still a long way off, his father saw him and felt compassion, 
and ran and embraced him and kissed him. 
And the son said to him, 'Father, I have sinned against heaven and before you. 
I am no longer worthy to be called your son.' But the father said to his servants,
'Bring quickly the best robe, and put it on him, and put a ring on his hand, 
and shoes on his feet. And bring the fattened calf and kill it, and let us eat and celebrate. 
For this my son was dead, and is alive again; he was lost, and is found.' 
And they began to celebrate.

"Now his older son was in the field, and as he came and drew near to the house, 
he heard music and dancing. And he called one of the servants and asked what these things meant. 
And he said to him, 'Your brother has come, and your father has killed the fattened calf, 
because he has received him back safe and sound.' 
But he was angry and refused to go in. His father came out and entreated him, 
but he answered his father, 'Look, these many years I have served you, 
and I never disobeyed your command, yet you never gave me a young goat, 
that I might celebrate with my friends. 
But when this son of yours came, who has devoured your property with prostitutes, 
you killed the fattened calf for him!' 
And he said to him, 'Son, you are always with me, and all that is mine is yours. 
It was fitting to celebrate and be glad, for this your brother was dead, and is alive; 
he was lost, and is found.'"
'''
# Modern linguistic sample texts: texts that offer good coverage over verb tenses, noun cases, and idioms
text1 = '''
Once there was a king. He was childless. The king wanted a son. He asked his priest: 
"May a son be born to me!" The priest said to the king: "Pray to the god Werunos." 
The king approached the god Werunos to pray now to the god. "Hear me, father Werunos!" 
The god Werunos came down from heaven. "What do you want?" "I want a son." 
"Let this be so," said the bright god Werunos. The king's lady bore a son.
'''
text1 = '''
A sheep that had no wool saw horses, one of them pulling a heavy wagon, 
one carrying a big load, one carrying a man quickly. The sheep said to the horses: 
"My heart pains me, seeing a man driving horses." The horses said: 
"Listen, sheep, our hearts pain us when we see this: a man, the master, 
makes the wool of the sheep into a warm garment for himself. And the sheep has no wool." 
Having heard this, the sheep fled into the plain.
'''
text1 = '''
The wren used to have his nest in the garage. One time, the parents had both flown out - 
looking for something for the fledglings to eat - and had left them there all alone.
After a while, Father Wren returned back home.
"What's happened here?" he asked. "Who got you all riled up like this, eh? You're all scared witless!"
"Oh, Dad," they said, "some big monster just came by. He was really awful and scarey! 
He looked right into the nest with his big eyes and we got really scared!"
"Is that right?" Father Wren asked, "where did he go?"
"Well," they said, "he went off over there."
"Just wait here!" Father Wren said, "I'm going to go after him. 
Don't you worry about a thing, children. I'm going to get him." And with that he flew off after him.-
When he came around the next corner, he saw a lion walking along there.
But the wren was not afraid. He landed on the lion's back and started chewing him out. 
"What business do you have coming to my house," he said, 
"and terrifying my children, eh?! You're really offside, you know."
The lion ignored him completely and kept on going.
But now the little wren was really pissed. "You have no business being there, I tell you! 
And if you come back," he said, "well, then you'll see! I don't really want to do it," 
he said and finally lifted one of his legs, "but I'll break your back with my leg in a second!"
And with that he flew back to the nest.
"There you go, children," he said, "I've taught that old lion a lesson he'll never forget. 
It's not likely we'll see much of his kind anymore, eh?" 
'''

pronunciation = ''.join(pronounce(block) for block in re.findall('''[a-zA-Z']+|[^a-zA-Z']+''', text))

print(pronunciation)
print(featural.from_ipa(pronunciation))
print(featural.to_ipa(featural.from_ipa(pronunciation)))