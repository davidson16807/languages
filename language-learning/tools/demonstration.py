from .shorthands import EmojiPerson

def TextDemonstration(
            mood_templates, #series×language_type
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
        def verb(self, substitutions, stock_modifier, default_tree, debug=False):
            parsed_default_tree = parsing.parse(default_tree)
            def _demonstration(tags, tag_templates):
                tags = {**tags, **self.orthography.language.tags}
                semes = {
                    # 'test':      {**tags, **tag_templates['test']},
                    # 'modifier':  {**tags, **tag_templates['modifier']},
                    'test':      {**tags, **{'noun-form': 'personal', 'role':'agent', 'motion':'associated'}},
                    'modifier':  {**tags, **{'noun-form': 'common', 'role':'patient', 'subjectivity':'modifier', 'motion':'associated'}},
                    'speaker':   {
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
                            self.orthography.map(
                                parsed_default_tree, 
                                semes, 
                                completed_substitutions,
                                debug=debug,
                            ),
                            self.context(tags),
                        ).replace('∅',''))
            return _demonstration
        def case(self, substitutions, tree_lookup, debug=False, **junk):
            def _demonstration(tags, tag_templates):
                tags = {**tags, **self.orthography.language.tags}
                semes = {
                    'test':        {**tags, **tag_templates['test']},
                    'dummy':       {**tags, **tag_templates['dummy']},
                    'modifier':    {**tags, **(tag_templates['modifier'] if 'modifier' in tag_templates else {})},
                    'participle':  {**tags, **(tag_templates['participle'] if 'participle' in tag_templates else {})},
                }
                completed_substitutions = [
                    *substitutions,
                    *[{key: tools.replace(tags[key])}
                      for key in ['noun','adjective','verb']
                      if key in tags],
                ]
                return self.format_card(
                        self.assemble(tags,
                            self.orthography.map(
                                parsing.parse(tree_lookup[tags]),
                                semes, 
                                completed_substitutions,
                                debug=debug,
                            ),
                            self.context(tags),
                        ).replace('∅',''))

            return _demonstration
    return LanguageSpecificTextDemonstration

def EmojiDemonstration(
            nouns_to_depictions,
            noun_adjective_lookups,
            noun_lookups,
            mood_templates,
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
                        ('i' if 'clusivity' in tags and tags['clusivity']=='inclusive' else ''),
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
                            **{tag: tags[f'possessor-{tag}'].replace('-possessor','')
                               for tag in 'noun person number gender clusivity formality'.split()
                               if f'possessor-{tag}' in tags},
                            # 'person': tags['possessor-person'].replace('-possessor','')[0],
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
                template = '🚫' # match['emoji'] if 'emoji' in (match or {}) else '🚫'
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
