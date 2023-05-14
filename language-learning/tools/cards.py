from .shorthands import EmojiPerson

class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, tags):
        def subject(template):
            return self.predicates[template['subject-function'], template['subject-argument']]
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        candidates = self.templates[tags] if tags in self.templates else []
        templates = sorted([template for template in candidates
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: (-int(template['specificity']), len(declined_noun(template))))
        return templates[0] if len(templates) > 0 else None

class DeckGeneration:
    def __init__(self):
        pass
    def generate(self, 
            demonstrations,
            traversal, 
            tagspace,
            whitelists=[],
            blacklists=[],
            tag_templates={},
        ):
        for tuplekey in traversal.tuplekeys(tagspace):
            tags = {**tagspace, **traversal.dictkey(tuplekey)}
            if (all([tags in whitelist for whitelist in whitelists]) and 
                all([tags not in blacklist for blacklist in blacklists])):
                # yield ' '.join([str(demonstration(tags, tag_templates)) for demonstration in demonstrations])
                lines = [demonstration(tags, tag_templates) for demonstration in demonstrations]
                if all(lines):
                    yield ' '.join([str(line) for line in lines])

class CardFormatting:
    def __init__(self):
        pass
    def emoji_focus(self, content):
        fonts = ''' sans-serif, Twemoji, "Twemoji Mozilla", "Segoe UI Emoji", "Noto Color Emoji" '''
        return f'''<div style='font-size:3em; padding: 1em 0em; display:inline-box; font-family: {fonts}'>{content}</div>'''
    def foreign_focus(self, content):
        return f'''<div style='font-size:3em'>{content}</div>'''
    def foreign_side_note(self, content):
        return f'''<div style='font-size:2em'>{content}</div>'''
    def native_word(self, content):
        return f'''<div>{content}</div>'''


class OldDeckGeneration:
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
            whitelists=[], 
            blacklists=[], 
            substitutions = [],
            persons=[],
        ):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = {**tagspace, **traversal.dictkey(tuplekey)}
            if (all([test_tags in whitelist for whitelist in whitelists]) and 
                all([test_tags not in blacklist for blacklist in blacklists])):
                emoji_key = {**test_tags, 'script':'emoji', 'language-type': 'foreign'}
                emoji_text = self.emoji.conjugate(emoji_key, 
                    foreign_language_script.language.grammar.conjugation_lookups['argument'][emoji_key], 
                    persons) if emoji_key in foreign_language_script.language.grammar.conjugation_lookups['argument'] else '🚫'
                semes = {
                    'test-seme':      {**test_tags, **{'noun-form': 'personal', 'role':'agent', 'motion':'associated'}},
                    'modifier-seme':  {**test_tags, **{'noun-form': 'common', 'role':'modifier', 'motion':'associated'}},
                    'speaker-seme':   {
                        **test_tags, 
                        **{'noun-form': 'personal', 'role':'agent', 'motion':'associated', 
                           'person': '1', 'number':'singular', 
                           'tense':'present', 'aspect':'aorist', 'voice':'active', 'mood':'indicative'}},
                }
                completed_substitutions = [
                    *substitutions,
                    {'stock-modifier': foreign_language_script.language.grammar.stock_modifier},
                    *[{key: self.tools.replace(test_tags[key])}
                      for key in ['noun','adjective','verb']
                      if key in test_tags],
                ]
                foreign_text = foreign_language_script.map(self.parsing.parse(foreign_tree), semes, completed_substitutions)
                voice_prephrase = '[middle voice:]' if test_tags['voice'] == 'middle' else ''
                mood_prephrase = self.mood_templates[{**test_tags,'column':'prephrase'}]
                mood_postphrase = self.mood_templates[{**test_tags,'column':'postphrase'}]
                native_text = ' '.join([str(text) 
                    for text in [
                        voice_prephrase, mood_prephrase, 
                        self.native_language_script.map(self.parsing.parse(native_tree), semes, completed_substitutions), 
                        mood_postphrase]]).replace('∅','')
                if foreign_text:
                    yield ' '.join([
                            self.cardFormatting.emoji_focus(emoji_text), 
                            self.cardFormatting.native_word(native_text),
                            self.cardFormatting.foreign_focus(foreign_text),
                        ])
    def declension(self, 
            foreign_language_script, 
            traversal, 
            tagspace,
            whitelists=[],
            blacklists=[], 
            nouns_to_depictions={},
            substitutions = [],
            tag_templates={},
            persons=[]):
        for tuplekey in traversal.tuplekeys(tagspace):
            test_tags = {**tagspace, **traversal.dictkey(tuplekey)}
            if (all([test_tags in whitelist for whitelist in whitelists]) and 
                all([test_tags not in blacklist for blacklist in blacklists])):
                noun = test_tags['noun'] if 'noun' in test_tags else None
                predicate = nouns_to_depictions[noun] if noun in nouns_to_depictions else noun
                match = self.declension_template_matching.match(predicate, test_tags)
                if match:
                    # case = foreign_language_script.language.semantics.case_usage[test_tags]['case'] # TODO: see if you can get rid of this
                    emoji_key = {
                        **test_tags, 
                        **tag_templates['test'], 
                        **tag_templates['emoji'], 
                        # 'case':case,  # TODO: see if you can get rid of this
                        'noun':test_tags['noun'],
                        'script': 'emoji'
                    }
                    emoji_text   = self.emoji.decline(emoji_key, match['emoji'], persons)
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
                    completed_substitutions = [
                        *substitutions,
                        {'stock-modifier': foreign_language_script.language.grammar.stock_modifier},
                        *[{key: self.tools.replace(test_tags[key])}
                          for key in ['noun','adjective','verb']
                          if key in test_tags],
                    ]
                    foreign_tree = native_tree = self.parsing.parse(match['syntax-tree'])
                    foreign_text = foreign_language_script.map(foreign_tree, semes, completed_substitutions)
                    voice_prephrase = '[middle voice:]' if test_tags['voice'] == 'middle' else ''
                    mood_prephrase = self.mood_templates[{**test_tags,'column':'prephrase'}]
                    mood_postphrase = self.mood_templates[{**test_tags,'column':'postphrase'}]
                    native_text = ' '.join([str(text) 
                        for text in [voice_prephrase, mood_prephrase, 
                            self.native_language_script.map(native_tree, semes, completed_substitutions), 
                            mood_postphrase]]).replace('∅','')
                    if foreign_text: 
                        yield ' '.join([
                                self.cardFormatting.emoji_focus(emoji_text), 
                                self.cardFormatting.native_word(native_text),
                                self.cardFormatting.foreign_focus(foreign_text),
                            ])


class OldEmoji:
    def __init__(self,
            nouns_to_depictions,
            noun_adjective_lookups,
            noun_lookups, 
            mood_templates, 
            emojiInflectionShorthand, 
            htmlTenseTransform, 
            htmlProgressTransform):
        self.nouns_to_depictions = nouns_to_depictions
        self.noun_adjective_lookups = noun_adjective_lookups
        self.noun_lookups = noun_lookups
        self.emojiInflectionShorthand = emojiInflectionShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlProgressTransform = htmlProgressTransform
        self.mood_templates = mood_templates
    def conjugate(self, tags, argument, persons):
        audience_lookup = {
            'voseo':    '\\background{🇦🇷}\\n2{🧑\\g2\\c2}',
            'polite':   '\\n2{🧑\\g2\\c2\\💼}',
            'formal':   '\\n2{🤵\\c2\\g2}',
            'elevated': '\\n2{🤴\\g2\\c2}',
        }
        # TODO: reimplement formality as emoji modifier shorthand
        # audience = (audience_lookup[tags['formality']] 
        #          if tags['formality'] in audience_lookup 
        #          else '\\n2{🧑\\g2\\c2}')
        scene = getattr(self.htmlTenseTransform, tags['tense'])(
                    getattr(self.htmlProgressTransform, tags['progress'].replace('-','_'))(argument))
        encoded_recounting = self.mood_templates[{**tags,'column':'template'}]
        subject = EmojiPerson(
            ''.join([
                    (tags['number'][0]),
                    ('i' if tags['clusivity']=='inclusive' else ''),
                ]), 
            tags['gender'][0], 
            persons[int(tags['person'])-1].color)
        persons = [
            subject if str(i+1)==tags['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiInflectionShorthand.decode(recounting, subject, persons)
        return recounting
    def decline(self, tags, scene, persons):
        if tags['noun-form'] == 'personal-possessive':
            possessed = self.decline({**tags, 'noun-form':'common'}, '\\declined', persons)
            possessor = self.decline({
                    'noun-form': 'pronoun',
                    'noun': tags['possessor-noun'].replace('-possessor',''),
                    'person': tags['possessor-person'].replace('-possessor','')[0],
                    'number': tags['possessor-number'].replace('-possessor',''),
                    'gender': tags['possessor-gender'].replace('-possessor',''),
                    'clusivity': tags['possessor-clusivity'].replace('-possessor',''),
                    'formality': tags['possessor-formality'].replace('-possessor',''),
                    'script': 'emoji',
                }, '\\declined', persons)
            noun = '\\flex{'+possessed+'\\r{'+possessor+'}}'
        else:
            depiction = ('missing' if 'noun' not in tags 
                else tags['noun'] if tags['noun'] not in self.nouns_to_depictions 
                else self.nouns_to_depictions[tags['noun']])
            alttags = {**tags, 'noun':depiction}
            noun = (self.noun_adjective_lookups[tags] if tags in self.noun_adjective_lookups
                else self.noun_lookups[alttags] if alttags in self.noun_lookups
                else self.noun_lookups[tags] if tags in self.noun_lookups 
                else '🚫')
        scene = scene.replace('\\declined', noun)
        encoded_recounting = self.mood_templates[{**tags,'column':'template','mood':'indicative'}]
        subject = EmojiPerson(
            ''.join([
                    (tags['number'][0]),
                    ('i' if tags['clusivity']=='inclusive' else ''),
                ]), 
            tags['gender'][0], 
            persons[int(tags['person'])-1].color)
        persons = [
            subject if str(i+1)==tags['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiInflectionShorthand.decode(recounting, subject, persons)
        return recounting

