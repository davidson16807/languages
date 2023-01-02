import re
from transforms import *
from shorthands import *

def column(filename, column_id, *formatters, delimeter='\t', padding=' \t\r\n'):
    cells = []
    with open(filename) as file:
        for line in file.readlines():
            if not line.strip().startswith('#') and not len(line.strip()) < 1:
                row = [column.strip(padding) for column in line.split(delimeter)]
                cell = row[column_id]
                for formatter in formatters:
                    if cell is not None:
                        cell = formatter(cell)
                cells.append(cell)
    return cells

def strip_asterisks(cell):
    return cell.replace('*','')

def inside_first_parens(cell):
    return ', '.join(
        re.search('[(][^)]*?[)]', segment).group(0).strip('()') + re.split('[(][^)]*?[)]', segment, 1)[1]
        for segment in cell.split(',')
        if re.search('[(][^)]*?[)]', segment)
    )

def outside_first_parens(cell):
    return ', '.join(
        re.sub('[(][^)]*?[)]', '', segment, 1).strip()
        for segment in cell.split(',')
    )

def add_ipa_markers(cell):
    return ', '.join(f'/{segment.strip()}/' for segment in cell.split(','))

def strip_ipa_markers(cell):
    return ', '.join(segment.replace('/','').strip() for segment in cell.split(','))

def emoji(cell):
    fonts = "'sans-serif', 'Twemoji', 'Twemoji Mozilla', 'Segoe UI Emoji', 'Noto Color Emoji'"
    return f'<div style="font-size:3em; font-family: {fonts}">{cell}</div>'

def foreign_focus(cell):
    return f'<div style="font-size:3em">{cell}</div>'

def foreign_side_note(cell):
    return f'<div style="font-size:2em">{cell}</div>'

def english_word(cell):
    return f'<div>{cell}</div>'

def cloze(id):
    return lambda cell: '{{'+f'c{id}::{cell}'+'}}'

def require(cell):
    return cell if cell.strip() else None



def sound_laws(tuples):
    def _sound_laws(text):
        modified = text
        for (regex, replacement) in tuples:
            modified = re.sub(regex, replacement, modified)
        return modified
    return _sound_laws


def write(filename, columns):
    with open(filename, 'w') as file:
        for row in zip(*columns):
            if all(cell is not None for cell in row):
                file.write(''.join(row)+'\n')

def input_path(filename):
	return f'data/swadesh-tables/{filename}'

def output_path(filename):
	return f'flashcards/swadesh-tables/{filename}'

bracket_shorthand = BracketedShorthand(Enclosures())

shorthands = [
    EmojiPersonShorthand(
    EmojiNumberShorthand(
    HtmlNumberTransform(HtmlPersonPositioning()), bracket_shorthand)),
    EmojiBubbleShorthand(HtmlBubble(), bracket_shorthand),
    TextTransformShorthand(HtmlTextTransform(), bracket_shorthand),
    EmojiGestureShorthand(HtmlGesturePositioning(), bracket_shorthand),
    EmojiModifierShorthand()
]

emoji_skin_shorthand1 = EmojiVocabularyShorthand([1,2,3,4,5], *shorthands)
emoji_skin_shorthand2 = EmojiVocabularyShorthand([2,3,1,4,5], *shorthands)
emoji_skin_shorthand3 = EmojiVocabularyShorthand([3,2,4,1,5], *shorthands)
emoji_skin_shorthand4 = EmojiVocabularyShorthand([4,5,2,3,1], *shorthands)
emoji_skin_shorthand5 = EmojiVocabularyShorthand([5,4,3,2,1], *shorthands)

# english ↔ proto-indo-european
write(output_path('english-and-proto-indo-european.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('indo-european-branches.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-indo-european → proto-germanic
write(output_path('proto-indo-european-to-proto-germanic.html'), [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-european-branches.tsv'), 4, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-germanic
write(output_path('english-and-proto-germanic.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji),
    column(input_path('indo-european-branches.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-european-branches.tsv'), 4, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-germanic → old english
write(output_path('proto-germanic-to-old english.html'), [
    column(input_path('germanic-languages.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('germanic-languages.tsv'), 4, require, cloze(1), foreign_focus), 
])

# english ↔ old english
write(output_path('english-and-old-english.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji), 
    column(input_path('germanic-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('germanic-languages.tsv'), 4, require, cloze(2), foreign_focus), 
    column(input_path('germanic-languages.tsv'), 5, require, cloze(2), foreign_side_note), 
])

# old english → old english pronunciation
write(output_path('old-english-to-old-english-pronunciation.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, emoji), 
    column(input_path('germanic-languages.tsv'), 2, english_word), 
    column(input_path('germanic-languages.tsv'), 4, require, foreign_focus), 
    column(input_path('germanic-languages.tsv'), 5, require, cloze(1), foreign_side_note), 
])

# proto-germanic → old norse
write(output_path('proto-germanic-to-old-norse.html'), [
    column(input_path('germanic-languages.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('germanic-languages.tsv'), 16, require, cloze(1), foreign_focus), 
])

# english ↔ old-norse
write(output_path('english-and-old-norse.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji),
    column(input_path('germanic-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('germanic-languages.tsv'), 16, require, cloze(2), foreign_focus), 
])

# old norse → swedish
write(output_path('old-norse-to-swedish.html'), [
    column(input_path('germanic-languages.tsv'), 16, require, foreign_focus), 
    column(input_path('germanic-languages.tsv'), 18, require, cloze(1), foreign_focus), 
])

# english ↔ swedish
write(output_path('english-and-swedish.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji),
    column(input_path('germanic-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('germanic-languages.tsv'), 18, require, cloze(2), foreign_focus), 
])

# old norse → danish
write(output_path('old-norse-to-danish.html'), [
    column(input_path('germanic-languages.tsv'), 16, require, foreign_focus), 
    column(input_path('germanic-languages.tsv'), 17, require, cloze(1), foreign_focus), 
])

# english ↔ danish
write(output_path('english-and-danish.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji),
    column(input_path('germanic-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('germanic-languages.tsv'), 17, require, cloze(2), foreign_focus), 
])

# proto-indo-european → proto-italic
write(output_path('proto-indo-european-to-proto-italic.html'), [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-european-branches.tsv'), 5, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-italic
write(output_path('english-and-proto-italic.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('indo-european-branches.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-european-branches.tsv'), 5, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-italic → latin
write(output_path('proto-italic-to-latin.html'), [
    column(input_path('romance-languages.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('romance-languages.tsv'), 4, require, cloze(1), foreign_focus), 
])

# proto-indo-european → latin
write(output_path('proto-indo-european-to-latin.html'), [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('romance-languages.tsv'), 4, require, cloze(1), foreign_focus), 
])

# english ↔ latin
write(output_path('english-and-latin.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji), 
    column(input_path('romance-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('romance-languages.tsv'), 4, require, cloze(2), foreign_focus), 
    # column(input_path('romance-languages.tsv'), 5, require, cloze(2), foreign_side_note), 
])

# latin → latin pronunciation
write(output_path('latin-to-latin-pronunciation.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji), 
    column(input_path('romance-languages.tsv'), 2, english_word), 
    column(input_path('romance-languages.tsv'), 4, require, foreign_focus), 
    column(input_path('romance-languages.tsv'), 5, require, cloze(1), foreign_side_note), 
])

# english ↔ vulgar latin
write(output_path('english-and-latin.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji), 
    column(input_path('romance-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('romance-languages.tsv'), 6, require, cloze(2), foreign_focus), 
])

# latin → vulgar latin
write(output_path('latin-to-vulgar latin.html'), [
    column(input_path('romance-languages.tsv'), 4, require, foreign_focus), 
    column(input_path('romance-languages.tsv'), 6, require, strip_asterisks, cloze(1), foreign_focus), 
])

# vulgar latin → spanish
write(output_path('vulgar latin-to-spanish.html'), [
    column(input_path('romance-languages.tsv'), 6, require, strip_asterisks, foreign_focus), 
    column(input_path('romance-languages.tsv'), 9, require, cloze(1), foreign_focus), 
])

# english ↔ spanish
write(output_path('english-and-spanish.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('romance-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('romance-languages.tsv'), 9, require, cloze(2), foreign_focus), 
])

# vulgar latin → french
write(output_path('vulgar latin-to-french.html'), [
    column(input_path('romance-languages.tsv'), 6, require, strip_asterisks, foreign_focus), 
    column(input_path('romance-languages.tsv'), 7, require, cloze(1), foreign_focus), 
])

# english ↔ french
write(output_path('english-and-french.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, cloze(1), emoji), 
    column(input_path('romance-languages.tsv'), 2, cloze(1), english_word),
    column(input_path('romance-languages.tsv'), 7, require, cloze(2), foreign_focus),
    # column(input_path('romance-languages.tsv'), 8, require, cloze(2), foreign_side_note),
])

# french → french pronunciation
write(output_path('french-to-french-pronunciation.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand2.decode, emoji), 
    column(input_path('romance-languages.tsv'), 2, english_word),
    column(input_path('romance-languages.tsv'), 7, require, foreign_focus),
    column(input_path('romance-languages.tsv'), 8, require, cloze(1), foreign_side_note),
])

# proto-indo-european → proto-hellenic
write(output_path('proto-indo-european-to-proto-hellenic.html'), [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-european-branches.tsv'), 6, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-hellenic
write(output_path('english-and-proto-hellenic.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('indo-european-branches.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-european-branches.tsv'), 6, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-hellenic → ancient greek
write(output_path('proto-hellenic-to-ancient-greek.html'), [
    column(input_path('hellenic-languages.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('hellenic-languages.tsv'), 4, require, inside_first_parens, cloze(1), foreign_focus), 
])

# english ↔ ancient greek
write(output_path('english-and-ancient-greek.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('hellenic-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('hellenic-languages.tsv'), 4, require, outside_first_parens, cloze(2), foreign_focus), 
    column(input_path('hellenic-languages.tsv'), 4, require, inside_first_parens, cloze(2), foreign_side_note), 
])

# ancient greek ↔ ancient greek transliteration
write(output_path('ancient-greek-and-ancient-greek-transliteration.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, emoji),
    column(input_path('hellenic-languages.tsv'), 2, english_word), 
    column(input_path('hellenic-languages.tsv'), 4, require, outside_first_parens, cloze(1), foreign_focus), 
    column(input_path('hellenic-languages.tsv'), 4, require, inside_first_parens, cloze(2), foreign_side_note), 
])

# proto-indo-european → proto-indo-iranian
write(output_path('proto-indo-european-to-proto-indo-iranian.html'), [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-european-branches.tsv'), 7, require, strip_asterisks, cloze(1), foreign_focus), 
])

# english ↔ proto-indo-iranian
write(output_path('english-and-proto-indo-iranian.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand4.decode, cloze(1), emoji),
    column(input_path('indo-european-branches.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-european-branches.tsv'), 7, require, strip_asterisks, cloze(2), foreign_focus), 
])

# proto-indo-iranian → sanskrit
write(output_path('proto-indo-iranian-to-sanskrit.html'), [
    column(input_path('indo-iranian-languages.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-iranian-languages.tsv'), 4, require, inside_first_parens, cloze(1), foreign_focus), 
])

# english ↔ sanskrit
write(output_path('english-and-sanskrit.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand4.decode, cloze(1), emoji),
    column(input_path('indo-iranian-languages.tsv'), 2, cloze(1), english_word), 
    column(input_path('indo-iranian-languages.tsv'), 4, require, outside_first_parens, cloze(2), foreign_focus), 
    column(input_path('indo-iranian-languages.tsv'), 4, require, inside_first_parens, cloze(2), foreign_side_note), 
])

# english ↔ sanskrit transliteration
write(output_path('sanskrit-and-sanskrit-transliteration.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand4.decode, emoji),
    column(input_path('indo-iranian-languages.tsv'), 2, english_word), 
    column(input_path('indo-iranian-languages.tsv'), 4, require, outside_first_parens, cloze(1), foreign_focus), 
    column(input_path('indo-iranian-languages.tsv'), 4, require, inside_first_parens, cloze(2), foreign_side_note), 
])

# english ↔ vietnamese
write(output_path('english-and-vietnamese.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand3.decode, cloze(1), emoji),
    column(input_path('vietnamese.tsv'), 2, cloze(1), english_word), 
    column(input_path('vietnamese.tsv'), 3, require, cloze(2), foreign_focus), 
])

# english ↔ sumerian
write(output_path('english-and-sumerian.html'), [
    column(input_path('emoji.tsv'), 3, emoji_skin_shorthand4.decode, cloze(1), emoji),
    column(input_path('sumerian.tsv'), 2, cloze(1), english_word), 
    column(input_path('sumerian.tsv'), 3, require, cloze(2), foreign_focus), 
])














'''
# proto-indo-european → proto-italic
columns = [
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, foreign_focus), 
    column(input_path('indo-european-branches.tsv'), 3, require, strip_asterisks, 
        sound_laws([
            ('\bbʰ','f'), 
            ('\bdʰ','f'), 
            ('\bgʰ','h'), 
            ('\bgʷʰ','f'),
            ('bʰ','b'), 
            ('dʰ','d'), 
            ('gʰ','g'), 
            ('gʷʰ','v'),
            ('(r[aeiou]*)dʰ','\\1b'),
            ('([aeiou])s([aeiou])','\\1r\\2'),]), cloze(1), foreign_focus),
    column(input_path('romance-languages.tsv'), 4, require, cloze(1), foreign_focus), 
]
'''
