from .treemaps import ListTreeMap, RuleTreeMap

class Language:
    """
    A `Language` is a "tree mapping" class, analogous to those found under nodemaps.py.
    As a tree mapping class, `Language` is a category with at least one arrow
    that maps a syntax tree in one representation to another syntax tree in another representation.
    In this case, `Language` contains a single method `map()`
    that maps a syntax tree that is represented as nested lists storing language-agnostic codes
    to a syntax tree that is represented as a string containing one possible translation 
    of the meaning of the input tree to the natural language that is represented by `Language`.

    A `Language` can alternately be defined in a bottom-up way as a series of "node mapping" class instances that contain maps for individual nodes on trees
    These node mapping class instances can be seen in the parameters of the constructor for `Language`:
        grammar:    contains maps from nodes represented as nested lists of language agnostic codes to nodes represented as nested lists of inflected words as they would appear in a language
        syntax:     contains maps from nodes represented as nested and unordered `Rule` objects to nodes represented as nested `Rule` objects ordered as they would appear according to language ordering rules (e.g. sentence structure)
        formatting: contains maps between nodes represented as nested lists of strings indicating how constructs such as Anki "cloze" statements should be rendered as strings
        validation: contains maps from nodes represented as nested lists of Noneable strings to boolean indicating whether the node should be rendered as a string
        tools:      contains maps of nodes represented as nested lists of strings without concern to what the strings represent
    """
    def __init__(self, 
            grammar,
            syntax,
            tools,
            formatting,
            validation,
            substitutions=[]):
        self.substitutions = substitutions
        self.grammar = grammar
        self.syntax = syntax
        self.tools = tools
        self.validation = validation
        self.formatting = formatting
    def map(self, syntax_tree, script, semes={}, substitutions=[]):
        default_substitution = {
            'the': self.tools.replace(['det', 'the']),
            'a':   self.tools.replace(['det', 'a']),
        }
        tag_opcodes = {
            'informal':    {'formality': 'informal'},
            'indicative':  {'mood': 'indicative'},
            'perfective':  {'aspect': 'perfective'},
            'imperfective':{'aspect': 'imperfective'},
            'aorist':      {'aspect': 'aorist'},
            'active':      {'voice': 'active'},
            'passive':     {'voice': 'passive'},
            'middle':      {'voice': 'middle'},
            'infinitive':  {'verb-form': 'infinitive'},
            'finite':      {'verb-form': 'finite'},
            'participle':  {'verb-form': 'participle'},
            'common':      {'noun-form': 'common'},
            'personal':    {'noun-form': 'personal'},
            'theme':       {'role':'theme'},
            'common-possessive':   {'noun-form': 'common-possessive'},
            'personal-possessive': {'noun-form': 'personal-possessive'},
            **semes
        }
        tag_insertion = {tag:self.tools.tag({**opcode,'script':script}, remove=False) for (tag, opcode) in tag_opcodes.items()}
        tag_removal   = {tag:self.tools.tag({**opcode,'script':script}, remove=True)  for (tag, opcode) in tag_opcodes.items()}
        rules = 'clause cloze implicit parentheses det adj np vp n v stock-modifier stock-adposition'
        pipeline = [
            *[ListTreeMap({**tag_insertion, **substitution}) for substitution in substitutions],      # deck specific substitutions
            *[ListTreeMap({**tag_insertion, **substitution}) for substitution in self.substitutions], # language specific substitutions
            ListTreeMap({**tag_insertion, **default_substitution}),
            ListTreeMap({
                **tag_insertion, 
                'cloze':            self.tools.tag({'show-alternates':True}, remove=False),
                'v':                self.grammar.conjugate,
                'n':                self.grammar.decline,
                'det':              self.grammar.decline,
                'adj':              self.grammar.decline,
                'stock-adposition': self.grammar.stock_adposition,
            }),
            ListTreeMap({
                **tag_removal,
                **{tag:self.tools.rule() for tag in rules.split()},
            }),
            RuleTreeMap({
                'clause':  self.syntax.order_clause,
                'np':      self.syntax.order_noun_phrase,
            }),
        ]
        validation = RuleTreeMap({
            **{tag:self.validation.exists for tag in rules.split()},
        }) if self.validation else None
        formatting = RuleTreeMap({
            **{tag:self.formatting.default for tag in rules.split()},
            'cloze':   self.formatting.cloze,
            'implicit':self.formatting.implicit,
            'parentheses':self.formatting.parentheses,
        })
        tree = syntax_tree
        for i, step in enumerate(pipeline):
            # print(i)
            # print(tree)
            tree = step.map(tree, {'script': script})
        # return formatting.map(tree)
        return formatting.map(tree) if not validation or validation.map(tree) else None

