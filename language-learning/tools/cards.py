from .shorthands import EmojiPerson

class DeclensionTemplateMatching:
    def __init__(self, templates, predicates):
        self.templates = templates
        self.predicates = predicates
    def match(self, noun, tags):
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        candidates = self.templates[tags] if tags in self.templates else []
        templates = sorted([template for template in candidates
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: (-int(template['specificity']), len(declined_noun(template))))
        return templates[0] if len(templates) > 0 else None

class DeckGeneration:
    def __init__(self, omit_codes = ['—','❕','❔']):
        self.omit_codes = omit_codes
    def generate(self, 
            demonstrations,
            dictset, 
            tag_templates={},
        ):
        for tuplekey in dictset:
            dictkey = dictset.indexing.dictkey(tuplekey)
            card = ' '.join([
                str(demonstration(dictkey, tag_templates)) 
                for demonstration in demonstrations])
            if all([symbol not in card for symbol in self.omit_codes]):
                yield card

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

