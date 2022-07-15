import re
import inflection

import csv_functions
from featural_phonetic_alphabet import FeaturalPhoneticAlphabet
from international_phonetic_alphabet import EnglishIpaInflection, EnglishTextInflection, LanguageIpaInference, LanguageIpaReference
from sound_law import SoundLawNotation

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

ipa_text_tuples = csv_functions.tuples_from_csv('../english/pronunciation/ipa_narrow_us_pronunciation_to_word.tsv')
ipa_text_tuples_proscription = csv_functions.tuples_from_csv('../english/pronunciation/ipa_narrow_us_pronunciation_to_word_prescriptions.tsv')
text_to_ipa_lookup = csv_functions.setdict_from_tuples(ipa_text_tuples, ['pronunciation','word'], ['word'])
text_to_ipa_lookup.update(csv_functions.setdict_from_tuples(ipa_text_tuples_proscription, ['pronunciation','word'], ['word']))

ipa_inflection = EnglishIpaInflection()
text_inflection = EnglishTextInflection()
ipa_inference = LanguageIpaInference(csv_functions.tuples_from_csv('../english/pronunciation/regex_to_ipa_guess.tsv'))
ipa_reference = LanguageIpaReference(text_to_ipa_lookup, ipa_inflection, text_inflection)

'''
# uncomment this code in order to iterate through all possible words by frequency and examine correctness exhaustively
word_frequency_tuples = csv_functions.tuples_from_csv('../english/vocabulary/frequency_from_subtitles.txt', delimeter=' ')
for (i, (word, frequency)) in enumerate(word_frequency_tuples):
	if i < 1e3 and ipa_reference.pronounce(word) != ipa_inference.pronounce(word):
		print(word, '\t', ipa_reference.pronounce(word) or '', '\t', ipa_inference.pronounce(word))
'''

ipa = ''.join(ipa_reference.pronounce(block) or ipa_inference.pronounce(block) 
	for block in re.findall('''[a-zA-Z']+|[^a-zA-Z']+''', text))

featural_map = FeaturalPhoneticAlphabet(
	csv_functions.tuples_from_csv('../featural-alphabet/ipa-vowel-to-a-relative-featural.tsv'), 
	csv_functions.tuples_from_csv('../featural-alphabet/ipa-consonant-to-h-relative-featural.tsv'),
	# csv_functions.tuples_from_csv('../featural-alphabet/ipa-consonant-to-fricative-featural.tsv'),
)

'''
# uncomment this code in order to test that the featural alphabet can uniquely represent any text given to it
# This is done by demonstrating isomorphism with the ipa version of text
print(ipa)
print(featural_map.from_ipa(ipa))
print(featural_map.to_ipa(featural_map.from_ipa(ipa)))
'''

# ipa = 'dʒode'
# ipa = 'dʒode'
# sound_law_notation = SoundLawNotation([('F','ϕθʂçxχhfsʃħzʁ'), ('V','yiʏɪʉɨʊuɯøeɵɘəoɤœɛɞɜɐɔʌæɶaɒɑ')], [('∅','')])
sound_law_notation = SoundLawNotation(
	[
	("\b", "(?!([ha↑↓←→]|[ᴿᴸʳˡⁿⁱ'ᶠʰᵛᵖʷ]))"),
	("`", "[ᴿᴸʳˡⁿⁱ'ᶠʰᵛᵖʷ]")
	], 
	[('∅','')])
sound_laws = [
	#Grimm's Law                                                                      
	# ("(?<=[^sᵖʷ][F])ᵖ", "∅"), #voiceless stops fricativize                                                      
	# ("(?<=[F])ᵛᵖ",      "ᵖ"), #voiced stops unvoice                                                             
	# ("(?<=[F])ʰᵛᵖ",     "ᵛᵖ"),#voiced spirates unaspirate                                                       
]

def test(n, replaced, replacement, ipa):
	return featural_map.to_ipa( # featural_map.to_ipa
		sound_law_notation.apply(
			replaced.replace("{{n}}",str(n)), replacement, featural_map.from_ipa(ipa)))

# The following is the result of a traversal through Ohala (1983), "The Origin of Sound Patterns in Vocal Tract Constraints" 
# Identifying sound laws that can be described in a highly generic way using sound laws,
# along with examples of that sound law having occured in real languages, where possible

# voicing requires airflow but plosives cause rapid pressure build up and equilibration, preventing further sound
# so long voiced plosives cause issues, one resolution is to prenasalize (Japanese 'read' /dʒode/→/dʒonde/)     
print(test(8, "(a[↑→ʷⁿ]*)(h←{0,{{n}}})(`*?ᵛᵖ)a", "\\1\\2ⁿ\\2\\3a", 'dʒode'))# == 'dʒonde') # Japanese "read"
# voicing requires airflow but plosives cause rapid pressure build up and equilibration, preventing further sound
# so long voiced plosives cause issues, one resolution is to produce an implosive (Sindhi 'donkey' /gaddaha/→/gaɗahu/)       
print(test(8, "(h←{0,{{n}}}`*?)ᵛᵖa", "\\1ᶠᵛa", "da"))# == "ða") # Ngɔm, "lie down"
# voicing requires airflow but plosives cause rapid pressure build up and equilibration, preventing further sound
# so long voiced plosives cause issues, one resolution is to spirantize/fricativize (Ngɔm 'lie down' /daad/→/ðað/)             
print(test(8, "(a[↑→ʷⁿ]*)(h←{0,{{n}}}`*?)ᵛᵖa", "\\1\\2ⁱᵛᵖa", "gadaha")) # == "gaɗaha") # Sindhi "donkey"
# voicing requires airflow but plosives cause rapid pressure build up and equilibration, preventing further sound
# so long voiced plosives cause issues, one resolution is to devoice (Nubian 'scorpion' /mugɔn/→/mukɔn/)        
print(test(8, "(h←{0,{{n}}}`*?)ᵛᵖa", "\\1ᵖa", "mugɔn"))  # == "mukɔn") # Nubian "scorpion"
# voicing requires airflow but plosives cause rapid pressure build up and equilibration, preventing further sound
# but voicing can be enabled if the length of subsequent vowels are shortened (English 'butter' /bʌtər/→/bʌdər/)
print(test(8, "(h←{0,{{n}}}`*?)ᵖ(a[↑→ʷⁿ]*h←*`*?[ᴿʳ])", "\\1ᵛᵖ\\2", "bʌtəɹ")) # == "bʌdər" # English "butter"

# 
# voicing requires airflow and therefore need low pressure to go at length, but fricatives requires high pressure to be effective,
# so voiced fricatives causes issues, one resolution is to defricativize (English 'live', hypothetical sound law)
print(test(10, "(h←{0,{{n}}}`*?)ᶠᵛ`*\\b", "\\1ᵛᵖ", "lɪv")) # == "lib" # English "live", hypothetical example
# voicing requires airflow and therefore need low pressure to go at length, but fricatives requires high pressure to be effective,
# so voiced fricatives causes issues, one resolution is to devoice (English 'live', hypothetical sound law)
print(test(10, "(h←{0,{{n}}}`*?)ᶠᵛ`*\\b", "\\1ᶠ", "lɪv")) # == "lif" # English "live", hypothetical example

# DEVOICING FINAL VOWELS
# word boundaries require a cessation in pressure but closed vowels also cause constriction, 
# subglottal pressure, equilibration and thereby cessation, so final closed vowels tend to drop
print(test(6, "a↑{{{n}},}[→ʷⁿ]*\b", "", "nunt∫aku")) # == "live" # English "nunchuk"

# FRICATIVIZATION
# frication and affrication occurs with sufficient air velocity and thereby constriction
# so plosives followed by close vowels tend to fricativize, unless an adjacent nasal vents pressure elsewhere
print(test(6, "(?<!ⁿ)(h←*)([ⁱ'ʰ]*?)(ᵛ?)ᵖ([ʷ]*)(a↑{{{n}},}[→ʷ]*)(?!ⁿ)", "\\1\\2ᶠ\\3ᵖ\\4\\5", "bumo")) # == "bvumo" # Mvumbo "fruit"
# frication and affrication occurs with sufficient air velocity and thereby constriction, 
# so plosives followed by close vowels tend to fricativize, unless an adjacent nasal vents pressure elsewhere
print(test(6, "(?<!ⁿ)(h←{5,8})([ⁱ'ʰᵛ]*?)ᵖ([ʷ]*)(a↑{{{n}},}[→ʷ]*)(?!ⁿ)", "h←←←←←←\\2ᶠᵖ\\3\\4", "nætuɹəl")) # == "næt∫uɹəl" # English "natural"
print(test(6, "(?<!ⁿ)(h←{0,4})([ⁱ'ʰᵛ]*?)ᶠ([ʷ]*)(a↑{{{n}},}[→ʷ]*)(?!ⁿ)", "h←←←←\\2ᶠ\\3\\4", "hi")) # == "çi" # Fante "underlying"
print(test(6, "(?<!ⁿ)(h←{0,4})([ⁱ'ʰᵛ]*?)ᶠ([ʷ]*)(a↑{{{n}},}[→ʷ]*)(?!ⁿ)", "h←←←←\\2ᶠ\\3\\4", "hĩ")) # == "hĩ" # Fante "where"
# frication and affrication occurs with sufficient air velocity and thereby constriction
# so plosives followed by glides tend to fricativize, unless a preceding nasal vents pressure elsewhere
print(test(6, "(?<!ⁿ)(h←{5,8})([ⁱ'ʰᵛ]*?)ᵖ([ʷ]*)(h←*[ᴿᴸʳˡ]*)", "h←←←←←←\\2ᶠᵖ\\3\\4", "trʌk")) # == "t∫rʌk" # American English Dialect "truck"
# frication and affrication occurs with sufficient air velocity and thereby constriction
# so plosives followed by glides tend to fricativize, unless a preceding nasal vents pressure elsewhere
print(test(6, "(?<!ⁿ)(h←{0,4})([ⁱ'ʰ]*?)ᶠ([ʷ]*)(h←*[ᴿᴸʳˡ]*)", "\\1\\2ᶠᵖ\\3\\4", "hjumən")) # == "çjumən" # English mispronunciation "human"
print(test(6, "(?<!ⁿ)(h←{0,4})([ⁱ'ʰ]*?)ᶠ([ʷ]*)(h←*[ᴿᴸʳˡ]*)", "\\1\\2ᶠᵖ\\3\\4", "ʌnhjumən")) # == "ʌnhjumən", not "ʌnçjumən" # English mispronunciation "human"

# EPENTHESIS/ASSIMILATION
# the "valves" of the glottis and tongue do not open and close immediately, 
# so if two phonemes occur in sequence and use different valves, such as a fricative and nasal, 
# the speaker may anticipate the blend and produce a plosive 
print(test(6, "(h←*[ⁱ'ᶠʰᵛʷ]*)(h←*)ⁿ", "\\1\\2ᵖ\\2ⁿ", "krʂɳa")) # == "krʂʈɳa" # Indo-European variants "Krishna"
# the "valves" of the glottis and tongue do not open and close immediately, 
# so if two phonemes occur in sequence and use different valves, such as a fricative and nasal, 
# the speaker may perservere through the blend and produce a plosive
print(test(6, "(h←*)ⁿ(h←*[ⁱ'ᶠʰᵛʷ]*)(?!ᵖ)", "\\1ⁿ\\1ᵖ\\2", "wɔɹmθ")) # == "wɔɹmpθ" # English "warmth"
print(test(6, "(h←*)ⁿ(h←*[ᴿᴸʳˡ]*)(?!ᵖ)", "\\1ⁿ\\1ᵛᵖ\\2", "venre")) # == "vendre" # Spanish "sell"


# print(test(8, "(h←{0,{{n}}}[^ᵛᵖha]*)ᵖ(a[^h]*h←*[^ʳha]*[ᴿʳ])", "\\1ᵛᵖ\\2", ipa)) 

# print(ipa)
# featural = featural_map.from_ipa(ipa)
# print(featural)
# for replaced, replacement in sound_laws:
# 	featural = sound_law_notation.apply(replaced, replacement, featural)
# ipa = featural_map.to_ipa(featural)
# print(featural)
# print(ipa)

