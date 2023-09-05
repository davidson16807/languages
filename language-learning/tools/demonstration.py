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
            noun_verb_lookups,
            noun_declension_lookups,
            noun_lookups,
            verb_lookups,
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
        def decode(self, tags, scene):
            subject = EmojiPerson(
                ''.join([
                        tags['number'],
                        ('i' if 'clusivity' in tags and tags['clusivity']=='inclusive' else ''),
                    ]), 
                tags['gender'][0], 
                self.persons[int(tags['person'])-1].color if 'personal' in tags['noun-form'] else '4'
            )
            persons = [
                subject if str(i+1)==tags['person'] else person
                for i, person in enumerate(self.persons)]
            return emojiInflectionShorthand.decode(
                    scene, subject, persons)
        def case(self, **junk):
            def noun(tags, tag_templates):
                if tags['noun-form'] == 'personal-possessive':
                    possessed = noun({**tags, 'noun-form':'common'}, tag_templates)
                    possessor = noun({
                            'noun-form': 'personal',
                            **{tag: tags[f'possessor-{tag}'].replace('-possessor','')
                               for tag in 'template noun person number gender clusivity formality'.split()
                               if f'possessor-{tag}' in tags},
                            # 'person': tags['possessor-person'].replace('-possessor','')[0],
                            'script': 'emoji',
                        }, tag_templates)
                    return self.decode(tags, '\\flex{'+possessed+'\\r{'+possessor+'}}')
                else:
                    depiction = ('missing' if 'noun' not in tags 
                        else tags['noun'] if tags['noun'] not in nouns_to_depictions 
                        else nouns_to_depictions[tags['noun']])
                    alttags = {**tags, 'noun':depiction}
                    result = (noun_adjective_lookups[tags] if tags in noun_adjective_lookups
                        else noun_verb_lookups[tags] if tags in noun_verb_lookups
                        else noun_lookups[alttags] if alttags in noun_lookups
                        else noun_lookups[tags] if tags in noun_lookups 
                        else '🚫')
                    return self.decode(tags, result)
            def performance(tags, tag_templates):
                template = (verb_lookups[tags] if tags in verb_lookups else '\\subject'
                    .replace('\\subject', noun(tags, tag_templates)))
                return template
            def scene(clause_tags, tag_templates):
                test_tags = {
                        **({'verb':clause_tags['verb']} if 'verb' in clause_tags and clause_tags['subjectivity'] == 'subject' else {}),
                        **{tag: clause_tags[tag]
                           for tag in 'template noun-form noun person number gender clusivity formality'.split()
                           if tag in clause_tags},
                        **{f'possessor-{tag}': clause_tags[f'possessor-{tag}']
                           for tag in 'template noun-form noun person number gender clusivity formality'.split()
                           if f'possessor-{tag}' in clause_tags},
                        **tag_templates['test'], 
                        'script': 'emoji'
                    }
                dummy_tags = {
                        **({'verb':clause_tags['verb']} if 'verb' in clause_tags and clause_tags['subjectivity'] != 'subject' else {}),
                        **tag_templates['dummy'], 
                        'person': '3',
                        'script': 'emoji'
                    }
                template = (self.argument_lookups[clause_tags] if clause_tags in self.argument_lookups
                    else noun_declension_lookups[clause_tags] if clause_tags in noun_declension_lookups else '🚫')
                template = (template
                    .replace('\\dummy', performance(dummy_tags, tag_templates))
                    .replace('\\test',  performance(test_tags,  tag_templates)))
                return getattr(htmlTenseTransform, clause_tags['tense'])(
                                getattr(htmlProgressTransform, clause_tags['progress'].replace('-','_'))(template))
            def recounting(tags):
                return mood_templates[{**tags,'column':'template'}]
            def _demonstration(clause_tags, tag_templates):
                return self.format_card(
                    self.decode(
                        {**clause_tags, 'script':'emoji', 'language-type': 'foreign'}, 
                        recounting(clause_tags)
                            .replace('\\scene', scene(clause_tags, tag_templates))))
            return _demonstration
        def verb(self, **kwargs):
            return self.case(**kwargs)
    return LanguageSpecificEmojiDemonstration
 