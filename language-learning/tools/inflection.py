import re

'''
`inflection` expands upon `dictstores` to provide `DictLookup`s 
that are sensitive to concepts in language. 
'''

class RegularInflectionFallbackLookup:
    '''
    `RegularInflection` is a lookup for inflections that falls back to inflecting the lemma of a lexeme
    using inflection of a representative word that shares the same inflection pattern.

    `patterns_for_tags` is a lookup that maps tags to a list of (pattern, representative, replaced) tuples where:
    * `pattern` is a regular expression that must fully match the lemma,
       whose first group captures the portion of the lemma that replaces `replaced`,
    * `representative` is a word with an inflection in `inflection_for_tags`, and
    * `replaced` is the portion of the representative's inflection that is replaced.
    Patterns are attempted in order until an inflection is found.

    `patterns_for_tags` may be a `UniformDictLookup` if the same patterns apply to all tags,
    or a `DictLookup` if patterns only apply to certain tags, such as a script or the gender of a noun.

    `missing` displays in place of the word when no lemma is found. The suggested value is '...'.

    `unmatched` displays before the word when fallback fails when needed. Suggested 
    * superscript ! 'ꜝ'
    * superscript x 'ˣ'

    `inferred` displays before the word when the fallback is used. Suggested values include:
    * asterisk '*' 
    * upper dot '˙'
    * zero-width space '\u200b'
    * the empty string ''
    '''
    def __init__(self, part_of_speech, lemma_for_tags, inflection_for_tags, patterns_for_tags, 
            missing='...', unmatched='ꜝ', inferred='˙'):
        self.part_of_speech = part_of_speech
        self.lemma_for_tags = lemma_for_tags
        self.inflection_for_tags = inflection_for_tags
        self.patterns_for_tags = patterns_for_tags
        self.missing = missing
        self.unmatched = unmatched
        self.inferred = inferred
    def __getitem__(self, tags):
        if tags in self.inflection_for_tags:
            return self.inflection_for_tags[tags]
        elif tags in self.lemma_for_tags:
            lemma = self.lemma_for_tags[tags]
            patterns = self.patterns_for_tags[tags] if tags in self.patterns_for_tags else []
            for pattern, representative, replaced in patterns:
                match = re.fullmatch(pattern, lemma)
                if match:
                    representative_tags = {**tags, self.part_of_speech: representative}
                    if representative_tags in self.inflection_for_tags:
                        representative_inflection = self.inflection_for_tags[representative_tags]
                        return self.inferred + re.sub(replaced, match.group(1), representative_inflection)
            return self.unmatched + lemma
        return self.missing
    def __contains__(self, tags):
        return self[tags] != self.missing

'''
# example:
RegularInflection('verb', 
    {'swim':'nadar'},
    conjugation_lookup,
    UniformDictLookup([
        (r'(.+)gar',         'arrive',   'lle'),        # llegar → llegué
        (r'(.+)zar',         'throw',    'lan'),        # lanzar → lancé
        (r'(.+)zar',         'startle',  'atemori'),
        (r'(.*[^cgziu])ar',  'speak',    'habl'),       # hablar → hablé
        (r'(.*[^cgziu])ar',  'work',     'trabaj'),
        (r'(.+)ger',         'protect',  'prote'),      # proteger → protejo
        (r'(.*[^cgaeo])er',  'eat',      'com'),        # comer → como
        (r'(.*[^cgaeo])er',  'learn',    'aprend'),
        (r'(.*[^cgu])ir',    'suffer',   'sufr'),       # sufrir → sufro
        (r'(.*[^cgu])ir',    'part',     'part'),
    ]),
)
# example where patterns only apply to certain tags:
RegularInflection('noun',
    {('latin','wolf'):'loup', ('ipa','wolf'):'lu'},
    declension_lookup,
    DictLookup('patterns', DictTupleIndexing(['script']), {
        ('latin',): [(r'(.*[^sxz])', 'book', 'livre')], # loup → loups
        ('ipa',):   [(r'(.+)',       'book', 'livʁ')],  # lu   → lu
    }),
)
'''
