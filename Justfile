[private]
default:
    just --list --justfile {{justfile()}}

set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

poetry := "poetry run"
library := "betterletter"

# Runs development initialization steps, like installing the virtual environment.
init:
    poetry install
    {{poetry}} pre-commit install --hook-type pre-push --hook-type pre-commit --hook-type commit-msg

# Builds, then publishes the package to PyPI (requires previous login).
release:
    poetry build
    poetry publish

# Runs all available checks.
check: check-format check-lint check-types

# Runs unit tests.
test:
    {{poetry}} pytest \
        --cov={{library}} \
        --cov-report=html \
        --cov-report=term \
        --cov-report=xml \
        --capture=sys

# Runs formatting.
format:
    {{poetry}} black {{justfile_directory()}}

# Checks formatting.
check-format:
    {{poetry}} black --check --diff {{justfile_directory()}}

# Runs linting with auto-fixing.
lint:
    {{poetry}} ruff --fix {{justfile_directory()}}

# Checks linting.
check-lint:
    {{poetry}} ruff {{justfile_directory()}}
    @echo "Linting passed."

# Checks static types.
check-types:
    {{poetry}} mypy {{justfile_directory()}}

profile_file := if os_family() == "windows" { `(New-TemporaryFile).FullName` } else { `mktemp` }

# Runs profiling on a simple sample input.
profile:
    @echo "Huette Kaese Schluebbeldaebbel" | \
        {{poetry}} python -m cProfile --outfile='{{profile_file}}' -m '{{library}}' de
    {{poetry}} snakeviz '{{profile_file}}'
