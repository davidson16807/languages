from parse_wiktionary import *
import csv_functions

foreign_language_code, foreign_language_name = csv_functions.lines_from_file('language-ids.txt')

def roots(etymology_tags):
    for (word,part_of_speech), layer, tag in etymology_tags:
        sections = tag.split('|')
        type_ = sections[0]
        if type_ == f'{foreign_language_code}-verb form of' and len(sections) >= 2:
            candidates = [section for section in sections[1:] if '=' not in section]
            if len(candidates) == 1:
                verb = candidates[0]
                yield (word, 'verb'), layer, verb
                yield (verb, 'verb'), layer, verb
        if type_ == 'plural of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            singular = sections[2]
            yield (word, part_of_speech), layer, singular
            # yield (singular, part_of_speech), layer, singular
        if type_ == 'adj form of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            root = sections[2]
            yield (word, part_of_speech), layer, root
            # yield (root, part_of_speech), layer, root
        if type_ == 'alternative spelling of'  and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'feminine singular of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'feminine plural of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'plural of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'misspelling of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'obsolete spelling of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'inflection of' and len(sections) >= 3 and sections[1] == foreign_language_code:
            standardized = sections[2]
            yield (word, part_of_speech), layer, standardized
            # yield (standardized, part_of_speech), layer, standardized
        if type_ == 'Latn-def':
            standardized = sections[-2]
            # NOTE: we assign the names of letters (in this case Latin) to their own part of speech
            # this part of speech is omitted from the known parts of speech list for that word, 
            # so they don't appear in frequency-from-tallies.tsv, 
            # but that's okay since their use is rare and we aren't interested in learning them
            yield (word, 'letter'), layer, word
            # yield (standardized, 'letter'), layer, standardized
        if type_ == 'letter_disp2':
            # NOTE: we assign the names of letters (in this case Greek) to their own part of speech
            # this part of speech is omitted from the known parts of speech list for that word, 
            # so they don't appear in frequency-from-tallies.tsv, 
            # but that's okay since their use is rare and we aren't interested in learning them
            yield (word, 'letter'), layer, word
            # yield (standardized, 'letter'), layer, standardized

for (word, part_of_speech), layer, root in chain_compose(
        lambda max_line_count: raw(max_line_count, filename='../../enwiktionary-latest-pages-articles.xml'), 
        pages, 
        header2('Spanish'),
        part_of_speech_header('Adjective|Adverb|Noun|Verb|Interjection|Numeral|Conjunction|Determiner|Preposition|Particle|Pronoun|Phrase'),
        tags,
        roots,
        unique
    )(1e9):
    print(f'{word.lower()}\t{part_of_speech.lower()}\t{root}')
    # print(f'{word.upper():<15} {root}')
