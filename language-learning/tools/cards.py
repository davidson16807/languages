
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
    def native_word(self, content):
        return f'''<div>{content}</div>'''

class CardGeneration:
    def __init__(self, native_language_script, emoji, cardFormatting,
            declension_template_matching, 
            mood_templates,
            parsing, tools):
        self.native_language_script = native_language_script
        self.mood_templates = mood_templates
        self.emoji = emoji
        self.cardFormatting = cardFormatting
        self.declension_template_matching = declension_template_matching
        self.parsing = parsing
        self.tools = tools
    def conjugation(self, 
            foreign_language_script, 
            traversal, 
            tagspace,
            foreign_tree,
            native_tree,
            filter_lookups=[], 
            substitutions = [],
            persons=[],
        ):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = traversal.dictkey(tuplekey)
            if all([test_tags in filter_lookup for filter_lookup in filter_lookups]):
                noun = test_tags['noun'] if 'noun' in test_tags else None
                adjective = test_tags['adjective'] if 'adjective' in test_tags else None
                verb = test_tags['verb'] if 'verb' in test_tags else None
                voice_prephrase = '[middle voice:]' if test_tags['voice'] == 'middle' else ''
                mood_prephrase = self.mood_templates[{**test_tags,'column':'prephrase'}]
                mood_postphrase = self.mood_templates[{**test_tags,'column':'postphrase'}]
                test_seme = {**test_tags, **{'noun-form': 'personal', 'role':'agent', 'motion':'associated'}}
                modifier_seme = {**test_tags, **{'noun-form': 'common', 'role':'modifier', 'motion':'associated'}}
                speaker_seme = {**test_tags, 
                    **{'noun-form': 'personal', 'role':'agent', 'motion':'associated', 
                       'person': '1', 'number':'singular', 
                       'tense':'present', 'aspect':'aorist', 'voice':'active', 'mood':'indicative'}}
                semes = {
                    'test-seme':      test_seme,
                    'speaker-seme':   speaker_seme,
                    'modifier-seme':  modifier_seme,
                }
                foreign_text = foreign_language_script.map(self.parsing.parse(foreign_tree), semes,
                    substitutions = [
                        *substitutions,
                        {'stock-modifier': foreign_language_script.language.grammar.stock_modifier('foreign')},
                        {'noun':     self.tools.replace(noun)},
                        {'adjective':self.tools.replace(adjective)},
                        {'verb':     self.tools.replace(verb)},
                    ]
                )
                native_text = self.native_language_script.map(self.parsing.parse(native_tree), semes,
                    substitutions = [
                        *substitutions,
                        {'stock-modifier': foreign_language_script.language.grammar.stock_modifier('native')},
                        {'noun':     self.tools.replace(noun)},
                        {'adjective':self.tools.replace(adjective)},
                        {'verb':     self.tools.replace(verb)},
                    ]
                )
                emoji_key  = {**test_tags, 'script':'emoji'}
                if foreign_text and emoji_key in foreign_language_script.language.grammar.conjugation_lookups['infinitive']:
                    emoji_argument  = foreign_language_script.language.grammar.conjugation_lookups['infinitive'][emoji_key]
                    emoji_text      = self.emoji.conjugate(test_tags, emoji_argument, persons)
                    native_text    = ' '.join([voice_prephrase, mood_prephrase, native_text, mood_postphrase]).replace('∅','')
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.native_word(native_text),
                            self.cardFormatting.foreign_focus(foreign_text),
                        ])
    def declension(self, 
            foreign_language_script, 
            traversal, 
            tagspace,
            filter_lookups=[],
            nouns_to_depictions={},
            substitutions = [],
            tag_templates={},
            persons=[]):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = traversal.dictkey(tuplekey)
            if (all([test_tags in filter_lookup for filter_lookup in filter_lookups]) and 
                  test_tags in foreign_language_script.language.grammar.use_case_to_grammatical_case):
                noun = test_tags['noun'] if 'noun' in test_tags else None
                adjective = test_tags['adjective'] if 'adjective' in test_tags else None
                verb = test_tags['verb'] if 'verb' in test_tags else None
                predicate = nouns_to_depictions[noun] if noun in nouns_to_depictions else noun
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
                        'modifier-seme':    {**test_tags, **(tag_templates['modifier'] if 'modifier' in tag_templates else {})},
                        'participle-seme':  {**test_tags, **(tag_templates['participle'] if 'participle' in tag_templates else {})},
                    }
                    foreign_text = foreign_language_script.map(tree, semes, [
                        *substitutions,
                        {'stock-modifier': foreign_language_script.language.grammar.stock_modifier('foreign')},
                        {'noun':     self.tools.replace(noun)},
                        {'adjective':self.tools.replace(adjective)},
                        {'verb':     self.tools.replace(verb)},
                    ])
                    native_text = self.native_language_script.map(tree, semes, [
                        *substitutions,
                        {'stock-modifier': foreign_language_script.language.grammar.stock_modifier('native')},
                        {'noun':     self.tools.replace(noun)},
                        {'adjective':self.tools.replace(adjective)},
                        {'verb':     self.tools.replace(verb)},
                    ])
                    case = foreign_language_script.language.grammar.use_case_to_grammatical_case[test_tags]['case'] # TODO: see if you can get rid of this
                    emoji_key = {
                        **test_tags, 
                        **tag_templates['test'], 
                        **tag_templates['emoji'], 
                        'case':case, 
                        'noun':test_tags['noun'],
                        'script': 'emoji'
                    }
                    emoji_text   = self.emoji.decline(emoji_key, match['emoji'], persons)
                    voice_prephrase = '[middle voice:]' if test_tags['voice'] == 'middle' else ''
                    mood_prephrase = self.mood_templates[{**test_tags,'column':'prephrase'}]
                    mood_postphrase = self.mood_templates[{**test_tags,'column':'postphrase'}]
                    native_text = ' '.join([voice_prephrase, mood_prephrase, native_text, mood_postphrase]).replace('∅','')
                    if foreign_text: 
                        yield ' '.join([
                                self.cardFormatting.emoji_focus(emoji_text), 
                                self.cardFormatting.native_word(native_text),
                                self.cardFormatting.foreign_focus(foreign_text),
                            ])