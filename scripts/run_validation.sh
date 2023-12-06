#!/bin/bash
# ./scripts/run_validation.sh

set -e

script_dir=`dirname $0`
cd ${script_dir}/..
pip install -U pip
pip install -r requirements/testing.txt \
  -r requirements/optional.txt

black --check tests/ integration_tests/
# TODO: resolve linting errors for tests
# flake8 tests/ integration_tests/

python setup.py codegen
python setup.py validate
