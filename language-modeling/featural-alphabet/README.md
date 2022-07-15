The mapping tables in this directory are an attempt to create a computer friendly 
class of featural phonetic alphabets that can be used in place of the IPA to specify broad sound laws using regex.
It is not intended to be easily read or written by humans.
It is only meant to simplify the data entry of highly generalized sound laws
without having to consider all the possible characters that are supported by the IPA.

Vowels are depicted using modifiers relative to a base vowel.
Modifers exist to heighten/shorten vowels (↑/↓) or move them front/back (←/→) as they appear on the IPA vowel chart.
Vowel modifiers can be repeated, and the number of repetitions indicates cartesian coordinates on the IPA vowel chart.
A single vowel is chosen to represent the origin of the coordinate system, 
for which all other vowels in the sound law are expressed relative to.
For instance, 'u' could be denoted 'ə↑→ʷ' to simplify logic for a sound law that represents a rotation within vowel space,
or it can be denoted as 'a↑↑↑→→ʷ' to simplify logic for a broad vowel heightening or shortening
It is up to the user to select a base character that is best suited for the sound law.

To illustrate how the notation can be used to simplify sound law description, 
consider the following example, describing the Great Vowel Shift using regex:

```
'ɜ↑↑(?=[←→])' 	-> 	'ɜ↑ɜ↑↑'	# high front and back vowels are split
'ɜ(?=[↑↓]*[←→])'-> 	'ɜ↑' 	# lower vowels are heightened
'ɜ(?=↑*←)'  	-> 	'ɜ↑'  	# high front vowels are heightened again
'ɜ↑ɜ↑↑(?=[←→])'	-> 	'ɜ↓←ɜ↑'	# dipthongs introduced earlier are dropped again
```

Consonants are depicted by starting with a base consonant then adding modifiers to the fricatives characters of the IPA.
It is up to the user to select a base consonant that is best suited for the sound law.
the base character is modified by at least the following superscripts:

```
←	further forward than the base character
→	further backward than the base character
ᴿ	trills
ᴸ	taps/flaps
ʳ	approximates
ˡ	lateral approximates 
ⁿ 	nasals 
ⁱ	implosive
'	ejective
ᶠ 	fricatives 
ʰ 	aspirates 
ᵛ 	voiced consonants 
ᵖ 	plosives 
ʷ 	rounded/labialized
```

Affricatives are denoted by combining fricative and plosive modifiers, e.g. /t∫/→"∫ᶠᵖ"
It is up to the user to choose an order for modifiers that are best suited for the sound law.

By default, we order modifiers in the same way they are listed above: ←→ᴿᴸʳˡⁿⁱ'ᶠʰᵛᵖʷ
Using this order places modifiers roughly on a sonority hierarchy, 
which simplifies sound laws regarding sonorization/lenition.
Remaining ambiguity in the default order is resolved for no better reason 
than to make it trivially easy to express Grimm's Law using regex:

```
(?<=[^sᵖʷ]h←*)ᵖ	->	ᶠ  	# voiceless stops fricativize, unless after s, plosives, or rounded phonemes
(?<=h←*)ᵛᵖ 		->	ᵖ 	# voiced stops unvoice
(?<=h←*)ʰᵛᵖ		->	ᵛᵖ 	# voiced spirates unaspirate                                                                  
```

