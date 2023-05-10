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
        list_tools:      contains maps of nodes represented as nested lists of strings without concern to what the strings represent
        rule_tools:      contains maps of nodes represented as nested rules without concern to what the rules represent
    """
    def __init__(self, 
            semantics,
            grammar,
            syntax,
            list_tools,
            rule_tools,
            formatting,
            validation,
            substitutions=[]):
        self.semantics = semantics
        self.grammar = grammar
        self.syntax = syntax
        self.list_tools = list_tools
        self.rule_tools = rule_tools
        self.validation = validation
        self.formatting = formatting
        self.substitutions = substitutions
    def map(self, syntax_tree, script, semes={}, substitutions=[]):
        default_substitution = {
            'the': self.list_tools.replace(['det', 'the']),
            'a':   self.list_tools.replace(['det', 'a']),
        }
        tag_opcodes = {
            'informal':    {'formality': 'informal'},
            'indicative':  {'mood': 'indicative'},
            'perfective':  {'aspect': 'perfective'},
            'imperfective':{'aspect': 'imperfective'},
            'progressive': {'aspect': 'imperfective'},
            'aorist':      {'aspect': 'aorist'},
            'simple':      {'aspect': 'aorist'},
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
        tag_insertion = {tag:self.semantics.tag({**opcode,'script':script}, remove=False) for (tag, opcode) in tag_opcodes.items()}
        tag_removal   = {tag:self.semantics.tag({**opcode,'script':script}, remove=True)  for (tag, opcode) in tag_opcodes.items()}
        rules = 'clause cloze implicit parentheses det adj np vp n v stock-modifier stock-adposition'
        pipeline = [
            *[ListTreeMap({**tag_insertion, **substitution}) for substitution in substitutions],      # deck specific substitutions
            *[ListTreeMap({**tag_insertion, **substitution}) for substitution in self.substitutions], # language specific substitutions
            ListTreeMap({**tag_insertion, **default_substitution}),
            ListTreeMap({
                **tag_insertion, 
                'cloze':            self.list_tools.tag({'show-alternates':True}, remove=False),
                'stock-adposition': self.semantics.stock_adposition,
                'v':                self.grammar.conjugate,
                'n':                self.grammar.decline,
                'det':              self.grammar.decline,
                'adj':              self.grammar.decline,
            }),
            ListTreeMap({
                **tag_removal,
                **{tag:self.list_tools.rule() for tag in rules.split()},
            }),
            RuleTreeMap({
                'clause':  self.syntax.order_clause,
                'np':      self.syntax.order_noun_phrase,
                'v':       self.rule_tools.filter_tags(set(' '.join([
                    'verb evidentiality confidence aspect progress mood completion mood voice tense language-type script person number']).split())),
                'n':       self.rule_tools.filter_tags(set(' '.join([
                    'noun valency motion role case person number gender clusivity formality clitic partitivity strength language-type script', 
                    'possessor-person possessor-number possessor-gender possessor-clusivity possessor-formality']).split())),
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

