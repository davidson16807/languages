echo "standardize.py..."
python3 ../../vocabulary/standardize.py language.yaml > standardize.tsv
echo "part_of_speech.py..."
python3 ../../vocabulary/part_of_speech.py language.yaml > part_of_speech.tsv

echo "frequency_tallies.py..."
python3 ../../vocabulary/frequency_tallies.py language.yaml > frequency_tallies.tsv

echo "vocabulary_definition_source.py..."
python3 ../../vocabulary/vocabulary_definition_source.py language.yaml > vocabulary_definition_source.tsv
echo "vocabulary_translation_source.py..."
python3 ../../vocabulary/vocabulary_translation_source.py language.yaml > vocabulary_translation_source.tsv

echo "manually_translated_parts_of_speech_helper.py..."
python3 ../../vocabulary/manually_translated_parts_of_speech_helper.py language.yaml > manually_translated_parts_of_speech_helper.tsv
if [ ! -f manually_translated_parts_of_speech.tsv ]; then
    cp manually_translated_parts_of_speech_helper.tsv manually_translated_parts_of_speech.tsv
fi
if [ ! -f manually_translated_exceptions.tsv ]; then
    touch manually_translated_exceptions.tsv
fi

echo "vocabulary_sequence.py..."
python3 ../../vocabulary/vocabulary_sequence.py language.yaml > vocabulary_sequence.tsv

echo "vocabulary.py..."
python3 ../../vocabulary/vocabulary.py language.yaml > vocabulary.html

