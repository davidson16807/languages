from .shorthands import EmojiPerson

class DemonstrationTemplateMatching:
    def __init__(self, templates, predicates, nouns_to_depictions):
        self.templates = templates
        self.predicates = predicates
        self.nouns_to_depictions = nouns_to_depictions
    def case(self, tags):
        def declined_noun(template):
            return self.predicates[template['declined-noun-function'], template['declined-noun-argument']]
        noun = tags['noun'] if 'noun' in tags else None
        depiction = self.nouns_to_depictions[noun] if noun in self.nouns_to_depictions else noun
        candidates = self.templates[tags] if tags in self.templates else []
        templates = sorted([template for template in candidates
                            if self.predicates['be', noun] in declined_noun(template)],
                      key=lambda template: -int(template['specificity']))
        return templates[0] if len(templates) > 0 else None
    def verb(self, tags):
        return None


class DeckGeneration:
    def __init__(self, omit_codes = ['—','❕','❔']):
        self.omit_codes = omit_codes
    def generate(self, 
            demonstration_template_match,
            demonstrations,
            traversal, 
            whitelists=[],
            blacklists=[],
            tag_templates={},
        ):
        for tuplekey in traversal:
            tags = traversal.indexing.dictkey(tuplekey)
            if (all([tags in whitelist for whitelist in whitelists]) and 
                all([tags not in blacklist for blacklist in blacklists])):
                match = demonstration_template_match(tags)
                card = ' '.join([
                    str(demonstration(tags, tag_templates, match)) 
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

