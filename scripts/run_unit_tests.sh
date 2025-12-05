#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/run_unit_tests.sh
# single: ./scripts/run_unit_tests.sh tests/slack_sdk_async/web/test_web_client_coverage.py

set -e

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pip
pip install -U -r requirements/testing.txt \
  -U -r requirements/optional.txt \
  -U -r requirements/tools.txt

echo "Generating code ..." && python scripts/codegen.py --path .
echo "Running black (code formatter) ..." && ./scripts/format.sh --no-install

echo "Running tests ..."
test_target="${1:-tests/}"
PYTHONPATH=$PWD:$PYTHONPATH pytest $test_target
