
class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, motion, role):
        def subject(template):
            return self.predicates[template['subject-function'], template['subject-argument']]
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        candidates = self.templates[motion, role] if (motion, role) in self.templates else []
        templates = sorted([template for template in candidates
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: (-int(template['specificity']), len(declined_noun(template))))
        return templates[0] if len(templates) > 0 else None

class CardFormatting:
    def __init__(self):
        pass
    def emoji_focus(self, content):
        fonts = ''' sans-serif, Twemoji, "Twemoji Mozilla", "Segoe UI Emoji", "Noto Color Emoji" '''
        return f'''<div style='font-size:3em; padding: 0.5em; display:inline-box; font-family: {fonts}'>{content}</div>'''
    def foreign_focus(self, content):
        return f'''<div style='font-size:3em'>{content}</div>'''
    def foreign_side_note(self, content):
        return f'''<div style='font-size:2em'>{content}</div>'''
    def english_word(self, content):
        return f'''<div>{content}</div>'''

class CardGeneration:
    def __init__(self, english, emoji, cardFormatting,
            declension_template_matching, 
            parsing, tools):
        self.english = english
        self.emoji = emoji
        self.cardFormatting = cardFormatting
        self.declension_template_matching = declension_template_matching
        self.parsing = parsing
        self.tools = tools
    def conjugation(self, 
            foreign, 
            traversal, 
            filter_lookups=[], 
            tagspace={},
            english_map=lambda x:x,
            persons=[]):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = traversal.dictkey(tuplekey)
            test_tags = {**test_tags, **{'noun-form': 'personal', 'role':'agent', 'motion':'associated'}}
            modifier_tags = {**test_tags, **{'noun-form': 'common', 'role':'modifier', 'motion':'associated'}}
            if all([test_tags in filter_lookup for filter_lookup in filter_lookups]):
                tree = self.parsing.parse('clause [test-seme [np the n man] [vp cloze v conjugated]] [modifier-seme np stock-modifier conjugated]')
                semes = {
                    'test-seme':      test_tags,
                    'modifier-seme':  modifier_tags,
                }
                translated_text = foreign.map(tree,
                    semes = semes,
                    custom_substitution = {
                        'stock-modifier': foreign.grammar.stock_modifier('foreign'),
                        'conjugated':     self.tools.replace(test_tags['verb']),
                    },
                )
                english_text = self.english.map(tree,
                    semes = semes,
                    custom_substitution = {
                        'stock-modifier': foreign.grammar.stock_modifier('native'),
                        'conjugated':     self.tools.replace(test_tags['verb']),
                        'cloze':          self.tools.remove(),
                    },
                )
                emoji_key  = {**test_tags, 'script':'emoji'}
                if translated_text and emoji_key in foreign.grammar.conjugation_lookups['infinitive']:
                    emoji_argument  = foreign.grammar.conjugation_lookups['infinitive'][emoji_key]
                    emoji_text      = self.emoji.conjugate(test_tags, emoji_argument, persons)
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)),
                            self.cardFormatting.foreign_focus(translated_text),
                        ])
    def declension(self, 
            foreign, 
            traversal, 
            filter_lookups=[],
            nouns_to_predicates={},
            tagspace={},
            tag_templates={},
            english_map=lambda x:x,
            persons=[]):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = traversal.dictkey(tuplekey)
            if (all([test_tags in filter_lookup for filter_lookup in filter_lookups]) and 
                  test_tags in foreign.grammar.use_case_to_grammatical_case):
                noun = test_tags['noun']
                predicate = nouns_to_predicates[noun] if noun in nouns_to_predicates else noun
                match = self.declension_template_matching.match(predicate, test_tags['motion'], test_tags['role'])
                if match:
                    tree = self.parsing.parse(match['syntax-tree'])
                    semes = {
                        'test-seme':        {**test_tags, **tag_templates['test']},
                        'solitary-seme':    {**test_tags, **tag_templates['solitary'],   'role':'solitary', 'motion':'associated'},
                        'agent-seme':       {**test_tags, **tag_templates['agent'],      'role':'agent',    'motion':'associated'},
                        'theme-seme':       {**test_tags, **tag_templates['theme'],      'role':'theme',    'motion':'associated'},
                        'patient-seme':     {**test_tags, **tag_templates['patient'],    'role':'patient',  'motion':'associated'},
                        'possession-seme':  {**test_tags, **tag_templates['possession'], 'role':'solitary', 'motion':'associated'},
                    }
                    translated_text = foreign.map(tree,
                        semes = semes,
                        custom_substitution = {
                            'declined':       self.tools.replace(['cloze', 'n', noun]),
                        },
                    )
                    english_text = self.english.map(tree,
                        semes = semes,
                        custom_substitution = {
                            'declined':       self.tools.replace(['n', noun]),
                        },
                    )
                    case = foreign.grammar.use_case_to_grammatical_case[test_tags]['case'] # TODO: see if you can get rid of this
                    emoji_key = {**test_tags, **tag_templates['test'], **tag_templates['emoji'], 'case':case, 'script': 'emoji'}
                    emoji_text = self.emoji.decline(emoji_key, 
                        match['emoji'], foreign.grammar.declension_lookups[emoji_key][emoji_key], persons)
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.english_word(english_map(english_text)),
                            self.cardFormatting.foreign_focus(translated_text),
                        ])