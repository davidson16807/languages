# NOTE: We include Makefiles in subdirectories to allow locality of unit tests,
# Please use make files within subdirectories only for unit tests, and do not use recursively
# Subdirectory makefiles are not bad by themself, but recursive Makefiles are considered harmful! 

TEST = $(shell find ./ -type f -name '*.py')

all: $(TEST) ./Makefile
	python3 pronoun_possessives.py > pronoun-possessives.html && \
	python3 pronoun_declensions.py > pronoun-declensions.html && \
	python3 conjugations.py > conjugations.html && \
	python3 declensions.py > declensions.html && \
	python3 adjectives.py > adjectives.html && \
	python3 vocabulary.py > vocabulary.html

clean:
	rm -f *.html
