import re

from .shorthands import EmojiPerson
from .treemaps import ListTreeMap, RuleTreeMap

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
                    getattr(self.htmlAspectTransform, tags['aspect'].replace('-','_'))(argument))
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
    def decline(self, tags, scene, noun, persons):
        scene = scene.replace('\\declined', noun)
        scene = self.emojiInflectionShorthand.decode(scene, 
            EmojiPerson(
                tags['number'][0], 
                tags['gender'][0], 
                persons[int(tags['person'])-1].color), 
            persons)
        return scene


class Language:
    def __init__(self, 
            grammar,
            syntax,
            tools,
            formatting,
            validation,
            substitutions=[]):
        self.substitutions = substitutions
        self.grammar = grammar
        self.syntax = syntax
        self.tools = tools
        self.validation = validation
        self.formatting = formatting
    def map(self, syntax_tree, custom_substitution={}, semes={}):
        default_substitution = {
            'the':        self.tools.replace(['art', 'the']),
            'a':          self.tools.replace(['art', 'a']),
        }
        tag_opcodes = {
            'perfect':    {'aspect': 'perfect'},
            'imperfect':  {'aspect': 'imperfect'},
            'aorist':     {'aspect': 'aorist'},
            'infinitive': {'verb-form': 'infinitive'},
            'finite':     {'verb-form': 'finite'},
            'active':     {'voice': 'active'},
            'passive':    {'voice': 'passive'},
            'middle':     {'voice': 'middle'},
            **semes
        }
        tag_insertion = {tag:self.tools.tag(opcode, remove=False) for (tag, opcode) in tag_opcodes.items()}
        tag_removal   = {tag:self.tools.tag(opcode, remove=True)  for (tag, opcode) in tag_opcodes.items()}
        pipeline = [
            ListTreeMap({**tag_insertion, **default_substitution}),
            ListTreeMap({**tag_insertion, **custom_substitution}),
            *[ListTreeMap({**tag_insertion, **substitution}) for substitution in self.substitutions],
            ListTreeMap({
                **tag_insertion, 
                'v':                self.grammar.conjugate,
                'n':                self.grammar.decline,
                'art':              self.grammar.decline,
                'adj':              self.grammar.decline,
                'stock-adposition': self.grammar.stock_adposition,
            }),
            ListTreeMap({
                **tag_removal,
                **{tag:self.tools.rule() for tag in 'clause cloze art adj np vp n v stock-modifier stock-adposition'.split()},
            }),
            RuleTreeMap({
                'clause':  self.syntax.order_clause,
                'np':      self.syntax.order_noun_phrase,
            }),
        ]
        validation = RuleTreeMap({
            **{tag:self.validation.exists for tag in 'clause cloze art adp np vp n v'.split()},
        }) if self.validation else None
        formatting = RuleTreeMap({
            **{tag:self.formatting.default for tag in 'clause cloze art adj np vp n v stock-modifier stock-adposition'.split()},
            'cloze':   self.formatting.cloze,
            'implicit':self.formatting.implicit,
        })
        tree = syntax_tree
        for i, step in enumerate(pipeline):
            # print(i)
            # print(tree)
            tree = step.map(tree)
        return formatting.map(tree) if not validation or validation.map(tree) else None
