#!/usr/bin/env bash

set -e
set -x

mypy giga
ruff giga tests scripts
black giga tests --check
isort giga tests scripts --check-only
codespell
