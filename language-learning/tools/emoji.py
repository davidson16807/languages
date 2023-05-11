from .shorthands import EmojiPerson

class Emoji:
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
        scene = self.emojiInflectionShorthand.decode(scene, 
            EmojiPerson(
                tags['number'][0], 
                tags['gender'][0], 
                persons[int(tags['person'])-1].color), 
            persons)
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

