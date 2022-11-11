import re

class Plurality:
    def __init__(self, pluralize_regex, singularize_regex, uncountables, irregulars):
        super(Plurality, self).__init__()
        self.pluralize_regex = pluralize_regex
        self.singularize_regex = singularize_regex
        self.uncountables = uncountables
        self.irregular_singularize = {plural:singular for (singular,plural) in irregulars}
        self.irregular_pluralize = {singular:plural for (singular,plural) in irregulars}
    def pluralize(self, word: str) -> str:
        """
        Return the plural form of a word.
        """
        if word in self.irregular_pluralize:
            return self.irregular_pluralize[word]
        if not word or word.lower() in self.uncountables:
            return word
        else:
            for rule, replacement in self.pluralize_regex:
                if re.search(rule, word):
                    return re.sub(rule, replacement, word)
            return word
    def singularize(self, word: str) -> str:
        """
        Return the singular form of a word, the reverse of `pluralize`.
        """
        if word in self.irregular_singularize:
            return self.irregular_singularize[word]
        for inflection in self.uncountables:
            if re.search(r'(?i)\b(%s)\Z' % inflection, word):
                return word
        for rule, replacement in self.singularize_regex:
            if re.search(rule, word):
                return re.sub(rule, replacement, word)
        return word


english = Plurality(
    [
        (r"(?i)(ous)$", r'ous'),
        (r"(?i)(man)$", r'men'),
        (r"(?i)(quiz)$", r'\1zes'),
        (r"(?i)^(oxen)$", r'\1'),
        (r"(?i)^(ox)$", r'\1en'),
        (r"(?i)(m|l)ice$", r'\1ice'),
        (r"(?i)(m|l)ouse$", r'\1ice'),
        (r"(?i)(passer)s?by$", r'\1sby'),
        (r"(?i)(matr|vert|ind)(?:ix|ex)$", r'\1ices'),
        (r"(?i)(x|ch|ss|sh)$", r'\1es'),
        (r"(?i)([^aeiouy]|qu)y$", r'\1ies'),
        (r"(?i)(hive)$", r'\1s'),
        (r"(?i)([lr])f$", r'\1ves'),
        (r"(?i)([^f])fe$", r'\1ves'),
        (r"(?i)sis$", 'ses'),
        (r"(?i)([ti])a$", r'\1a'),
        (r"(?i)([ti])um$", r'\1a'),
        (r"(?i)(buffal|potat|tomat)o$", r'\1oes'),
        (r"(?i)(bu)s$", r'\1ses'),
        (r"(?i)(alias|status)$", r'\1es'),
        (r"(?i)(octop|vir)i$", r'\1i'),
        (r"(?i)(octop|vir)us$", r'\1i'),
        (r"(?i)^(ax|test)is$", r'\1es'),
        (r"(?i)s$", 's'),
        (r"$", 's'),
    ],
    [
        (r"(?i)(ous)$", r'ous'),
        (r"(?i)(men)$", r'man'),
        (r"(?i)(database)s$", r'\1'),
        (r"(?i)(quiz)zes$", r'\1'),
        (r"(?i)(matr)ices$", r'\1ix'),
        (r"(?i)(vert|ind)ices$", r'\1ex'),
        (r"(?i)(passer)sby$", r'\1by'),
        (r"(?i)^(ox)en", r'\1'),
        (r"(?i)(alias|status)(es)?$", r'\1'),
        (r"(?i)(octop|vir)(us|i)$", r'\1us'),
        (r"(?i)^(a)x[ie]s$", r'\1xis'),
        (r"(?i)(cris|test)(is|es)$", r'\1is'),
        (r"(?i)(shoe)s$", r'\1'),
        (r"(?i)(o)es$", r'\1'),
        (r"(?i)(bus)(es)?$", r'\1'),
        (r"(?i)(m|l)ice$", r'\1ouse'),
        (r"(?i)(x|ch|ss|sh)es$", r'\1'),
        (r"(?i)(m)ovies$", r'\1ovie'),
        (r"(?i)(s)eries$", r'\1eries'),
        (r"(?i)([^aeiouy]|qu)ies$", r'\1y'),
        (r"(?i)([lr])ves$", r'\1f'),
        (r"(?i)(tive)s$", r'\1'),
        (r"(?i)(hive)s$", r'\1'),
        (r"(?i)([^f])ves$", r'\1fe'),
        (r"(?i)(t)he(sis|ses)$", r"\1hesis"),
        (r"(?i)(s)ynop(sis|ses)$", r"\1ynopsis"),
        (r"(?i)(p)rogno(sis|ses)$", r"\1rognosis"),
        (r"(?i)(p)arenthe(sis|ses)$", r"\1arenthesis"),
        (r"(?i)(d)iagno(sis|ses)$", r"\1iagnosis"),
        (r"(?i)(b)a(sis|ses)$", r"\1asis"),
        (r"(?i)(a)naly(sis|ses)$", r"\1nalysis"),
        (r"(?i)([ti])a$", r'\1um'),
        (r"(?i)(n)ews$", r'\1ews'),
        (r"(?i)(ss)$", r'\1'),
        (r"(?i)s$", ''),
    ],
    {
        'the',
        'his',
        'us',
        'ours',
        'yours',
        'this',
        'equipment',
        'fish',
        'jeans',
        'money',
        'rice',
        'series',
        'sheep',
        'species'
        'information',
    },
    [
        ('person', 'people'),
        ('man', 'men'),
        ('human', 'humans'),
        ('child', 'children'),
        ('move', 'moves'),
        ('cow', 'kine'),
        ('zombie', 'zombies'),
        ('sex', 'sexes'),
        ('phenomenon', 'phenomena'),
        ('datum', 'data'),
    ]
)