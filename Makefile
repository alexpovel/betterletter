# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html#Special-Targets
# A phony target: not a file, just some routine.
.PHONY: venv tests checks formatting profile

RUN = poetry run

all: tests checks

venv:
	@poetry install

tests:
	@echo "Running tests."
	@$(RUN) pytest

checks:
	@echo "Running type checks."
	@$(RUN) mypy --package betterletter

formatting:
	@echo "Running formatting."
	@$(RUN) black .

# Implicit rules, see:
# https://www.gnu.org/software/make/manual/html_node/Implicit-Rules.html#Implicit-Rules
# Automatic Variables, see:
# https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html
# $*: "The stem with which an implicit rule matches"
# $<: "The name of the first prerequisite"
# $@: "The file name of the target of the rule"
# $^: "The names of all the prerequisites, with spaces between them"

%.profile:
	@echo "Huette Kaese Schluebbeldaebbel" | \
		$(RUN) python -m cProfile --outfile="$@" -m "$*" de

profile: betterletter.profile
	@$(RUN) snakeviz "$<"
