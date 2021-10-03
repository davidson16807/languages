import re

def sound_law(pronunciations, include_alternatives=False):
    removals = 'ʔⁿʰʷˀ[]/.ːˑˈˌ|‖↗︎↘︎ꜛꜜ‿˥꜒˦꜓˧꜔˨꜕˩꜖꜈꜉꜊꜋꜌꜍꜎꜏꜐꜑◌̩◌̯◌̍◌̑◌ʰʰ◌̚◌ⁿⁿ◌ˡˡ◌ᶿᶿ◌ˣˣ◌ᵊᵊ◌̥◌̬◌̊◌̤◌̰◌̪◌̼◌͆◌̺◌̻◌̟◌̠◌˖˖◌˗˗˗◌̈◌̽◌̝◌̞◌˔˔◌˕˕˕◌̹◌̜ʷ̜◌͗◌͑ʷ◌ʷʷ◌ʲʲ◌ˠˠ◌̴ᵶ◌ˤˤ◌̘◌̙◌̃◌'
    vowels = 'aeiouæɑɒʌɛɪɔʊəɜɐ'
    replacements = {
        ('˞', 'ɑɹ'),
        ('ɚ', 'əɹ'),
        ('ɝ', 'ɛɹ'),
        ('ä', 'a'),
        ('ẽ', 'e'),
        ('ĭ', 'i'),
        ('ɨ', 'i'),
        ('õ', 'o'),
        ('œ', 'o'),
        ('ũ', 'u'),
        ('ʉ', 'u'),
        ('ŭ', 'u'),
        ('ɞ', 'ə'),
        ('ɘ', 'ə'),
        ('d͡ʒ', 'dʒ'),
        ('t͡ʃ', 'tʃ'),
        ('ɓ', 'b'),
        ('ɫ', 'l'),
        ('ɬ', 'l'),
        ('ɵ', 'θ'),
        ('ɸ', 'f'),
        ('ɱ', 'm'),
        ('ɲ', 'n'),
        ('ɾ̃', 'n'),
        ('c', 'k'),
        ('q', 'k'),
        ('ɾ', 't'),
        ('ɡ', 'g'),
        ('ʍ', 'w'),
        ('x', 'k'),
        ('ɦ', 'h'),
        ('ç', 'h'),
        ('ɤ', 'l'),
        ('χ', 'k'),
        ('ɹ', 'r'),
        ('ʁ', 'r'),
        ('ɻ', 'r'),
        ('ɕ', 'ʃ'),
        ('ʈ', 't'),
        ('˞', 'r'),
        ('ɽ', 'r'),
        ('ɳ', 'n'),
        ('ɖ', 'd'),
        ('ʋ', 'w'),
        ('bs', 'bz'),
        ('hw', 'w'),
    }
    parens_regex = re.compile('\\([^)]*\\)')
    Cdj_regex = re.compile('(?<=[nkb])dʒ')
    Cdsh_regex = re.compile('(?<=[nkp])tʃ')
    for word, layer, pronunciation in pronunciations:
        simplification = pronunciation.lower()
        for removed in removals:
            simplification = simplification.replace(removed, '')
        for old, new in replacements:
            simplification = simplification.replace(old, new)
        # simplification = start_mid_regex.sub('ə', simplification)
        # simplification = end_mid_regex.sub('ə', simplification)
        # simplification = mid_regex.sub('ə', simplification)
        # simplification = mid2_regex.sub('ə', simplification)
        simplification = Cdj_regex.sub('ʒ', simplification)
        simplification = Cdsh_regex.sub('ʃ', simplification)
        simplification = simplification.replace('ɹ', 'r')
        simplification = simplification.replace('ʃən', 'ʃn')
        simplification = simplification.strip()
        simplification = simplification.replace('(r)', 'r')
        if parens_regex.search(simplification):
            if include_alternatives:
                yield word, layer, parens_regex.sub('', simplification)
            yield word, layer, simplification.replace('(', '').replace(')', '')
        elif len(simplification.strip('')) > 0:
            yield word, layer, simplification


def narrow(pronunciations):
    replacements = {
        ('ɞ', 'ə'),
        ('ɘ', 'ə'),
        ('ɵ', 'θ'),
        ('ɸ', 'f'),
        ('ð', 'θ'),
    }
    # er_regex = re.compile('\\B[aɑɒɔɐeʌɛəɜ]*[ɹr]')
    start_mid_regex = re.compile('\\b[aɑɒɔɐeʌɛəɜɪʊ](?![ui])')
    end_mid_regex = re.compile('[aɑɒɔɐeʌɛəɜɪʊ]\\b')
    mid_regex = re.compile('\\B[aɑɒɔɐeʌɛəɜɪʊ]+(?![ui])\\B')
    mid2_regex = re.compile('əə+')
    ou_regex = re.compile('[eoʌɛɔəɜ][ʊu]')
    au_regex = re.compile('[æɑɒaɐ][ʊu]')
    oi_regex = re.compile('[oɔʊ][iɪ]')
    ai_regex = re.compile('[aɑɒɔɐ][iɪ]')
    ei_regex = re.compile('[eʌɛəɜ][iɪ]')
    for word, layer, pronunciation in sound_law(pronunciations, True):
        for old, new in replacements:
            simplification = simplification.replace(old, new)
        simplification = au_regex.sub('au', simplification)
        simplification = ou_regex.sub('o', simplification)
        simplification = oi_regex.sub('oi', simplification)
        simplification = ai_regex.sub('ai', simplification)
        simplification = ei_regex.sub('ei', simplification)
        simplification = start_mid_regex.sub('ə', simplification)
        simplification = end_mid_regex.sub('ə', simplification)
        simplification = mid_regex.sub('ə', simplification)
        simplification = mid2_regex.sub('ə', simplification)
        # simplification = er_regex.sub('r', simplification)
        yield word, layer, simplification


def broad(pronunciations):
    for word, layer, pronunciation in narrow(pronunciations):
        simplification = pronunciation
        simplification = re.compile('[aeiouæɑɒʌɛɪɔʊəɜ]+').sub('ə', simplification)
        yield word, layer, simplification

def mispronunciation(pronunciations):
    replacements = {
        ('b', 'p'),
        ('d', 't'),
        ('g', 'k'),
        ('v', 'f'),
        ('z', 's'),
        ('ʒ', 'ʃ'),
        ('ts', 's'),
        ('tʃ', 'ʃ'),
        ('h', ''),
    }
    for word, layer, pronunciation in broad(pronunciations):
        simplification = pronunciation
        for old, new in replacements:
            simplification = simplification.replace(old, new)
        yield word, layer, simplification
