from .shorthands import EmojiPerson

def TextDemonstration(
            mood_templates, #series×language_type
            label_editing, 
            label_filtering, 
            parsing, 
            tools,
        ):
    class LanguageSpecificTextDemonstration:
        def __init__(self, format_card, orthography):
            self.format_card = format_card
            self.orthography = orthography
        def assemble(self, dependant, independant):
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
        def generator(self, tree_lookup, substitutions=[], debug=False, **junk):
            def demonstrate(tags, tag_templates):
                tags = {**tags, **self.orthography.language.tags}
                semes = {
                    label:{
                        **tags, 
                        **label_editing.termaxis_to_term(
                            label_filtering.termaxis_to_term(tags, label),
                            strip=label),
                        **(tag_templates[label]  if label in tag_templates else {})}
                    for label in 'test dummy speaker modifier participle'.split()
                }
                completed_substitutions = [
                    *substitutions,
                    *[{key: tools.replace(tags[key])}
                      for key in ['noun','adjective','verb']
                      if key in tags],
                ]
                return self.format_card(
                        self.assemble(
                            self.orthography.map(
                                parsing.parse(tree_lookup[tags]),
                                semes, 
                                completed_substitutions,
                                debug=debug,
                            ),
                            self.context(tags),
                        ).replace('∅',''))
            return demonstrate
    return LanguageSpecificTextDemonstration

def EmojiDemonstration(
            nouns_to_depictions,
            noun_adjective_lookups,
            noun_verb_lookups,
            noun_declension_lookups,
            noun_lookups,
            verb_lookups,
            mood_templates,
            label_editing, 
            label_filtering, 
            emojiInflectionShorthand,
            htmlTenseTransform,
            htmlProgressTransform,
        ):
    class LanguageSpecificEmojiDemonstration:
        def __init__(self, format_card, persons):
            self.format_card = format_card
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
            return emojiInflectionShorthand.decode(scene, subject, persons)
        def generator(self, **junk):
            def noun(tags, tag_templates):
                if tags['noun-form'] == 'personal-possessive':
                    possessed = noun({**tags, 'noun-form':'common'}, tag_templates)
                    possessor = noun({
                            'noun-form': 'personal',
                            **label_editing.termaxis_to_term(
                                label_filtering.termaxis_to_term(tags, 'possessor'),
                                strip='possessor'),
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
                        else noun_adjective_lookups[tags] if tags in noun_adjective_lookups
                        else '🚫')
                    return self.decode(tags, result)
            def performance(tags, tag_templates):
                template = ((verb_lookups[tags] if tags in verb_lookups else '\\subject')
                    .replace('\\subject', noun(tags, tag_templates)))
                return template
            def scene(clause_tags, tag_templates):
                is_actor_test = {**clause_tags, **tag_templates['test']}['role'] in {'agent', 'force'}
                test_tags = {
                    **{tagaxis: clause_tags[tagaxis]
                       for tagaxis in clause_tags.keys()
                       if tagaxis != 'verb' or is_actor_test},
                    **label_filtering.termaxis_to_term(clause_tags, 'possessor'),
                    **tag_templates['test'], 
                    'script': 'emoji'
                }
                dummy_tags = {
                    **({'verb':clause_tags['verb']} if 'verb' in clause_tags and not is_actor_test else {}),
                    **label_editing.termaxis_to_term(
                        label_filtering.termaxis_to_term(clause_tags, 'dummy'),
                        strip='dummy'),
                    **tag_templates['dummy'], 
                    'script': 'emoji'
                }
                actor_tags = test_tags if is_actor_test else dummy_tags
                argument_tags = test_tags if not is_actor_test else dummy_tags
                copulative_tags = {
                    **clause_tags, 
                    'adjective':dummy_tags['noun'] if 'noun' in dummy_tags else 'missing'
                }
                template = (noun_adjective_lookups[copulative_tags] if copulative_tags in noun_adjective_lookups
                    else noun_declension_lookups[argument_tags] if argument_tags in noun_declension_lookups 
                    else noun_declension_lookups[actor_tags] if actor_tags in noun_declension_lookups 
                    else '🚫')
                template = (template
                    .replace('\\actor',  performance(actor_tags, tag_templates))
                    .replace('\\argument', noun(argument_tags, tag_templates))
                )
                return getattr(htmlTenseTransform, clause_tags['tense'])(
                            getattr(htmlProgressTransform, clause_tags['progress'].replace('-','_'))(template))
            def recounting(tags):
                return mood_templates[{**tags,'column':'template'}]
            def demonstrate(clause_tags, tag_templates):
                return self.format_card(
                    self.decode(
                        {**clause_tags, 'script':'emoji', 'language-type': 'foreign'}, 
                        recounting(clause_tags)
                            .replace('\\scene',     scene(clause_tags, tag_templates))
                            .replace('\\addressee', performance(clause_tags, tag_templates)
                                if clause_tags['subjectivity']=='addressee' else '\\n2{🧑\\g2\\c2}')
                        ))
            return demonstrate
    return LanguageSpecificEmojiDemonstration
