from .shorthands import EmojiPerson

def TextDemonstration(
            nouns_to_depictions, #series
            mood_templates, #series×language_type
            declension_template_matching, #series
            parsing, 
            tools,
        ):
    class LanguageSpecificTextDemonstration:
        def __init__(self, format_card, orthography):
            self.format_card = format_card
            self.orthography = orthography
        def assemble(self, tags, dependant, independant):
            return independant.replace('\\placeholder', dependant)
        def context(self, tags):
            voice_prephrase = '[middle voice:]' if tags['voice'] == 'middle' else ''
            mood_prephrase = mood_templates[{**tags,'column':'prephrase'}]
            mood_postphrase = mood_templates[{**tags,'column':'postphrase'}]
            if tags['language-type'] == 'native':
                return ' '.join([
                    voice_prephrase,
                    mood_templates[{**tags,'column':'prephrase'}],
                    '\\placeholder',
                    mood_templates[{**tags,'column':'postphrase'}],
                ])
            else:
                return '\\placeholder'
        def verb(self, substitutions, stock_modifier, default_tree):
            def _demonstration(tags, tag_templates):
                tags = {**tags, **self.orthography.language.tags}
                semes = {
                    # 'test-seme':      {**tags, **tag_templates['test']},
                    # 'modifier-seme':  {**tags, **tag_templates['modifier']},
                    'test-seme':      {**tags, **{'noun-form': 'personal', 'role':'agent', 'motion':'associated'}},
                    'modifier-seme':  {**tags, **{'noun-form': 'common', 'role':'modifier', 'motion':'associated'}},
                    'speaker-seme':   {
                        **tags, 
                        **{'noun-form': 'personal', 'role':'agent', 'motion':'associated', 
                           'person': '1', 'number':'singular', 
                           'tense':'present', 'aspect':'aorist', 'voice':'active', 'mood':'indicative'}},
                }
                completed_substitutions = [
                    *substitutions,
                    {'stock-modifier': stock_modifier},
                    *[{key: tools.replace(tags[key])}
                      for key in ['noun','adjective','verb']
                      if key in tags],
                ]
                return self.format_card(self.assemble(tags,
                            self.orthography.map(parsing.parse(default_tree), semes, completed_substitutions),
                            self.context(tags),
                        ).replace('∅',''))
            return _demonstration
        def case(self, substitutions, stock_modifier, **junk):
            def _demonstration(tags, tag_templates):
                tags = {**tags, **self.orthography.language.tags}
                noun = tags['noun'] if 'noun' in tags else None
                predicate = nouns_to_depictions[noun] if noun in nouns_to_depictions else noun
                match = declension_template_matching.match(predicate, tags)
                semes = {
                    'test-seme':        {**tags, **tag_templates['test']},
                    'solitary-seme':    {**tags, **tag_templates['solitary'],   'role':'solitary', 'motion':'associated'},
                    'agent-seme':       {**tags, **tag_templates['agent'],      'role':'agent',    'motion':'associated'},
                    'theme-seme':       {**tags, **tag_templates['theme'],      'role':'theme',    'motion':'associated'},
                    'patient-seme':     {**tags, **tag_templates['patient'],    'role':'patient',  'motion':'associated'},
                    'possession-seme':  {**tags, **tag_templates['possession'], 'role':'solitary', 'motion':'associated'},
                    'modifier-seme':    {**tags, **(tag_templates['modifier'] if 'modifier' in tag_templates else {})},
                    'participle-seme':  {**tags, **(tag_templates['participle'] if 'participle' in tag_templates else {})},
                }
                completed_substitutions = [
                    *substitutions,
                    {'stock-modifier': stock_modifier},
                    *[{key: tools.replace(tags[key])}
                      for key in ['noun','adjective','verb']
                      if key in tags],
                ]
                return self.format_card(
                        self.assemble(tags,
                            self.orthography.map(parsing.parse(match['syntax-tree']), semes, completed_substitutions),
                            self.context(tags),
                        ).replace('∅','')) if match else '—'

            return _demonstration
    return LanguageSpecificTextDemonstration

def EmojiDemonstration(
            nouns_to_depictions,
            noun_adjective_lookups,
            noun_lookups,
            mood_templates,
            declension_template_matching, 
            emojiInflectionShorthand,
            htmlTenseTransform,
            htmlProgressTransform,
        ):
    class LanguageSpecificEmojiDemonstration:
        def __init__(self, format_card, argument_lookups, persons):
            self.format_card = format_card
            self.argument_lookups = argument_lookups
            self.persons = persons
        def context(self, tags):
            return mood_templates[{**tags,'column':'template'}]
        def assemble(self, tags, scene, recounting):
            subject = EmojiPerson(
                ''.join([
                        (tags['number'][0]),
                        ('i' if tags['clusivity']=='inclusive' else ''),
                    ]), 
                tags['gender'][0], 
                self.persons[int(tags['person'])-1].color)
            persons = [
                subject if str(i+1)==tags['person'] else person
                for i, person in enumerate(self.persons)]
            return emojiInflectionShorthand.decode(
                    recounting.replace('\\scene', scene), subject, persons)
        def verb(self, **junk):
            def scene(tags):
                template = self.argument_lookups[tags] if tags in self.argument_lookups else '🚫'
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
                return getattr(htmlTenseTransform, tags['tense'])(
                            getattr(htmlProgressTransform, tags['progress'].replace('-','_'))(template))
            def _demonstration(test_tags, tag_templates):
                tags = {**test_tags, 'script':'emoji', 'language-type': 'foreign'}
                return self.format_card(self.assemble(tags, scene(tags), self.context(tags)))
            return _demonstration
        def case(self, **junk):
            def scene(tags, tag_templates):
                if tags['noun-form'] == 'personal-possessive':
                    possessed = scene({**tags, 'noun-form':'common'}, tag_templates)
                    possessor = scene({
                            'noun-form': 'pronoun',
                            'noun': tags['possessor-noun'].replace('-possessor',''),
                            'person': tags['possessor-person'].replace('-possessor','')[0],
                            'number': tags['possessor-number'].replace('-possessor',''),
                            'gender': tags['possessor-gender'].replace('-possessor',''),
                            'clusivity': tags['possessor-clusivity'].replace('-possessor',''),
                            'formality': tags['possessor-formality'].replace('-possessor',''),
                            'script': 'emoji',
                        }, tag_templates)
                    return '\\flex{'+possessed+'\\r{'+possessor+'}}'
                else:
                    depiction = ('missing' if 'noun' not in tags 
                        else tags['noun'] if tags['noun'] not in nouns_to_depictions 
                        else nouns_to_depictions[tags['noun']])
                    alttags = {**tags, 'noun':depiction}
                    return (noun_adjective_lookups[tags] if tags in noun_adjective_lookups
                        else noun_lookups[alttags] if alttags in noun_lookups
                        else noun_lookups[tags] if tags in noun_lookups 
                        else '🚫')
            def _demonstration(test_tags, tag_templates):
                noun = test_tags['noun'] if 'noun' in test_tags else None
                predicate = nouns_to_depictions[noun] if noun in nouns_to_depictions else noun
                match = declension_template_matching.match(predicate, test_tags)
                template = match['emoji'] if match else '🚫'
                tags = {
                        **test_tags, 
                        **tag_templates['test'], 
                        **tag_templates['emoji'], 
                        # 'case':case,  # TODO: see if you can get rid of this
                        'noun':test_tags['noun'],
                        'script': 'emoji'
                    }
                return self.format_card(self.assemble(tags, template.replace('\\declined', scene(tags, tag_templates)), self.context(tags)))
            return _demonstration
    return LanguageSpecificEmojiDemonstration
