"""Generate two-column Gaulish lemma tables from the repository's PDFs.

Run with Python 3 and Poppler's pdftotext installed.
"""

import argparse
from pathlib import Path
import re
import subprocess
import unicodedata


GAULISH = (
    Path(__file__).resolve().parent
    / 'data/inflection/indo-european/celtic/gaulish'
)
PARTS_OF_SPEECH = ('verb', 'noun', 'adjective')
VOWEL_LENGTH = str.maketrans('âêîôûÂÊÎÔÛ', 'āēīōūĀĒĪŌŪ')
WORD = r'[^\W\d_]+'
GLOSS = re.compile(r'[a-z]+(?:[’\'-][a-z]+)*(?: [a-z]+(?:[’\'-][a-z]+)*)*')
DICTIONARY_CLASS = re.compile(
    r'(?<!\w)(?:D?(?:AII|AI|BIII|BII|BIV|BI|BV)|irr(?:eg)?\.\s*v\.?)'
    r'(?=[\s.;,]|$)'
)
NOUN_TAG = re.compile(r'\b[mfn][oainustrgcdl](?:\.|(?=/[mfn][oainustrgcdl]\.))')
ADJECTIVE_TAG = re.compile(r'\badj\.(?:o/a\.)?')
HANDBOOK_NOMINAL = re.compile(
    r'^(?:\S |\x03)(?P<head>[^,\n]+),[^:\n]+:\s*[‘“](?P<gloss>[^’”]+)[’”]',
    re.MULTILINE,
)
HANDBOOK_VERB = re.compile(
    r'^☸\s*(?P<stem>[^:\s]+)\s*:?\s*\[(?P<class>[^\]]+)\]'
    r'\s*:?\s*[‘“](?P<gloss>[^’”]+)[’”]',
    re.MULTILINE,
)
HANDBOOK_VERB_ENDINGS = {
    'A1': (('ye/o', 'iet'), ('e/o', 'et')),
    'A2': (('ye/o', 'iet'), ('e/o', 'et')),
    'A3b': (('ne/o', 'net'),),
    'B1': (('ā', 'āt'),),
    'B2': (('ī', 'īt'), ('ye/o', 'iet')),
    'B3': (('ye/o', 'iet'),),
    'C1': (('éye/o', 'īt'), ('eye/o', 'īt'), ('ī', 'īt')),
}


def read_pdf(path, mode):
    return subprocess.run(
        ['pdftotext', mode, '-enc', 'UTF-8', str(path), '-'],
        check=True,
        capture_output=True,
        encoding='utf-8',
    ).stdout


def headword(text):
    lemma = re.split(r'\s*[~,/><=]\s*|\s+', text.strip(), maxsplit=1)[0]
    lemma = unicodedata.normalize('NFC', lemma.strip('*?!').replace('·', ''))
    return lemma.translate(VOWEL_LENGTH) if re.fullmatch(WORD, lemma) else ''


def gloss_keys(text, part):
    # Brackets usually contain sources and parentheses qualify a sense.
    text = re.split(r'\[|\b(?:Inferred|From Gaul)\b', text, maxsplit=1)[0]
    text = re.sub(r'\([^()]*\)', '', text)
    for sense in re.split(r'[,;/]', text):
        sense = ' '.join(sense.strip(' .?!“”‘’"').lower().split())
        if part == 'verb':
            sense = sense.removeprefix('to ')
        if GLOSS.fullmatch(sense) and sense not in {'to', 'or', 'and'}:
            yield sense.replace(' ', '-')


def dictionary_articles(text):
    article = []
    for line in text.splitlines():
        line = line.strip()
        if ':' in line:
            if article:
                yield ' '.join(article)
            article = [line]
        elif article and line and not (line.isdigit() or (len(line) == 1 and line.isupper())):
            article.append(line)
    if article:
        yield ' '.join(article)


def dictionary_entries(text):
    for article in dictionary_articles(text):
        header, _, gloss = article.partition(':')
        classes = list(DICTIONARY_CLASS.finditer(header))
        if classes:
            start = 0
            for label in classes:
                lemma = headword(header[start:label.start()].lstrip(' .;~'))
                if lemma and lemma not in {'moni', 'uidre'}:
                    yield 'verb', lemma, gloss
                start = label.end()
            continue

        # The first tag describes the headword. Subsequent tags on the same
        # line can describe alternants, e.g. a feminine form or another stem.
        adjective = ADJECTIVE_TAG.search(header)
        noun = NOUN_TAG.search(header)
        lemma = headword(header)
        if lemma and adjective and (not noun or adjective.start() < noun.start()):
            yield 'adjective', lemma, gloss
        elif lemma and noun:
            yield 'noun', lemma, gloss


def handbook_verb_headword(stem, verb_class):
    stem = stem.rstrip('-*').lower()
    stem = stem.replace('·', '').replace('-', '')
    family = verb_class if verb_class == 'A3b' else verb_class[:2]
    if not re.fullmatch(r'(?:[AB][1-3][abc]?|C1)', verb_class):
        return ''
    for ending, present in HANDBOOK_VERB_ENDINGS.get(family, ()):
        if stem.endswith(ending):
            return headword(stem.removesuffix(ending) + present)
    return ''


def handbook_entries(text):
    _, nouns = text.split('6.2 ANWANA / NOUNS', 1)
    nouns, rest = nouns.split('6.3 ADJECTIVES', 1)
    adjectives, verbs = rest.split('6.4 VERBS — BRĒTRĀS', 1)
    verbs = verbs.split('6.5 SELECTED THEONYMS', 1)[0]

    for part, section in (('noun', nouns), ('adjective', adjectives)):
        for entry in HANDBOOK_NOMINAL.finditer(section):
            lemma = headword(entry['head'].lower())
            if lemma:
                yield part, lemma, entry['gloss']
    for entry in HANDBOOK_VERB.finditer(verbs):
        lemma = handbook_verb_headword(entry['stem'], entry['class'])
        if lemma:
            yield 'verb', lemma, entry['gloss']


def lemma_tables(sources):
    tables = {part: {} for part in PARTS_OF_SPEECH}
    for source_order, entries in enumerate(sources):
        for part, lemma, gloss in entries:
            for sense_order, key in enumerate(gloss_keys(gloss, part)):
                rank = (source_order, sense_order)
                previous = tables[part].get(key)
                if previous is None or rank < previous[0]:
                    tables[part][key] = rank, lemma
    return {
        part: [(key, lemma) for key, (_, lemma) in sorted(entries.items())]
        for part, entries in tables.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=GAULISH)
    parser.add_argument('--output-dir', type=Path, default=GAULISH)
    args = parser.parse_args()

    try:
        dictionary = read_pdf(args.source_dir / 'Uoxtlosernis Galatis.pdf', '-layout')
        handbook = read_pdf(args.source_dir / 'yextis_keltika_eng.pdf', '-raw')
        tables = lemma_tables((dictionary_entries(dictionary), handbook_entries(handbook)))
    except FileNotFoundError:
        parser.exit(1, 'pdftotext is required. Install Poppler and run again.\n')
    except subprocess.CalledProcessError as error:
        parser.exit(1, error.stderr)
    except ValueError:
        parser.exit(1, 'Could not locate the handbook glossary sections.\n')

    if not all(tables.values()):
        parser.exit(1, 'The PDFs yielded an empty lemma table.\n')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for part, rows in tables.items():
        path = args.output_dir / f'{part}-lemmas.tsv'
        path.write_text(''.join(f'{key}\t{lemma}\n' for key, lemma in rows), encoding='utf-8')
        print(f'{path.name}: {len(rows)} lemmas')


if __name__ == '__main__':
    main()
