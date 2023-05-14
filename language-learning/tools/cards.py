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
                lines = [demonstration(tags, tag_templates) for demonstration in demonstrations]
                if all(['—' not in line for line in lines]):
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

