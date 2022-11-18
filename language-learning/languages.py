import re

from shorthands import EmojiPerson
from syntax import (Cloze, NounPhrase, Adjective, Adposition, Article, StockModifier, Clause)

class English:
    def __init__(self, 
            plurality,
            declension_lookups, 
            conjugation_lookups, 
            predicate_templates, 
            mood_templates):
        self.plurality = plurality
        self.declension_lookups = declension_lookups
        self.conjugation_lookups = conjugation_lookups
        self.predicate_templates = predicate_templates
        self.mood_templates = mood_templates
    def decline(self, grammemes, content):
        grammemes = {**grammemes, 'language-type':'english'}
        if content is None:
            case = grammemes['case'] if grammemes['case'] in {'nominative','genitive'} else 'oblique'
            grammemes = {**grammemes, 'case': case}
            return (
                self.declension_lookups[grammemes][grammemes] if grammemes['noun-form'] != 'common'
                else self.plurality.pluralize(grammemes['noun']) if grammemes['number'] != 'singular'
                else grammemes['noun'])
        if type(content) in {list,set}:
            return [self.decline(grammemes, element) for element in content]
        elif type(content) in {str}:
            # NOTE: string types are degenerate cases of None types invocations
            #  where grammemes contain the lemma for the declension
            return self.decline({**grammemes, 'noun':content}, None) 
        elif type(content) in {NounPhrase}:
            grammemes = {**grammemes, **content.grammemes}
            case = grammemes['case'] if grammemes['case'] in {'nominative','genitive'} else 'oblique'
            grammemes = {**grammemes, 'case': case}
            return NounPhrase(grammemes, self.decline(grammemes, content.content))
        elif type(content) in {StockModifier}:
            return content.lookup[grammemes] if grammemes in content.lookup else []
        elif type(content) in {Adjective, Article}:
            return (content if grammemes['noun-form'] == 'common' else [])
        elif type(content) in {Adposition}:
            return content
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.decline(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def conjugate(self, grammemes, content):
        if type(content) in {list,set}:
            return [self.conjugate(grammemes, element) for element in content]
        elif type(content) in {str}:
            grammemes = {**grammemes, 'language-type':'translated'}
            if grammemes not in self.conjugation_lookups['finite']:
                return None
            return self.conjugation_lookups['finite'][grammemes]
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.conjugate(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def format(self, content):
        if type(content) in {Clause}:
            clause = content
            dependant_clause = {
                **clause.grammemes,
                'language-type': 'english',
            }
            independant_clause = {
                **clause.grammemes,
                'language-type': 'english',
                'aspect': 'aorist',
                'tense':     
                    'past' if dependant_clause['aspect'] in {'perfect', 'perfect-progressive'} else
                    'present' if dependant_clause['tense'] in {'future'} else
                    dependant_clause['tense']
            }
            verb = self.format(clause.verb)
            lemmas = ['be', 'have', 
                      'command', 'forbid', 'permit', 'wish', 'intend', 'be able', 
                      verb]
            mood_replacements = [
                ('{predicate}',            self.predicate_templates[{**dependant_clause,'verb-form':'finite'}]),
                ('{predicate|infinitive}', self.predicate_templates[{**dependant_clause,'verb-form':'infinitive'}]),
            ]
            sentence = self.mood_templates[{**dependant_clause,'column':'template'}]
            for replaced, replacement in mood_replacements:
                sentence = sentence.replace(replaced, replacement)
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                sentence = sentence.replace('{'+noun+'}', 
                    self.format(self.decline(clause.grammemes, 
                        clause.nouns[noun] if noun in clause.nouns else [])))
            for noun in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                for case in ['nominative','oblique']:
                    sentence = sentence.replace('{'+f'{noun}|{case}'+'}', 
                        self.format(self.decline({**clause.grammemes, 'case':case}, 
                            clause.nouns[noun] if noun in clause.nouns else [])))
            sentence = sentence.replace('{verb', '{'+verb)
            table = self.conjugation_lookups['finite']
            for lemma in lemmas:
                replacements = [
                    ('{'+lemma+'|independant}',         table[{**independant_clause, 'verb':lemma, }]),
                    ('{'+lemma+'|independant|speaker}', table[{**independant_clause, 'verb':lemma, 'person':'1', 'number':'singular'}]),
                    ('{'+lemma+'|present}',             table[{**dependant_clause,   'verb':lemma, 'tense':  'present',  'aspect':'aorist'}]),
                    ('{'+lemma+'|past}',                table[{**dependant_clause,   'verb':lemma, 'tense':  'past',     'aspect':'aorist'}]),
                    ('{'+lemma+'|perfect}',             table[{**dependant_clause,   'verb':lemma, 'aspect': 'perfect'    }]),
                    ('{'+lemma+'|imperfect}',           table[{**dependant_clause,   'verb':lemma, 'aspect': 'imperfect'  }]),
                    ('{'+lemma+'|infinitive}',          lemma),
                ]
                for replaced, replacement in replacements:
                    sentence = sentence.replace(replaced, replacement)
            if dependant_clause['voice'] == 'middle':
                sentence = f'[middle voice:] {sentence}'
            sentence = re.sub('\s+', ' ', sentence)
            return sentence
        if content is None:
            return ''
        if type(content) in {list,set}:
            return ' '.join([self.format(element) for element in content])
        elif type(content) in {str}:
            return content
        elif type(content) in {NounPhrase, Adjective, Article}:
            return self.format(content.content)
        elif type(content) in {Adposition}:
            return self.format(content.native)
        elif type(content) in {Cloze}:
            # NOTE: Cloze is only ever used to prompt for the foreign language being learned,
            # so for the user's native language it is simply equal to the formatted content.
            return self.format(content.content) 
    def parse(self, NodeClass, text):
        if NodeClass in {set}:
            return set(text.split(' '))
        if NodeClass in {list}:
            return text.split(' ')
        elif NodeClass in {str}:
            return text
        else:
            return NodeClass(self.parse(text))

class Emoji:
    def __init__(self, 
            mood_templates, 
            emojiInflectionShorthand, 
            htmlTenseTransform, 
            htmlAspectTransform):
        self.emojiInflectionShorthand = emojiInflectionShorthand
        self.htmlTenseTransform = htmlTenseTransform
        self.htmlAspectTransform = htmlAspectTransform
        self.mood_templates = mood_templates
    def conjugate(self, grammemes, argument, persons):
        audience_lookup = {
            'voseo':    '\\background{🇦🇷}\\n2{🧑\\g2\\c2}',
            'polite':   '\\n2{🧑\\g2\\c2\\💼}',
            'formal':   '\\n2{🤵\\c2\\g2}',
            'elevated': '\\n2{🤴\\g2\\c2}',
        }
        # TODO: reimplement formality as emoji modifier shorthand
        # audience = (audience_lookup[grammemes['formality']] 
        #          if grammemes['formality'] in audience_lookup 
        #          else '\\n2{🧑\\g2\\c2}')
        scene = getattr(self.htmlTenseTransform, grammemes['tense'])(
                    getattr(self.htmlAspectTransform, grammemes['aspect'].replace('-','_'))(argument))
        encoded_recounting = self.mood_templates[{**grammemes,'column':'template'}]
        subject = EmojiPerson(
            ''.join([
                    (grammemes['number'][0]),
                    ('i' if grammemes['clusivity']=='inclusive' else ''),
                ]), 
            grammemes['gender'][0], 
            persons[int(grammemes['person'])-1].color)
        persons = [
            subject if str(i+1)==grammemes['person'] else person
            for i, person in enumerate(persons)]
        recounting = encoded_recounting
        recounting = recounting.replace('\\scene', scene)
        recounting = self.emojiInflectionShorthand.decode(recounting, subject, persons)
        return recounting
    def decline(self, grammemes, scene, noun, persons):
        scene = scene.replace('\\declined', noun)
        scene = self.emojiInflectionShorthand.decode(scene, 
            EmojiPerson(
                grammemes['number'][0], 
                grammemes['gender'][0], 
                persons[int(grammemes['person'])-1].color), 
            persons)
        return scene

class Translation:
    def __init__(self, 
            conjugation_lookups, 
            declension_lookups, 
            use_case_to_grammatical_case,
            mood_templates,
            category_to_grammemes,
            persons):
        self.conjugation_lookups = conjugation_lookups
        self.declension_lookups = declension_lookups
        self.use_case_to_grammatical_case = use_case_to_grammatical_case
        self.mood_templates = mood_templates
        self.category_to_grammemes = category_to_grammemes
        self.persons = persons
    def parse(self, NodeClass, text):
        if NodeClass in {set}:
            return set(text.split(' '))
        elif NodeClass in {list}:
            return text.split(' ')
        elif NodeClass in {str}:
            return text
        else:
            return NodeClass(text.split(' '))
    def format(self, content):
        if type(content) in {Clause}:
            sentence = self.mood_templates[content.grammemes['mood']]
            sentence = sentence.replace('{verb}', self.format(content.verb))
            for noun_tag in ['subject', 'direct-object', 'indirect-object', 'modifiers']:
                sentence = sentence.replace('{'+noun_tag+'}', 
                    self.format(content.nouns[noun_tag] if noun_tag in content.nouns else ''))
            sentence = re.sub('\s+', ' ', sentence)
            return sentence
        elif content is None:
            return ''
        elif type(content) in {list,set}:
            return ' '.join([self.format(element) for element in content])
            # TODO: implement language agnostic way to specify word order in noun phrases
        elif type(content) in {str}:
            return content
        elif type(content) in {NounPhrase}:
            return self.format(content.content)
            # TODO: implement language agnostic way to specify location of adpositions
        elif type(content) in {Adjective, Article}:
            return self.format(content.content)
        elif type(content) in {Adposition}:
            return self.format(content.foreign)
        elif type(content) in {Cloze}:
            return '{{c'+str(content.id)+'::'+self.format(content.content)+'}}'
    def exists(self, content):
        if content is None:
            return False
        elif type(content) in {list,set}:
            return all([self.exists(element) for element in content])
        elif type(content) in {str}:
            return True
        elif type(content) in {Adjective, Article, Adposition}:
            return True
        elif type(content) in {NounPhrase}:
            return self.exists(content.content)
        elif type(content) in {Clause}:
            return self.exists(content.verb)
        elif type(content) in {Cloze}:
            return self.exists(content.content)
    def decline(self, grammemes, content):
        grammemes = {**grammemes, 'language-type':'translated'}
        if content is None:
            # NOTE: if content is a None type, then rely solely on the grammeme
            #  This logic provides a natural way to encode for pronouns
            if grammemes not in self.declension_lookups:
                return None
            if grammemes not in self.declension_lookups[grammemes]:
                return None
            return self.declension_lookups[grammemes][grammemes]
        elif type(content) in {list,set}:
            return [self.decline(grammemes, element) for element in content]
        elif type(content) in {str}:
            # NOTE: string types are degenerate cases of None types invocations
            #  where grammemes contain the lemma for the declension
            return self.decline({**grammemes, 'noun':content}, None) 
        elif type(content) in {NounPhrase}:
            return NounPhrase({**grammemes, **content.grammemes}, 
                self.decline({**grammemes, **content.grammemes}, content.content))
        elif type(content) in {StockModifier}:
            return content.lookup[grammemes] if grammemes in content.lookup else []
        elif type(content) in {Adjective}:
            return (Adjective(self.decline(grammemes, content.content)) if grammemes['noun-form'] == 'common' else [])
        elif type(content) in {Article}:
            return (Article(self.decline(grammemes, content.content)) if grammemes['noun-form'] == 'common' else [])
        elif type(content) in {Adposition}:
            return Adposition(
                native=content.native, 
                foreign=content.foreign)
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.decline(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def conjugate(self, grammemes, content):
        if type(content) in {list,set}:
            return [self.conjugate(grammemes, element) for element in content]
        elif type(content) in {str}:
            grammemes = {**grammemes, 'language-type':'translated', 'verb':content}
            if grammemes not in self.conjugation_lookups['finite']:
                return None
            else:
                return self.conjugation_lookups['finite'][grammemes]
        elif type(content) in {Cloze}:
            return Cloze(content.id, self.conjugate(grammemes, content.content))
        else:
            raise TypeError(f'Content of type {type(content).__name__}: \n {content}')
    def inflect(self, grammemes, content):
        if type(content) in {Clause}:
            grammemes = {**grammemes, **content.grammemes}
            return Clause(grammemes,
                self.conjugate(grammemes, content.verb), 
                {key:self.decline(grammemes, value) for (key,value) in content.nouns.items()})
        elif type(content) in {list,set}:
            return [self.inflect(grammemes, element) for element in content]
        elif type(content) in {NounPhrase}:
            grammemes = {**grammemes, **content.grammemes}
            return self.decline(grammemes, content)
