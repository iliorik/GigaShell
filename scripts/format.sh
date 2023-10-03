#!/bin/sh -e
set -x

ruff giga tests scripts --fix
black giga tests scripts
isort giga tests scripts
codespell --write-changes
