from tools.nodes import Rule
from tools.nodemaps import RuleSyntax

def definiteness(machine, tree, memory):
    '''creates articles when necessary to express definiteness'''
    definiteness = memory['definiteness'] if 'definiteness' in memory else 'indefinite'
    subjectivity = memory['subjectivity']
    nounform = memory['noun-form']
    if definiteness == 'definite' and subjectivity != 'addressee' and nounform != 'personal': 
        return [['det','the'], tree]
    if definiteness == 'indefinite' and subjectivity != 'addressee' and nounform != 'personal': 
        return [['det','a'], tree]
    else:
        return tree

class ModernRomanceRuleSyntax(RuleSyntax):
    def __init__(self, noun_phrase_structure, sentence_structure, content_question_structure=None):
        super().__init__(noun_phrase_structure, sentence_structure, content_question_structure)
    def order_clause(self, treemap, clause):
        rules = clause.content
        nouns = [phrase for phrase in rules if phrase.tag in {'np'}]
        # enclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'enclitic'}]
        # proclitic_subjects = [noun for noun in subjects if noun.tags['clitic'] in {'proclitic'}]
        noun_lookup = {
            subjectivity: [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == subjectivity]
            for subjectivity in 'subject adverbial adnominal'.split()
        }
        verbs = [phrase
            for phrase in rules 
            if phrase.tag in {'vp'}]
        interrogatives = [noun 
            for noun in nouns 
            if noun.tags['noun-form'] == 'interrogative']
        phrase_lookup = {
            **noun_lookup,
            'personal-direct-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'direct-object'
                and noun.tags['noun-form'] == 'personal'],
            'common-direct-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'direct-object'
                and noun.tags['noun-form'] != 'personal'],
            'personal-indirect-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'indirect-object'
                and noun.tags['noun-form'] == 'personal'],
            'common-indirect-object': [noun 
                for noun in nouns 
                if noun.tags['subjectivity'] == 'indirect-object'
                and noun.tags['noun-form'] != 'personal'],
            'verb': verbs,
        }
        ordered = Rule(clause.tag, 
            clause.tags,
            treemap.map([
                phrase
                for phrase_type in (self.content_question_structure if interrogatives else self.sentence_structure)
                for phrase in phrase_lookup[phrase_type]
            ]))
        return ordered
