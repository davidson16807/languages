"""
"trees.py" contains representations for the nodes of abstract syntax trees.
"""

class Rule:
    def __init__(self, tag, tags, content):
        self.tag = tag
        self.tags = tags
        self.content = content
    def __getitem__(self, key):
        return self.content[key]
    def __str__(self):
        return '' + self.tag + '{'+' '.join([str(member) for member in self.content])+'}'
    def __repr__(self):
        return ' '.join([
                self.tag,
                '{'+' '.join([str(member) for member in self.content])+'}',
                '{'+'\n'.join([f'  {key}:{value}' for key, value in self.tags.items()])+'}',
            ])
