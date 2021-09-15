# This script resets tables manually from the helper tables
# This operation is destruction, which is why the title refers to it as dangerous
# We omit resetting the table for articles since that table is to simple to ever require regeneration
cp manually_translated_conjunctions_helper.tsv manually_translated_conjunctions.tsv
cp manually_translated_determiners_helper.tsv manually_translated_determiners.tsv
cp manually_translated_interjections_helper.tsv manually_translated_interjections.tsv
cp manually_translated_particles_helper.tsv manually_translated_particles.tsv
cp manually_translated_prepositions_helper.tsv manually_translated_prepositions.tsv
cp manually_translated_pronouns_helper.tsv manually_translated_pronouns.tsv
