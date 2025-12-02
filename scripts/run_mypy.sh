#!/bin/bash
# ./scripts/run_mypy.sh

set -e

script_dir=$(dirname $0)
cd ${script_dir}/..

pip install -U pip setuptools wheel
pip install -U -r requirements/testing.txt \
  -U -r requirements/optional.txt \
  -U -r requirements/tools.txt

mypy --config-file pyproject.toml
