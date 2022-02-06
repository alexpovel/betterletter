# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html#Special-Targets
# A phony target: not a file, just some routine.
.PHONY: venv tests checks formatting profile help

.DEFAULT_GOAL := help

# From https://news.ycombinator.com/item?id=30137254
define PRINT_HELP_PYSCRIPT # start of Python section
import re
import sys

output = []
# Loop through the lines in this file
for line in sys.stdin:
    # if the line has a command and a comment start with
    #   two pound signs, add it to the output
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        output.append("%-10s %s" % (target, help))
# Sort the output in alphanumeric order
output.sort()
# Print the help result
print('\n'.join(output))
endef
export PRINT_HELP_PYSCRIPT # End of python section

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

RUN = poetry run

all: tests checks

venv:  ## Install the virtual environment.
	@poetry install

release:  ## Builds, then publishes the package on PyPI.
	@poetry build
	@poetry publish

tests:  ## Run all tests.
	@echo "Running tests."
	@$(RUN) pytest

typecheck:  ## Run type checks.
	@echo "Running type checks."
	@$(RUN) mypy --package betterletter

formatting:  ## Run formatting.
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

profile: betterletter.profile  ## Profile the module using a test input.
	@$(RUN) snakeviz "$<"
