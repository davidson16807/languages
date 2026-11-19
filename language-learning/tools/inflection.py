import re

'''
`inflection` expands upon `dictstores` to provide `DictLookup`s 
that are sensitive to concepts in language. 
'''

class RegularInflectionFallbackLookup:
    '''
    `RegularInflection` is a lookup for inflections that falls back to inflecting a lexeme
    using inflection of a representative word that shares the same inflection pattern.
    `patterns` is a list of (pattern, representative, replaced) tuples where:
    * `pattern` is a regular expression that must fully match the lexeme,
       whose first group captures the portion of the lexeme that replaces `replaced`,
    * `representative` is a word with an inflection in `inflection_for_tags`, and
    * `replaced` is the portion of the representative's inflection that is replaced.
    Patterns are attempted in order until an inflection is found.
    '''
    def __init__(self, part_of_speech, lexeme_for_tags, inflection_for_tags, patterns, 
            missing='...', unmatched='ꜝ', inferred='\u200b'):
        self.part_of_speech = part_of_speech
        self.lexeme_for_tags = lexeme_for_tags
        self.inflection_for_tags = inflection_for_tags
        self.patterns = patterns
        self.missing = missing
        self.unmatched = unmatched
        self.inferred = inferred
    def __getitem__(self, tags):
        if tags in self.inflection_for_tags:
            return self.inflection_for_tags[tags]
        elif tags in self.lexeme_for_tags:
            lexeme = self.lexeme_for_tags[tags]
            for pattern, representative, replaced in self.patterns:
                match = re.fullmatch(pattern, lexeme)
                if match:
                    representative_tags = {**tags, self.part_of_speech: representative}
                    if representative_tags in self.inflection_for_tags:
                        representative_inflection = self.inflection_for_tags[representative_tags]
                        return self.inferred + re.sub(replaced, match.group(1), representative_inflection)
            return self.unmatched + lexeme
        return self.missing
    def __contains__(self, tags):
        return self[tags] != self.missing

'''
# example:
RegularInflection('verb', 
    {'swim':'nadar'},
    conjugation_lookup,
    [
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
    ],
)
'''
